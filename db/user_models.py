from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED, ID_KEY
from libs.security import (generate_hash_and_salt, generate_user_hash_and_salt,
                           compare_password, device_hash, generate_user_password_and_salt,
                           generate_easy_alphanumeric_string, generate_random_string)

"""#############################################################################
################################### USER STUFF #################################
#############################################################################"""


class User( DatabaseObject ):
    """ The User database object contains the password hashes and unique user names of any
    patients in the study.  Elements in the database have the functionality described here,
    and two convenience method static methods that can be run on the User class/object itself.
    
    Users have passwords hashed once with sha256 and a many times (as defined in security.py)
    with PBKDF2, and salted using a cryptographically secure random number generator.  The sha256
    check duplicates the storage of the password on the mobile device, so that the user's
    password is never stored in a reversible manner. """
    PATH = "beiwe.users"
    
    # Column Name:Default Value.  Use REQUIRED to indicate a non-nullable value.
    # We are using the patient's assigned ID as a unique Id.
    DEFAULTS = { "password":REQUIRED,
                'device_id':None,
                'salt':REQUIRED,
                'study_id':REQUIRED,
                'os_type': None }
    
    @classmethod
    def create(cls, study_id):
        """ Creates a new patient with random patient_id and password."""
        patient_id = generate_easy_alphanumeric_string()
        if User(patient_id): cls.create(study_id) #if user exists, recurse.

        password, password_hash, salt = generate_user_password_and_salt()

        new_client = { ID_KEY: patient_id, "password":password_hash,
                      'device_id':None, "salt":salt, 'study_id':study_id }
        super(User, cls).create(new_client)
        return patient_id, password
    
    def validate_password(self, compare_me):
        """ Checks if the input matches the instance's password hash."""
        return compare_password( compare_me, self['salt'], self['password'] )
    
    def debug_validate_password(self, compare_me):
        """ Checks if the input matches the instance's password hash, but does
        the hashing for you for use on the command line."""
        compare_me = device_hash(compare_me)
        return compare_password( compare_me, self['salt'], self['password'] )
    
    def reset_password(self):
        """ Resets the patient's password to match an sha256 hash of the returned string."""
        password = generate_easy_alphanumeric_string()
        self.set_password( password )
        return password
    
    def set_device(self, device_id):
        """ Sets the device id to the new value"""
        self['device_id'] =  device_id
        self.save()

    def set_os_type(self, os_type):
        """ Sets the os_type to the new value"""
        self['os_type'] =  os_type
        self.save()

    def clear_device(self):
        """ Clears the device entry."""
        self['device_id'] =  None
        self.save()
    
    def set_password(self, password):
        """ Sets the instance's password hash to match the hash of the
            provided string."""
        password, salt  = generate_user_hash_and_salt( password )
        self['password'] = password
        self['salt'] = salt
        self.save()


class Users( DatabaseCollection ):
    """ The Users database."""
    OBJTYPE = User
    
"""#############################################################################
################################### ADMIN STUFF ################################
#############################################################################"""

class Admin( DatabaseObject ):
    PATH = "beiwe.admins"
    
    DEFAULTS = { "password":REQUIRED, 'salt':REQUIRED, "system_admin":REQUIRED,
                "access_key_id":None, "access_key_secret":None,
                "access_key_secret_salt":None }
    
    @classmethod
    def create(cls, username, password):
        """ Creates a new Admin with provided password and user name."""
        password, salt = generate_hash_and_salt( password )
        new_admin = {ID_KEY :username, 'password':password, 'salt':salt,
                     "system_admin": False, "access_key_id":None, "access_key_secret":None}
        return super(Admin, cls).create(new_admin)
    
    @classmethod
    def create_without_password(cls, username):
        """
        Create a new Admin with provided username and no password
        """
        
        new_admin = {
            ID_KEY: username,
            'password': None,
            'salt': 'cab',
            'system_admin': False,
            'access_key_id': None,
            'access_key_secret': None,
        }
        return super(Admin, cls).create(new_admin)
    
    @classmethod
    def check_password(cls, username, compare_me ):
        """ Checks if the provided password matches the hash of the provided
            Admin's password."""
        if not Admin.exists( username ):
            return False
        admin = Admin( username )
        return admin.validate_password( compare_me )
    
    def validate_password(self, compare_me):
        """ Checks if the input matches the instance's password hash."""
        return compare_password( compare_me, self['salt'], self['password'] )
    
    def set_password(self, new_password):
        """Sets the instances password hash to match the provided password."""
        password, salt = generate_hash_and_salt( new_password )
        self['password'] = password
        self['salt'] = salt
        self.save()
    
    def elevate_to_system_admin(self):
        """Makes the admin a system_admin."""
        self['system_admin'] = True
        self.save()
    
    def validate_access_credentials(self, proposed_secret_key):
        """ Returns True/False if the provided secret key is correct for this user."""
        return compare_password(proposed_secret_key,
                                self['access_key_secret_salt'],
                                self['access_key_secret'])
    
    def reset_access_credentials(self):
        access_key = generate_random_string()[:64]
        secret_key = generate_random_string()[:64]
        secret_hash, secret_salt = generate_hash_and_salt(secret_key)
        self["access_key_id"] = access_key
        self["access_key_secret"] = secret_hash
        self["access_key_secret_salt"] = secret_salt
        self.save()
        return access_key, secret_key
    
class Admins( DatabaseCollection ):
    """ The Admins Database."""
    OBJTYPE = Admin
