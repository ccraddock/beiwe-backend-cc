from datetime import datetime

from bson import ObjectId
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

# AJK TODO before this is run, collapse migrations

print("start:", datetime.now())
# Add the parent directory to the path in order to enable imports from sister directories
from os.path import abspath as _abspath
from sys import path as _path

_one_folder_up = _abspath(__file__).rsplit('/', 2)[0]
_path.insert(1, _one_folder_up)

from cronutils.error_handler import ErrorHandler, null_error_handler
import json

# Load the Django settings
from config import load_django

# Import Mongolia models
from db.data_access_models import ChunksRegistry as MChunkSet, ChunkRegistry as MChunk
from db.profiling import Uploads as MUploadSet
from db.study_models import (
    StudyDeviceSettings as MSettings, StudyDeviceSettingsCollection as MSettingsSet,
    Studies as MStudySet, Survey as MSurvey, Surveys as MSurveySet
)
from db.user_models import Admins as MAdminSet, Users as MUserSet

# Import Django models
from database.study_models import DeviceSettings as DSettings, Study as DStudy, Survey as DSurvey
from database.data_access_models import ChunkRegistry as DChunk
from database.profiling_models import UploadTracking as DUpload
from database.user_models import Participant as DUser, Researcher as DAdmin


class NoSuchDatabaseObject(Exception): pass
class MissingRequiredForeignKey(Exception): pass
class ObjectCreationException(Exception): pass


# Utils
def create_dummy_survey(object_id, study_object_id):
    # print orphaned_surveys
    # print object_id
    # print object_id in orphaned_surveys
    # from time import sleep
    # sleep(1)
    # if DSurvey.objects.filter(object_id=str(object_id)).exists():
    #     raise Exception("wtf")
    
    try:
        d_study = DStudy.objects.get(object_id=str(study_object_id))
    except ObjectDoesNotExist:
        d_study = create_dummy_study(study_object_id)
    
    s = DSurvey(
        survey_type=DSurvey.DUMMY_SURVEY,
        object_id=str(object_id),
        deleted=True,
        study=d_study
        # use these fields' defaults
        # content=json.dumps(m_survey['content']),
        # settings=json.dumps(m_survey['settings']),
        # timings=json.dumps(m_survey['timings'])
    )
    s.save()
    survey_id_dict[object_id] = {"pk": s.id}
    return s


def create_dummy_study(object_id):
    s = DStudy(
        name="Old Unnamed Study %s" % object_id,
        encryption_key="0"*32,
        object_id=str(object_id),
        deleted=True,
    )
    s.save()
    study_id_dict[object_id] = {"pk": s.id}
    return s


def duplicate_chunk_path_severity(chunk_path):
    """ Compare contents of all chunks matching this path, blow up if any values are different.
        (They should all be identical.) """
    collisions = {key: set() for key in MChunk.DEFAULTS.keys()}
    for key in MChunk.DEFAULTS.iterkeys():
        for chunk in MChunkSet(chunk_path=chunk_path):
            collisions[key].add(chunk[key])

    for key, collision in collisions.iteritems():
        if len(collision) > 1:
            raise Exception('actually a collision:\n%s' % collisions)


# Migration functions
def migrate_studies():
    d_study_list = []
    for m_study in MStudySet.iterator():
        with error_handler:
            # Create a Django Study object modeled off the Mongolia Study
            study_name = m_study['name']
            d_study = DStudy(
                name=study_name,
                encryption_key=m_study['encryption_key'],
                object_id=m_study['_id'],
                deleted=m_study['deleted'],
                is_test=m_study['is_test'],
            )
    
            # Validate the new Study object and add it to the bulk create list
            d_study.full_clean()
            d_study_list.append(d_study)
    
            # Get lists of Mongolia Surveys, Admins and StudyDeviceSettings attached to this Study
            m_survey_list = m_study['surveys']
            m_admin_list = m_study['admins']
            m_device_settings = m_study['device_settings']
            study_referents[study_name] = {
                'survey_list': m_survey_list,
                'admin_list': m_admin_list,
                'device_settings': m_device_settings,
            }

    # Bulk create the Django Studies
    DStudy.objects.bulk_create(d_study_list)

    # Create a reference from Mongolia Study IDs to Django Studies that doesn't require
    # any future database calls.
    for m_study in MStudySet.iterator():
        with error_handler:
            m_study_id = m_study['_id']
            d_study_id = DStudy.objects.filter(name=m_study['name']).values('pk', 'deleted').get()
            study_id_dict[m_study_id] = d_study_id


