## Ignore line length limits in this file.
import json
from os.path import join as path_join, abspath

####################################################################################################
##################################### General Constants ############################################
####################################################################################################
from copy import copy

REMOTE_USERNAME = 'ubuntu'
# Note: port 50,001 is used for supervisord
RABBIT_MQ_PORT = 5672

## EC2 Instance Deployment Variables
APT_WORKER_INSTALLS = [
    'ack-grep',  # Search within files
    'build-essential',  # Includes a C compiler for compiling python
    'htop',
    'libbz2-dev',
    'libreadline-gplv2-dev',
    'libsqlite3-dev',
    'libssl-dev',
    'mailutils',  # Necessary for cronutils
    'moreutils',  # Necessary for cronutils
    'nload',
    'sendmail',  # Necessary for cronutils
    'silversearcher-ag',  # Search within files
]

APT_MANAGER_INSTALLS = copy(APT_WORKER_INSTALLS)
APT_MANAGER_INSTALLS.append('rabbitmq-server')  # Queue tasks to run using celery

APT_SINGLE_SERVER_AMI_INSTALLS = copy(APT_WORKER_INSTALLS)
APT_SINGLE_SERVER_AMI_INSTALLS.extend([
    'apache2',
    'haveged',  # For generating Flask secret key random string
    'libapache2-mod-wsgi',
    'postgresql',
    'postgresql-contrib',
    'sysv-rc-conf',
    'python-pip',
])

# Files to push from the local server before the rest of launch
# This is a list of 2-tuples of (local_path, remote_path) where local_path is located in
# PUSHED_FILES_FOLDER and remote_path is located in REMOTE_HOME_DIRECTORY.
FILES_TO_PUSH = [
    ('bash_profile.sh', '.profile'),  # standard bash profile
    ('.inputrc', '.inputrc'),  # modifies what up-arrow, tab etc. do
    ('known_hosts', '.ssh/known_hosts'),  # allows git clone without further prompting
]

## Errors
class DBInstanceNotFound(Exception): pass


## ERROR_MESSAGES
EB_SEC_GRP_COUNT_ERROR = "%s has had multiple security groups associated with it.  This action is not supported by this console tool."

VALIDATE_GLOBAL_CONFIGURATION_MESSAGE = "before you can take any action with this tool you must fill out the contents of the global_configuration.json file in the general_configuration folder."

VALIDATE_AWS_CREDENTIALS_MESSAGE = "before you can take any action with this tool you must fill out the contents of the aws_credentials.json file in the general_configuration folder."

GLOBAL_CONFIGURATION_FILE_KEYS = [
    "DEPLOYMENT_KEY_NAME",
    "DEPLOYMENT_KEY_FILE_PATH",
    "VPC_ID",
    "AWS_REGION",
    "SYSTEM_ADMINISTRATOR_EMAIL"
]

AWS_CREDENTIALS_FILE_KEYS = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
####################################################################################################
######################################## Static Files ##############################################
####################################################################################################

# Local folder paths
CLUSTER_MANAGEMENT_FOLDER = abspath(__file__).rsplit('/', 2)[0]
PUSHED_FILES_FOLDER = path_join(CLUSTER_MANAGEMENT_FOLDER, 'pushed_files')
USER_SPECIFIC_CONFIG_FOLDER = path_join(CLUSTER_MANAGEMENT_FOLDER, 'environment_configuration')
GENERAL_CONFIG_FOLDER = path_join(CLUSTER_MANAGEMENT_FOLDER, 'general_configuration')
STAGED_FILES = path_join(CLUSTER_MANAGEMENT_FOLDER, 'staged_files')

## Global EC2 Instance __remote__ folder paths
REMOTE_HOME_DIR = path_join('/home', REMOTE_USERNAME)

## Global EC2 Instance remote file paths
DEPLOYMENT_ENVIRON_SETTING_REMOTE_FILE_PATH = path_join(REMOTE_HOME_DIR, 'beiwe-backend/config/remote_db_env.py')
LOG_FILE = path_join(REMOTE_HOME_DIR, 'server_setup.log')


