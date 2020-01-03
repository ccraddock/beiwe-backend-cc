from datetime import timedelta

from django.db import models
from django.utils import timezone
from database.models import AbstractModel
from database.user_models import Researcher

class PipelineExecutionTracking(AbstractModel):

    researcher = models.ForeignKey('Researcher', on_delete=models.PROTECT, related_name='researcher_pipelines')
    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='study_pipelines')
    pipeline_submission_timestamp = models.DateTimeField()

    email_address_list = models.CharField(max_length=256, blank=True, null=True)
    query_start_datetime = models.CharField(max_length=256, blank=True, null=True)
    query_end_datetime = models.CharField(max_length=256, blank=True, null=True)
    participants = models.CharField(max_length=256, blank=True, null=True)

    batch_job_id = models.CharField(max_length=256, blank=True, null=True)

    execution_status = models.CharField(max_length=256)
    execution_error_text = models.TextField(blank=True, null=True)
    execution_start_datetime = models.DateTimeField(blank=True, null=True)
    execution_end_datetime = models.DateTimeField(blank=True, null=True)
    execution_time_minutes = models.FloatField(blank=True, null=True)
    
    @classmethod
    def pipeline_scheduled(cls, researcher_name, study_id, submission_timestamp,
        email_address_list, query_start_datetime, query_end_datetime, participants):

        researcher = Researcher.objects.get(username = researcher_name)

        study = researcher.studies.get(pk=study_id)

        obj=cls.objects.create(
            researcher = researcher,
            study = study, 
            pipeline_submission_timestamp = submission_timestamp,
            email_address_list = email_address_list,
            query_start_datetime = query_start_datetime,
            query_end_datetime = query_end_datetime,
            participants = participants,
            execution_status = 'queued')

        return obj.pk

    @classmethod
    def pipeline_started(cls, pipeline_id, start_timestamp):

        try:  
            pipeline_object = cls.objects.get(pk=pipeline_id)
        except Pipeline.DoesNotExist:
            print('Could not find pipeline {0} in pipeline database'.format(pipeline_id))
            raise

        pipeline_object.update( 
            execution_status = 'running',
            execution_start_datetime = start_timestamp)
       
        return

    @classmethod
    def pipeline_completed(cls, pipeline_id, end_timestamp):

        pipeline_object = cls.objects.get(pk=pipeline_id)

        pipeline_object.update( 
            execution_status = 'completed',
            execution_end_datetime = end_timestamp,
            execution_time_minutes = (end_timestamp - pipeline_object.execution_start_datetime).seconds / 60.0
            )
       
        return

    @classmethod
    def pipeline_crashed(cls, pipeline_id, error_timestamp, error_message):

        pipeline_object = cls.objects.get(pk=pipeline_id)

        # The error may occur after the job has been marked complete, if this is the case
        # lets ignore the error
        if 'completed' not in pipeline_object.execution_status:

            execution_time_minutes = 0.0
            if pipeline_object.execution_start_datetime:
                execution_time_minutes = (error_timestamp - pipeline_object.execution_start_datetime).seconds / 60.0

            pipeline_object.update( 
                execution_status = 'failed',
                execution_end_datetime = error_timestamp,
                execution_time_minutes = execution_time_minutes,
                execution_error_text = error_message
            )
        else:
            print('Job has already completed, ignoring error')
       
        return 

    @classmethod
    def pipeline_set_batch_job_id(cls, pipeline_id, batch_job_id):

        pipeline_object = cls.objects.get(pk=pipeline_id)

        pipeline_object.update( 
            batch_job_id = batch_job_id
            )

    @classmethod
    def terminate_job(cls, pipeline_id, terminate_time_stamp, reason=''):

        pipeline_object = cls.objects.get(pk=pipeline_id)
        
        execution_time_minutes = 0.0
        if pipeline_object.execution_start_datetime:
            execution_time_minutes = (terminate_time_stamp - pipeline_object.execution_start_datetime).seconds / 60.0

        pipeline_object.update( 
            execution_status = 'terminated',
            execution_end_datetime = terminate_time_stamp,
            execution_time_minutes = execution_time_minutes,
            execution_error_text = reason
            )
       
       