def remap_study_relationships():
    
    for study_name, object_ids in study_referents.iteritems():
        with error_handler:
        
            m_admin_id_list = object_ids['admin_list']
            m_survey_id_list = object_ids['survey_list']
            m_settings_id = object_ids['device_settings']
            d_study = DStudy.objects.get(name=study_name)
    
            for m_survey_id in m_survey_id_list:
                with error_handler:
                    m_survey = MSurvey(m_survey_id)
                    if not m_survey:
                        msg = 'Survey {} referenced by Study but does not exist.'.format(m_survey_id)
                        print(msg)
                        # raise NoSuchDatabaseObject(msg)
                    d_study_survey_dict[m_survey_id] = d_study
    
            for m_admin_id in m_admin_id_list:
                # Add the Study-Researcher pair to the list of pairs
                d_study_admin_list.append((d_study.pk, m_admin_id))
    
            m_settings = MSettings(m_settings_id)
            if not m_settings:
                msg = 'DeviceSettings {} referenced by Study but does not exist.'.format(m_settings_id)
                print(msg)
                # raise NoSuchDatabaseObject(msg)
            d_study_settings_dict[m_settings_id] = d_study


def migrate_surveys():
    d_survey_list = []
    
    # Build all Surveys
    for m_survey in MSurveySet.iterator():
        with error_handler:
            try:
                d_study = d_study_survey_dict[m_survey['_id']]
            except KeyError:  # This MSurvey has no corresponding Study
                print('Survey {} does not connect to any Study.'.format(m_survey['_id']))
                orphaned_surveys[m_survey['_id']] = m_survey
                continue
            d_survey = DSurvey(
                content=json.dumps(m_survey['content']),
                survey_type=m_survey['survey_type'],
                settings=json.dumps(m_survey['settings']),
                timings=json.dumps(m_survey['timings']),
                object_id=m_survey['_id'],
                study_id=d_study.pk,
                deleted=d_study.deleted,
            )
            
            # Validate the Survey and add it to the bulk_create list
            d_survey.full_clean()
            d_survey_list.append(d_survey)
    
    # Bulk_create the list of Researchers
    DSurvey.objects.bulk_create(d_survey_list)
    
    # Create a mapping from Surveys' Mongolia ids to their Django primary keys
    for m_survey in MSurveySet.iterator():
        with error_handler:
            m_survey_id = m_survey['_id']
            try:
                d_survey_id = DSurvey.objects.filter(object_id=m_survey['_id']).values('pk').get()
            except DSurvey.DoesNotExist:
                print('Survey {} was not created.'.format(m_survey_id))
                continue
            survey_id_dict[m_survey_id] = d_survey_id


