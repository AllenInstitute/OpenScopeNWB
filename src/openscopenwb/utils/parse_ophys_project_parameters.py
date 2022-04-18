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


def get_ids(project_dict):
    """Gets the relevant session and experiment ids from the project_dict

    Parameters
    ----------
    project_dict: dict
    A dictionary containing all the project's json values

    Returns
    -------
    id_list: list
    a lists of the ids used by the project
    """

    id_list = project_dict['session_ids']
    return id_list
