import json

from flask import Blueprint, flash, Markup, redirect, render_template, request,\
    session

from libs import admin_authentication
from libs.admin_authentication import authenticate_admin_login,\
    authenticate_admin_study_access, get_admins_allowed_studies, get_admins_allowed_studies_as_query_set,\
    admin_is_system_admin
from libs.security import check_password_requirements

from database.study_models import Study
from database.user_models import Researcher, ParticipantAliases, Participant
from database.data_access_models import ChunkRegistry
from database.profiling_models import ReceivedDataStats
from datetime import datetime
from collections import OrderedDict
import numpy
import sys 
import pytz

admin_pages = Blueprint('admin_pages', __name__)

# TODO: Document.


@admin_pages.route('/choose_study', methods=['GET'])
@authenticate_admin_login
def choose_study():
    allowed_studies = get_admins_allowed_studies_as_query_set()

    # If the admin is authorized to view exactly 1 study, redirect to that study
    if allowed_studies.count() == 1:
        return redirect('/view_study/{:d}'.format(allowed_studies.values_list('pk', flat=True).get()))

    # Otherwise, show the "Choose Study" page
    allowed_studies_json = Study.query_set_as_native_json(allowed_studies)
    return render_template(
        'choose_study.html',
        studies=allowed_studies_json,
        allowed_studies=allowed_studies_json,
        system_admin=admin_is_system_admin()
    )

@admin_pages.route('/create_new_alias/<string:study_id>', methods=['GET', 'POST'])
@authenticate_admin_study_access
def create_new_alias(study_id=None):
    if request.method == 'GET':
        return render_template(
            'create_new_alias.html',
            study_id=study_id,
            allowed_studies=get_admins_allowed_studies(),
            system_admin=admin_is_system_admin()
        )

    # Drop any whitespace or special characters from the username
    reference_id = ''.join(e for e in request.form.get('reference_id', '') if e.isalnum())
    alias_id = ''.join(e for e in request.form.get('alias_id', '') if e.isalnum())

    for participant_id in [reference_id, alias_id]:
        if not Participant.objects.filter(patient_id=participant_id).exists():
            flash('ID {0} was not found in the Participant database, alias was not added to database'.format(participant_id), 'danger')
            return redirect('/create_new_alias/{:d}'.format(int(study_id)))

    if ParticipantAliases.objects.filter(reference_id=reference_id, alias_id=alias_id).exists():
        flash("There is already an alias {0} => {1}".format(reference_id, alias_id), 'danger')
        return redirect('/create_new_alias/{:d}'.format(int(study_id)))

    try:
        new_alias = ParticipantAliases(study_id=study_id, reference_id=reference_id, alias_id=alias_id)
        new_alias.save()
    except:
        flash("Error, There is a problem with one or both of the entered IDs ({0}, {1}). They should be 8 character alphanumeric strings.".format(reference_id, alias_id), 'danger')
        return redirect('/create_new_alias/{:d}'.format(int(study_id)))

    return redirect('/view_study/{:d}'.format(int(study_id)))

@admin_pages.route('/delete_alias', methods=["POST"])
@authenticate_admin_study_access
def delete_alias():
    """
    Deletes an alias from the ParticipantsAlias table
    """

    alias_id = request.values['alias_id']
    study_id = request.values['study_id']
    try:
        ParticipantAliases.objects.filter(id=alias_id).delete()
    except:
        flash('Sorry, something went wrong when trying to delete the alias.', 'danger')

    return redirect('/view_study/{:s}'.format(study_id))