def migrate_settings():
    d_settings_list = []
    
    # Build a new DeviceSettings object
    for m_settings in MSettingsSet.iterator():
        with error_handler:
            try:
                d_study = d_study_settings_dict[m_settings['_id']]
            except KeyError:  # This MSettings has no corresponding Study
                print('DeviceSettings {} is not connected to any Study.'.format(m_settings['_id']))
                continue
            d_settings = DSettings(
                accelerometer=m_settings['accelerometer'],
                gps=m_settings['gps'],
                calls=m_settings['calls'],
                texts=m_settings['texts'],
                wifi=m_settings['wifi'],
                bluetooth=m_settings['bluetooth'],
                power_state=m_settings['power_state'],
                proximity=m_settings['proximity'],
                gyro=m_settings['gyro'],
                magnetometer=m_settings['magnetometer'],
                devicemotion=m_settings['devicemotion'],
                reachability=m_settings['reachability'],
                allow_upload_over_cellular_data=m_settings['allow_upload_over_cellular_data'],
                accelerometer_off_duration_seconds=m_settings['accelerometer_off_duration_seconds'],
                accelerometer_on_duration_seconds=m_settings['accelerometer_on_duration_seconds'],
                bluetooth_on_duration_seconds=m_settings['bluetooth_on_duration_seconds'],
                bluetooth_total_duration_seconds=m_settings['bluetooth_total_duration_seconds'],
                bluetooth_global_offset_seconds=m_settings['bluetooth_global_offset_seconds'],
                check_for_new_surveys_frequency_seconds=m_settings['check_for_new_surveys_frequency_seconds'],
                create_new_data_files_frequency_seconds=m_settings['create_new_data_files_frequency_seconds'],
                gps_off_duration_seconds=m_settings['gps_off_duration_seconds'],
                gps_on_duration_seconds=m_settings['gps_on_duration_seconds'],
                seconds_before_auto_logout=m_settings['seconds_before_auto_logout'],
                upload_data_files_frequency_seconds=m_settings['upload_data_files_frequency_seconds'],
                voice_recording_max_time_length_seconds=m_settings['voice_recording_max_time_length_seconds'],
                wifi_log_frequency_seconds=m_settings['wifi_log_frequency_seconds'],
                gyro_off_duration_seconds=m_settings['gyro_off_duration_seconds'],
                gyro_on_duration_seconds=m_settings['gyro_on_duration_seconds'],
                magnetometer_off_duration_seconds=m_settings['magnetometer_off_duration_seconds'],
                magnetometer_on_duration_seconds=m_settings['magnetometer_on_duration_seconds'],
                devicemotion_off_duration_seconds=m_settings['devicemotion_off_duration_seconds'],
                devicemotion_on_duration_seconds=m_settings['devicemotion_on_duration_seconds'],
                about_page_text=m_settings['about_page_text'],
                call_clinician_button_text=m_settings['call_clinician_button_text'],
                consent_form_text=m_settings['consent_form_text'],
                survey_submit_success_toast_text=m_settings['survey_submit_success_toast_text'],
                consent_sections=json.dumps(m_settings['consent_sections']),
                study_id=d_study.pk,
                deleted=d_study.deleted,
            )
            
            d_settings_list.append(d_settings)
        
    # Bulk_create the objects built above
    DSettings.objects.bulk_create(d_settings_list)


def migrate_admins():
    
    d_admin_list = []
    
    # Build all Researchers
    for m_admin in MAdminSet.iterator():
        with error_handler:
            d_admin = DAdmin(
                username=m_admin['_id'],
                admin=m_admin['system_admin'],
                access_key_id=m_admin['access_key_id'] or None,  # access_key_id is unique and therefore nullable
                access_key_secret=m_admin['access_key_secret'] or '',
                access_key_secret_salt=m_admin['access_key_secret_salt'] or '',
                password=m_admin['password'] or 'NoPassword',
                salt=m_admin['salt'],
                deleted=False,
            )
            
            # Validate the Researcher and add it to the bulk_create list
            d_admin.full_clean()
            d_admin_list.append(d_admin)
    
    # Bulk_create the list of Researchers
    DAdmin.objects.bulk_create(d_admin_list)
    
    # Now that the Researchers have primary keys, fill in the Study-Researcher ManyToMany relationship
    # Create a mapping from Researcher's username to primary key
    admin_username_to_pk_dict = dict(DAdmin.objects.values_list('username', 'pk'))
    
    d_study_admin_relation_list = []
    for study_id, admin_username in d_study_admin_list:
        with error_handler:
            try:
                admin_id = admin_username_to_pk_dict[admin_username]
            except KeyError:
                # study_name = DStudy.objects.get(pk=study_id).name
                print('Admin {} is referenced by a Study but does not exist.'.format(admin_username))
                continue
            # Populate a list of database objects in the Study-Researcher relationship table
            new_relation = DAdmin.studies.through(study_id=study_id, researcher_id=admin_id)
            d_study_admin_relation_list.append(new_relation)
        
    # Bulk_create the Study-Researcher relationship objects
    with error_handler:
        DAdmin.studies.through.objects.bulk_create(d_study_admin_relation_list)


