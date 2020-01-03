
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from database.study_models import DeviceSettings, Study, Survey, SurveyArchive


@receiver(post_save, sender=Study)
def populate_study_device_settings(sender, **kwargs):
    """
    Ensure that every newly created Study object has a DeviceSettings object. This essentially
    makes the OneToOneField have null=False in both directions.
    """

    my_study = kwargs['instance']
    if kwargs['created'] and not hasattr(my_study, 'device_settings'):
        # If my_study has just been created and doesn't have a DeviceSettings
        # attached to it, create one with the default parameters.
        DeviceSettings.objects.create(study=my_study)


@receiver(pre_save, sender=Survey)
def create_survey_archive(sender, **kwargs):
    """
    Ensure that every time a Survey is edited, a SurveyArchive (SA) is stored which holds the
    current contents of the Survey before saving, as well as a pair of timestamps marking the
    time range over which the SA applies.
    """
    
    # The Survey instance being passed has the updated contents of the Survey. To get
    # the preexisting contents of the Survey, make a database call using the passed
    # instance's primary key. If we get an ObjectDoesNotExist error short-circuit because
    # that means it is the initial save operation.
    my_survey_plus_updates = kwargs['instance']
    try:
        my_survey = Survey.objects.get(pk=my_survey_plus_updates.pk)
    except ObjectDoesNotExist:
        return
    
    # All fields present in AbstractSurvey, plus the study foreign key which is
    # separately present in Survey and SurveyArchive.
    survey_fields = [f.name for f in super(Survey, my_survey)._meta.fields]
    survey_fields.append('study_id')
    
    # Prepare a new archive containing the archive-specific information
    new_archive = SurveyArchive(survey=my_survey, archive_start=my_survey.last_updated)
    
    try:
        # Get the most recent archive for this Survey, to check whether the Survey has been edited
        last_archive = my_survey.archives.latest('archive_end')
    except SurveyArchive.DoesNotExist:
        survey_dirty = True  # If there is no previous archive, we automatically make a new one
    else:
        survey_dirty = False
    
    for shared_field in survey_fields:

        # Update all of the shared fields in the archive to have the original survey's values
        if shared_field == 'name':
            setattr(new_archive, shared_field, '{0} {1}'.format(getattr(my_survey, shared_field), timezone.now().isoformat()))
        else: 
            setattr(new_archive, shared_field, getattr(my_survey, shared_field))
        
        if not survey_dirty and getattr(my_survey, shared_field) != getattr(last_archive, shared_field):
            # If the survey has been edited since the last archive was made, mark the survey as
            # dirty. This tells us that we have to make a new archive object.
            survey_dirty = True
    
    if survey_dirty:
        # If the survey has been edited, save the new archive. This automatically sets the
        # archive_end field to be the current time.
        new_archive.save()
    else:
        # If the survey has not been edited, we don't save the new archive. Update the
        # previous archive to extend to the current time. Note that object.update saves the
        # object, unlike QuerySet.update. See base_models.AbstractModel for details.
        last_archive.update(archive_end=timezone.now())
