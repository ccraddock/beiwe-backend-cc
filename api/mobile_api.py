import calendar
import time

from django.utils import timezone
from flask import Blueprint, request, abort, render_template, json
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequestKeyError

from config.constants import ALLOWED_EXTENSIONS, DEVICE_IDENTIFIERS_HEADER
from database.data_access_models import FileToProcess
from database.profiling_models import UploadTracking, DecryptionKeyError, ReceivedDataStats
from database.user_models import Participant
from libs.android_error_reporting import send_android_error_report
from libs.encryption import decrypt_device_file, HandledError, DecryptionKeyInvalidError
from libs.http_utils import determine_os_api
from libs.bw_logging import log_error
from libs.s3 import s3_upload
from libs.client_key_management import get_client_public_key_string, get_client_private_key
from libs.sentry import make_sentry_client
from libs.user_authentication import (authenticate_user, authenticate_user_registration,
    authenticate_user_ignore_password)
from libs.s3 import construct_s3_raw_data_path

from database.study_models import ParticipantSurvey

################################################################################
############################# GLOBALS... #######################################
################################################################################
mobile_api = Blueprint('mobile_api', __name__)

################################################################################
################################ UPLOADS #######################################
################################################################################

# @mobile_api.route('/loaderio-8ed6e63e16e9e4d07d60a051c4ca6ecb/')
# def temp():
#     from io import StringIO
#     from flask import Response
#     return Response(StringIO(u"loaderio-8ed6e63e16e9e4d07d60a051c4ca6ecb"),
#                     mimetype="txt",
#                     headers={'Content-Disposition':'attachment; filename="loaderio-8ed6e63e16e9e4d07d60a051c4ca6ecb.txt"'})


