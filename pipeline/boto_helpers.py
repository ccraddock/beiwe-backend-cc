import boto3

from configuration_getters import get_custom_config


def get_boto_client(client_type, pipeline_region=None):
    from config.settings import BEIWE_SERVER_AWS_ACCESS_KEY_ID, BEIWE_SERVER_AWS_SECRET_ACCESS_KEY
    print pipeline_region
    region_name = pipeline_region or get_custom_config()['region_name']
    
    return boto3.client(
            client_type,
            aws_access_key_id=BEIWE_SERVER_AWS_ACCESS_KEY_ID,
            aws_secret_access_key=BEIWE_SERVER_AWS_SECRET_ACCESS_KEY,
            region_name=region_name,
    )
