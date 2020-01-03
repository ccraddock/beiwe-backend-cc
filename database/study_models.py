# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import models
from django.db.models import F, Func
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from config.study_constants import (
    ABOUT_PAGE_TEXT, CONSENT_FORM_TEXT, DEFAULT_CONSENT_SECTIONS_JSON,
    SURVEY_SUBMIT_SUCCESS_TOAST_TEXT, AUDIO_SURVEY_SETTINGS, IMAGE_SURVEY_SETTINGS
)
from database.user_models import Researcher
from database.validators import (
    LengthValidator
)

from database.models import JSONTextField, AbstractModel, is_object_id


class Study(AbstractModel):
    
    # When a Study object is created, a default DeviceSettings object is automatically
    # created alongside it. If the Study is created via the researcher interface (as it
    # usually is) the researcher is immediately shown the DeviceSettings to edit. The code
    # to create the DeviceSettings object is in database.signals.populate_study_device_settings.
    name = models.TextField(unique=True, help_text='Name of the study; can be of any length')
    encryption_key = models.CharField(max_length=32, validators=[LengthValidator(32)],
                                      help_text='Key used for encrypting the study data')
    object_id = models.CharField(max_length=24, unique=True, validators=[LengthValidator(24)],
                                 help_text='ID used for naming S3 files')

    is_test = models.BooleanField(default=True)
    
    @classmethod
    def create_with_object_id(cls, **kwargs):
        """
        Creates a new study with a populated object_id field
        """
        
        study = cls(object_id=cls.generate_objectid_string("object_id"), **kwargs)
        study.save()
        return study

    @classmethod
    def get_all_studies_by_name(cls):
        """
        Sort the un-deleted Studies a-z by name, ignoring case.
        """
        return (cls.objects
                .filter(deleted=False)
                .annotate(name_lower=Func(F('name'), function='LOWER'))
                .order_by('name_lower'))

    def get_surveys_for_study(self, requesting_os):
        survey_json_list = []
        for survey in self.surveys.filter(deleted=False):
            survey_dict = survey.as_native_python()
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

    def get_survey_ids_for_study(self, survey_type='tracking_survey'):
        return self.surveys.filter(survey_type=survey_type, deleted=False).values_list('id', flat=True)

    def get_survey_ids_and_object_ids_for_study(self, survey_type='tracking_survey'):
        return self.surveys.filter(survey_type=survey_type, deleted=False).values_list('id', 'object_id', 'name')

    def get_survey_timings_for_study(self, survey_type='tracking_survey'):
        return self.surveys.filter(survey_type=survey_type, deleted=False).values_list('id', 'object_id', 'name', 'timings')

    def get_study_device_settings(self):
        return self.device_settings

    def get_researchers(self):
        return Researcher.objects.filter(studies=self)

    # We override the as_native_python function to not include the encryption key.
    def as_native_python(self, remove_timestamps=True, remove_encryption_key=True):
        ret = super(Study, self).as_native_python(remove_timestamps=remove_timestamps)
        ret.pop("encryption_key")
        return ret

class StudyConfig(AbstractModel):

    study = models.ForeignKey('Study', on_delete=models.PROTECT)
    study_configuration = JSONField()

    @classmethod
    def create_from_file(cls, json_file):

        with open(json_file, 'r') as json_fd:
            study_configuration = json.load(json_fd)

        if 'STUDY_OBJECT_ID' not in study_configuration:
            raise ValueError('Configuration file {0} does not contain a STUDY_OBJECT_ID key or value'.format(json_file))

        # check to see if the config alread exists, if it does, delete it and then re-add
        study_configs = cls.objects.exclude(deleted=True).filter(study__object_id=study_configuration['STUDY_OBJECT_ID'])

        for study_config in study_configs.all():
            print('Found an existing study configuration for {0}, replacing with contents of file {1}'.format(study_configuration['STUDY_OBJECT_ID'], json_file))
            study_config.mark_deleted()

        # connect to the database to get a list of data
        if not is_object_id(study_configuration['STUDY_OBJECT_ID']):
            raise ValueError('{0} is not a correct study object id'.format(study_configuration['STUDY_OBJECT_ID']))

        try:
            print('Looking for study {0}'.format(study_configuration['STUDY_OBJECT_ID']))
            study = Study.objects.get(object_id=study_configuration['STUDY_OBJECT_ID'])
        except Study.DoesNotExist:
            print('Study {0} does not exist.'.format(study_configuration['STUDY_OBJECT_ID']))
            raise

        return cls.objects.create(**{'study': study, 'study_configuration': study_configuration}) 
    
