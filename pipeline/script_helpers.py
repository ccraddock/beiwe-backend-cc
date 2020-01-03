import subprocess

# Do not modify this * import, this is how we solve all the pipeline/scripts folder's import problems
from configuration_getters import get_custom_config


def set_default_region():
    aws_object_names = get_custom_config()
    region_name = aws_object_names['region_name']
    subprocess.check_call(['aws', 'configure', 'set', 'default.region', region_name])

