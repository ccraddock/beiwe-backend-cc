from libs import encryption
from libs.s3 import s3_upload, s3_retrieve, construct_s3_key_paths

################################################################################
######################### Client Key Management ################################
################################################################################

def create_client_key_pair(patient_id, study_id):
    """Generate key pairing, push to database, return sanitized key for client."""
    public, private = encryption.generate_key_pairing()
    key_pair_paths = construct_s3_key_paths(study_id, patient_id)
    s3_upload(key_pair_paths['private'], private, study_id, raw_path=True )
    s3_upload(key_pair_paths['public'], public, study_id, raw_path=True )
    return

def get_client_public_key_string(patient_id, study_id):
    """Grabs a user's public key string from s3."""
    key_pair_paths = construct_s3_key_paths(study_id, patient_id)
    key_string = s3_retrieve(key_pair_paths['public'], study_id, raw_path=True)
    return encryption.prepare_X509_key_for_java( key_string )

def get_client_public_key(patient_id, study_id):
    """Grabs a user's public key file from s3."""
    key_pair_paths = construct_s3_key_paths(study_id, patient_id)
    key = s3_retrieve(key_pair_paths['public'], study_id, raw_path=True)
    return encryption.import_RSA_key( key )

def get_client_private_key(patient_id, study_id):
    """Grabs a user's private key file from s3."""
    key_pair_paths = construct_s3_key_paths(study_id, patient_id)
    try:
        key = s3_retrieve(key_pair_paths['private'], study_id, raw_path=True)
    except:
        print('Could not find key {0} in {1}'.format('private', key_pair_paths))
        raise

    return encryption.import_RSA_key( key )