@admin_pages.route('/view_study/<string:study_id>', methods=['GET'])
@authenticate_admin_study_access
def view_study(study_id=None):

    settings_strings = { 'accelerometer': 'Accelerometer', 'bluetooth': 'Bluetooth', 'calls': 'Calls', 'gps': 'GPS', 
        'identifiers': 'Identifiers', 'app_log': 'Android Log', 'ios_log': 'IOS Log', 'power_state': 'Power State', 
        'survey_answers': 'Survey Answers', 'survey_timings': 'Survey Timings', 'texts': 'Texts', 
        'audio_recordings': 'Audio Recordings', 'image_survey': 'Image Survey', 'wifi': 'Wifi', 'proximity': 'Proximity', 
        'gyro': 'Gyro', 'magnetometer': 'Magnetometer', 'devicemotion': 'Device Motion', 'reachability': 'Reachability' }
    study = Study.objects.get(pk=study_id)
    settings = study.get_study_device_settings().as_native_python()
    data_types_dict = {}
    for setting_key, setting_label in settings_strings.items():
        if setting_key in settings and settings[setting_key] is True:
            data_types_dict[setting_key] = setting_label
    tracking_survey_ids = study.get_survey_ids_and_object_ids_for_study('tracking_survey')
    if len(tracking_survey_ids) > 0:
        data_types_dict['survey_answers'] = settings_strings['survey_answers']
        data_types_dict['survey_timings'] = settings_strings['survey_timings']
    audio_survey_ids = study.get_survey_ids_and_object_ids_for_study('audio_survey')
    if len(audio_survey_ids) > 0:
        data_types_dict['audio_recordings'] = settings_strings['audio_recordings']
    image_survey_ids = study.get_survey_ids_and_object_ids_for_study('image_survey')
    participants = study.participants.all()

    data_types_dict = OrderedDict(sorted(data_types_dict.items(), key=lambda t: t[0]))

    #print >> sys.stderr, data_types_dict


    #chunk_fields = ["pk", "participant_id", "data_type", "chunk_path", "time_bin", "chunk_hash",
                    #"participant__patient_id", "study_id", "survey_id", "survey__object_id"]

    #data_received_dates = {}
    #for participant in participants:
        #if not participant.patient_id in data_received_dates:
            #data_received_dates[participant.patient_id] = {}
        #for data_type in data_types_dict.keys():
            #latest_chunk = ChunkRegistry.objects.filter(study_id=study_id,
                                                        #participant__patient_id=participant.patient_id,
                                                        #data_type=data_type).order_by('-time_bin').first()
            #if latest_chunk:
                #data_received_dates[participant.patient_id][data_type] = latest_chunk.time_bin

    #participant_ids = [participant.patient_id for participant in participants]
    #chunks = ChunkRegistry.get_chunks_time_range(study_id = study_id, user_ids = participant_ids).values(*chunk_fields)
    #print >> sys.stderr, chunks
    #for chunk in chunks:
        #pt = chunk['participant__patient_id']
        #dt = chunk['data_type']
        #time_bin = chunk['time_bin']


        #if not dt in data_received_dates[pt] or time_bin > data_received_dates[pt][dt]:
            #data_received_dates[pt][dt] = time_bin

    #datetime_now = datetime.now()
    #fmt = "%Y-%m-%d %H:%M:%S"
    #received_data = {}
    #for participant in data_received_dates.keys():
        #if not participant in received_data:
            #received_data[participant] = {}
        #for dt in data_received_dates[participant].keys():
            #if not dt in received_data[participant]:
                #received_data[participant][dt] = {}
#
            #date_diff = (datetime_now - data_received_dates[participant][dt]).total_seconds() / 3600.0
            #date_string = data_received_dates[participant][dt].replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Chicago')).strftime(fmt)
#
            #if date_diff < 6.0:
                 #date_color = 'btn-success'
            #if date_diff >= 6.0:
                 #date_color = 'btn-warning'
            #if date_diff >= 12.0:
                 #date_color = 'btn-danger'
           #
            #received_data[participant][dt]['date_color'] = date_color
            #received_data[participant][dt]['date_string'] = date_string
            ##print >> sys.stderr, "%s %f %s"%(date_string, date_diff, date_color)

    aliases = ParticipantAliases.objects.filter(study_id=study_id)

    return render_template(
        'view_study.html',
        study=study,
        patients=participants,
        aliases=aliases,
        data_types=data_types_dict,
        audio_survey_ids=audio_survey_ids,
        image_survey_ids=image_survey_ids,
        tracking_survey_ids=tracking_survey_ids,
        allowed_studies=get_admins_allowed_studies(),
        system_admin=admin_is_system_admin()
    )

