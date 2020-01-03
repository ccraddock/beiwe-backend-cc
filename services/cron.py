# modify python path so that this script can be targeted directly but still import everything.
import imp as _imp
from os.path import abspath as _abspath
_current_folder_init = _abspath(__file__).rsplit('/', 1)[0]+ "/__init__.py"
_imp.load_source("__init__", _current_folder_init)

# start actual cron-related code here
from sys import argv
from cronutils import run_tasks
from services.celery_data_processing import create_file_processing_tasks
from pipeline import index

FIVE_MINUTES = "five_minutes"
HOURLY = "hourly"
FOUR_HOURLY = "four_hourly"
DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"
VALID_ARGS = [FIVE_MINUTES, HOURLY, FOUR_HOURLY, DAILY, WEEKLY, MONTHLY]

# Crontab used for the current:
# # m h dom mon dow   command
# note that for the cluster the five_minutes task actually runs every 15 minutes
# */5 * * * * : five_minutes; cd $PROJECT_PATH; chronic python cron.py five_minutes
# 19 * * * * : hourly; cd $PROJECT_PATH; chronic python cron.py hourly
# 30 */4 * * * : four_hourly; cd $PROJECT_PATH; chronic python cron.py four_hourly
# @daily : daily; cd $PROJECT_PATH; chronic python cron.py daily
# 0 2 * * 0 : weekly; cd $PROJECT_PATH; chronic python cron.py weekly
# 48 4 1 * * : monthly; cd $PROJECT_PATH; chronic python cron.py monthly

TASKS = {
    FIVE_MINUTES: [create_file_processing_tasks],
    HOURLY: [index.hourly],
    FOUR_HOURLY: [],
    DAILY: [index.daily],
    WEEKLY: [index.weekly],
    MONTHLY: [index.monthly],
}

# We run the hourly task... hourly.  When multiples of this job overlap we disallow it and get
# the error report notification. So, we set the time limit very high to avoid the extra
# notification.
# we never want to kill or cap runtime of our cron jobs.
TIME_LIMITS = {
    FIVE_MINUTES: 10*60*60*24*365,    # 10 years (never kill)
    HOURLY: 10*60*60*24*365,          # 10 years (never kill)
    FOUR_HOURLY: 10*60*60*24*365,     # 10 years (never kill)
    DAILY: 10*60*60*24*365,           # 10 years (never kill)
    WEEKLY: 10*60*60*24*365,          # 10 years (never kill)
}

KILL_TIMES = TIME_LIMITS

if __name__ == "__main__":
    if len(argv) <= 1:
        raise Exception("Not enough arguments to cron\n")
    elif argv[1] in VALID_ARGS:
        cron_type = argv[1]
        if cron_type in KILL_TIMES:
            run_tasks(TASKS[cron_type], TIME_LIMITS[cron_type], cron_type, KILL_TIMES[cron_type])
        else:
            run_tasks(TASKS[cron_type], TIME_LIMITS[cron_type], cron_type)
    else:
        raise Exception("Invalid argument to cron\n")
