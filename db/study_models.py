from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED


class Study(DatabaseObject):
    PATH = "beiwe.studies"
    
    DEFAULTS = {
        "name": REQUIRED,
        "admins": [],  # admins for the study.
        "super_admins": [],  # admins that can add admins. this variable can be used in the yet-to-be-implemented 3-tier user model.
        "surveys": [],  # the surveys pushed in this study.
        "device_settings": REQUIRED,  # the device settings for the study.
        "encryption_key": REQUIRED,  # the study's config encryption key.
        "deleted": False,
        # is_test means the test is a test study, and therefore cannot download raw data.
        "is_test": True,
    }
    
    @classmethod
    def create_default_study(cls, name, encryption_key, is_test):
        if Studies(name=name):
            raise StudyAlreadyExistsError("a study named %s already exists" % name)
        if len(encryption_key) != 32:
            error_text = "the encryption key must be 32 characters, you " +\
                         "entered %d characters" % len(encryption_key)
            raise InvalidEncryptionKeyError(error_text)
        device_settings = StudyDeviceSettings.create_default()
        study = {
            "name": name,
            "encryption_key": encryption_key,
            "device_settings": device_settings._id,
            "is_test": is_test,
        }
        return Study.create(study, random_id=True)
        
    #Editors
    def add_admin(self, admin_id):
        """ Note: admin ids are strings, not ObjectIds. """
        if not (admin_id in self["admins"]):
            self["admins"].append(admin_id)
            self.save()
    
    def remove_admin(self, admin_id):
        """ Note: admin ids are strings, not ObjectIds. """
        if admin_id in self['admins']:
            self["admins"].remove(admin_id)
            self.save()
    
    def add_survey(self, survey):
        """ Note: this takes survey objects, not survey ids."""
        self["surveys"].append(survey._id)
        self.save()
    
    def remove_survey(self, survey):
        """ Note: this takes survey objects, not survey ids."""
        if survey._id not in self['surveys']:
            raise SurveyDoesNotExistError
        self["surveys"].remove(survey._id)
        self.save()
    
    #Accessors
    def get_surveys_for_study(self):
        """ Returns a dict of survey_id strings paired with their survey data. """
        ret = [ dict(Survey(survey_id)) for survey_id in self['surveys'] ]
        for x in ret:
            x['_id'] = str(x['_id'])
        return ret
    
    def get_survey_ids_for_study(self, survey_type='tracking_survey'):
        return [Survey(survey_id)['_id'] for survey_id in self['surveys']
                if Survey(survey_id)['survey_type'] == survey_type]
    
    def get_study_device_settings(self):
        return StudyDeviceSettings(self['device_settings'])
    
    
class StudyDeviceSettings( DatabaseObject ):
    """ The DeviceSettings database contains the structure that defines
        settings pushed to devices of users in of a study."""
    PATH = "beiwe.device_settings"
    #If anything here changes...
    # ensure that any changes here are well defined and enforced in frontend
    # and on the app.
    # Ensure that any toggles displayed on the website using CHECKBOXES are enumerated in CHECKBOX_TOGGLES in constants.
    # the default data streams are enabled/disable by request.
    DEFAULTS = {
        "accelerometer":True,
        "gps":True,
        "calls":True,
        "texts":True,
        "wifi":True,
        "bluetooth":False,
        "power_state":True,
        # iOS-specific data streams
        "proximity":False,
        "gyro":False,
        "magnetometer":False,
        "devicemotion":False,
        "reachability":True,
        # upload over cellular data or only over WiFi (WiFi-only is default)
        "allow_upload_over_cellular_data": False,
        # timer variables
        "accelerometer_off_duration_seconds":10,
        "accelerometer_on_duration_seconds":10,
        "bluetooth_on_duration_seconds":60,
        "bluetooth_total_duration_seconds":300,
        "bluetooth_global_offset_seconds":0,
        "check_for_new_surveys_frequency_seconds":3600 * 6,
        "create_new_data_files_frequency_seconds":15 * 60,
        "gps_off_duration_seconds":600,
        "gps_on_duration_seconds":60,
        "seconds_before_auto_logout":600,
        "upload_data_files_frequency_seconds":3600,
        "voice_recording_max_time_length_seconds":240,
        "wifi_log_frequency_seconds":300,
        # iOS-specific timer variables
        "gyro_off_duration_seconds":600,
        "gyro_on_duration_seconds":60,
        "magnetometer_off_duration_seconds":600,
        "magnetometer_on_duration_seconds":60,
        "devicemotion_off_duration_seconds":600,
        "devicemotion_on_duration_seconds":60,
        # text strings
        "about_page_text":"The Beiwe application runs on your phone and helps researchers collect information about your behaviors. Beiwe may ask you to fill out short surveys or to record your voice. It may collect information about your location (using phone GPS) and how much you move (using phone accelerometer). Beiwe may also monitor how much you use your phone for calling and texting and keep track of the people you communicate with. Importantly, Beiwe never records the names or phone numbers of anyone you communicate with. While it can tell if you call the same person more than once, it does not know who that person is. Beiwe also does not record the content of your text messages or phone calls. Beiwe may keep track of the different Wi-Fi networks and Bluetooth devices around your phone, but the names of those networks are replaced with random codes.\n\nAlthough Beiwe collects large amounts of data, the data is processed to protect your privacy. This means that it does not know your name, your phone number, or anything else that could identify you. Beiwe only knows you by an identification number. Because Beiwe does not know who you are, it cannot communicate with your clinician if you are ill or in danger. Researchers will not review the data Beiwe collects until the end of the study. To make it easier for you to connect with your clinician, the 'Call my Clinician' button appears at the bottom of every page.\n\nBeiwe was conceived and designed by Dr. Jukka-Pekka 'JP' Onnela at the Harvard T.H. Chan School of Public Health. Development of the Beiwe smartphone application and data analysis software is funded by NIH grant 1DP2MH103909-01 to Dr. Onnela. The smartphone application was built by Zagaran, Inc., in Cambridge, Massachusetts.",
        "call_clinician_button_text":"Call My Clinician",
        "consent_form_text":" I have read and understood the information about the study and all of my questions about the study have been answered by the study researchers.",
        "survey_submit_success_toast_text":"""Thank you for completing the survey.  A clinician will not see your answers immediately, so if you need help or are thinking about harming yourself, please contact your clinician.  You can also press the "Call My Clinician" button.""",
        #Consent sections
        "consent_sections": { "welcome": { "text": "", "more": "" }, "data_gathering": { "text": "", "more": "" }, "privacy": { "text": "", "more": "" }, "data_use": { "text": "", "more": "" }, "time_commitment": { "text": "", "more": "" }, "study_survey": { "text": "", "more": "" }, "study_tasks": { "text": "", "more": "" }, "withdrawing": { "text": "", "more": "" } }
    }
    @classmethod
    def create_default(cls):
        return StudyDeviceSettings.create(cls.DEFAULTS, random_id=True)
    
    