@admin_pages.route('/view_statistics/<string:study_id>', methods=['GET'])
@authenticate_admin_study_access
def view_statistics(study_id=None):

    settings_strings = { 'accelerometer': 'Accelerometer', 'bluetooth': 'Bluetooth', 'calls': 'Calls', 'gps': 'GPS', 
        'identifiers': 'Identifiers', 'app_log': 'Android Log', 'ios_log': 'IOS Log', 'power_state': 'Power State', 
        'survey_answers': 'Survey Answers', 'survey_timings': 'Survey Timings', 'texts': 'Texts', 
        'audio_recordings': 'Audio Recordings', 'image_survey': 'Image Survey', 'wifi': 'Wifi', 'proximity': 'Proximity', 
        'gyro': 'Gyro', 'magnetometer': 'Magnetometer', 'devicemotion': 'Device Motion', 'reachability': 'Reachability' }

    study = Study.objects.get(pk=study_id)
    settings = study.get_study_device_settings().as_native_python()

    data_types_dict = {}
    for setting_key, setting_label in settings_strings.items():
        if setting_key in settings and settings[setting_key] is True:
            data_types_dict[setting_key] = setting_label

    tracking_survey_ids = study.get_survey_ids_and_object_ids_for_study('tracking_survey')
    if len(tracking_survey_ids) > 0:
        data_types_dict['survey_answers'] = settings_strings['survey_answers']
        data_types_dict['survey_timings'] = settings_strings['survey_timings']

    audio_survey_ids = study.get_survey_ids_and_object_ids_for_study('audio_survey')
    if len(audio_survey_ids) > 0:
        data_types_dict['audio_recordings'] = settings_strings['audio_recordings']

    image_survey_ids = study.get_survey_ids_and_object_ids_for_study('image_survey')
    participants = study.participants.exclude(os_type__exact='')

    data_types_dict = OrderedDict(sorted(data_types_dict.items(), key=lambda t: t[0]))

    datetime_now = datetime.now()
    date_format = "%Y-%m-%d %H:%M:%S"

    received_data_stats_dict = {}
    received_data_stats_totals_dict = {}
    for stat in ReceivedDataStats.objects.filter(participant__in=participants):

        if stat.data_type not in received_data_stats_totals_dict:
            received_data_stats_totals_dict[stat.data_type] = {'number_of_uploads':0, 'number_bytes_uploaded':0}

        received_data_stats_totals_dict[stat.data_type]['number_of_uploads'] += stat.number_of_uploads
        received_data_stats_totals_dict[stat.data_type]['number_bytes_uploaded'] += stat.number_bytes_uploaded

        date_diff = (datetime_now - stat.last_upload_timestamp).total_seconds() / 3600.0
        date_diff_days = int(numpy.floor(date_diff / 24.0))
        date_string = stat.last_upload_timestamp.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/Chicago')).strftime(date_format)

        if stat.participant.patient_id not in received_data_stats_dict:
            received_data_stats_dict[stat.participant.patient_id] = { 'days_since_last_contact': date_diff_days }
        elif date_diff_days < received_data_stats_dict[stat.participant.patient_id]['days_since_last_contact']:
            received_data_stats_dict[stat.participant.patient_id]['days_since_last_contact'] = date_diff_days

        if stat.number_bytes_uploaded / 1024.0 < 1.0:
            download_size_string = '{:d} B'.format(stat.number_bytes_uploaded)
        elif stat.number_bytes_uploaded / 1024.0 ** 2 < 1.0:
            download_size_string = '{:0.1f} KB'.format(stat.number_bytes_uploaded / 1024.0)
        elif stat.number_bytes_uploaded / 1024.0 ** 3 < 1.0:
            download_size_string = '{:0.1f} MB'.format(stat.number_bytes_uploaded / (1024.0 ** 2))
        else:
            download_size_string = '{:0.1f} GB'.format(stat.number_bytes_uploaded / (1024.0 ** 3))

        stats_string = '{0} | {1} | {2}'.format(stat.number_of_uploads, download_size_string, date_string)

        if date_diff < 6.0:
            date_color = 'btn-success'
        if date_diff >= 6.0:
            date_color = 'btn-warning'
        if date_diff >= 12.0:
            date_color = 'btn-danger'

        received_data_stats_dict[stat.participant.patient_id][stat.data_type] = \
            {
              'stats_string': stats_string,
              'stats_color': date_color,
            }

    for data_type in received_data_stats_totals_dict.keys():

        if received_data_stats_totals_dict[data_type]['number_bytes_uploaded'] / 1024.0 < 1.0:
            received_data_stats_totals_dict[data_type]['size_string'] = '{:d} B'.format(received_data_stats_totals_dict[data_type]['number_bytes_uploaded'])
        elif received_data_stats_totals_dict[data_type]['number_bytes_uploaded'] / 1024.0 ** 2 < 1.0:
            received_data_stats_totals_dict[data_type]['size_string'] = '{:0.1f} KB'.format(received_data_stats_totals_dict[data_type]['number_bytes_uploaded'] / 1024.0)
        elif received_data_stats_totals_dict[data_type]['number_bytes_uploaded'] / 1024.0 ** 3 < 1.0:
            received_data_stats_totals_dict[data_type]['size_string'] = '{:0.1f} MB'.format(received_data_stats_totals_dict[data_type]['number_bytes_uploaded'] / (1024.0 ** 2))
        else:
            received_data_stats_totals_dict[data_type]['size_string'] = '{:0.1f} GB'.format(received_data_stats_totals_dict[data_type]['number_bytes_uploaded'] / (1024.0 ** 3))

    return render_template(
        'view_statistics.html',
        study=study,
        patients=participants,
        data_types=data_types_dict,
        received_data_stats=received_data_stats_dict,
        received_data_stats_totals=received_data_stats_totals_dict,
        allowed_studies=get_admins_allowed_studies(),
        system_admin=admin_is_system_admin()
    )


