from config.constants import (API_TIME_FORMAT, VOICE_RECORDING, ALL_DATA_STREAMS, DEFAULT_S3_RETRIES,
    SURVEY_ANSWERS, SURVEY_TIMINGS, IMAGE_FILE)
from config.settings import (S3_BUCKET, BEIWE_SERVER_AWS_ACCESS_KEY_ID,
    BEIWE_SERVER_AWS_SECRET_ACCESS_KEY, S3_REGION_NAME)
import config.load_django
from database.models import ReceivedDataStats, UploadTracking, Participant, Study, StudyConfig, Survey, ParticipantSurvey
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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Beiwe study tool")


    parser.add_argument('--list_study_participants', help='list all of the participants for the study',
        action='store_true', default=False)

    parser.add_argument('--unregister_all_study_participants', help='unregister all of the participants for the study',
        action='store_true', default=False)

    parser.add_argument('--upload_study_config', help='upload study configuration file to the database',
        nargs=1, type=str)

    parser.add_argument('--print_study_config', help='upload study configuration file to the database',
        action='store_true', default=False) 

    parser.add_argument('study_id', help='id of the study to perform the operation on',
        nargs=1, type=str)

    args = parser.parse_args()

    if args.list_study_participants:

        for participant in Participant.objects.filter(study=int(args.study_id[0])).exclude(device_id=''):
            print("{0}: {1}, {2}, {3}".format(participant.patient_id, participant.device_id, participant.os_type, participant.study))

    if args.unregister_all_study_participants:

        for participant in Participant.objects.filter(study=int(args.study_id[0])).exclude(device_id=''):
            participant.clear_device()

    if args.upload_study_config and args.upload_study_config[0] != " ":
        StudyConfig.create_from_file(args.upload_study_config[0])

    if args.print_study_config:

        try:
            study_config = StudyConfig.objects.exclude(deleted=True).get(study__object_id=args.study_id[0])
        except StudyConfig.DoesNotExist as e:
            print('Did not find study config for {0}'.format(args.study_id[0]))
            raise

        print(json.dumps(study_config.study_configuration, indent=4))
       
