from datetime import timedelta

from django.db import models
from django.utils import timezone

from config.constants import UPLOAD_FILE_TYPE_MAPPING
from libs.security import decode_base64
from libs.parse_filename import parse_filename
from database.models import JSONTextField, AbstractModel
from database.user_models import Participant

class EncryptionErrorMetadata(AbstractModel):
    
    file_name = models.CharField(max_length=256)
    total_lines = models.PositiveIntegerField()
    number_errors = models.PositiveIntegerField()
    error_lines = JSONTextField()
    error_types = JSONTextField()
    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, null=True)


class LineEncryptionError(AbstractModel):

    AES_KEY_BAD_LENGTH = "AES_KEY_BAD_LENGTH"
    EMPTY_KEY = "EMPTY_KEY"
    INVALID_LENGTH = "INVALID_LENGTH"
    IV_BAD_LENGTH = "IV_BAD_LENGTH"
    IV_MISSING = "IV_MISSING"
    LINE_EMPTY = "LINE_EMPTY"
    LINE_IS_NONE = "LINE_IS_NONE"
    MALFORMED_CONFIG = "MALFORMED_CONFIG"
    MP4_PADDING = "MP4_PADDING"
    PADDING_ERROR = "PADDING_ERROR"
    
    ERROR_TYPE_CHOICES = (
        (AES_KEY_BAD_LENGTH, AES_KEY_BAD_LENGTH),
        (EMPTY_KEY, EMPTY_KEY),
        (INVALID_LENGTH, INVALID_LENGTH),
        (IV_BAD_LENGTH, IV_BAD_LENGTH),
        (IV_MISSING, IV_MISSING),
        (LINE_EMPTY, LINE_EMPTY),
        (LINE_IS_NONE, LINE_IS_NONE),
        (MP4_PADDING, MP4_PADDING),
        (MALFORMED_CONFIG, MALFORMED_CONFIG),
        (PADDING_ERROR, PADDING_ERROR),
    )
    
    type = models.CharField(max_length=32, choices=ERROR_TYPE_CHOICES)
    line = models.TextField(blank=True)
    base64_decryption_key = models.CharField(max_length=256)
    prev_line = models.TextField(blank=True)
    next_line = models.TextField(blank=True)
    participant = models.ForeignKey(Participant, null=True, on_delete=models.PROTECT)


class DecryptionKeyError(AbstractModel):
    
    file_path = models.CharField(max_length=256)
    contents = models.TextField()
    traceback = models.TextField(null=True)
    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='decryption_key_errors')
    
    def decode(self):
        return decode_base64(self.contents)


class ReceivedDataStatsHourly(AbstractModel):

    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='received_data_stats_hourly')
    data_type = models.CharField(max_length=256)
    data_collection_hour = models.DateTimeField()

    number_of_observations = models.PositiveIntegerField()

    class Meta:
        unique_together = ('participant', 'data_type', 'data_collection_hour')
    
    @classmethod
    def update_statistics(cls, file_path, participant, number_of_observations, timestamp):
 
        # determine file type
        data_type = parse_filename(file_path)['data_type']

        # round timestamp down to the nearest hour
        timestamp_hour = timestamp.replace(microsecond=0, second=0, minute=0)

        if not cls.objects.filter(participant=participant, data_type=data_type, data_collection_hour=timestamp_hour).exists():
            cls.objects.create(
                participant = participant,
                data_type = data_type,
                data_collection_hour = timestamp_hour,
                number_of_observations = number_of_observations
            )

        else:
            statistics_object = cls.objects.get(participant=participant, data_type=data_type, data_collection_hour=timestamp_hour)
            statistics_object.update(
                number_of_observations = statistics_object.number_of_observations + number_of_observations
            )

        return
 
class ReceivedDataStats(AbstractModel):

    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='received_data_stats')
    data_type = models.CharField(max_length=256)

    last_upload_timestamp = models.DateTimeField()

    number_of_uploads = models.PositiveIntegerField()
    number_bytes_uploaded = models.BigIntegerField()

    class Meta:
        unique_together = ('participant', 'data_type')
    
    @classmethod
    def update_statistics(cls, file_path, participant, file_size, timestamp):

        # determine file type
        data_type = parse_filename(file_path)['data_type']

        if not cls.objects.filter(participant=participant, data_type=data_type).exists():
            cls.objects.create(
                participant = participant,
                data_type = data_type,
                last_upload_timestamp = timestamp,
                number_of_uploads = 1,
                number_bytes_uploaded = file_size
            )

        else:
            statistics_object = cls.objects.get(participant=participant, data_type=data_type)
            statistics_object.update(
                number_of_uploads = statistics_object.number_of_uploads + 1,
                number_bytes_uploaded = statistics_object.number_bytes_uploaded + file_size
            )
 
            if timestamp > statistics_object.last_upload_timestamp:
                statistics_object.update(
                    last_upload_timestamp = timestamp
                )
                 

class UploadTracking(AbstractModel):
    
    file_path = models.CharField(max_length=256)
    file_size = models.PositiveIntegerField()
    timestamp = models.DateTimeField()

    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='upload_trackers')
    
    @classmethod
    def get_trailing_count(cls, time_delta):
        cls.objects.filter(timestamp__gte=timezone.now() - time_delta).count()
    
    @classmethod
    def weekly_stats(cls, days=7, get_usernames=False):
        ALL_FILETYPES = UPLOAD_FILE_TYPE_MAPPING.values()
        if get_usernames:
            data = {filetype: {"megabytes": 0., "count": 0, "users": set()} for filetype in ALL_FILETYPES}
        else:
            data = {filetype: {"megabytes": 0., "count": 0} for filetype in ALL_FILETYPES}
        
        data["totals"] = {}
        data["totals"]["total_megabytes"] = 0
        data["totals"]["total_count"] = 0
        data["totals"]["users"] = set()
        days_delta = timezone.now() - timedelta(days=days)
        # .values is a huge speedup, .iterator isn't but it does let us print progress realistically
        query = UploadTracking.objects.filter(timestamp__gte=days_delta).values(
                "file_path", "file_size", "participant"
        ).iterator()
        
        for i, upload in enumerate(query):
            # global stats
            data["totals"]["total_count"] += 1
            data["totals"]["total_megabytes"] += upload["file_size"]/ 1024. / 1024.
            data["totals"]["users"].add(upload["participant"])
            
            # get data stream type from file_path (woops, ios log broke this code, fixed)
            data_type = parse_filename(file_path)['data_type']

            # update per-data-stream information
            data[file_type]["megabytes"] += upload["file_size"]/ 1024. / 1024.
            data[file_type]["count"] += 1
            
            if get_usernames:
                data[file_type]["users"].add(upload["participant"])
            if i % 10000 == 0:
                print("processed %s uploads..." % i)
        
        data["totals"]["user_count"] = len(data["totals"]["users"])
        
        if not get_usernames:  # purge usernames if we don't need them.
            del data["totals"]["users"]
        
        return data
