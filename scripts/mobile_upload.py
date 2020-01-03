from config.constants import (API_TIME_FORMAT, VOICE_RECORDING, ALL_DATA_STREAMS, DEFAULT_S3_RETRIES,
    SURVEY_ANSWERS, SURVEY_TIMINGS, IMAGE_FILE)
from config.settings import (S3_BUCKET, BEIWE_SERVER_AWS_ACCESS_KEY_ID,
    BEIWE_SERVER_AWS_SECRET_ACCESS_KEY, S3_REGION_NAME)
import config.load_django
from database.models import ReceivedDataStats, UploadTracking, Participant, Study, Survey, ParticipantSurvey
from database.data_access_models import ChunkRegistry, FileProcessLock, FileToProcess
from libs.client_key_management import get_client_public_key
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
import sys
import numpy.random as rnd
import pandas
import numpy as np
from io import BytesIO as StringIO
from Crypto.Cipher import AES

austin_coordinates = {'latitude': 30.2672 ,
                      'longitude': 97.7431}

gps_sd = .5
gps_altitude = 150
gps_accuracy = 65
gps_samples_per_second = 1

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Beiwe study tool, mobile upload")


    parser.add_argument('--start_date', help='date to start generating data for',
        type=str)

    parser.add_argument('--num_hours', help='number of hours of data to generate',
        type=int)

    parser.add_argument('participant_id', help='id of the participant who generated the data',
        type=str)

    args = parser.parse_args()

    if not Participant.objects.filter(patient_id=args.participant_id).exists():
        print('Could not find participant {0}'.format(args.participant_id))
        sys.exit(1)

    participant = Participant.objects.get(patient_id=args.participant_id)

    if args.start_date:
        start_datetime = datetime.datetime.strptime(args.start_date, API_TIME_FORMAT)
    else:
        start_datetime = datetime.datetime.now()

    if args.num_hours:
        num_hours = args.num_hours
    else:
        num_hours = 3

    print('Creating {0} hours worth of upload data for {1} starting at time {2}'.format(num_hours, participant,
        start_datetime))

    ## now we create the random gps data
     
    # create random gps data and upload it
    on_duration = participant.study.device_settings.gps_on_duration_seconds
    off_duration = participant.study.device_settings.gps_off_duration_seconds

    sampling_frequency = '{0:d}L'.format(int(np.ceil(100.0/gps_samples_per_second)))

    start_time = start_datetime
    end_time = start_datetime + datetime.timedelta(hours=num_hours)
   
    sample_datetimes = []
    sample_latitudes = []
    sample_longitudes = []
    sample_altitude = []
    sample_accuracy = []
 
    while start_time < end_time:
        if on_duration > (end_time - start_time).seconds:
            on_duration = (end_time - start_time).seconds

        sample_datetimes += pandas.date_range(start_time, periods=on_duration*gps_samples_per_second, freq='S')
        sample_latitudes += rnd.normal(loc=austin_coordinates['latitude'], scale=gps_sd,
            size=on_duration*gps_samples_per_second).tolist()
        sample_longitudes += rnd.normal(loc=austin_coordinates['longitude'], scale=gps_sd,
            size=on_duration*gps_samples_per_second).tolist()
        sample_altitude += [gps_altitude] * on_duration*gps_samples_per_second
        sample_accuracy += [gps_accuracy] * on_duration*gps_samples_per_second

        start_time += datetime.timedelta(seconds=off_duration)

    gps_dataframe = pandas.DataFrame({'times': sample_datetimes,
                                      'latitude': sample_latitudes,
                                      'longitude': sample_longitudes,
                                      'altitude': sample_altitude,
                                      'accuracy': sample_accuracy})

    def datetime_to_timestamp(date_and_time):
        return int(date_and_time.strftime('%s'))*100

    def datetime_to_timestring(date_and_time):
        return date_and_time.strftime(API_TIME_FORMAT)

    gps_dataframe['timestamp'] = gps_dataframe.apply(lambda row: datetime_to_timestamp(row['times']), axis=1)
    gps_dataframe['UTC time'] = gps_dataframe.apply(lambda row: datetime_to_timestring(row['times']), axis=1)
    gps_dataframe = gps_dataframe[['timestamp', 'UTC time', 'latitude', 'longitude', 'altitude', 'accuracy']]
    gps_dataframe = gps_dataframe.set_index('timestamp')

    string_io = StringIO()
    gps_dataframe.to_csv(string_io)
    print(string_io.getvalue())

    client_public_key = get_client_public_key(participant.patient_id, participant.study.object_id)
    print(client_public_key)

    iv = os.urandom(16)
    encrypted_table = AES.new(client_public_key, AES.MODE_CFB, segment_size=8, IV=iv).encrypt('cameron is awsome')

    #return iv + AES.new( encryption_key, AES.MODE_CFB, segment_size=8, IV=iv ).encrypt( input_string )

