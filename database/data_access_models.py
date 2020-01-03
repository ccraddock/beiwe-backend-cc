import json
import random
import string

from datetime import datetime

from django.db import models
from django.utils import timezone

from config.constants import ALL_DATA_STREAMS, CHUNKABLE_FILES, CHUNK_TIMESLICE_QUANTUM, PIPELINE_FOLDER
from database.validators import LengthValidator
from libs.security import chunk_hash, low_memory_chunk_hash
from database.models import AbstractModel
from database.study_models import Study


class FileProcessingLockedError(Exception): pass
class UnchunkableDataTypeError(Exception): pass
class ChunkableDataTypeError(Exception): pass


class ChunkRegistry(AbstractModel):

    DATA_TYPE_CHOICES = tuple([(stream_name, stream_name) for stream_name in ALL_DATA_STREAMS])

    is_chunkable = models.BooleanField()
    chunk_path = models.CharField(max_length=256, db_index=True)  # , unique=True)
    chunk_hash = models.CharField(max_length=25, blank=True)

    data_type = models.CharField(max_length=32, choices=DATA_TYPE_CHOICES, db_index=True)
    time_bin = models.DateTimeField(db_index=True)

    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='chunk_registries', db_index=True)
    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='chunk_registries', db_index=True)
    survey = models.ForeignKey('Survey', blank=True, null=True, on_delete=models.PROTECT, related_name='chunk_registries', db_index=True)

    number_of_observations = models.PositiveIntegerField(blank=True, null=True)
    
    @classmethod
    def register_chunked_data(cls, data_type, time_bin, chunk_path, file_contents, study_id, participant_id, survey_id=None):
        
        if data_type not in CHUNKABLE_FILES:
            raise UnchunkableDataTypeError

        # we want to make sure that there are no extraneous newline characters at the
        # end of the line. we want the line to end in exactly one newline character
        file_contents = file_contents.rstrip('\n') + '\n'

        # we subtract one to exclude the header line
        chunk_file_number_of_observations = file_contents.count('\n') - 1

        chunk_hash_str = chunk_hash(file_contents)

        
        time_bin = int(time_bin) * CHUNK_TIMESLICE_QUANTUM
        time_bin = timezone.make_aware(datetime.utcfromtimestamp(time_bin), timezone.utc)
        # previous time_bin form was this:
        # datetime.fromtimestamp(time_bin)
        # On the server, but not necessarily in development environments, datetime.fromtimestamp(0)
        # provides the same date and time as datetime.utcfromtimestamp(0).
        # timezone.make_aware(datetime.utcfromtimestamp(0), timezone.utc) creates a time zone
        # aware datetime that is unambiguous in the UTC timezone and generally identecal timestamps.
        # Django's behavior (at least on this project, but this project is set to the New York
        # timezone so it should be generalizable) is to add UTC as a timezone when storing a naive
        # datetime in the database.
        
        cls.objects.create(
            is_chunkable=True,
            chunk_path=chunk_path,
            chunk_hash=chunk_hash_str,
            data_type=data_type,
            time_bin=time_bin,
            study_id=study_id,
            participant_id=participant_id,
            survey_id=survey_id,
            number_of_observations=chunk_file_number_of_observations
        )
    
    @classmethod
    def register_unchunked_data(cls, data_type, unix_timestamp, chunk_path, study_id, participant_id, survey_id=None):
        # see comment in register_chunked_data above
        time_bin = timezone.make_aware(datetime.utcfromtimestamp(unix_timestamp), timezone.utc)
        
        if data_type in CHUNKABLE_FILES:
            raise ChunkableDataTypeError
        
        # we want to make sure that there are no extraneous newline characters at the
        # end of the line. we want the line to end in exactly one newline character
        file_contents = file_contents.rstrip('\n') + '\n'

        # we subtract one to exclude the header line
        chunk_file_number_of_observations = file_contents.count('\n') - 1

        cls.objects.create(
            is_chunkable=False,
            chunk_path=chunk_path,
            chunk_hash='',
            data_type=data_type,
            time_bin=time_bin,
            study_id=study_id,
            participant_id=participant_id,
            survey_id=survey_id,
            number_of_observations=chunk_file_number_of_observations
        )

    @classmethod
    def get_chunks_time_range(cls, study_id, user_ids=None, data_types=None, start=None, end=None):
        """
        This function uses Django query syntax to provide datetimes and have Django do the
        comparison operation, and the 'in' operator to have Django only match the user list
        provided.
        """

        query = {'study_id': study_id, 'deleted': False}
        if user_ids:
            query['participant__patient_id__in'] = user_ids
        if data_types:
            query['data_type__in'] = data_types
        if start:
            query['time_bin__gte'] = start
        if end:
            query['time_bin__lte'] = end
        return cls.objects.filter(**query)

    def update_chunk_hash(self, data_to_hash):
        # we want to make sure that there are no extraneous newline characters at the
        # end of the line. we want the line to end in exactly one newline character
        data_to_hash = data_to_hash.rstrip('\n') + '\n'

        # we subtract one to exclude the header line
        chunk_file_number_of_observations = data_to_hash.count('\n') - 1

        self.chunk_hash = chunk_hash(data_to_hash)
        self.number_of_observations = chunk_file_number_of_observations
        self.save()

    def low_memory_update_chunk_hash(self, list_data_to_hash):
        # we want to make sure that there are no extraneous newline characters at the
        # end of the line. we want the line to end in exactly one newline character
        data_to_hash = list_data_to_hash[0].rstrip('\n') + '\n'

        # we subtract one to exclude the header line
        chunk_file_number_of_observations = data_to_hash.count('\n') - 1

        self.chunk_hash = low_memory_chunk_hash([data_to_hash])
        self.number_of_observations = chunk_file_number_of_observations
        self.save()


