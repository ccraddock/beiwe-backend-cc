from bson import ObjectId

print "This is the legacy shell for interfacing with mongodb.  This has been deprecated and will be removed"
from config import load_django

from libs.s3 import *
from db.user_models import User, Users, Admin, Admins
from db.study_models import Survey, Surveys, Study, Studies, StudyDeviceSettings, StudyDeviceSettingsCollection
from db.data_access_models import ChunkRegistry, ChunksRegistry, FileProcessLock, FileProcessLockCollection, FilesToProcess, FileToProcess, PipelineUpload, PipelineUploads
from db.profiling import EncryptionErrorMetadata, LineEncryptionError, DecryptionKeyError, UploadTracking, EncryptionErrorMetadatas, DecryptionKeyErrors, LineEncryptionErrors, Uploads
