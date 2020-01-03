import json
import os
from os.path import join as path_join, abspath

# We raise this error, it is eventually used to raise a useful error on the frontend if pipeline
# is not set up.
class DataPipelineNotConfigured(Exception): pass

#
# Path getters
#
def get_pipeline_folder():
    return abspath(__file__).rsplit('/', 1)[0]

def get_configs_folder():
    return path_join(get_pipeline_folder(), 'configs')

def get_aws_object_names_file():
    return path_join(get_configs_folder(), 'aws-object-names.json')

def get_custom_settings():
    return path_join(get_configs_folder(), 'custom-settings.json')


#
# Configuration getters and validator
#

# generic config components are not recommended to be set by the user.
# Problems with these reduce to generic AWS administration problems.
generic_config_components = [
    "ami_name",
    "ecr_repo_name",
    "instance_profile",
    "comp_env_name",
    "comp_env_role",
    "queue_name", # used in creating a job
    "job_defn_name", # used in creating a job
    "job_name", # used in creating a job
    "access_key_ssm_name",
    "secret_key_ssm_name",
    "security_group",
]

# custom config components must be set by the administrator.
custom_config_components = [
    "pipeline_region",  # needed whenever we create a batch client
    "server_url",
]

def get_generic_config():
    return _validate_and_get_configs(generic_config_components, get_aws_object_names_file())

def get_custom_config():
    base_settings = _validate_and_get_configs(custom_config_components, get_custom_settings())
    # "pipeline_region" was changed from region_name for clarity after pipeline was built, rather
    # than change it we just patch it here, same for server_url
    base_settings['region_name'] = base_settings.pop('pipeline_region')
    return base_settings

def get_aws_object_names():
    settings = get_generic_config()
    settings.update(get_custom_config())
    return settings


def _validate_and_get_configs(config_list, config_file_path):
    """ There are two cases that need to be handled, and one significant administrative feature.
    1. we check for the json files (expected to be used by the pipeline setup scripts)
    2. we override/populate all environment variables
    """
    # attempt to load the json settings file...
    try:
        config_data = _load_json_file(config_file_path)
    except DataPipelineNotConfigured:
        config_data = {}
    
    # override/populate everything that has an environment variable for it
    for setting in config_list:
        if setting in os.environ:
            config_data[setting] = os.environ[setting]
    
    # if there are any missing settings, fail with helpful error message
    missing_configs = [setting for setting in config_list if setting not in config_data]
    if missing_configs:
        raise DataPipelineNotConfigured(
                "could not find the following settings: %s" % ", ".join(missing_configs)
        )
    return config_data


def _load_json_file(file_path):
    try:
        with open(file_path) as fn:
            return json.load(fn)
    except IOError as e:
        raise DataPipelineNotConfigured(e)