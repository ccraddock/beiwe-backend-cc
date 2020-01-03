from boto import connect_s3
from boto.s3.key import Key

source_bucket_name = "beiwe"
destination_bucket_name = "beiwe-backup"

source_s3_connection = connect_s3(aws_access_key_id="fill_me_in",aws_secret_access_key="fill_me_in")
source_bucket = source_s3_connection.get_bucket(source_bucket_name)

destination_s3_connection = connect_s3(aws_access_key_id="fill_me_in",aws_secret_access_key="fill_me_in")
destination_bucket = destination_s3_connection.get_bucket(destination_bucket_name)

just_in_time_list_o_files = source_bucket.list(prefix="")

for f in just_in_time_list_o_files:
    f_path = f.name
    if f_path.startswith("logs/") or f_path.startswith("CHUNKED_DATA/"):
        print "SKIPPING", f_path
        continue
    else:
        print "CHECKING", f_path, "...",

    f_already_exists = f_path in [x.name for x in destination_bucket.list(prefix=f_path)]

    if f_already_exists:
        print "already exists."
    else:
        print "does not exist, backing up ...",
        try:
            print "downloading...",
            data = Key(source_bucket, f_path).read()
            print "uploading...",
            destination_bucket.new_key(f_path).set_contents_from_string(data)
            print "Done."
            del data #these files can, potentially, be large.
        except Exception as e:
            print "ENCOUNTERED ERROR WHILE UPLOADING."
            print type(e), e.message