class AbstractSurvey(AbstractModel):
    """ AbstractSurvey contains all fields that we want to have copied into a survey backup whenever
    it is updated. """
    
    AUDIO_SURVEY = 'audio_survey'
    TRACKING_SURVEY = 'tracking_survey'
    DUMMY_SURVEY = 'dummy'
    IMAGE_SURVEY = 'image_survey'
    SURVEY_TYPE_CHOICES = (
        (AUDIO_SURVEY, AUDIO_SURVEY),
        (TRACKING_SURVEY, TRACKING_SURVEY),
        (DUMMY_SURVEY, DUMMY_SURVEY),
        (IMAGE_SURVEY, IMAGE_SURVEY)
    )
   
    name = models.TextField(unique=True, null=False, help_text='Name of the study; can be of any length')
    content = JSONTextField(default='[]', help_text='JSON blob containing information about the survey questions.')
    survey_type = models.CharField(max_length=16, choices=SURVEY_TYPE_CHOICES,
                                   help_text='What type of survey this is.')
    settings = JSONTextField(default='{}', help_text='JSON blob containing settings for the survey.')
    timings = JSONTextField(default=json.dumps([[], [], [], [], [], [], []]),
                            help_text='JSON blob containing the times at which the survey is sent.')

    def mark_deleted(self):
        self.name = '{0} Deleted {1}'.format(self.name, timezone.now().isoformat())
        self.deleted = True
        self.save()

    class Meta:
        abstract = True


class Survey(AbstractSurvey):
    """
    Surveys contain all information the app needs to display the survey correctly to a participant,
    and when it should push the notifications to take the survey.

    Surveys must have a 'survey_type', which is a string declaring the type of survey it
    contains, which the app uses to display the correct interface.

    Surveys contain 'content', which is a JSON blob that is unpacked on the app and displayed
    to the participant in the form indicated by the survey_type.

    Timings schema: a survey must indicate the day of week and time of day on which to trigger;
    by default it contains no values. The timings schema mimics the Java.util.Calendar.DayOfWeek
    specification: it is zero-indexed with day 0 as Sunday. 'timings' is a list of 7 lists, each
    inner list containing any number of times of the day. Times of day are integer values
    indicating the number of seconds past midnight.
    
    Inherits the following fields from AbstractSurvey
    content
    survey_type
    settings
    timings
    """

    # This is required for file name and path generation
    object_id = models.CharField(max_length=24, unique=True, validators=[LengthValidator(24)])
    # the study field is not inherited because we need to change its related name
    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='surveys')

    @classmethod
    def create_with_object_id(cls, **kwargs):
        object_id = cls.generate_objectid_string("object_id")
        survey = cls.objects.create(object_id=object_id, **kwargs)
        return survey

    @classmethod
    def create_with_settings(cls, survey_type, **kwargs):
        """
        Create a new Survey with the provided survey type and attached to the given Study,
        as well as any other given keyword arguments. If the Survey is audio/image and no other
        settings are given, give it the default audio/image survey settings.
        """
        
        if survey_type == cls.AUDIO_SURVEY and 'settings' not in kwargs:
            kwargs['settings'] = json.dumps(AUDIO_SURVEY_SETTINGS)
        elif survey_type == cls.IMAGE_SURVEY and 'settings' not in kwargs:
            kwargs['settings'] = json.dumps(IMAGE_SURVEY_SETTINGS)

        survey = cls.create_with_object_id(survey_type=survey_type, **kwargs)
        return survey

class ParticipantSurvey(AbstractSurvey):
    """
    Survey can now be participant specific!

    Surveys contain all information the app needs to display the survey correctly to a participant,
    and when it should push the notifications to take the survey.

    Surveys must have a 'survey_type', which is a string declaring the type of survey it
    contains, which the app uses to display the correct interface.

    Surveys contain 'content', which is a JSON blob that is unpacked on the app and displayed
    to the participant in the form indicated by the survey_type.

    Timings schema: a survey must indicate the day of week and time of day on which to trigger;
    by default it contains no values. The timings schema mimics the Java.util.Calendar.DayOfWeek
    specification: it is zero-indexed with day 0 as Sunday. 'timings' is a list of 7 lists, each
    inner list containing any number of times of the day. Times of day are integer values
    indicating the number of seconds past midnight.
    
    Inherits the following fields from AbstractSurvey
    content
    survey_type
    settings
    timings
    """

    # This is required for file name and path generation
    object_id = models.CharField(max_length=24, unique=True, validators=[LengthValidator(24)])
    # the study field is not inherited because we need to change its related name
    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='participant_surveys')
    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='participant_surveys')

    @classmethod
    def create_with_object_id(cls, **kwargs):
        object_id = cls.generate_objectid_string("object_id")
        survey = cls.objects.create(object_id=object_id, **kwargs)
        return survey

    @classmethod
    def create_with_settings(cls, survey_type, **kwargs):
        """
        Create a new Survey with the provided survey type and attached to the given Study,
        as well as any other given keyword arguments. If the Survey is audio/image and no other
        settings are given, give it the default audio/image survey settings.
        """
        
        if survey_type == cls.AUDIO_SURVEY and 'settings' not in kwargs:
            kwargs['settings'] = json.dumps(AUDIO_SURVEY_SETTINGS)
        elif survey_type == cls.IMAGE_SURVEY and 'settings' not in kwargs:
            kwargs['settings'] = json.dumps(IMAGE_SURVEY_SETTINGS)

        survey = cls.create_with_object_id(survey_type=survey_type, **kwargs)
        return survey

