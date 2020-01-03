import functools
from datetime import datetime, timedelta

from flask import session, redirect, request, json
from werkzeug.exceptions import abort

from database.study_models import Study
from database.user_models import Researcher
from libs.security import generate_easy_alphanumeric_string


################################################################################
############################ Website Functions #################################
################################################################################


def authenticate_admin_login(some_function):
    """Decorator for functions (pages) that require a login.
       Redirects to index if not authenticate_admin_login"""
    
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        if is_logged_in():
            return some_function(*args, **kwargs)
        else:
            return redirect("/")

    return authenticate_and_call


def log_in_admin(username):
    session['admin_uuid'] = generate_easy_alphanumeric_string()
    session['expiry'] = datetime.now() + timedelta(hours=6)
    session['admin_username'] = username


def logout_loggedin_admin():
    if "admin_uuid" in session:
        del session['admin_uuid']
    if "expiry" in session:
        del session['expiry']


def is_logged_in():
    if 'expiry' in session and session['expiry'] > datetime.now():
        return 'admin_uuid' in session
    logout_loggedin_admin()

################################################################################
########################## Study Editing Privileges ############################
################################################################################

class ArgumentMissingException(Exception): pass

def authenticate_admin_study_access(some_function):
    """ This authentication decorator checks whether the user has permission to to access the
    study/survey they are accessing.
    This decorator requires the specific keywords "survey_id" or "study_id" be provided as
    keywords to the function, and will error if one is not.
    The pattern is for a url with <string:survey/study_id> to pass in this value.
    A system admin is always able to access a study or survey. """
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):

        # Check for regular login requirement
        if not is_logged_in():
            return redirect("/")

        username = session["admin_username"]
        try:
            researcher = Researcher.objects.get(username=username)
        except Researcher.DoesNotExist:
            return abort(404)

        # Get values first from kwargs, then from the POST request
        survey_id = kwargs.get('survey_id', request.values.get('survey_id', None))
        study_id = kwargs.get('study_id', request.values.get('study_id', None))

        # Check proper syntax usage.
        if not survey_id and not study_id:
            raise ArgumentMissingException()

        # We want the survey_id check to execute first if both args are supplied.
        if survey_id:
            study_set = Study.objects.filter(surveys=survey_id)
            if not study_set.exists():
                return abort(404)

            # Check that researcher is either a researcher on the study or an admin
            study_id = study_set.values_list('pk', flat=True).get()
            if not researcher.admin:
                if not researcher.studies.filter(pk=study_id).exists():
                    return abort(403)

        if study_id:
            study_set = Study.objects.filter(pk=study_id)
            if not study_set.exists():
                return abort(404)

            if not researcher.admin:
                if not researcher.studies.filter(pk=study_id).exists():
                    return abort(403)

        return some_function(*args, **kwargs)

    return authenticate_and_call


# TODO: Low priority. Josh.  Find a way to do these solely in the nav bar template.
def admin_is_system_admin():
    # TODO: Low Priority. Josh. find a more efficient way of checking this and
    # "allowed_studies" than passing it to every render_template.
    researcher = Researcher.objects.get(username=session['admin_username'])
    return researcher.admin


def get_admins_allowed_studies_as_query_set():
    researcher = Researcher.objects.get(username=session['admin_username'])
    return Study.get_all_studies_by_name().filter(researchers=researcher)


def get_admins_allowed_studies(as_json=True):
    """
    Return a list of studies which the currently logged-in researcher is authorized to view and edit.
    """
    researcher = Researcher.objects.get(username=session['admin_username'])
    study_set = [
        study for study in
        Study.get_all_studies_by_name().filter(researchers=researcher)
            .values("name", "object_id", "id", "is_test")
    ]
    if as_json:
        return json.dumps(study_set)
    else:
        return study_set


################################################################################
########################## System Administrator ################################
################################################################################

def authenticate_system_admin(some_function):
    """ Authenticate system admin checks whether a user is a system admin before allowing access
    to pages marked with this decorator.  If a study_id variable is supplied as a keyword
    argument, the decorator will automatically grab the ObjectId in place of the string provided
    in a route.
    
    NOTE: if you are using this function along with the authenticate_admin_study_access decorator
    you must place this decorator below it, otherwise behavior is undefined and probably causes a
    500 error inside the authenticate_admin_study_access decorator. """
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        # Check for regular login requirement
        if not is_logged_in():
            return redirect("/")

        researcher = Researcher.objects.get(username=session['admin_username'])
        if not researcher.admin:
            # TODO: Low Priority. Josh. redirect to a URL, not a template file
            return abort(403)

        if 'study_id' in kwargs:
            if not Study.objects.filter(pk=kwargs['study_id']).exists():
                return redirect("/")

        return some_function(*args, **kwargs)

    return authenticate_and_call

