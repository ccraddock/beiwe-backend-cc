from database.study_models import Study
from database.user_models import Researcher
from database.pipeline_models import PipelineExecutionTracking
from libs.sentry import make_error_sentry

# This component of pipeline is part of the Beiwe server, the correct import is 'from pipeline.xyz...'
from pipeline.boto_helpers import get_boto_client
from pipeline.configuration_getters import get_generic_config

from config.constants import API_TIME_FORMAT
import datetime

def str_to_datetime(time_string):
    """ Translates a time string to a datetime object, raises a 400 if the format is wrong."""
    try:
        return datetime.datetime.strptime(time_string, API_TIME_FORMAT)
    except ValueError as e:
        if "does not match format" in e.message:
            return abort(400)

def refresh_data_access_credentials(freq, ssm_client=None):
    """
    Refresh the data access credentials for a particular BATCH USER user and upload them
    (encrypted) to the AWS Parameter Store. This enables AWS batch jobs to get the
    credentials and thereby access the data access API (DAA).
    :param freq: string, one of 'hourly' | 'daily' | 'weekly' | 'monthly' | 'manually'
    This is used to know what call the data access credentials on AWS.
    """
    
    # Get or create Researcher with no password. This means that nobody can log in as this
    # Researcher in the web interface.
    researcher_name = 'BATCH USER {}'.format(freq)
    mock_researchers = Researcher.objects.filter(username=researcher_name)
    if not mock_researchers.exists():
        mock_researcher = Researcher.create_without_password(researcher_name)
    else:
        mock_researcher = mock_researchers.get()
        mock_researcher.save()

    # Ensure that the Researcher is attached to all Studies. This allows them to access all
    # data via the DAA.
    for study in Study.objects.all():
        study.researchers.add(mock_researcher)
    
    # Reset the credentials. This ensures that they aren't stale.
    access_key, secret_key = mock_researcher.reset_access_credentials()

    generic_config = get_generic_config()
    # Append the frequency to the SSM (AWS Systems Manager) names. This ensures that the
    # different frequency jobs' keys do not overwrite each other.
    access_key_ssm_name = '{}-{}'.format(generic_config['access_key_ssm_name'], freq)
    secret_key_ssm_name = '{}-{}'.format(generic_config['secret_key_ssm_name'], freq)

    # Put the credentials (encrypted) into AWS Parameter Store
    if not ssm_client:
        ssm_client = get_boto_client('ssm')
    ssm_client.put_parameter(
        Name=access_key_ssm_name,
        Value=access_key,
        Type='SecureString',
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name=secret_key_ssm_name,
        Value=secret_key,
        Type='SecureString',
        Overwrite=True,
    )


def create_one_job(freq, object_id, owner_id, destination_email_addresses='', data_start_datetime='', data_end_datetime='', participants='', client=None):
    """
    Create an AWS batch job
    The aws_object_names and client parameters are optional. They are provided in case
    that this function is run as part of a loop, to avoid an unnecessarily large number of
    file operations or API calls.
    :param freq: string e.g. 'daily', 'manually'
    :param object_id: string representing the Study object_id e.g. '56325d8297013e33a2e57736'
    :param client: a credentialled boto3 client or None
    
    config needs are the following: job_name, job_defn_name, queue_name
    """
    # Get the AWS parameters and client if not provided
    aws_object_names = get_generic_config()
    # requires region_name be defined.
    if client is None:
        client = get_boto_client('batch')

    # clean up list of participants
    if isinstance(participants, list):
        participants = " ".join(participants)
    elif ',' in participants:
        participants = " ".join(participants.split(','))
    print('participants [{0}]'.format(participants))

    # clean up list of destination email addresses
    if isinstance(destination_email_addresses, list):
        destination_email_addresses = " ".join(destination_email_addresses)
    elif ',' in destination_email_addresses:
        destination_email_addresses = " ".join(destination_email_addresses.split(','))

    print("scheduling pipeline for study {0}".format(Study.objects.get(object_id=object_id).id))
    pipeline_id = PipelineExecutionTracking.pipeline_scheduled(owner_id,
                                                               Study.objects.get(object_id=object_id).id,
                                                               datetime.datetime.now(),
                                                               destination_email_addresses,
                                                               data_start_datetime,
                                                               data_end_datetime,
                                                               participants)

    response = None
    try:
        response = client.submit_job(
            jobName=aws_object_names['job_name'].format(freq=freq),
            jobDefinition=aws_object_names['job_defn_name'],
            jobQueue=aws_object_names['queue_name'],
            containerOverrides={
                'environment': [
                    {
                        'name': 'pipeline_id',
                        'value': str(pipeline_id),
                    },
                    {
                        'name': 'study_object_id',
                        'value': str(object_id),
                    },
                    {
                        'name': 'study_name',
                        'value': Study.objects.get(object_id=object_id).name,
                    },
                    {
                        'name': 'FREQ',
                        'value': freq,
                    },
                    {
                        'name': 'destination_email_address',
                        'value': destination_email_addresses,
                    },
                    {
                        'name': 'data_start_datetime',
                        'value': data_start_datetime,
                    },
                    {
                        'name': 'data_end_datetime',
                        'value': data_end_datetime,
                    },
                    {
                        'name': 'participants',
                        'value': participants,
                    }
                ],
            },
        )

    except Exception as e:
        PipelineExecutionTracking.pipeline_crashed(pipeline_id, datetime.datetime.now(), str(e))
        raise

    if response and 'jobId' in response:
        PipelineExecutionTracking.pipeline_set_batch_job_id(pipeline_id, response['jobId'])

    return


def create_all_jobs(freq):
    """
    Create one AWS batch job for each Study object
    :param freq: string e.g. 'daily', 'monthly'
    """
    
    # TODO: Boto3 version 1.4.8 has AWS Batch Array Jobs, which are extremely useful for the
    # task this function performs. We should switch to using them.
    
    # Get new data access credentials for the user
    # aws_object_names = get_aws_object_names()
    refresh_data_access_credentials(freq)
    
    # TODO: If there are issues with servers not getting spun up in time, make this a
    # ThreadPool with random spacing over the course of 5-10 minutes.
    error_sentry = make_error_sentry("data", tags={"pipeline_frequency": freq})
    for study in Study.objects.filter(deleted=False):
        with error_sentry:
            # For each study, create a job
            object_id = study.object_id
            create_one_job(freq, object_id)


def hourly():
    create_all_jobs('hourly')


def daily():
    create_all_jobs('daily')


def weekly():
    create_all_jobs('weekly')


def monthly():
    create_all_jobs('monthly')

def terminate_job(pipeline_id, user_id, client=None):

    # Get the AWS parameters and client if not provided
    aws_object_names = get_generic_config()

    # requires region_name be defined.
    if client is None:
        client = get_boto_client('batch')

    pipeline = PipelineExecutionTracking.objects.get(id = pipeline_id)

    if not pipeline.batch_job_id:
        raise ValueError('Error terminating pipeline {0}, batch job id not found'.format(pipeline_id))

    client.terminate_job(jobId=pipeline.batch_job_id, reason='Terminated by user {0}'.format(user_id))

    pipeline.terminate_job(pipeline_id, datetime.datetime.now(), reason='Terminated by user {0}'.format(user_id))

    return