@mobile_api.route('/upload', methods=['POST'])
@mobile_api.route('/upload/ios/', methods=['GET', 'POST'])
@determine_os_api
@authenticate_user_ignore_password
def upload(OS_API=""):
    """ Entry point to upload GPS, Accelerometer, Audio, PowerState, Calls Log, Texts Log,
    Survey Response, and debugging files to s3.

    Behavior:
    The Beiwe app is supposed to delete the uploaded file if it receives an html 200 response.
    The API returns a 200 response when the file has A) been successfully handled, B) the file it
    has been sent is empty, C) the file did not decrypt properly.  We encountered problems in
    production with incorrectly encrypted files (as well as Android generating "rList" files
    under unknown circumstances) and the app then uploads them.  When the device receives a 200
    that is its signal to delete the file.
    When a file is undecryptable (this was tracked to a scenario where the device could not
    create/write an AES encryption key) we send a 200 response to stop that device attempting to
    re-upload the data.
    In the event of a single line being undecryptable (can happen due to io errors on the device)
    we drop only that line (and store the erroring line in an attempt to track it down.

    A 400 error means there is something is wrong with the uploaded file or its parameters,
    administrators will be emailed regarding this upload, the event will be logged to the apache
    log.  The app should not delete the file, it should try to upload it again at some point.

    If a 500 error occurs that means there is something wrong server side, administrators will be
    emailed and the event will be logged. The app should not delete the file, it should try to
    upload it again at some point.

    Request format:
    send an http post request to [domain name]/upload, remember to include security
    parameters (see user_authentication for documentation). Provide the contents of the file,
    encrypted (see encryption specification) and properly converted to Base64 encoded text,
    as a request parameter entitled "file".
    Provide the file name in a request parameter entitled "file_name". """
    patient_id = request.values['patient_id']
    user = Participant.objects.get(patient_id=patient_id)

    # first we check to make sure that the participant is currently registered, if not we reject the upload and
    # tell the mobile app to delete it so it will not be resent
    if user.device_id == '': 
        error_message ="an upload has failed " + patient_id
        error_message += ". Participant is not registered, returning 200 OK so device deletes bad file."
        log_error(Exception("upload error"), error_message)
        return render_template('blank.html'), 200

    # Slightly different values for iOS vs Android behavior.
    # Android sends the file data as standard form post parameter (request.values)
    # iOS sends the file as a multipart upload (so ends up in request.files)
    # if neither is found, consider the "body" of the post the file
    # ("body" post is not currently used by any client, only here for completeness)
    print('finding file contents')
    if "file" in request.files:
        uploaded_file = request.files['file']
    elif "file" in request.values:
        uploaded_file = request.values['file']
    else:
        uploaded_file = request.data
    
    if isinstance(uploaded_file, FileStorage):
        print('reading file contents')
        uploaded_file = uploaded_file.read()

    print('finding file name')
    if 'file_name' in request.values and request.values['file_name']:
        file_name = request.values['file_name']
    else:
        error_message ="an upload has failed " + patient_id
        error_message += ". Request did not include a file_name."
        log_error(Exception("upload error"), error_message)
        return render_template('blank.html'), 200
    print('filename is {0}'.format(file_name))

    if "crashlog" in file_name.lower():
        send_android_error_report(patient_id, uploaded_file)
        return render_template('blank.html'), 200

    if file_name[:6] == "rList-":
        return render_template('blank.html'), 200
   
    print('retrieving private key') 
    client_private_key = get_client_private_key(patient_id, user.study.object_id)
    print('decrypting device file') 
    try:
        uploaded_file = decrypt_device_file(patient_id, uploaded_file, client_private_key, user)
    except HandledError as e:
        # when decrypting fails, regardless of why, we rely on the decryption code
        # to log it correctly and return 200 OK to get the device to delete the file.
        # We do not want emails on these types of errors, so we use log_error explicitly.
        print("the following error was handled:")
        log_error(e, "%s; %s; %s" % (patient_id, file_name, e.message))
        return render_template('blank.html'), 200
    #This is what the decryption failure mode SHOULD be, but we are still identifying the decryption bug
    except DecryptionKeyInvalidError:
        tags = {
            "participant": patient_id,
            "operating system": "ios" if "ios" in request.path.lower() else "android",
            "DecryptionKeyError id": str(DecryptionKeyError.objects.last().id),
            "file_name": file_name,
        }
        make_sentry_client('eb', tags).captureMessage("DecryptionKeyInvalidError")
        
        return render_template('blank.html'), 200

    # print "decryption success:", file_name
    # if uploaded data a) actually exists, B) is validly named and typed...
    if uploaded_file and file_name and contains_valid_extension(file_name):
        print('constructing rawdata filename') 
        raw_data_filename = construct_s3_raw_data_path(user.study.object_id, file_name.replace("_", "/"))
        print('rawdata filename {0}'.format(raw_data_filename)) 
        s3_upload(raw_data_filename, uploaded_file, user.study.object_id, raw_path=True)
        print('file uploaded to s3, now adding to FTP') 
        FileToProcess.append_file_for_processing(raw_data_filename, user.study.object_id, participant=user)
        print('next is update upload tracking database')
        UploadTracking.objects.create(
            file_path=raw_data_filename,
            file_size=len(uploaded_file),
            timestamp=timezone.now(),
            participant=user,
        )
        print('next is update received data stats database')
        ReceivedDataStats.update_statistics(
            file_path = raw_data_filename,
            file_size = len(uploaded_file),
            timestamp = timezone.now(),
            participant = user,
        )
        print('finished processing the upload')
        return render_template('blank.html'), 200
    else:
        error_message ="an upload has failed " + patient_id + ", " + file_name + ", "
        if not uploaded_file:
            # it appears that occasionally the app creates some spurious files
            # with a name like "rList-org.beiwe.app.LoadingActivity"
            error_message += "there was no/an empty file, returning 200 OK so device deletes bad file."
            log_error(Exception("upload error"), error_message)
            return render_template('blank.html'), 200
        
        elif not file_name:
            error_message += "there was no provided file name, this is an app error."
        elif file_name and not contains_valid_extension( file_name ):
            error_message += "contains an invalid extension, it was interpretted as "
            error_message += grab_file_extension(file_name)
        else:
            error_message += "AN UNKNOWN ERROR OCCURRED."

        tags = {"upload_error": "upload error", "user_id": patient_id}
        sentry_client = make_sentry_client('eb', tags)
        sentry_client.captureMessage(error_message)
        
        return abort(400)


################################################################################
############################## Registration ####################################
################################################################################

