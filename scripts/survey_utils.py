from config.constants import (API_TIME_FORMAT, VOICE_RECORDING, ALL_DATA_STREAMS, DEFAULT_S3_RETRIES,
    SURVEY_ANSWERS, SURVEY_TIMINGS, IMAGE_FILE)
from config.settings import (S3_BUCKET, BEIWE_SERVER_AWS_ACCESS_KEY_ID,
    BEIWE_SERVER_AWS_SECRET_ACCESS_KEY, S3_REGION_NAME)
import config.load_django
from database.models import ReceivedDataStats, UploadTracking, Participant, Study, Survey, ParticipantSurvey
from database.data_access_models import ChunkRegistry, FileProcessLock, FileToProcess

from config.constants import UPLOAD_FILE_TYPE_MAPPING
import argparse
import config.remote_db_env
import json
import os
import re
import requests
import random, math
import time
import datetime

def create_uuid():
    d = int(time.time())

    uuid_template = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    uuid = ""
    for value in uuid_template:
        if value in ['x', 'y']:
            r = (d + random.randint(0,16)) % 16
            d = int(math.floor(d / 16))
            if value == 'y':
                r = r & 0x7 | 0x8
            uuid += '{:x}'.format(r)
        else:
            uuid += value
 
    return(uuid)


tracking_survey_template_dict = {
        "name": "{survey_name}",
        "id": "{survey_id}",
        "deleted": False,
        "content": [], 
        "survey_type": "{survey_type}", 
        "timings": [
            [], 
            [], 
            [], 
            [], 
            [], 
            [], 
            []
        ], 
        "settings": {
            "number_of_random_questions": None, 
            "trigger_on_first_download": False, 
            "randomize": False, 
            "randomize_with_memory": False
        }
    }

tracking_survey_question_template_dict = {
       "display_if": None, 
       "question_text": "{question_text}", 
       "question_type": "{question_type}", 
       "answers": [], 
       "question_id": "{question_id}"
    } 

tracking_survey_answer_template_dict = {
       "text": "{answer_text}"
   }

get_survey_url = 'https://beiwe-dev.ut-wcwh.org/download_surveys/ios/'