## Management Tool Configuration Files
AWS_CREDENTIALS_FILE = path_join(GENERAL_CONFIG_FOLDER, 'aws_credentials.json')
GLOBAL_CONFIGURATION_FILE = path_join(GENERAL_CONFIG_FOLDER, 'global_configuration.json')
AWS_PEM_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, 'aws_deployment_key.pem')

## Management Tool Configuration Loaders
def get_global_config():
    with open(GLOBAL_CONFIGURATION_FILE, 'r') as f:
        return json.load(f)


## EC2 Instance Configuration Files
def get_aws_credentials():
    with open(AWS_CREDENTIALS_FILE, 'r') as f:
        return json.load(f)


## Elastic Beanstalk Environment Files
ELASTICBEANSTALK_ASSUME_ROLE_POLICY_DOCUMENT_PATH = path_join(GENERAL_CONFIG_FOLDER, "elasticbeanstalk_assume_role_policy_document.json")
INSTANCE_ASSUME_ROLE_POLICY_DOCUMENT_PATH = path_join(GENERAL_CONFIG_FOLDER, "instance_assume_role_policy_document.json")
AUTOMATION_POLICY_PATH = path_join(GENERAL_CONFIG_FOLDER, "beiwe_automation_policy.json")
BEIWE_SERVER_AWS_ACCESS_PATH = path_join(GENERAL_CONFIG_FOLDER, "beiwe_server_aws_access.json")


## Elastic Beanstalk File Loaders
def get_elasticbeanstalk_assume_role_policy_document():
    with open(ELASTICBEANSTALK_ASSUME_ROLE_POLICY_DOCUMENT_PATH) as document:
        return document.read()

def get_instance_assume_role_policy_document():
    with open(INSTANCE_ASSUME_ROLE_POLICY_DOCUMENT_PATH) as document:
        return document.read()

def get_automation_policy():
    with open(AUTOMATION_POLICY_PATH, "r") as document:
            return document.read()

def get_aws_access_policy():
    with open(BEIWE_SERVER_AWS_ACCESS_PATH, "r") as document:
        return document.read()

## Worker and Processor server files
# (files with the prefix LOCAL are on this machine, REMOTE files are file paths on the remote server)
LOCAL_CRONJOB_WORKER_FILE_PATH = path_join(PUSHED_FILES_FOLDER, 'cron_worker.txt')
LOCAL_CRONJOB_MANAGER_FILE_PATH = path_join(PUSHED_FILES_FOLDER, 'cron_manager.txt')
LOCAL_CRONJOB_SINGLE_SERVER_AMI_FILE_PATH = path_join(PUSHED_FILES_FOLDER, 'cron_ami.txt')
REMOTE_CRONJOB_FILE_PATH = path_join(REMOTE_HOME_DIR, 'cronjob.txt')
LOCAL_GIT_KEY_PATH = path_join(PUSHED_FILES_FOLDER, 'git_read_only_key')
REMOTE_GIT_KEY_PATH = path_join(REMOTE_HOME_DIR, '.ssh/id_rsa')
LOCAL_PYENV_INSTALLER_FILE = path_join(PUSHED_FILES_FOLDER, 'install_pyenv.sh')
REMOTE_PYENV_INSTALLER_FILE = path_join(REMOTE_HOME_DIR, 'install_pyenv.sh')
LOCAL_INSTALL_CELERY_WORKER = path_join(PUSHED_FILES_FOLDER, 'install_celery_worker.sh')
REMOTE_INSTALL_CELERY_WORKER = path_join(REMOTE_HOME_DIR, 'install_celery_worker.sh')

LOCAL_CELERY_USER = path_join(PUSHED_FILES_FOLDER, 'rabbitmq.json')
REMOTE_CELERY_USER = path_join(REMOTE_HOME_DIR, 'rabbitmq.json')

LOCAL_CELERY_CONFIGURATION =  path_join(PUSHED_FILES_FOLDER, 'celery_configuration.sh')
REMOTE_CELERY_CONFIGURATION =  path_join(PUSHED_FILES_FOLDER, 'celery_configuration.sh')

