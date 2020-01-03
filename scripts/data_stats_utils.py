from config.constants import (API_TIME_FORMAT, VOICE_RECORDING, ALL_DATA_STREAMS, DEFAULT_S3_RETRIES,
    SURVEY_ANSWERS, SURVEY_TIMINGS, IMAGE_FILE)
from config.settings import (S3_BUCKET, BEIWE_SERVER_AWS_ACCESS_KEY_ID,
    BEIWE_SERVER_AWS_SECRET_ACCESS_KEY, S3_REGION_NAME)
import config.load_django
from database.models import ReceivedDataStats, UploadTracking, Participant
from config.constants import UPLOAD_FILE_TYPE_MAPPING
import argparse
import config.remote_db_env
import json
import os
import re

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Beiwe database received data statistics tool")

    parser.add_argument('--update_statistics', help='Add aliases from a json file, should be followed by the name of',
        action='store_true', default=False)

    parser.add_argument('--print_statistics', help='Prints all of the aliase information found in the database',
        action='store_true', default=False)

    parser.add_argument('--delete_statistics', help='Removes all of the statistics for a specified study.',
        action='store_true', default=False)

    args = parser.parse_args()

    if args.print_statistics:
        print('Printing all statistics')
        for statistics in ReceivedDataStats.objects.all():
            print('{0} {1} {2} {3} {4}'.format(statistics.participant.patient_id, statistics.data_type, statistics.number_of_uploads, 
                statistics.number_bytes_uploaded, statistics.last_upload_timestamp))

    if args.delete_statistics:
        ReceivedDataStats.objects.all().delete()
        print('Deleting all statistics')

    if args.update_statistics:
        count = 0

        for participant in Participant.objects.all():
            print('Updating data for {0}'.format(participant.patient_id))
            for upload in UploadTracking.objects.filter(participant=participant.id):
                ReceivedDataStats.update_statistics(
                    file_path = upload.file_path,
                    participant = participant,
                    file_size = upload.file_size,
                    timestamp = upload.timestamp
                )
                count += 1
                if count > 0 and count % 1000 == 0:
                    print('Processed {0} uploads'.format(count))
