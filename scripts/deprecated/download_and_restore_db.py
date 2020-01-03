print "double check that the database backup has been removed from the /tmp folder."

from config.settings import MONGO_PASSWORD, MONGO_USERNAME
from mongobackup import restore
from subprocess import check_call
from shlex import split
from os import chdir

from libs.s3 import backup_list_files, backup_retrieve

print "finding most recent backup..."
backup_name = backup_list_files("")[-1]

print "getting most recent backup... %s" % backup_name
data = backup_retrieve(backup_name)

file_path = "/tmp/%s" % backup_name
check_call(["touch", file_path])

print "writing backup to file..."
with open(file_path, 'w') as f:
    f.write(data)
    f.close()

restore(MONGO_USERNAME, MONGO_PASSWORD, file_path,
        backup_directory_output_path="/tmp/backup_mongo_dump",
        drop_database=True, cleanup=True, silent=False,
        skip_system_and_user_files=True)

print "deleting the backup..."
check_call( split("rm -f %s" % file_path) )

print "\n\n Database purge and restore complete."