import json


def parse_json(project_parameter_json):
    """Gets all relevant information from the parameter_json

    Parameters
    ----------
    project_parameter_path: str
    The path for the parameter_json

    Returns
    -------
    project_dict: dict
    """
    param_file = open(project_parameter_json)
    project_dict = json.load(param_file)
    param_file.close()
    return project_dict


def get_probes(project_dict):
    """Gets the relevant probe ids from the project_dict

    Parameters
    ----------
    project_dict: dict

    Returns
    -------
    probe_id_list: list
    a list of the session ids used by the project
    """
    probe_id_list = project_dict['probes']
    return probe_id_list


def get_session_ids(project_dict):
    """Gets the relevant session ids from the project_dict

    Parameters
    ----------
    project_dict: dict

    Returns
    -------
    session_id_list: list
    a list of the session ids used by the project
    """
    session_id_list = project_dict['sessions']
    return session_id_list


def get_modules(project_dict):
    """Gets the relevant modules from the project_dict

    Parameters
    ----------
    project_dict: dict

    Returns
    -------
    module_list: list
    a list of the modules used by the project
    """
    module_list = project_dict['modules']
    return module_list


def get_output_json_directory(project_dict):
    """Gets the relevant write directory for output json files
    from the dictionary

    Parameters
    ----------
    project_dict: dict

    Returns
    -------
    output_json_dir: str
    a string of the output json directory used by the project
    """
    output_json_dir = project_dict['output_json']
    return output_json_dir


def get_input_json_directory(project_dict):
    """Gets the relevant write directory for input json files
    from the project_dict

    Parameters
    ----------
    project_dict: dict

    Returns
    -------
    input_json_dir: str
    a string of the inputput json directory used by the project
    """
    input_json_dir = project_dict['input_json']
    return input_json_dir


def get_lims_path(project_dict):
    """Gets the relevant read directory for LIMS files from the project_dict

    Parameters
    ----------
    project_dict: dict

    Returns
    -------
    lims_dir: str
    a string of the output lims directory used by the project
    """
    lims_dir = project_dict['lims']
    return lims_dir


def get_output_nwb_path(project_dict):
    """Gets the relevant write directory for output nwb files
    from the project_dict

    Parameters
    ----------
    project_dict: dict

    Returns
    -------
    output_nwb_dir: str
    a string of the output nwb directory used by the project
    """
    output_nwb_dir = project_dict['nwb_path']
    return output_nwb_dir


def get_session_dir(project_dict):
    """Gets the session directory to read from the project_dict

    Parameters
    ----------
    project_dict: dict

    Returns
    -------
    session_base_dir
    a string of the session specific paths used by the project
    """
    session_base_dir = project_dict['session_dir']
    return session_base_dir


def get_trim(project_dict):
    trim = project_dict['trim_discontiguous_frame_times']
    return trim


def generate_session_params(project_dict, session, probe_count):
    """Generates a single session parameters using the project dict

    Parameters
    ----------
    project_dict: dict
    session: string
    The specific session we are generating the parameters for
    probe_count: int
    The amount of probes that the session is using

    Returns
    -------
    session_parameters: dict
    Session level parameters such as the base directory, session id, etc
    """
    session_parameters = {}
    session_paths = get_session_dir(project_dict)
    probes = get_probes(project_dict)
    final_probe = probes[-1]
    trim = get_trim(project_dict)
    session_parameters = {
        'session_id': session,
        'base_directory': session_paths,
        'last_unit_id': probe_count,
        'probes': probes,
        'final_probe': final_probe,
        'probe_dict_list': {},
        'trim': trim
    }
    return session_parameters


def generate_all_session_params(project_dict):
    """Generates a all session parameters using the project dict

    Parameters
    ----------
    project_dict: dict
 

    Returns
    -------
    session_parameters_list: dict
    Session level parameters such as the base directory, session id, etc
    """
    sessions = get_session_ids(project_dict)
    probe_count = len(get_probes(project_dict))
    session_parameters_list = []
    for session in sessions:
        session_parameters_list.append(generate_session_params(
            project_dict, session, probe_count))
    return session_parameters_list