def migrate_users():

    m_user_list = MUserSet.iterator()
    d_user_list = []

    for m_user in m_user_list:
        with error_handler:

            # Get information about the Participant's Study
            m_study_id = m_user['study_id']
            try:
                d_study_info = study_id_dict[m_study_id]
            except KeyError:
                print('Study {} is referenced by a User but does not exist.'.format(m_study_id))
                continue
    
            # Django convention is to use the empty string rather than None in CharFields
            device_id = m_user['device_id'] or ''
            os_type = m_user['os_type'] or ''
    
            # Build a new Django Participant
            d_user = DUser(
                patient_id=m_user['_id'],
                device_id=device_id,
                os_type=os_type,
                study_id=d_study_info['pk'],
                password=m_user['password'],
                salt=m_user['salt'],
                deleted=d_study_info['deleted'],
            )
    
            # Validate the Participant and add it to the bulk_create list
            d_user.full_clean()
            d_user_list.append(d_user)

    # Bulk_create the Participants
    DUser.objects.bulk_create(d_user_list)

    for m_user in MUserSet.iterator():
        with error_handler:
            m_user_id = m_user['_id']
            try:
                d_user_id = DUser.objects.filter(patient_id=m_user['_id']).values('pk').get()
            except DUser.DoesNotExist:
                msg = 'User {} was not created.'.format(m_user_id)
                print(msg)
                # raise ObjectCreationException(msg)
            user_id_dict[m_user_id] = d_user_id


def migrate_chunk_registries():
    # Calculate the number of chunks that will be used to go through all of MChunkSet()
    
    d_chunk_list = []
    num_registries_handled = 0
    num_bulk_creates = 0
    for i, m_chunk in enumerate(MChunkSet.iterator()):
        if i % 10000 == 0:
            print i, "..."
        with error_handler:
            try:
                d_study_info = study_id_dict[m_chunk.study_id]
            except KeyError:
                msg = 'Study {} referenced in chunk but does not exist, creating it.'.format(m_chunk['study_id'])
                print(msg)
                create_dummy_study(m_chunk.study_id)
                # raise NoSuchDatabaseObject(msg)
            try:
                d_user_info = user_id_dict[m_chunk.user_id]
            except KeyError:
                msg = 'User {} referenced in chunk but does not exist.'.format(m_chunk['user_id'])
                print(msg)
                continue
                # raise NoSuchDatabaseObject(msg)
            
            # some chunks have survey_ids that are string representations of objectids, fix.
            # (and sometimes this can be an empty string, handle that too.)
            if m_chunk.survey_id and isinstance(m_chunk.survey_id, (str, unicode)):
                m_chunk.survey_id = ObjectId(m_chunk.survey_id)
            
            if not m_chunk.survey_id:
                d_survey_pk = None
            elif m_chunk.survey_id in survey_id_dict:
                d_survey_pk = survey_id_dict[m_chunk.survey_id]['pk']
            else:
                print('Survey {} referenced in chunk but does not exist, creating it.'.format(m_chunk.survey_id))
                new_survey = create_dummy_survey(m_chunk.survey_id, m_chunk.study_id)
                d_survey_pk = new_survey.pk

            d_chunk = DChunk(
                is_chunkable=m_chunk.is_chunkable,
                chunk_path=m_chunk.chunk_path,
                chunk_hash=m_chunk.chunk_hash or '',
                data_type=m_chunk.data_type,
                time_bin=m_chunk.time_bin,
                study_id=d_study_info['pk'],
                participant_id=d_user_info['pk'],
                survey_id=d_survey_pk,
                deleted=d_study_info['deleted'],
            )
            
            # d_chunk.full_clean()  # Don't bother full cleaning, it is slow and unnecessary here.
            d_chunk_list.append(d_chunk)
            
            num_registries_handled += 1
            if num_registries_handled % CHUNK_SIZE == 0:
                # Every 10.000 database objects, bulk create and print to stdout
                num_bulk_creates += 1
                if num_bulk_creates % 10 == 0:
                    print(num_bulk_creates * CHUNK_SIZE)
                    
                # there are a lot of unique chunk path issues
                try:
                    DChunk.objects.bulk_create(d_chunk_list)
                except IntegrityError as e:
                    # This can't happen, because chunk_path does has unique=False at the time of the
                    # migration, and only has unique=True set later in a separate Django migration.
                    if "UNIQUE" in e.message:
                        for d_chunk in d_chunk_list:
                            if DChunk.objects.filter(chunk_path=d_chunk.chunk_path).exists():
                                try:
                                    print("duplicate path:",)
                                    duplicate_chunk_path_severity(d_chunk.chunk_path)
                                    print("...nevermind.")
                                except Exception as e2:
                                    print(d_chunk.chunk_path)
                                    print(e2.message)
                                    # raise e2
                            else:
                                d_chunk.save()
                    else:
                        raise e
                finally:
                    d_chunk_list = []
    
    DChunk.objects.bulk_create(d_chunk_list)


