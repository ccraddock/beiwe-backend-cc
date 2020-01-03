from datetime import datetime, timedelta

from db.mongolia_setup import DatabaseObject, DatabaseCollection
from config.constants import UPLOAD_FILE_TYPE_MAPPING
from mongolia.constants import REQUIRED_STRING, REQUIRED, REQUIRED_INT, REQUIRED_LIST, REQUIRED_DATETIME
from libs.security import decode_base64

PADDING_ERROR = "PADDING_ERROR"
MP4_PADDING = "MP4_PADDING"
EMPTY_KEY = "EMPTY_KEY"
MALFORMED_CONFIG = "MALFORMED_CONFIG"
IV_MISSING = "IV_MISSING"
LINE_EMPTY = "LINE_EMPTY"
LINE_IS_NONE = "LINE_EMPTY"
INVALID_LENGTH = "INVALID_LENGTH"
AES_KEY_BAD_LENGTH = "AES_KEY_BAD_LENGTH"
IV_BAD_LENGTH = "IV_BAD_LENGTH"

class EncryptionErrorMetadata(DatabaseObject):
    PATH = "beiwe.encryption_error_metadata"
    
    DEFAULTS = {
        "file_name":REQUIRED_STRING,
        "total_lines":REQUIRED_INT,
        "number_errors":REQUIRED_INT,
        "errors_lines":REQUIRED_LIST,
        "error_types":REQUIRED_LIST
    }
    
    
class LineEncryptionError(DatabaseObject):
    PATH = "beiwe.line_encryption_errors"

    DEFAULTS = {
        "type": REQUIRED_STRING,
        "line":REQUIRED_STRING,
        "base64_decryption_key": "",
        "prev_line": "",
        "next_line": ""
    }
    
    
class DecryptionKeyError(DatabaseObject):
    PATH = "beiwe.decryption_key_error"
    
    DEFAULTS = {
        "file_path": REQUIRED_STRING,
        "contents": REQUIRED,
        "user_id": REQUIRED_STRING
    }
    
    def decode(self):
        return decode_base64(self.contents)
    
    # def decrypt(self):
    #     from libs.s3 import get_client_private_key
    #     private_key = get_client_private_key(self.user_id, User(self.user_id).study_id)
    #     return private_key.decrypt( self.decode() )


class UploadTracking(DatabaseObject):
    PATH = "beiwe.upload_tracking"
    
    DEFAULTS = {
        "file_path": REQUIRED_STRING,
        "timestamp": REQUIRED_DATETIME,
        "user_id": REQUIRED_STRING,
        "file_size": None
    }
    
class EncryptionErrorMetadatas(DatabaseCollection):
    OBJTYPE = EncryptionErrorMetadata

class DecryptionKeyErrors(DatabaseCollection):
    OBJTYPE = DecryptionKeyError

class LineEncryptionErrors(DatabaseCollection):
    OBJTYPE = LineEncryptionError

class Uploads(DatabaseCollection):
    OBJTYPE = UploadTracking
    
    @classmethod
    def get_trailing(cls, time_delta, as_iterator=False):
        if as_iterator:
            return cls.iterator(query={"timestamp":{"$gte":datetime.utcnow() - time_delta}})
        else:
            return cls(query={"timestamp":{"$gte":datetime.utcnow() - time_delta}})

    @classmethod
    def get_trailing_count(cls, time_delta):
        return cls.count(query={"timestamp":{"$gte":datetime.utcnow() - time_delta}})
    
    @classmethod
    def weekly_stats(cls, days=7, get_usernames=False):
        ALL_FILETYPES = UPLOAD_FILE_TYPE_MAPPING.values()
        if get_usernames:
            data = {filetype:{"megabytes":0., "count":0, "users":set()} for filetype in ALL_FILETYPES}
        else:
            data = {filetype:{"megabytes":0., "count":0} for filetype in ALL_FILETYPES}
        
        data["totals"] = {}
        data["totals"]["total_megabytes"] = 0
        data["totals"]["total_count"] = 0
        data["totals"]["users"] = set()
        
        for i, upload in enumerate(cls.get_trailing(timedelta(days=days), as_iterator=True)):
            #global stats
            data["totals"]["total_count"] += 1
            data["totals"]["total_megabytes"] += upload['file_size'] / 1024. / 1024.
            data["totals"]["users"].add(upload['user_id'])
            
            #get data stream type from file_path
            file_type = UPLOAD_FILE_TYPE_MAPPING[upload['file_path'].split("/", 2)[1]]
            #update per-data-stream information
            data[file_type]["megabytes"] += upload['file_size'] / 1024. / 1024.
            data[file_type]["count"] += 1

            if get_usernames:
                data[file_type]["users"].add(upload["user_id"])
            if i % 10000 == 0:
                print "processed %s uploads..." % i
        
        data["totals"]["user_count"] = len(data["totals"]["users"])
        
        if not get_usernames: #purge usernames if we don't need them.
            del data["totals"]["users"]
        
        return data