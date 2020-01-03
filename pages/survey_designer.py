from flask import abort, Blueprint, render_template, request, redirect, flash
from django.core.exceptions import ValidationError

from config.settings import DOMAIN_NAME
from database.study_models import Survey
from libs.admin_authentication import authenticate_admin_study_access,\
    get_admins_allowed_studies, admin_is_system_admin


survey_designer = Blueprint('survey_designer', __name__)

# TODO: Low Priority. implement "study does not exist" page.
# TODO: Low Priority. implement "survey does not exist" page.


@survey_designer.route('/create_survey/<string:study_id>/<string:survey_type>', methods=['GET', 'POST'])
@authenticate_admin_study_access
def create_survey(study_id=None, survey_type='tracking_survey'):
    if request.method == 'GET':
        return render_template(
            'create_survey.html',
            allowed_studies=get_admins_allowed_studies(),
            study_id=study_id,
            survey_type=survey_type,
            system_admin=admin_is_system_admin()
        )

    # Drop any whitespace or special characters from the username
    survey_name = request.form.get('survey_name', '')

    try:
        new_survey = Survey.create_with_settings(study_id=study_id, survey_type=survey_type, name=survey_name)
    except ValidationError:
        flash("Please choose a different name, {0} is already in use.".format(survey_name), 'danger')
        return redirect('/create_survey/{0:d}/{1}'.format(int(study_id), survey_type))

    return redirect('/edit_survey/{:d}'.format(new_survey.id))

@survey_designer.route('/edit_survey/<string:survey_id>')
@authenticate_admin_study_access
def render_edit_survey(survey_id=None):
    try:
        survey = Survey.objects.get(pk=survey_id)
    except Survey.DoesNotExist:
        return abort(404)

    s = survey.as_native_python()
    study = survey.study
    return render_template(
        'edit_survey.html',
        survey=survey.as_native_python(),
        study=study,
        allowed_studies=get_admins_allowed_studies(),
        system_admin=admin_is_system_admin(),
        domain_name=DOMAIN_NAME,  # used in a Javascript alert, see survey-editor.js
    )