LOCAL_AMI_ENV_CONFIG_FILE_PATH = path_join(PUSHED_FILES_FOLDER, 'ami_env_config.py')
LOCAL_APACHE_CONFIG_FILE_PATH = path_join(PUSHED_FILES_FOLDER, 'ami_apache.conf')
REMOTE_APACHE_CONFIG_FILE_PATH = path_join(REMOTE_HOME_DIR, 'ami_apache.conf')

####################################################################################################
####################################### Dynamic Files ##############################################
####################################################################################################

## EC2 Instance Configuration Files
def get_pushed_full_processing_server_env_file_path(eb_environment_name):
    """ This is the python file that contains the environment details for an ubuntu install. """
    return path_join(USER_SPECIFIC_CONFIG_FOLDER, eb_environment_name + '_remote_db_env.py')

def get_finalized_credentials_file_path(eb_environment_name):
    return path_join(USER_SPECIFIC_CONFIG_FOLDER, eb_environment_name + '_finalized_settings.json')

def get_finalized_environment_variables(eb_environment_name):
    with open(get_finalized_credentials_file_path(eb_environment_name), 'r') as f:
        return json.load(f)

## Database configuration
def get_db_credentials_file_path(eb_environment_name):
    """ Use the get_full_db_credentials function in rds to get database credentials. """
    return path_join(USER_SPECIFIC_CONFIG_FOLDER, eb_environment_name + "_database_credentials.json")

## Beiwe Environment Files
def get_beiwe_python_environment_variables_file_path(eb_environment_name):
    return path_join(USER_SPECIFIC_CONFIG_FOLDER, eb_environment_name + "_beiwe_environment_variables.json")

def get_beiwe_environment_variables(eb_environment_name):
    with open(get_beiwe_python_environment_variables_file_path(eb_environment_name), 'r') as f:
        return json.load(f)

## Processing worker and management servers
def get_server_configuration_file_path(eb_environment_name):
    return path_join(USER_SPECIFIC_CONFIG_FOLDER, eb_environment_name + '_server_settings.json')

def get_server_configuration_file(eb_environment_name):
    with open(get_server_configuration_file_path(eb_environment_name), 'r') as f:
        return json.load(f)
    
####################################################################################################
########################################## Strings #################################################
####################################################################################################

# IAM names
BEIWE_AUTOMATION_POLICY_NAME = "beiwe_automation_policy"
EB_SERVICE_ROLE = "beiwetest-elasticbeanstalk-service-role"
EB_INSTANCE_PROFILE_ROLE = "beiwetest-elasticbeanstalk-instance-profile-role"
EB_INSTANCE_PROFILE_NAME = "beiwetest-elasticbeanstalk-instance-profile"

# Elastic Beanstalk strings
BEIWE_APPLICATION_NAME = "beiwe-application"

# EB service role arns
AWS_EB_SERVICE = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkService"
AWS_EB_ENHANCED_HEALTH = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth"

# EB instance profile arns
AWS_EB_MULTICONTAINER_DOCKER = "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker"
AWS_EB_WEB_TIER = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
AWS_EB_WORKER_TIER = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier"


####################################################################################################
###################################### UI Strings ##################################################
####################################################################################################

DO_SETUP_EB_UPDATE_OPEN = "This command prepares the selected version of the codebase for deployment.  \n\nTo download the most recent version of the code base go to\nhttps://github.com/onnela-lab/beiwe-backend/tree/production\nand download the zip file version of the github repository, then place it into the staged_files folder.\n"

ENVIRONMENT_NAME_RESTRICTIONS = "Names must be 4 to 40 characters in length.\n" \
"Names can only contain letters, numbers, and hyphens, and cannot start or end with a hyphen.\n"

EXTANT_ENVIRONMENT_PROMPT = "Enter the name of the Elastic Beanstalk Environment you want to run this operation on:"

DO_CREATE_ENVIRONMENT ="Please enter the name of the environment for which you have filled out the required settings:"

HELP_SETUP_NEW_ENVIRONMENT = "Enter the name of the environment you want to create:"