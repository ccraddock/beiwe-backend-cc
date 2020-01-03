from datetime import datetime
import os
import config.constants as constants

def resolve_survey_id_from_file_name(name):
    return parse_filename(name)['survey_id']
    #return name.rsplit("/", 2)[1]

def parse_filename(filename):
    """
    Parse filename into dictionary that reflects different properties of its corrsponding object, 
    such as datatype and date of acquisition.
    """ 
    filename = filename.rstrip()
    file_object_dict = {'filename': filename}

    file_values_list = filename.split('/')
    # try to resolve whether it is a 'new' format or an 'old' format and handle approporiately

    name, ext = os.path.splitext(os.path.basename(filename))

    if ext and ext[0] == '.':
        ext = ext[1:]

    if not ext:
        file_object_dict["file_type"] = constants.REGISTRATION_MARKER

    elif ext in constants.ALLOWED_EXTENSIONS:
        file_object_dict["file_extension"] = ext

        # chunk data is always obvious, so lets start with that
        if constants.CHUNKS_FOLDER in filename:
            file_object_dict['file_type'] = constants.CHUNK_DATA
            index_mapping = constants.CHUNK_PATH_MAPPING
        else:
            file_object_dict['file_type'] = constants.RAW_DATA
            if constants.RAW_DATA_FOLDER in filename:
                index_mapping = constants.NEW_RAW_PATH_MAPPING
            else:
                index_mapping = constants.OLD_RAW_PATH_MAPPING

        file_object_dict['study_object_id'] = file_values_list[index_mapping['STUDY_ID_INDEX']]
        file_object_dict['patient_id'] = file_values_list[index_mapping['PATIENT_ID_INDEX']]
    
        if constants.IDENTIFIERS in file_values_list[index_mapping['DATA_TYPE_INDEX']]:
            file_object_dict['data_type'] = constants.IDENTIFIERS
            file_object_dict['datetime'] = file_values_list[index_mapping['DATA_TYPE_INDEX']].split('_')[-1][:-4]
        else:

            file_object_dict['datetime'] = file_values_list[index_mapping["FILE_NAME_INDEX"]].split('_')[-1][:-4]

            if 'ios' in file_values_list[index_mapping['DATA_TYPE_INDEX']]:
                file_object_dict['data_type'] = constants.IOS_LOG_FILE
            else:
                if file_object_dict['file_type'] == constants.CHUNK_DATA:
                    file_object_dict['data_type'] = file_values_list[index_mapping['DATA_TYPE_INDEX']]
                else:
                    file_object_dict['data_type'] = constants.UPLOAD_FILE_TYPE_MAPPING[file_values_list[index_mapping['DATA_TYPE_INDEX']]]

                    if file_object_dict['data_type'] in [constants.SURVEY_ANSWERS, constants.SURVEY_TIMINGS, constants.VOICE_RECORDING, constants.IMAGE_FILE]:
                        # sometimes the survey id isn't in the filename, not sure why, but lets handle it anyway
                        if file_values_list[index_mapping['SURVEY_ID_INDEX']] != file_values_list[index_mapping["FILE_NAME_INDEX"]]:
                            file_object_dict['survey_id'] = file_values_list[index_mapping['SURVEY_ID_INDEX']]
                        else:
                            print('Could not find a survey id for {0}'.format(filename))
    
                        if file_object_dict['data_type'] == constants.IMAGE_FILE:
                            file_object_dict['image_survey_user_instance'] = file_values_list[index_mapping['IMAGE_SURVEY_USER_INSTANCE']]
                    
    else:
        print('Extension is not appropriate {0}'.format(ext))

    return file_object_dict 
