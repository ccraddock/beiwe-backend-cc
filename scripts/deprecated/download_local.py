#This script is intended for use locally, to download raw data to a local instance
#of the codebase for testing.

#This code has been run exactly once in June 2016, it is not guaranteed to work.

from os import makedirs
from multiprocessing.pool import ThreadPool

from boto import connect_s3
from boto.s3.key import Key
# We cannot actually import the contents of s3_local due to hooking into encryption
# also we want those trailing slashes.
####################################################################################
from os import listdir
from os.path import isfile, isdir, join
local_files = "local_s3"
file_name_cutoff = len(local_files)
def local_list(prefix):
    """ Mimics the function of s3_list on the local_s3 folder"""
    def get_files_in_folder(path):
        """Gets recursively retrieves a list of files in the provided directory."""
        ret = []
        for f in listdir(path):
            if f[0] == '.':
                continue
            ff = join(path, f)
            if isfile(ff):
                ret.append(ff)
            if isdir(ff):
                ret.append(ff + "/") #include / on folders
                ret.extend( get_files_in_folder(ff) ) #recurse to get folder contents
        return ret
    #chop off the extra leading local folder
    return [ f[file_name_cutoff:].strip("/") for f in get_files_in_folder(local_files) if f.startswith(prefix) ]
####################################################################################

all_local_files = set(local_list(""))
print all_local_files

bucket_name = "beiwe"
connection = connect_s3(aws_access_key_id="AKIAI63QZHDTE3VMMC7A",
                  aws_secret_access_key="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")
bucket = connection.get_bucket(bucket_name)

study_ids = ["55d231c197013e3a1c9b8c31",
            "55d2332397013e3a1c9b8c33",
            "55d235d397013e3a1c9b8c39",
            "56a0f93a1206f7615f9ce096",
            "55d3826297013e3a1c9b8c3e",
            "560027a997013e4579f98d21",
            "561426aa97013e703b725e65",
            "56325d8297013e33a2e57736",
            "56a795a31206f75bfce275ec",
            "5613ceaa97013e703b725e61",
            "56cf16231206f7536acbaf58",
            "571a5c6d1206f722f557e84a",
            "5721136c1206f76ce19e0b56"]


def batch_download(s3_file):
    s3_file_path = s3_file.name

    if s3_file_path in all_local_files or s3_file_path[-4] != ".":
        print "%s ... skipping." % s3_file_path
        return

    try:
        with open( join(local_files, s3_file_path) , 'w+') as f:
            print "%s ... downloading." % s3_file_path
            f.write( Key(bucket, s3_file).read() )
    except IOError:
        print "%s ... creating directory." % s3_file_path
        folder_path = join(local_files, s3_file_path.rsplit("/", 1)[0])

        try:
            makedirs(folder_path)
        except OSError:
            #this happens when multiple simultaneous folder creations occur.
            pass


# class dummy_pool():
#     def map(self, *args, **kwargs):
#         map(*args, **kwargs)
#     def close(self): pass
#     def terminate(self): pass
# pool = dummy_pool()

for study_id_string in study_ids:
    print "\n\n====================== Starting %s =======================\n\n" % study_id_string
    pool = ThreadPool(20)
    just_in_time_list_o_files = bucket.list(prefix=study_id_string)
    pool.map(batch_download, just_in_time_list_o_files)
    pool.close()
    pool.terminate()
    print "NEXT!"