timings_dict = {'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}

def robust_json_decode(json_entity, instance_type):
    """ Decodes through up to 100 attempts a json entity until it has deserialized to a list. """
    decoded_json = json.loads(json_entity)
    if not isinstance(decoded_json, instance_type):
        t_string = '\\n'.join([re.sub(r'\\+','', t) for t in json_entity.split(u'\\n')]).strip('"')
        try:
            decoded_json = json.loads(t_string)
        except:
            raise

    return decoded_json

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Beiwe survey tool")

    parser.add_argument('--update_survey', help='Add surveys from a json file to a study, should be followed by the name of the file',
        nargs=2, type=str)

    parser.add_argument('--print_survey', help='Prints all of the survey information found in the database for a study',
        nargs=1, type=str)

    parser.add_argument('--write_survey_config', help='Writes a survey config yml for a study',
        nargs=1, type=str)

    parser.add_argument('--create_uuid', help='create uuid and print it out',
        action='store_true', default=False)

    parser.add_argument('--unlock_fileprocessing_lock', help='unlock the file processing lock',
        action='store_true', default=False)

    parser.add_argument('--delete_participant_surveys', help='Removes all of the surveys for a specified participants.',
        nargs=1, type=str)

    parser.add_argument('--delete_study_surveys', help='Removes all of the surveys for a specified study.',
        nargs=1, type=str)

    parser.add_argument('--delete_survey', help='Removes all of the surveys for a specified study.',
        nargs=1, type=str)

    parser.add_argument('--get_survey', help='Use the mobile API to retrieve all surveys for participant.',
        nargs=1, type=str)

    parser.add_argument('--create_participant_survey', help='Create a survey for a participant using the contents of a json file',
        nargs=2, type=str)

    parser.add_argument('--send_participant_message', help='Create a survey for a participant with a single informational text question that includes the given string',
        nargs=2, type=str)

    args = parser.parse_args()

    if args.unlock_fileprocessing_lock:
        FileProcessLock.unlock()
        print('Unlocked')

    if args.write_survey_config:

        try:
            study = Study.objects.get(pk=int(args.write_survey_config[0]))
        except Study.DoesNotExist:
            print("Could not find study {0}".format(args.write_survey_config[0]))
            raise

        survey_config = {}

        for survey in study.surveys.filter(deleted=False): 

            if survey.deleted:
                continue

            if not survey.object_id:
                print('Survey {0} missing object_id, skipping ...'.format(survey))
                continue

            timing_struct = []
            if survey.timings:
                try:
                    timing_struct = json.loads(survey.timings)
                except:
                    print('Error decoding {0}'.format(repr(survey.timings)))
                    raise 

            intended_hour_list = []
            for day_timings in timing_struct:
                for hour in day_timings:
                    intended_hour_list.append(hour // (60*60))
            intended_hour_list = list(set(intended_hour_list))
           
            # add the survey and inteded hours into the survey_config
            if 'SURVEYS' not in survey_config:
                survey_config['SURVEYS'] = {}

            if 'QUESTIONS' not in survey_config:
                survey_config['QUESTIONS'] = {}

            if survey.object_id in survey_config['SURVEYS']:
                print('Survey {0} already found in the config, replacing ...'.format(survey.object_id))

            survey_config['SURVEYS'][survey.object_id] = {"intended_hour": intended_hour_list,
                                                          "survey_name": survey.name}
            
            content_struct = []
            if survey.content:
                try:
                    content_struct = robust_json_decode(survey.content, list)
                except:
                    print('Error decoding {0}'.format(repr(survey.content)))
                    raise

            for question in content_struct:
                if question['question_id'] not in survey_config['QUESTIONS']:
                    survey_config['QUESTIONS'][question['question_id']] = { 
                        "question": question['question_text'],
                        "answers": {},
                        "stats": ["TBD"],
                        "question_id": ["TBD"]
                    }
   
                    if 'answers' in question:

                        answers_dict = {}
                        answer_num = 1

                        for answer in question['answers']:
                            answers_dict[answer['text']] = answer_num
                            answer_num += 1

                        survey_config['QUESTIONS'][question['question_id']]['answers'] = answers_dict


        print(json.dumps(survey_config, sort_keys=True, indent=4))

    if args.print_survey:

        try:
            study = Study.objects.get(pk=int(args.print_survey[0]))
        except Study.DoesNotExist:
            print("Could not find study {0}".format(args.print_survey[0]))
            raise

        for survey in study.surveys.filter(deleted=False): 
            if survey.deleted:
                continue

            content_struct = []
            if survey.content:
                try:
                    content_struct = robust_json_decode(survey.content, list)
                except:
                    print('Error decoding {0}'.format(repr(survey.content)))
                    raise
            if survey.settings:
                try:
                    settings_struct = robust_json_decode(survey.settings, dict)
                except:
                    print('Error decoding {0}'.format(repr(survey.settings)))
                    raise

            if survey.name:
                print('{0}\n'.format(survey.name))

            print('{0} :: {1} :: {2}\nCONTENT {3}\nSETTINGS {4}\nTIMING {5}\n'.format(survey.object_id, survey.study, survey.survey_type, 
                json.dumps(content_struct, indent=4), 
                json.dumps(settings_struct, indent=4),
                json.dumps(json.loads(survey.timings), indent=4)))

    if args.get_survey:
        print('Retrieving surveys for {0}'.format(args.get_survey[0]))
        data = { "patient_id": args.get_survey[0] }
        response = requests.post(url=get_survey_url, data=data)
        if response.status_code != 200:
            print('Failed to retreive surveys: received {0}'.format(response.status_code))
        else:
            print(json.dumps(json.loads(response.content), indent=4))

    if args.delete_participant_surveys:

        print('Print deleting participant id: {0}'.format(args.delete_participant_surveys[0]))

        try:
            surveys = ParticipantSurvey.objects.filter(participant__patient_id=args.delete_participant_surveys[0])
        except:
            print("Could not find surveys for participant {0}".format(args.delete_participant_surveys[0]))
            raise

        for survey in surveys: 
            print("Deleting {0}".format(survey))
            survey.mark_deleted()

    if args.delete_study_surveys:

        print('Print deleting survey id: {0}'.format(args.delete_study_surveys[0]))

        try:
            study = Study.objects.get(pk=int(args.delete_study_surveys[0]))
        except Study.DoesNotExist:
            print("Could not find study {0}".format(args.delete_study_surveys[0]))
            raise

        for survey in study.surveys.filter(deleted=False): 
            print("Deleting {0}".format(survey))
            survey.mark_deleted()

    if args.delete_survey:

        print('Print deleting survey id: {0}'.format(args.delete_survey[0]))

        survey = None

        try_participant_survey = False
        try:
            survey = Survey.objects.get(object_id=args.delete_survey[0])
        except Survey.DoesNotExist:
            try_participant_survey = True

        if try_participant_survey:
            try:
                survey = ParticipantSurvey.objects.get(object_id=args.delete_survey[0])
            except ParticipantSurvey.DoesNotExist:
                print('Could not find survey {0} in study or participant surveys'.format(args.delete_survey[0]))
 
        if survey:
            survey.mark_deleted()

    if args.update_survey:

        try:
            study = Study.objects.get(pk=int(args.update_survey[1]))
        except Study.DoesNotExist:
            print("Could not find survey object {0}".format(args.update_survey[1]))
            raise

        print('Print uploading surveys from {0} into survey {1}'.format(args.update_survey[0], args.update_survey[1]))

        with open(args.update_survey[0]) as infd:
            survey_configuration_dict = json.load(infd)

        for survey_key, survey_dict in survey_configuration_dict["Surveys"].items():

            survey_questions = []
            for question_identifier in survey_dict['SurveyQuestions']:
                question_key, prompt_key = question_identifier.split('::')
                survey_question_dict = {
                    "display_if": None, 
                    "question_text": survey_configuration_dict['QuestionGroups'][question_key]['Prompts'][prompt_key], 
                    "question_type": survey_configuration_dict['QuestionGroups'][question_key]['QuestionType'], 
                    "answers": [], 
                    "question_id": create_uuid() 
                }

                answer_values = survey_configuration_dict['QuestionGroups'][question_key]['Answers'].values()
                for index in range(0, len(survey_configuration_dict['QuestionGroups'][question_key]['Answers'].values())):
                    survey_question_dict['answers'].append({"text": "{0}".format(survey_configuration_dict['QuestionGroups'][question_key]['Answers'][str(index)])}) 

                survey_questions.append(survey_question_dict)

                #for scheduled_time in time_values:
            for scheduled_time, weekdays in survey_dict['Timing'].items():
                timings_list = [ [], [], [], [], [], [], [] ]
                (hour, minute) = scheduled_time.split(':')
                seconds_from_midnight = int(hour) * 60 * 60 + int(minute) * 60
                dayhour = int(hour) % 12
                if dayhour == 0:
                    dayhour = 12

                daytime = '{0}:{1}'.format(dayhour, minute) 
                if int(hour) > 11: 
                    daytime = daytime + ' PM'
                else:
                    daytime = daytime + ' AM'

                if survey_dict["SplitDaysAcrossSurveys"] is False:

                    for weekday in weekdays:
                        timings_list[timings_dict[weekday]].append(seconds_from_midnight)

                    survey_name = ' '.join([survey_key, scheduled_time])
                    survey_type = 'tracking_survey'

                    this_surveys_questions = survey_questions 
                    if "SurveyInstruction" in survey_dict and survey_dict["SurveyInstruction"] != '':
                        survey_instruction = {
                            "display_if": None, 
                            "question_text": survey_dict["SurveyInstruction"].format(**{'Daytime': daytime}),
                            "question_type": "info_text_box", 
                            "question_id": create_uuid() 
                        }
                        this_surveys_questions = [survey_instruction] + survey_questions 

                    survey = Survey.create_with_settings(study_id=study.id, survey_type=survey_type, name=survey_name)
                    survey.update(content=json.dumps(this_surveys_questions), timings=json.dumps(timings_list),
                        settings=json.dumps(survey_dict["SurveySettings"]))

                else:
                    for weekday in weekdays:
                        timings_list[timings_dict[weekday]].append(seconds_from_midnight)
                        survey_name = ' '.join([survey_key, weekday, scheduled_time])
                        survey_type = 'tracking_survey'

                        this_surveys_questions = survey_questions 
                        if "SurveyInstruction" in survey_dict and survey_dict["SurveyInstruction"] != '':
                            survey_instruction = {
                                "display_if": None, 
                                "question_text": survey_dict["SurveyInstruction"].format(**{'Weekday': weekday, 'Daytime': daytime}),
                                "question_type": "info_text_box", 
                                "question_id": create_uuid() 
                            }
                            this_surveys_questions = [survey_instruction] + survey_questions 

                        survey = Survey.create_with_settings(study_id=study.id, survey_type=survey_type, name=survey_name)
                        survey.update(content=json.dumps(this_surveys_questions), timings=json.dumps(timings_list),
                            settings=json.dumps(survey_dict["SurveySettings"]))

    if args.create_participant_survey:
        print('Creating survey for {0} using {1}'.format(args.create_participant_survey[0], args.create_participant_survey[1]))

    if args.create_uuid:
        print('UUID: {0}'.format(create_uuid()))

    if args.send_participant_message:
        participant = Participant.objects.get(patient_id=args.send_participant_message[0])

        current_time = datetime.datetime.now()
        survey_name = "message for {0} at {1}".format(args.send_participant_message[0], current_time.isoformat())
        survey = ParticipantSurvey.create_with_settings(participant=participant,
            study_id=participant.study.id, survey_type="tracking_survey", name=survey_name)
        
        participant_message = {
            "display_if": None, 
            "question_text": args.send_participant_message[1], 
            "question_type": "info_text_box", 
            "question_id": create_uuid() 
        }
        content = json.dumps([participant_message])

        schedule_time = current_time.hour * 3600 + current_time.minute * 60 + 60
        timings = [[], [], [], [], [], [], []]
        #timings[(current_time.weekday() + 1) % 7].append(schedule_time)

        settings = {
            "number_of_random_questions": None, 
            "trigger_on_first_download": True, 
            "randomize": False, 
            "randomize_with_memory": False
        }

        survey.update(content=content, timings=json.dumps(timings), settings=json.dumps(settings))