@mobile_api.route('/register_user', methods=['GET', 'POST'])
@mobile_api.route('/register_user/ios/', methods=['GET', 'POST'])
@determine_os_api
@authenticate_user_registration
def register_user(OS_API=""):
    """ Checks that the patient id has been granted, and that there is no device registered with
    that id.  If the patient id has no device registered it registers this device and logs the
    bluetooth mac address.
    Check the documentation in user_authentication to ensure you have provided the proper credentials.
    Returns the encryption key for this patient/user. """

    #CASE: If the id and password combination do not match, the decorator returns a 403 error.
    #the following parameter values are required.
    patient_id = request.values['patient_id']
    phone_number = request.values['phone_number']
    device_id = request.values['device_id']

    # These values may not be returned by earlier versions of the beiwe app
    try: device_os = request.values['device_os']
    except BadRequestKeyError: device_os = "none"
    try: os_version = request.values['os_version']
    except BadRequestKeyError: os_version = "none"
    try: product = request.values["product"]
    except BadRequestKeyError: product = "none"
    try: brand = request.values["brand"]
    except BadRequestKeyError: brand = "none"
    try: hardware_id = request.values["hardware_id"]
    except BadRequestKeyError: hardware_id = "none"
    try: manufacturer = request.values["manufacturer"]
    except BadRequestKeyError: manufacturer = "none"
    try: model = request.values["model"]
    except BadRequestKeyError: model = "none"
    try: beiwe_version = request.values["beiwe_version"]
    except BadRequestKeyError: beiwe_version = "none"
    # This value may not be returned by later versions of the beiwe app.
    try: mac_address = request.values['bluetooth_id']
    except BadRequestKeyError: mac_address = "none"

    user = Participant.objects.get(patient_id=patient_id)
    study_id = user.study.object_id

    if user.device_id and user.device_id != request.values['device_id']:
        # CASE: this patient has a registered a device already and it does not match this device.
        #   They need to contact the study and unregister their their other device.  The device
        #   will receive a 405 error and should alert the user accordingly.
        # Provided a user does not completely reset their device (which resets the device's
        # unique identifier) they user CAN reregister an existing device, the unlock key they
        # need to enter to at registration is their old password.
        # KG: 405 is good for IOS and Android, no need to check OS_API
        return abort(405)
    
    if user.os_type and user.os_type != OS_API:
        # CASE: this patient has registered, but the user was previously registered with a
        # different device type. To keep the CSV munging code sane and data consistent (don't
        # cross the iOS and Android data streams!) we disallow it.
        return abort(400)
    
    # At this point the device has been checked for validity and will be registered successfully.
    # Any errors after this point will be server errors and return 500 codes. the final return
    # will be the encryption key associated with this user.
    
    # Upload the user's various identifiers.
    unix_time = str(calendar.timegm(time.gmtime()))
    file_name = patient_id + '/identifiers_' + unix_time + ".csv"
    
    # Construct a manual csv of the device attributes
    file_contents = (DEVICE_IDENTIFIERS_HEADER + "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" %
                     (patient_id, mac_address, phone_number, device_id, device_os,
                      os_version, product, brand, hardware_id, manufacturer, model,
                      beiwe_version))
    # print(file_contents + "\n")
    raw_data_filename = construct_s3_raw_data_path(user.study.object_id, file_name)
    s3_upload(raw_data_filename, file_contents, user.study.object_id, raw_path=True)
    FileToProcess.append_file_for_processing(raw_data_filename, user.study.object_id, participant=user)

    # set up device.
    user.set_device(device_id)
    user.set_os_type(OS_API)
    user.set_password(request.values['new_password'])
    device_settings = user.study.device_settings.as_native_python()
    device_settings.pop('_id', None)
    return_obj = {'client_public_key': get_client_public_key_string(patient_id, study_id),
                  'device_settings': device_settings}
    return json.dumps(return_obj), 200


################################################################################
############################### USER FUNCTIONS #################################
################################################################################

@mobile_api.route('/set_password', methods=['GET', 'POST'])
@mobile_api.route('/set_password/ios/', methods=['GET', 'POST'])
@determine_os_api
@authenticate_user
def set_password(OS_API=""):
    """ After authenticating a user, sets the new password and returns 200.
    Provide the new password in a parameter named "new_password"."""
    participant = Participant.objects.get(patient_id=request.values['patient_id'])
    participant.set_password(request.values["new_password"])
    return render_template('blank.html'), 200

################################################################################
########################## FILE NAME FUNCTIONALITY #############################
################################################################################


def grab_file_extension(file_name):
    """ grabs the chunk of text after the final period. """
    return file_name.rsplit('.', 1)[1]


def contains_valid_extension(file_name):
    """ Checks if string has a recognized file extension, this is not necessarily limited to 4 characters. """
    return '.' in file_name and grab_file_extension(file_name) in ALLOWED_EXTENSIONS

################################################################################
################################# Download #####################################
################################################################################

def get_surveys_for_participant(participant, requesting_os):

    survey_json_list = []
    for survey in ParticipantSurvey.objects.filter(participant=participant, deleted=False):

        try:
            survey_dict = survey.as_native_python()
        except:
            print("Could not decode survey {0} {1}".format(survey.object_id, survey.name))
            raise

        # Make the dict look like the old Mongolia-style dict that the frontend is expecting
        survey_dict.pop('id')
        survey_dict.pop('deleted')
        survey_dict.pop('name')
        survey_dict['_id'] = survey_dict.pop('object_id')

        # Exclude image surveys for the Android app to avoid crashing it
        if requesting_os == "ANDROID" and survey.survey_type == "image_survey":
            pass
        else:
            survey_json_list.append(survey_dict)

    return survey_json_list

@mobile_api.route('/download_surveys', methods=['GET', 'POST'])
@mobile_api.route('/download_surveys/ios/', methods=['GET', 'POST'])
@determine_os_api
# @authenticate_user
def get_latest_surveys(OS_API=""):
    participant = Participant.objects.get(patient_id=request.values['patient_id'])
    study = participant.study
    surveys = study.get_surveys_for_study(requesting_os=OS_API)
    pt_surveys = get_surveys_for_participant(participant, requesting_os=OS_API)
    if pt_surveys:
        surveys += pt_surveys
    print("received get_survey {0}: returning {1} surveys".format(request.values, len(surveys)))
    return json.dumps(surveys)