class FileToProcess(AbstractModel):

    s3_file_path = models.CharField(max_length=256, blank=False)

    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='files_to_process')
    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='files_to_process')

    @classmethod
    def append_file_for_processing(cls, file_path, study_object_id, **kwargs):
        # Get the study's primary key
        study_pk = Study.objects.filter(object_id=study_object_id).values_list('pk', flat=True).get()
        
        #if file_path[:24] == study_object_id:
        cls.objects.create(s3_file_path=file_path, study_id=study_pk, **kwargs)
        #else:
            #cls.objects.create(s3_file_path=study_object_id + '/' + file_path, study_id=study_pk, **kwargs)


class FileProcessLock(AbstractModel):
    
    lock_time = models.DateTimeField(null=True)
    
    @classmethod
    def lock(cls):
        if cls.islocked():
            raise FileProcessingLockedError('File processing already locked')
        else:
            cls.objects.create(lock_time=timezone.now())
    
    @classmethod
    def unlock(cls):
        cls.objects.all().delete()
    
    @classmethod
    def islocked(cls):
        return cls.objects.exists()
    
    @classmethod
    def get_time_since_locked(cls):
        return timezone.now() - FileProcessLock.objects.last().lock_time


class InvalidUploadParameterError(Exception): pass


class PipelineUpload(AbstractModel):
    REQUIREDS = [
        "study_id",
        "tags",
        "file_name",
    ]
    
    # no related name, this is
    object_id = models.CharField(max_length=24, unique=True, validators=[LengthValidator(24)])
    study = models.ForeignKey(Study, related_name="pipeline_uploads")
    file_name = models.TextField()
    s3_path = models.TextField()
    file_hash = models.CharField(max_length=128)

    @classmethod
    def get_creation_arguments(cls, params, file_object):
        errors = []

        # ensure required are present, we don't allow falsey contents.
        for field in PipelineUpload.REQUIREDS:
            if not params.get(field, None):
                errors.append('missing required parameter: "%s"' % field)

        # if we escape here early we can simplify the code that requires all parameters later
        if errors:
            raise InvalidUploadParameterError("\n".join(errors))

        # validate study_id
        study_id_object_id = params["study_id"]
        if not Study.objects.get(object_id=study_id_object_id):
            errors.append(
                'encountered invalid study_id: "%s"'
                % params["study_id"] if params["study_id"] else None
            )

        study_id = Study.objects.get(object_id=study_id_object_id).id

        if len(params['file_name']) > 256:
            errors.append("encountered invalid file_name, file_names cannot be more than 256 characters")

        if cls.objects.filter(file_name=params['file_name']).count():
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
            tags = None
            errors.append("could not parse tags, ensure that your uploaded list of tags is a json compatible array.")

        if errors:
            raise InvalidUploadParameterError("\n".join(errors))

        created_on = timezone.now()
        file_hash = low_memory_chunk_hash(file_object.read())
        file_object.seek(0)

        s3_path = "%s/%s/%s/%s/%s" % (
            PIPELINE_FOLDER,
            params["study_id"],
            params["file_name"],
            created_on.isoformat(),
            ''.join(random.choice(string.ascii_letters + string.digits) for i in range(32)),
            # todo: file_name?
        )

        creation_arguments = {
            "created_on": created_on,
            "s3_path": s3_path,
            "study_id": study_id,
            "file_name": params["file_name"],
            "file_hash": file_hash,
        }

        return creation_arguments, tags


class PipelineUploadTags(AbstractModel):
    pipeline_upload = models.ForeignKey(PipelineUpload, related_name="tags")
    tag = models.TextField()