class Survey( DatabaseObject ):
    """ Surveys contain all information the app needs to display the survey correctly to a user,
    and when it should push the notifications to take the survey.
        
    Surveys must have a 'survey_type', which is a string declaring the type of survey it
    contains, which the app uses to display the correct interface.
    
    Surveys contain 'content', which is a json string that is unpacked on the app and displayed
    to the user in the form indicated by the survey_type.
    
    Timings schema: a survey must indicate the day of week and time of day on which to trigger,
    by default it contains no values. The timings schema mimics the Java.util.Calendar.DayOfWeek
    specification, i.e. it is zero-indexed with day 0 of Sunday.  'timings' is a list of 7
    inner-lists, each inner list contains any number of times of the day, times of day are
    integer values indicating the "seconds past 12am". """
    
    # it doesn't need to be in this document, but this should say where to find it.
    PATH = "beiwe.surveys"
    DEFAULTS = {
        "content": [],
        "timings": [[], [], [], [], [], [], []],
        "survey_type": REQUIRED,
        "settings": {},
    }

    # enhanced audio survey.   The following settings will be added to the settings dict
    # "audio_survey_type" maps to either "compressed" or "raw"
    # The app should default to a "compressed" survey if audio_survey_type is not present.
    # "raw" should always be paired with the keyword "sample_rate", which should map to
    #       an integer value.  Valid values are... 16000, 22050, and 44100.
    #     (Those values may change, almost definitely this is an android limitation.)
    #     (The app should default to 44100 if there is no sample_rate key, but this
    #       case probably will not occur outside of testing.)
    # "compressed" should always be paired with the keyword "bit_rate", which should
    #       map to an integer value.  Valid values are... 32, 64, 96, 128, 192, and 256.
    #     (The app should default to 64 if no value is provided.  This will occur when
    #       audio_survey_type is not provided.)
    # Example settings dict parameters:
    #   'settings': {'audio_survey_type': 'compressed', 'bit_rate': 64000}

    @classmethod
    def create_default_survey(cls, survey_type):
        #FIXME: this variable has been renamed, find it.
        if survey_type not in SURVEY_TYPES:
            raise SurveyTypeError("%s is not a valid survey type" % survey_type)

        if survey_type == "audio_survey":
            survey = {"survey_type":survey_type}
            survey["settings"] = {"audio_survey_type":"compressed",
                                  "bit_rate":64000, "sample_rate":44100}

        else: survey = { "survey_type": survey_type }
        return Survey.create(survey, random_id=True)

    #debugging function
#     def set_alarms_thirty_seconds(self):
#         now = datetime.now() - timedelta(seconds = 3600*4) #EDT, server is UTC.
#         start_of_day = datetime(now.year, now.month, now.day)
#         time_diff = int((now - start_of_day).total_seconds() + 30)
#         self['timings'] =[ [time_diff],   # 1
#                            [time_diff],   # 2
#                            [time_diff],   # 3
#                            [time_diff],   # 4
#                            [time_diff],   # 5
#                            [time_diff],   # 6
#                            [time_diff] ]  # 7
#         self.save()

"""############################ Collections #################################"""
class Studies( DatabaseCollection ):
    """ The Studies database."""
    OBJTYPE = Study
    
    @classmethod
    def get_all_studies(cls):
        return sorted(cls(deleted=False), key=lambda x: x.name.lower())

class StudyDeviceSettingsCollection( DatabaseCollection ):
    """ The per-study device settings. """
    OBJTYPE = StudyDeviceSettings
class Surveys( DatabaseCollection ):
    """ The Surveys database."""
    OBJTYPE = Survey

"""############################# Exceptions #################################"""
class SurveyDoesNotExistError(Exception): pass
class SurveyTypeError(Exception): pass
class UserDoesNotExistError(Exception): pass
class StudyAlreadyExistsError(Exception): pass
class InvalidEncryptionKeyError(Exception): pass
