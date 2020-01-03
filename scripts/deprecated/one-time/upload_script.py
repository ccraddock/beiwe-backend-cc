import requests

AUDIO="audio"
SURVEY_ANSWERS="survey_answers"

#Notes:
# I have tried to make this as obvious and simple as possible.  The server will
# return strings if you send it invalid values that Should be sufficient.
# if you get anything like a missing parameter (which this should catch anyway).
#
# This "API" only works for survey answers and survey timings.  The files you point
# at should be unencrypted, they will be encrypted in transit (HTTPS) and by the server
# before they are put on S3.
#
# I can check what files you uploaded but if you could try and keep a record that be
# greatly appreciated.
#
# The API will not let you upload a file that already exists, though the script
# will see this behavior as an error and raise one if you do.
#
# Credentials:
# Provide your data API credentials as secret and access keys.
# Missing or invalid credentials will result in 403 errors, the server will correctly
# error and not allow you to upload to a study for which you do not have access.
#
# file_path:
# is a file path your computer can read, it does not matter what the
# name of the file is, just get the parameters correct.  This file should be the
# plain text of a survey or the mp4 file of a voice recording.
#
# user_id:
# is the unique identifier of the person who took this survey.
#
# data_stream:
# use one of the above AUDIO and SURVEY_ANSWERS strings, other strings will cause errors.
#
# survey_id:
# the survey_id of the correct survey. (Be sure to double check this one, we don't
# want erroneous survey ids, that would cause chaos. I cannot check this one server side because some surveys
# may have been deleted.)
#
# unix_millisecond_timestamp_string:
# this one is the name that the eventual file will have, which is why it is named so
# verbosely.  I don't really know what happens if you stick an int value, so please
# ensure it is a string.
#
# Send me an email if you think anything got screwed up, my job is solving that.
#
# And again, thank you for having backups and being willing to do this.
def upload_data_file(file_path=None, user_id=None, study_id=None, survey_id=None,
                     data_stream=None, unix_millisecond_timestamp_string=None,
                     secret_key=None,access_key=None):

    if not file_path: raise Exception( "you must provide a value to file_path" )
    if not user_id: raise Exception( "you must provide a value to user_id" )
    if not study_id: raise Exception( "you must provide a value to study_id" )
    if not survey_id: raise Exception( "you must provide a value to survey_id" )
    if not access_key: raise Exception( "you must provide a value to access_key" )
    if not secret_key: raise Exception( "you must provide a value to secret_key" )
    if not data_stream: raise Exception( "you must provide a value to data_stream" )

    if not unix_millisecond_timestamp_string: raise Exception( "you must provide a value to unix_millisecond_timestamp_string" )
    if not secret_key: raise Exception( "you must provide a value to secret_key" )

    with open(file_path, "rb") as f:
        r = requests.post('https://studies.beiwe.org/data-upload-apiv1',
                          files={'file':open(file_path,'rb') },
                          data={"user_id": user_id,
                                "study_id": study_id,
                                "survey_id": survey_id,
                                "unix_millisecond_timestamp_string":
                                    unix_millisecond_timestamp_string,
                                "data_stream": data_stream,
                                "access_key": access_key,
                                "secret_key": secret_key, } )

    if r.status_code != 200:
        r.raise_for_status()
    if r.text != "file successfully uploaded.":
        raise Exception(r.text)
    return [file_path, r.status_code]