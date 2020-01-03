import json
import random
import string

from bson import ObjectId
from datetime import datetime
from mongolia.constants import REQUIRED_STRING, REQUIRED_DATETIME, REQUIRED_LIST, REQUIRED_OBJECTID

from config.constants import (CHUNKABLE_FILES, CHUNK_TIMESLICE_QUANTUM, CONCURRENT_NETWORK_OPS,
    PIPELINE_FOLDER)
from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED
from db.study_models import Studies
from libs.security import chunk_hash, low_memory_chunk_hash


class FileProcessingLockedError(Exception): pass

class ChunkRegistry(DatabaseObject):
    PATH = "beiwe.chunk_registry"
    
    #study_id, data_type, user_id, survey_id, and time_bin should have indexes,
    # there is a create_indexes script to do this.
    DEFAULTS = {"study_id":REQUIRED,
                "user_id":REQUIRED_STRING,
                "data_type": "",
                "time_bin": REQUIRED,
                "chunk_hash": None,
                "chunk_path": REQUIRED_STRING,
                "is_chunkable": REQUIRED,
                "survey_id": None}

    @classmethod
    def add_new_chunk(cls, study_id, user_id, data_type, s3_file_path,
                      time_bin, file_contents=None, survey_id=None):
        is_chunkable = data_type in CHUNKABLE_FILES
        if is_chunkable: time_bin = int(time_bin)*CHUNK_TIMESLICE_QUANTUM

        ChunkRegistry.create(
            {"study_id": study_id,
            "user_id": user_id,
            "data_type": data_type,
            "chunk_path": s3_file_path,
            "chunk_hash": chunk_hash(file_contents) if is_chunkable else None,
            "time_bin": datetime.fromtimestamp(time_bin),
            "is_chunkable": is_chunkable,
            "survey_id": survey_id }, #the survey_id field is only used by the timings file.
            random_id=True )
#         print "new chunk:", s3_file_path
    
    def update_chunk_hash(self, data_to_hash):
        self["chunk_hash"] = chunk_hash(data_to_hash)
        self.save()
#         print "upd chunk", self['chunk_path']

    def low_memory_update_chunk_hash(self, list_data_to_hash):
        self["chunk_hash"] = low_memory_chunk_hash(list_data_to_hash)
        self.save()

class FileToProcess(DatabaseObject):
    PATH = "beiwe.file_to_process"
    DEFAULTS = { "s3_file_path":REQUIRED_STRING,
                 "study_id": REQUIRED,
                 "user_id": REQUIRED_STRING }
    
    @classmethod
    def append_file_for_processing(cls, file_path, study_id, user_id):
        if file_path[:24] == str(study_id): 
            FileToProcess.create( {"s3_file_path":file_path, "study_id":study_id,
                                    "user_id":user_id}, random_id=True)
        else: FileToProcess.create( {"s3_file_path":str(study_id)+'/'+file_path,
                                     "study_id":study_id, "user_id":user_id},
                                     random_id=True)

class FileProcessLock(DatabaseObject):
    PATH = "beiwe.file_process_running"
    DEFAULTS = {"mark":None}
    @classmethod
    def lock(cls):
        if FileProcessLockCollection.count() > 0:
            raise FileProcessingLockedError
        FileProcessLock.create({"mark":datetime.utcnow()}, random_id=True)
    @classmethod
    def unlock(cls):
        for f in FileProcessLockCollection():
            f.remove()
    @classmethod
    def islocked(cls):
        if FileProcessLockCollection.count() > 0:
            return True
        return False
    @classmethod
    def get_time_since_locked(cls):
        return datetime.utcnow() - FileProcessLockCollection()[0]["mark"]
        

################################################################################

class ChunksRegistry(DatabaseCollection):
    OBJTYPE = ChunkRegistry
    
    @classmethod
    def get_chunks_time_range(cls, study_id, user_ids=None, data_types=None, start=None, end=None):
        """ This function uses mongo query syntax to provide datetimes and have mongo do the
        comparison operation, and the 'in' operator to have mongo only match the user list
        provided. """

        query = {"study_id":study_id}
        if user_ids: query["user_id"] = { "$in":user_ids }
        if data_types: query["data_type"] = { "$in":data_types }
        if start and end: query["time_bin"] = {"$gte": start, "$lte": end }
        if start and not end: query["time_bin"] = { "$gte": start}
        if end and not start: query["time_bin"] = { "$lte": end }
        print(query)
        return cls.iterator(query=query, page_size=10*CONCURRENT_NETWORK_OPS)

class FilesToProcess(DatabaseCollection):
    OBJTYPE = FileToProcess
class FileProcessLockCollection(DatabaseCollection):
    OBJTYPE = FileProcessLock

####################################################################################################
####################################################################################################
####################################################################################################

class InvalidUploadParameterError(Exception): pass


class PipelineUpload(DatabaseObject):
    PATH = "beiwe.pipeline_registry"
    
    REQUIREDS = {
        "study_id": REQUIRED_OBJECTID,
        "tags": REQUIRED_LIST,
        "file_name": REQUIRED_STRING
    }
    
    INTERNALS = {
        "creation_time": REQUIRED_DATETIME,
        "s3_path": REQUIRED_STRING,
        "file_hash": REQUIRED_STRING,
    }
    
    DEFAULTS = {}
    DEFAULTS.update(INTERNALS)
    DEFAULTS.update(REQUIREDS)
    
    @classmethod
    def get_creation_arguments(cls, params, file_object):
        errors = []
    
        # ensure required are present, we don't allow falsey contents.
        for key in PipelineUpload.REQUIREDS:
            if not params.get(key, None):
                errors.append('missing required parameter: "%s"' % key)
        
        # if we escape here early we can simplify the code that requires all parameters later
        if errors:
            raise InvalidUploadParameterError("\n".join(errors))
        
        # validate study_id
        study_id_object_id = ObjectId(params["study_id"])
        if not Studies(_id=study_id_object_id):
            errors.append(
                    'encountered invalid study_id: "%s"'
                    % params["study_id"] if params["study_id"] else None
            )
    
        print 'file_name' in params
        print params['file_name']
        if len(params['file_name']) > 256:
            errors.append("encountered invalid file_name, file_names cannot be more than 256 characters")
    
        if PipelineUploads.count(file_name=params['file_name']):
            errors.append('a file with the name "%s" already exists' % params['file_name'])
            
        try:
            tags = json.loads(params["tags"])
            if not isinstance(tags, list):
                # must be json list, can't be json dict, number, or string.
                raise ValueError()
            if not tags:
                errors.append("you must provide at least one tag for your file.")
            tags = [str(_) for _ in tags]
        except ValueError:
            errors.append("could not parse tags, ensure that your uploaded list of tags is a json compatible array.")
            
        if errors:
            raise InvalidUploadParameterError("\n".join(errors))
    
        creation_time = datetime.utcnow()
        file_hash = low_memory_chunk_hash(file_object.read())
        file_object.seek(0)
    
        s3_path = "%s/%s/%s/%s/%s" % (
            PIPELINE_FOLDER,
            params["study_id"],
            params["file_name"],
            creation_time.isoformat(),
            ''.join(random.choice(string.ascii_letters + string.digits) for i in range(32)),
            # todo: file_name?
        )
    
        return {
            "creation_time": creation_time,
            "s3_path": s3_path,
            "study_id": study_id_object_id,
            "tags": tags,
            "file_name": params["file_name"],
            "file_hash": file_hash,
        }
    
    
class PipelineUploads(DatabaseCollection):
    OBJTYPE = PipelineUpload