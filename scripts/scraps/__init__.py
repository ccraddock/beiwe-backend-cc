from os.path import abspath as _abspath
from sys import path as _path
_one_folder_up = _abspath(__file__).rsplit('/',2)[0]
_two_folders_up = _abspath(__file__).rsplit('/',3)[0]
_path.insert(1, _one_folder_up)
_path.insert(1, _two_folders_up)

#stick this at the top of your script to be able to run it bare
# if __name__ == "__main__":
#     from os.path import abspath as _abspath
#     import imp as _imp
#     _current_folder_init = _abspath(__file__).rsplit('/', 1)[0]+ "/__init__.py"
#     _imp.load_source("__init__", _current_folder_init)