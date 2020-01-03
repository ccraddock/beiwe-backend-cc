from os.path import abspath as _abspath
from sys import path as _path
_one_folder_up = _abspath(__file__).rsplit('/',2)[0]
_path.insert(1, _one_folder_up)

# if __name__ == "__main__":
#     from os.path import abspath as _abspath
#     import imp as _imp
#     _current_folder_init = _abspath(__file__).rsplit('/', 1)[0]+ "/__init__.py"
#     _imp.load_source("__init__", _current_folder_init)