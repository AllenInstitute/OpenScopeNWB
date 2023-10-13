import os
import re

from dandi import dandiapi

from openscopenwb.utils import clean_up_functions as cuf
from openscopenwb.utils import firebase_functions as fb


def check_sess_info(project, dandi_id, path):
    """Update a session's dandi location

    Parameters
    ----------
    project : str
        The project id
    dandi_id : str
        The dandi id
    path : str
        The path to the file

    Returns
    -------
    """
    if "probe" in path:
        return None
    sess_id = ""
    sub_id = ""
    print(str(path))
    match = re.search(r'ses-(\d+)', str(path))
    if match:
        sess_id = match.group(1)
        print("Session ID: " + sess_id)
    else:
        print("Session ID not found.")
    if sess_id == "":
        return None
    if project != 'OpenScopeDendriteCoupling':
        fb.update_session_dandi(project, sess_id, str(path))
    else:
        match = re.search(r'sub-(\d+)', str(path))
        if match:
            sub_id = match.group(1)
            print(sub_id)
            fb.update_session_dandi(
                project,
                sess_id,
                r'https://dandiarchive.org/dandiset/000336/draft/files?' +
                'location=' +
                "sub-" + sub_id)
        return None


def find_dandiset_sessions(project, dandi_id):
    """Update a project's dandi locations

    Parameters
    ----------
    project : str
        The project id
    dandi_id : str
        The dandi id

    Returns
    -------
    """
    os.environ['DANDI_API_KEY'] = cuf.get_dandi_creds()
    dandi_api_key = os.environ['DANDI_API_KEY']
    my_dandiset = dandiapi.DandiAPIClient(
        token=dandi_api_key).get_dandiset(dandi_id)
    for file in my_dandiset.get_assets():
        path = file.path
        check_sess_info(project, dandi_id, path)


def extract_session_number(file_path):
    # Extract the number after "ses-"
    parts = file_path.split("ses-")
    if len(parts) > 1:
        session_number = parts[1].split("-")[0]
        return session_number
    else:
        return None


def find_files_with_missing_raw(project, dandi_id):
    # Set DANDI API key
    os.environ['DANDI_API_KEY'] = cuf.get_dandi_creds()
    dandi_api_key = os.environ['DANDI_API_KEY']

    # Initialize DANDI client
    my_dandiset = dandiapi.DandiAPIClient(
        token=dandi_api_key).get_dandiset(dandi_id)

    # Create an array to store all file paths
    all_files = []

    for file in my_dandiset.get_assets():
        path = file.path
        all_files.append(path)

    # Create a dictionary to store pairs of raw and non-raw file paths
    file_pairs = {}

    for file_path in all_files:
        # Check if "raw" is present in the path
        if 'raw' not in file_path:
            # Remove "raw" and store in the dictionary
            path_without_raw = file_path
            file_pairs[path_without_raw] = file_path
        elif 'raw' in file_path:
            file_pairs[file_path] = file_path

    # Create a list to store file paths where raw is missing
    missing_raw_files = []

    for path_without_raw, path_with_raw in file_pairs.items():
        if path_with_raw not in all_files:
            print(path_with_raw)
            missing_raw_files.append(path_with_raw)

    session_numbers = [extract_session_number(
        file_path) for file_path in missing_raw_files]

    return session_numbers


def find_files_with_raw_status(project, dandi_id):
    # Set DANDI API key
    os.environ['DANDI_API_KEY'] = cuf.get_dandi_creds()
    dandi_api_key = os.environ['DANDI_API_KEY']

    # Initialize DANDI client
    my_dandiset = dandiapi.DandiAPIClient(
        token=dandi_api_key).get_dandiset(dandi_id)

    # Create an array to store all file paths
    all_files = []

    for file in my_dandiset.get_assets():
        path = file.path
        all_files.append(path)

    # Create a dictionary to store acq values and their corresponding status
    acq_status_dict = {}
    acq_sess_dict = {}

    for file_path in all_files:
        # Extract the acq value
        parts = file_path.split("acq-")
        if len(parts) > 1:
            acq_value = ''.join(filter(str.isdigit, parts[1].split("_")[0]))
            sess_id_match = re.search(r'ses-(\d+)', file_path)
            if sess_id_match:
                sess_id = sess_id_match.group(1)
            acq_sess_dict[acq_value] = sess_id

            # Check if "raw" or non-raw version exists
            raw_exists = False
            non_raw_exists = False

            if "raw_ophys.nwb" in file_path:
                raw_exists = True
            elif "ophys.nwb" in file_path:
                non_raw_exists = True

            # Update the dictionary
            if acq_value in acq_status_dict:
                existing_raw, existing_non_raw = acq_status_dict[acq_value]
                acq_status_dict[acq_value] = (
                    existing_raw or raw_exists,
                    existing_non_raw or non_raw_exists)
            else:
                acq_status_dict[acq_value] = (raw_exists, non_raw_exists)

    # Filter and return only the values where both raw
    # and non-raw files do not exist
    filtered_raw_result = dict(
        (key, value)
        for key, value in acq_status_dict.items()
        if value == (True, False))
    filtered_non_raw_result = dict(
        (key, value)
        for key, value in acq_status_dict.items()
        if value == (False, True))
    filtered_missing_result = dict(
        (key, value)
        for key, value in acq_status_dict.items()
        if value == (False, False))
    raw_acqs = []
    non_raw_acqs = []
    missing_acqs = []
    for i in filtered_raw_result:
        raw_acqs.append(i)
    for i in filtered_non_raw_result:
        non_raw_acqs.append(i)
    for i in filtered_missing_result:
        missing_acqs.append(i)
    return raw_acqs, non_raw_acqs, missing_acqs


def generate_exp_list(project, dandi_id):
    """Generate a list of experiments on dandi
       for a project

    Parameters
    ----------
    project : str
        The project id
    dandi_id : str
        The dandi id

    Returns
    -------
    exp_list : list
        A list of experiments on dandi
    """

    os.environ['DANDI_API_KEY'] = cuf.get_dandi_creds()
    dandi_api_key = os.environ['DANDI_API_KEY']
    my_dandiset = dandiapi.DandiAPIClient(
        token=dandi_api_key).get_dandiset(dandi_id)

    session_experiments = {}  # Dictionary to store experiments per session

    for file in my_dandiset.get_assets():
        path = file.path
        match = re.search(r'ses-(\d+)', str(path))
        if match:
            sess_id = match.group(1)
        else:
            print("ses_id not found for: " + str(path))
            continue
        match = re.search(r'acq-(\d+)', str(path))
        if match:
            exp_id = match.group(1)
        else:
            print("exp_id not found for: " + str(path))
            continue

        if sess_id not in session_experiments:
            # Create an empty list for a new session
            session_experiments[sess_id] = []
        if exp_id not in session_experiments[sess_id]:
            # Check if the experiment ID is not already present
            session_experiments[sess_id].append(exp_id)
    for i in session_experiments:
        session_experiments[i].append(len(session_experiments[i]))
    return session_experiments