class SurveyArchive(AbstractSurvey):
    """ All felds declared in abstract survey are copied whenever a change is made to a survey """
    archive_start = models.DateTimeField()
    archive_end = models.DateTimeField(default=timezone.now)
    # two new foreign key references
    survey = models.ForeignKey('Survey', on_delete=models.PROTECT, related_name='archives')
    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='surveys_archive')


class DeviceSettings(AbstractModel):
    """
    The DeviceSettings database contains the structure that defines
    settings pushed to devices of users in of a study.
    """

    # Whether various device options are turned on
    accelerometer = models.BooleanField(default=True)
    gps = models.BooleanField(default=True)
    calls = models.BooleanField(default=True)
    texts = models.BooleanField(default=True)
    wifi = models.BooleanField(default=True)
    bluetooth = models.BooleanField(default=False)
    power_state = models.BooleanField(default=True)
    use_anonymized_hashing = models.BooleanField(default=True)

    # Whether iOS-specific data streams are turned on
    proximity = models.BooleanField(default=False)
    gyro = models.BooleanField(default=False)
    magnetometer = models.BooleanField(default=False)
    devicemotion = models.BooleanField(default=False)
    reachability = models.BooleanField(default=True)

    # Upload over cellular data or only over WiFi (WiFi-only is default)
    allow_upload_over_cellular_data = models.BooleanField(default=False)

    # Timer variables
    accelerometer_off_duration_seconds = models.PositiveIntegerField(default=10)
    accelerometer_on_duration_seconds = models.PositiveIntegerField(default=10)
    bluetooth_on_duration_seconds = models.PositiveIntegerField(default=60)
    bluetooth_total_duration_seconds = models.PositiveIntegerField(default=300)
    bluetooth_global_offset_seconds = models.PositiveIntegerField(default=0)
    check_for_new_surveys_frequency_seconds = models.PositiveIntegerField(default=3600 * 6)
    create_new_data_files_frequency_seconds = models.PositiveIntegerField(default=15 * 60)
    gps_off_duration_seconds = models.PositiveIntegerField(default=600)
    gps_on_duration_seconds = models.PositiveIntegerField(default=60)
    seconds_before_auto_logout = models.PositiveIntegerField(default=600)
    upload_data_files_frequency_seconds = models.PositiveIntegerField(default=3600)
    voice_recording_max_time_length_seconds = models.PositiveIntegerField(default=240)
    wifi_log_frequency_seconds = models.PositiveIntegerField(default=300)

    # iOS-specific timer variables
    gyro_off_duration_seconds = models.PositiveIntegerField(default=600)
    gyro_on_duration_seconds = models.PositiveIntegerField(default=60)
    magnetometer_off_duration_seconds = models.PositiveIntegerField(default=600)
    magnetometer_on_duration_seconds = models.PositiveIntegerField(default=60)
    devicemotion_off_duration_seconds = models.PositiveIntegerField(default=600)
    devicemotion_on_duration_seconds = models.PositiveIntegerField(default=60)

    # Text strings
    about_page_text = models.TextField(default=ABOUT_PAGE_TEXT)
    call_clinician_button_text = models.TextField(default='Call My Clinician')
    consent_form_text = models.TextField(default=CONSENT_FORM_TEXT)
    survey_submit_success_toast_text = models.TextField(default=SURVEY_SUBMIT_SUCCESS_TOAST_TEXT)

    # Consent sections
    consent_sections = JSONTextField(default=DEFAULT_CONSENT_SECTIONS_JSON)

    study = models.OneToOneField('Study', on_delete=models.PROTECT, related_name='device_settings')
