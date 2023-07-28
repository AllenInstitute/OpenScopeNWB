import os
import re

import fsspec
import h5py
import pandas as pd
import json
import shutil
import time


from pathlib import Path
from dandi import dandiapi
from fsspec.implementations.cached import CachingFileSystem
from pynwb import NWBHDF5IO
from pynwb.base import Images
from glob import glob
from os.path import join
from shutil import rmtree

from openscopenwb.utils import clean_up_functions as cuf
from openscopenwb.utils import firebase_functions as fb


from dandi.dandiapi import DandiAPIClient as dandi


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
    os.environ['DANDI_API_KEY'] = cuf.get_creds()
    dandi_api_key = os.environ['DANDI_API_KEY']
    my_dandiset = dandiapi.DandiAPIClient(
        token=dandi_api_key).get_dandiset(dandi_id)
    for file in my_dandiset.get_assets():
        path = file.path
        check_sess_info(project, dandi_id, path)


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

    os.environ['DANDI_API_KEY'] = cuf.get_creds()
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
