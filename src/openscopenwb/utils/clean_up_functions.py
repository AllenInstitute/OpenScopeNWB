import json
import os
import numpy as np

from glob import glob


def get_dandi_creds():
    """Gets the dandi credentials locally

    Parameters
    ----------
    None

    Returns
    -------
    api_key: str
    The api key for dandi
    """
    dir = os.path.dirname(__file__)
    credential_file = glob(os.path.join(dir, '.cred',
                                        'dandi.json'))
    cred_file = open(credential_file[0])
    cred_json = json.load(cred_file)
    return cred_json['api_key']


def get_firebase_creds():
    """Gets the firebase credentials locally

    Parameters
    ----------
    None

    Returns
    -------
    cred_json: str
    The credentials for firebase
    """
    dir = os.path.dirname(__file__)
    credential_file = glob(os.path.join(
                           dir, '.cred',
                           'firebase_backend_credentials.json'))
    try:
        cred_json = credential_file[0]
    except IndexError:
        return os.environ.get('FIREBASE_CREDENTIALS_PATH')
    return cred_json


def clean_up_nan_and_inf(value):
    """ Replaces Nan and inf values with -1

    Parameters
    ----------
    value: float
    A floating point value

    Returns
    -------
    value: float
    A floating point value, -1 if the original value was nan or inf
    """
    if np.isnan(value) or np.isinf(value):
        return -1
    else:
        return value