@admin_pages.route('/data-pipeline/<string:study_id>', methods=['GET'])
@authenticate_admin_study_access
def view_study_data_pipeline(study_id=None):
    study = Study.objects.get(pk=study_id)
    pipelines = study.study_pipelines.all()
    study_participants = [str(user.patient_id) for user in study.participants.exclude(os_type__exact='')]

    return render_template(
        'data-pipeline.html',
        study=study,
        pipelines=pipelines,
        study_participants=study_participants,
        allowed_studies=get_admins_allowed_studies(),
    )


"""########################## Login/Logoff ##################################"""


@admin_pages.route('/')
@admin_pages.route('/admin')
def render_login_page():
    if admin_authentication.is_logged_in():
        return redirect("/choose_study")
    return render_template('admin_login.html')


@admin_pages.route("/logout")
def logout():
    admin_authentication.logout_loggedin_admin()
    return redirect("/")


@admin_pages.route("/validate_login", methods=["GET", "POST"])
def login():
    """ Authenticates administrator login, redirects to login page if authentication fails. """
    if request.method == 'POST':
        username = request.values["username"]
        password = request.values["password"]
        if Researcher.check_password(username, password):
            admin_authentication.log_in_admin(username)
            return redirect("/choose_study")
        else:
            flash("Incorrect username & password combination; try again.", 'danger')

    return redirect("/")


@admin_pages.route('/manage_credentials')
@authenticate_admin_login
def manage_credentials():
    return render_template('manage_credentials.html',
                           allowed_studies=get_admins_allowed_studies(),
                           system_admin=admin_is_system_admin())


@admin_pages.route('/reset_admin_password', methods=['POST'])
@authenticate_admin_login
def reset_admin_password():
    username = session['admin_username']
    current_password = request.values['current_password']
    new_password = request.values['new_password']
    confirm_new_password = request.values['confirm_new_password']
    if not Researcher.check_password(username, current_password):
        flash("The Current Password you have entered is invalid", 'danger')
        return redirect('/manage_credentials')
    if not check_password_requirements(new_password, flash_message=True):
        return redirect("/manage_credentials")
    if new_password != confirm_new_password:
        flash("New Password does not match Confirm New Password", 'danger')
        return redirect('/manage_credentials')
    Researcher.objects.get(username=username).set_password(new_password)
    flash("Your password has been reset!", 'success')
    return redirect('/manage_credentials')


@admin_pages.route('/reset_download_api_credentials', methods=['POST'])
@authenticate_admin_login
def reset_download_api_credentials():
    researcher = Researcher.objects.get(username=session['admin_username'])
    access_key, secret_key = researcher.reset_access_credentials()
    msg = """<h3>Your Data-Download API access credentials have been reset!</h3>
        <p>Your new <b>Access Key</b> is:
          <div class="container-fluid">
            <textarea rows="1" cols="85" readonly="readonly" onclick="this.focus();this.select()">%s</textarea></p>
          </div>
        <p>Your new <b>Secret Key</b> is:
          <div class="container-fluid">
            <textarea rows="1" cols="85" readonly="readonly" onclick="this.focus();this.select()">%s</textarea></p>
          </div>
        <p>Please record these somewhere; they will not be shown again!</p>""" \
        % (access_key, secret_key)
    flash(Markup(msg), 'warning')
    return redirect("/manage_credentials")
