if __name__ == "__main__":
    from os.path import abspath as _abspath
    import imp as _imp
    _current_folder_init = _abspath(__file__).rsplit('/', 1)[0]+ "/__init__.py"
    _imp.load_source("__init__", _current_folder_init)

from libs.s3 import s3_list_files
from db.data_access_models import FileToProcess, FilesToProcess
from bson import ObjectId

study_id_obj = ObjectId("5873fe38644ad7557b168e43")
study_id_str = str(study_id_obj)

for purgeable in FilesToProcess(user_id='prx7ap5x'):
    purgeable.remove()

for i, path in enumerate(s3_list_files(study_id_str , as_generator=True)):
    if i > 500:
        break
    if path[-3:] != 'csv':
        continue # skip if not a csv file...
    user_id = path[:-4].split('/')[1]
    path_sans_study = path.split("/", 1)[1]
    if FileToProcess(s3_file_path=path):
        print "%s already in FilesToProcess." % path
        continue
    FileToProcess.append_file_for_processing(path_sans_study, study_id_obj, user_id)