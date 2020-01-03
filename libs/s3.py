import boto3
import os

from config.constants import DEFAULT_S3_RETRIES, KEY_FOLDER, RAW_DATA_FOLDER, CHUNKS_FOLDER, API_TIME_FORMAT, CHUNK_TIMESLICE_QUANTUM
from config.settings import (S3_BUCKET, BEIWE_SERVER_AWS_ACCESS_KEY_ID,
    BEIWE_SERVER_AWS_SECRET_ACCESS_KEY, S3_REGION_NAME)
from libs import encryption
from botocore.exceptions import ClientError
from datetime import datetime

conn = boto3.client('s3',
                    aws_access_key_id=BEIWE_SERVER_AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=BEIWE_SERVER_AWS_SECRET_ACCESS_KEY,
                    region_name=S3_REGION_NAME)

def unix_time_to_string(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime( API_TIME_FORMAT )

def s3_delete(key_path, study_object_id, raw_path=False):
    if not raw_path:
        key_path = os.path.join(study_object_id, key_path)
    conn.delete_object(Bucket=S3_BUCKET, Key=key_path)

def s3_exists(key_path, study_object_id, raw_path=False):

    return_value = True

    if not raw_path:
        key_path = os.path.join(study_object_id, key_path)

    try:
        conn.head_object(Bucket=S3_BUCKET, Key=key_path)
    except ClientError:
        return_value = False

    return return_value
        
def s3_move(source_key_path, destination_key_path, study_object_id, raw_path=False):

    if not raw_path:
        source_key_path = os.path.join(study_object_id, source_key_path)
        destination_key_path = os.path.join(study_object_id, destination_key_path)

    try:
        conn.copy_object(CopySource={'Bucket': S3_BUCKET, 'Key': source_key_path}, 
                         Bucket=S3_BUCKET, Key=destination_key_path)
    except:
        print('Could not copy key {0} {1}'.format(S3_BUCKET, source_key_path))
        raise

    conn.delete_object(Bucket=S3_BUCKET, Key=source_key_path)

def s3_upload(key_path, data_string, study_object_id, raw_path=False):

    if not raw_path:
        key_path = study_object_id + "/" + key_path
    data = encryption.encrypt_for_server(data_string, study_object_id)
    conn.put_object(Body=data, Bucket=S3_BUCKET, Key=key_path, ContentType='string')

def s3_upload_public(key_path, data_string, study_object_id, raw_path=False):

    if not raw_path:
        key_path = study_object_id + "/" + key_path

    conn.put_object(Body=data_string, Bucket=S3_BUCKET, Key=key_path, ContentType='string', ACL='public-read')
    return 'https://{0}.s3.amazonaws.com/{1}'.format(S3_BUCKET, key_path)

def s3_retrieve(key_path, study_object_id, raw_path=False, number_retries=DEFAULT_S3_RETRIES):
    """ Takes an S3 file path (key_path), and a study ID.  Takes an optional argument, raw_path,
    which defaults to false.  When set to false the path is prepended to place the file in the
    appropriate study_id folder. """
    if not raw_path:
        key_path = study_object_id + "/" + key_path
    encrypted_data = _do_retrieve(S3_BUCKET, key_path, number_retries=number_retries)['Body'].read()
    return encryption.decrypt_server(encrypted_data, study_object_id)


def _do_retrieve(bucket_name, key_path, number_retries=DEFAULT_S3_RETRIES):
    """ Run-logic to do a data retrieval for a file in an S3 bucket."""
    try:
        return conn.get_object(Bucket=bucket_name, Key=key_path, ResponseContentType='string')
    except Exception:
        if number_retries > 0:
            print("s3_retrieve failed with incomplete read, retrying on %s" % key_path)
            return _do_retrieve(bucket_name, key_path, number_retries=number_retries - 1)
        raise


def s3_list_files(prefix, as_generator=False):
    """ Method fetches a list of filenames with prefix.
        note: entering the empty string into this search without later calling
        the object results in a truncated/paginated view."""
    return _do_list_files(S3_BUCKET, prefix, as_generator=as_generator)


def _do_list_files(bucket_name, prefix, as_generator=False):
    paginator = conn.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
    if as_generator:
        return _do_list_files_generator(page_iterator)
    else:
        items = []
        for page in page_iterator:
            if 'Contents' in page.keys():
                for item in page['Contents']:
                    items.append(item['Key'].strip("/"))
        return items


def _do_list_files_generator(page_iterator):
    for page in page_iterator:
        if 'Contents' not in page.keys():
            return
        for item in page['Contents']:
            yield item['Key'].strip("/")


"""################################ S3 PATHS ################################"""

def construct_s3_key_paths(study_id, participant_id):
    """ S3 file paths for chunks are of this form:
        RAW_DATA/study_id/user_id/data_type/time_bin.csv """
    return {'private': os.path.join(KEY_FOLDER, study_id, participant_id + "_private"),
            'public': os.path.join(KEY_FOLDER, study_id, participant_id + "_public")}

def construct_s3_raw_data_path(study_id, filename):
    """ S3 file paths for chunks are of this form:
        RAW_DATA/study_id/user_id/data_type/time_bin.csv """
    return os.path.join(RAW_DATA_FOLDER, study_id, filename)

def construct_s3_chunk_path(study_id, user_id, data_type, time_bin):
    """ S3 file paths for chunks are of this form:
        CHUNKED_DATA/study_id/user_id/data_type/time_bin.csv """
    return "%s/%s/%s/%s/%s.csv" % (CHUNKS_FOLDER, study_id, user_id, data_type,
        unix_time_to_string(time_bin*CHUNK_TIMESLICE_QUANTUM) )

def construct_s3_chunk_path_from_raw_data_path(raw_data_path):
    return raw_data_path.replace(RAW_DATA_FOLDER, CHUNKS_FOLDER)

