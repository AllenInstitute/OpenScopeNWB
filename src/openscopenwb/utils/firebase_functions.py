from openscopenwb.utils import postgres_functions as post_gres

import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import glob


def get_creds():
    dir = os.path.dirname(__file__)
    credential_file = glob.glob(os.path.join(dir, '.cred',
                                'firebase_backend_credentials.json'))
    cred_json = credential_file[0]
    return cred_json


def start(cred_path):
    cred = credentials.Certificate(cred_path)
    app = firebase_admin.initialize_app(cred, {
        'databaseURL':
            'https://openscopetest-d7614-default-rtdb.firebaseio.com/'
    })
    return app


def upload_session(project_id, session_id):
    """Uploads a specific session's information

    Parameters
    ----------
    project_id: int
    The project's id value
    session_id: int
    The session's id value

    Returns
    -------
    """
    ref = db.reference('/Sessions')
    sessions = ref.get()
    meta_dict = post_gres.get_sess_info(session_id)

    for key in sessions.items():
        if key == session_id:
            print("editing session info")
            ref.child(key).update({project_id: {
                                   'session_date': meta_dict['date'],
                                   'session_mouse': meta_dict['mouse'],
                                   'session_stimulus_type': meta_dict['stim'],
                                   'session_img_depth': meta_dict['img'],
                                   'session_operator': meta_dict['operator'],
                                   'session_equipment': meta_dict['equip']}})


def upload_project(project_id):
    """Uploads a specific project's information

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    """
    init_project(project_id)
    meta_dict = post_gres.get_proj_info(project_id)
    for session in meta_dict['sessions']:
        upload_session(project_id, session)


def init_project(project_id):
    """Initializes a specific project's information

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    """
    ref = db.reference('/Projects')
    meta_dict = post_gres.get_proj_info(project_id)
    ref.update({project_id: meta_dict})


def init_session(project_id, session_id):
    """Initializes a specific sessions's information

    Parameters
    ----------
    project_id: int
    The project's id value
    session_id: int
    The session's id value

    Returns
    -------
    """
    ref = db.reference('/Sessions/' + str(session_id))
    meta_dict = post_gres.get_sess_info(session_id)
    ref.update({project_id: meta_dict})


def update_project_status(project_id, status):
    """Updates a project's conversion status

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    """
    ref = db.reference('/Statuses')
    ref.update({project_id: {"Status": status}})


def update_session_status(project_id, session_id, status):
    """Updates a session's conversion status

    Parameters
    ----------
    project_id: int
    The project's id value
    session_id: int
    The session's id value

    Returns
    -------
    """
    # fb = start(get_creds())
    ref = db.reference('/Sessions/' + project_id + "/" + session_id +
                       "/status/")
    ref.update({"status": status})


def view_session(project_id, session_id):
    """Returns all relevant metadata for a session

    Parameters
    ----------
    project_id: int
    The project's id value
    session_id: int
    The session's id value

    Returns
    -------
    meta_dict: dict
    A dict of all the metadata for the session
    """
    ref = db.reference('/Sessions/' + str(project_id) + '/' + str(session_id))
    meta_dict = ref.get()
    print(meta_dict)
    return meta_dict


def view_proj_sessions(project_id):
    """Returns all relevant metadata for the sessions of a project

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    sess_dict_list: list
    A list of dicts of all the metadata for the sessions
    """
    ref = db.reference('/Sessions/' + project_id)
    sess_dict_list = []
    for session in ref:
        if session != "Metadata":
            sess_dict_list.append(view_session(project_id, session))
    return sess_dict_list


def view_project(project_id):
    """Returns all relevant metadata of a project

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    meta_dict: dict
    A dict of all the project's metadata
    """
    ref = db.reference('/Sessions/' + project_id + '/' + 'Metadata')
    meta_dict = ref.get()
    return meta_dict


def get_sessions(project_id):
    """Returns all sessions of a project

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    sess_list: list
    A list of all the sessions
    """
    ref = db.reference('/Sessions/' + project_id)
    sess_list = []
    for session in ref:
        if session != "Metadata":
            sess_list.append(session)
    return sess_list


def update_ephys_statuses():
    """Updates all initalized statuses to converting

    Parameters
    ----------

    Returns
    -------
    session_list: list
    A list of the sessions that need to be converted
    """
    ref = db.reference('/Sessions/')
    session_list = []
    Projects = ref.get()
    for project, value in Projects.items():
        proj_ref = db.reference('/Sessions/'+project)
        proj = proj_ref.get()
        for session, value in proj.items():
            if value['status']['status'] == "Initialized" and \
               value['session_type'] == "Ecephys":
                update_session_status(project, session, "Converting")
                session_list.append(session)
    return session_list