def migrate_upload_trackers():
    d_upload_list = []
    num_uploads_handled = 0
    num_bulk_creates = 0
    for i, m_upload in enumerate(MUploadSet.iterator()):
        if i % 10000 == 0:
            print i, '...'
        with error_handler:
            try:
                d_user_info = user_id_dict[m_upload.user_id]
            except KeyError:
                msg = 'User {} referenced in upload tracker but does not exist.'.format(m_upload['user_id'])
                print(msg)
                continue
            
            d_upload = DUpload(
                file_path=m_upload.file_path,
                file_size=m_upload.file_size or 0,
                timestamp=m_upload.timestamp,
                participant_id=d_user_info['pk'],
                deleted=False,
            )
            
            d_upload_list.append(d_upload)
            
            num_uploads_handled += 1
            if num_uploads_handled % CHUNK_SIZE == 0:
                # Every 10.000 database objects, bulk create and print to stdout
                num_bulk_creates += 1
                if num_bulk_creates % 10 == 0:
                    print(num_bulk_creates * CHUNK_SIZE)
                
                DUpload.objects.bulk_create(d_upload_list)
                d_upload_list = []
    
    # Bulk create any remaining database objects
    DUpload.objects.bulk_create(d_upload_list)


def run_all_migrations():
    print "migrate_studies..."
    migrate_studies()
    print "remap_study_relationships..."
    remap_study_relationships()
    print "migrate_surveys..."
    migrate_surveys()
    print "migrate_settings..."
    migrate_settings()
    print "migrate_admins..."
    migrate_admins()
    print "migrate_users..."
    migrate_users()
    print "migrate_chunk_registries..."
    migrate_chunk_registries()
    print "migrate_upload_trackers..."
    migrate_upload_trackers()


if __name__ == '__main__':
    study_referents = {}
    study_id_dict = {}
    user_id_dict = {}
    survey_id_dict = {}
    
    orphaned_surveys = {}
    
    d_study_admin_list = []  # A list of study-researcher pairs
    d_study_survey_dict = {}  # A mapping of surveys to their associated studies
    d_study_settings_dict = {}  # A mapping of device settings to their associated studies

    CHUNK_SIZE = 10000
    
    # error_handler = ErrorHandler()
    error_handler = null_error_handler()
    
    print(MStudySet.count(), MSurveySet.count(), MSettingsSet.count(),
          MAdminSet.count(), MUserSet.count(), MChunkSet.count(), MUploadSet.count())
    with error_handler:
        run_all_migrations()
    print(DStudy.objects.count(), DSurvey.objects.count(), DSettings.objects.count(),
          DAdmin.objects.count(), DUser.objects.count(), DChunk.objects.count(), DUpload.objects.count())
    print("end:", datetime.now())
    
    error_handler.raise_errors()
