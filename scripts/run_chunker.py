from config.constants import (API_TIME_FORMAT, VOICE_RECORDING, ALL_DATA_STREAMS, DEFAULT_S3_RETRIES,
    SURVEY_ANSWERS, SURVEY_TIMINGS, IMAGE_FILE)
from config.settings import (S3_BUCKET, BEIWE_SERVER_AWS_ACCESS_KEY_ID,
    BEIWE_SERVER_AWS_SECRET_ACCESS_KEY, S3_REGION_NAME)
import config.load_django
from database.data_access_models import ChunkRegistry, FileProcessLock, FileToProcess

from config.constants import UPLOAD_FILE_TYPE_MAPPING
from libs.file_processing import process_file_chunks_lambda
import argparse
import config.remote_db_env
import json
import os
import re
import requests
import random, math
import time
import datetime
from libs.s3 import s3_retrieve
from multiprocessing.pool import ThreadPool

def check_and_update_number_of_observations(chunk):

    if chunk.data_type == VOICE_RECORDING:
        chunk.number_of_observations = 1
        chunk.save()
    else:
        file_contents = s3_retrieve(chunk.chunk_path,
                                    study_object_id=chunk.study.object_id,
                                    raw_path=True)

        # we want to make sure that there are no extraneous newline characters at the
        # end of the line. we want the line to end in exactly one newline character
        file_contents = file_contents.rstrip('\n') + '\n'
    
        # we subtract one to exclude the header line
        chunk.number_of_observations = file_contents.count('\n') - 1
        chunk.save()

    print('Updated chunk {0} with {1} observations'.format(chunk, chunk.number_of_observations))

    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Beiwe chunker tool")

    # run through all of the jobs waiting to be process and chunk them

    parser.add_argument('--process_ftps', help='Chunk all of the data in the FilesToProcess table.',
        action='store_true', default=False)

    parser.add_argument('--set_num_obs', help='Set the number of observations for each chunk',
        action='store_true', default=False)

    parser.add_argument('--run_serially', help='process the files in serial, default is to process in parallel using a threadpool',
        action='store_true', default=False)

    parser.add_argument('--num_to_process', help='Only process the first N chunks, defaults to 25, set to 0 to do all',
        type=int, default=25)

    #parser.add_argument('--print_study_config', help='upload study configuration file to the database',
        #action='store_true', default=False) 

    #parser.add_argument('study_id', help='id of the study to perform the operation on',
        #nargs=1, type=str)

    args = parser.parse_args()

    if args.process_ftps:
        process_file_chunks_lambda()

    if args.set_num_obs:

        pool = None
        if not args.run_serially:
            pool = ThreadPool(8)

        if args.num_to_process > 0:
            chunks_to_fix = ChunkRegistry.objects.filter(number_of_observations=None)[0:args.num_to_process]
        else:
            chunks_to_fix = list(ChunkRegistry.objects.filter(number_of_observations=None))

        if args.run_serially:
            for chunk in chunks_to_fix:
                check_and_update_number_of_observations(chunk)

        else:
            pool.map(check_and_update_number_of_observations, chunks_to_fix)
            pool.close()
            pool.terminate()
            

