from flask import abort, Blueprint, redirect, request
from flask.templating import render_template

from config.settings import DOMAIN_NAME, IS_STAGING
from database.study_models import Study
from database.user_models import Researcher
from libs.admin_authentication import (
    authenticate_system_admin, authenticate_admin_login, admin_is_system_admin,
    get_admins_allowed_studies
)
from libs.security import check_password_requirements

admin_api = Blueprint('admin_api', __name__)

"""######################### Study Administration ###########################"""


@admin_api.route('/add_researcher_to_study', methods=['POST'])
@authenticate_system_admin
def add_researcher_to_study():
    researcher_id = request.values['researcher_id']
    study_id = request.values['study_id']
    Researcher.studies.through.objects.get_or_create(researcher_id=researcher_id, study_id=study_id)

    # This gets called by both edit_researcher and edit_study, so the POST request
    # must contain which URL it came from.
    return redirect(request.values['redirect_url'])


@admin_api.route('/remove_researcher_from_study', methods=['POST'])
@authenticate_system_admin
def remove_researcher_from_study():
    researcher_id = request.values['researcher_id']
    study_id = request.values['study_id']
    Researcher.objects.get(pk=researcher_id).studies.remove(study_id)

    return redirect(request.values['redirect_url'])


@admin_api.route('/delete_researcher/<string:researcher_id>', methods=['GET', 'POST'])
@authenticate_system_admin
def delete_researcher(researcher_id):
    try:
        researcher = Researcher.objects.get(pk=researcher_id)
    except Researcher.DoesNotExist:
        return abort(404)
    
    researcher.studies.clear()
    researcher.delete()
    return redirect('/manage_researchers')


@admin_api.route('/set_researcher_password', methods=['POST'])
@authenticate_system_admin
def set_researcher_password():
    researcher = Researcher.objects.get(pk=request.form.get('researcher_id', None))
    new_password = request.form.get('password', '')
    if check_password_requirements(new_password, flash_message=True):
        researcher.set_password(new_password)
    return redirect('/edit_researcher/{:d}'.format(researcher.pk))


@admin_api.route('/rename_study/<string:study_id>', methods=['POST'])
@authenticate_system_admin
def rename_study(study_id=None):
    study = Study.objects.get(pk=study_id)
    new_study_name = request.form.get('new_study_name', '')
    study.name = new_study_name
    study.save()
    return redirect('/edit_study/{:d}'.format(study.pk))


"""##### Methods responsible for distributing APK file of Android app. #####"""


@admin_api.route("/downloads")
@authenticate_admin_login
def download_page():
    return render_template(
        "download_landing_page.html",
        system_admin=admin_is_system_admin(),
        allowed_studies=get_admins_allowed_studies(),
        domain_name=DOMAIN_NAME,
    )


@admin_api.route("/download")
def download_current():
    return redirect("https://s3.amazonaws.com/beiwe-app-backups/release/Beiwe-2.4.1-onnelaLabServer-release.apk")


@admin_api.route("/download_debug")
@authenticate_admin_login
def download_current_debug():
    return redirect("https://s3.amazonaws.com/beiwe-app-backups/release/Beiwe-debug.apk")


@admin_api.route("/download_beta")
@authenticate_admin_login
def download_beta():
    return redirect("https://s3.amazonaws.com/beiwe-app-backups/release/Beiwe.apk")


@admin_api.route("/download_beta_debug")
@authenticate_admin_login
def download_beta_debug():
    return redirect("https://s3.amazonaws.com/beiwe-app-backups/debug/Beiwe-debug.apk")


@admin_api.route("/download_beta_release")
@authenticate_admin_login
def download_beta_release():
    return redirect("https://s3.amazonaws.com/beiwe-app-backups/release/Beiwe-2.2.3-onnelaLabServer-release.apk")


@admin_api.route("/privacy_policy")
def download_privacy_policy():
    return redirect("https://s3.amazonaws.com/beiwe-app-backups/Beiwe+Data+Privacy+and+Security.pdf")

"""########################## Debugging Code ###########################"""

# This is here to check whether staging is correctly configured
if IS_STAGING:
    @admin_api.route("/is_staging")
    def is_staging():
        return "yes"
