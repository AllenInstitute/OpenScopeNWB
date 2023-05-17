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


def upload_o_session(project_id, session_id):
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
    meta_dict = post_gres.get_o_sess_info(session_id)

    for key in sessions.items():
        if key == session_id:
            ref.update({project_id: {session_id: {
                'name': meta_dict['name'],
                'date': meta_dict['date'],
                'mouse': meta_dict['mouse'],
                'stim': meta_dict['stim'],
                'img': meta_dict['img'],
                'operator': meta_dict['operator'],
                'equipment': meta_dict['equip'],
                'path': meta_dict['path'],
                'status': meta_dict['status'],
                'type': meta_dict['type'],
                'experiments': meta_dict['experiments']
            }}})


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
    meta_dict = post_gres.get_e_sess_info(session_id)

    for key in sessions.items():
        if key == session_id:
            ref.update({project_id: {session_id: {
                'session_date': meta_dict['date'],
                'session_mouse': meta_dict['mouse'],
                'session_stimulus_type': meta_dict['stim'],
                'session_img_depth': meta_dict['img'],
                'session_operator': meta_dict['operator'],
                'session_equipment': meta_dict['equip']}}})


def upload_project(project_id):
    """Uploads a specific project's information

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    """
    start(get_creds())
    meta_dict = post_gres.get_e_proj_info(project_id)
    for session in meta_dict['sessions']:
        session = str(session)
        session = ''.join((c for c in session if c.isdigit()))
        init_session(project_id, session)



def upload_o_project(project_id):
    """Uploads a specific project's information

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    """
    start(get_creds())
    meta_dict = post_gres.get_o_proj_info(project_id)
    for session in meta_dict['sessions']:
        session = str(session)
        session = ''.join((c for c in session if c.isdigit()))
        init_o_session(project_id, session)


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
    meta_dict = post_gres.get_e_proj_info(project_id)
    ref.update({project_id: meta_dict})


def init_o_project(project_id):
    """Initializes a specific project's information

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    """
    ref = db.reference('/Projects')
    meta_dict = post_gres.get_o_proj_info(project_id)
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
    ref = db.reference('/Sessions/' + project_id + '/' + session_id)
    meta_dict = post_gres.get_e_sess_info(session_id)
    ref.update(meta_dict)


def init_o_session(project_id, session_id):
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
    ref = db.reference('/Sessions/' + project_id + '/' + session_id)
    meta_dict = post_gres.get_o_sess_info(session_id)
    ref.update(meta_dict)

    
def get_portion_of_o_sess(project_id):
    """Gets a portion of a specific session's information

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    """
    ref = db.reference('/Sessions/' + project_id)
    sessions = ref.get()
    sess_list_flag_present = []
    sess_list_flag_not_present = []
    sess_flags = []
    for session, value in sessions.items():
        if value['workflow'] ==  'uploaded' and value['fails'] == ['No Flags']:
            sess_list_flag_present.append(session)
    for session, value in sessions.items():
        if value['workflow'] ==  'uploaded' and value['fails'] != ['No Flags']:
            sess_list_flag_not_present.append(session)
            sess_flags.append((session, value['fails']))
    sess_len = len(sess_list_flag_present)
    sess_no_flag_len = len(sess_list_flag_not_present)
    return "Number of sessions with no Flag:" + str(len(sess_list_flag_present)) + "Number of sessions with Flags " + str(len(sess_list_flag_not_present)) + "List of flags: " + str(sess_flags)
    

def update_o_session(project_id, session_id):
    """Updates a specific sessions's information while keeping current status

    Parameters
    ----------
    project_id: int
    The project's id value
    session_id: int
    The session's id value

    Returns
    -------
    """
    ref = db.reference('/Sessions/' + project_id + '/' + session_id)
    meta_dict = post_gres.get_o_sess_info(session_id)
    print(meta_dict)

    status = view_session(project_id, session_id)['status']
    notes = view_session(project_id, session_id)['notes']
    dandi = view_session(project_id, session_id)['dandi']
    meta_dict['status'] = status
    meta_dict['notes'] = notes
    meta_dict['dandi'] = dandi    
    ref.update(meta_dict)


def update_session_dandi(project_id, session_id, path):
    """Updates a specific sessions's information while keeping current status

    Parameters
    ----------
    project_id: int
    The project's id value
    session_id: int
    The session's id value
    path: str
    The path on dandi for the session

    Returns
    -------
    """
    ref = db.reference('/Sessions/' + project_id + '/' + session_id + '/dandi')
    ref.update(path)


def update_session(project_id, session_id):
    """Updates a specific sessions's information while keeping current status

    Parameters
    ----------
    project_id: int
    The project's id value
    session_id: int
    The session's id value

    Returns
    -------
    """
    ref = db.reference('/Sessions/' + project_id + '/' + session_id)
    meta_dict = post_gres.get_e_sess_info(session_id)
    status = view_session(project_id, session_id)['status']
    notes = view_session(project_id, session_id)['notes']
    allen_dir = view_session(project_id, session_id)['allen']
    dandi = view_session(project_id, session_id)['dandi']
    meta_dict['status'] = status
    meta_dict['notes'] = notes
    meta_dict['allen'] = allen_dir
    meta_dict['dandi'] = dandi    
    ref.update(meta_dict)


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
    ref = db.reference('/Sessions/' + project_id + "/" + session_id +
                       "/status/")
    ref.update({"status": status})


def update_session_dir(project_id, session_id, path):
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
    ref = db.reference('/Sessions/' + str(project_id) + "/" + str(session_id) +
                       "/allen/")
    ref.update(path)




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


def get_experiments(project_id, session_id):
    ref = db.reference(
        '/Sessions/' +
        project_id +
        '/' +
        session_id +
        '/experiments')
    experiments = ref.get()
    exp_list = []
    for experiment in experiments:
        if experiment != "Metadata":
            exp_list.append(experiment)
    return exp_list


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
    sessions = ref.get()
    sess_list = []
    for session in sessions:
        if session != "Metadata":
            sess_list.append(session)
    return sess_list


def get_ecephys_upload_sessions(project_id):
    """Returns all converted but not uploaded sessions of a project

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    sess_list: list
    A list of all the sessions
    """
    ref = db.reference('/Sessions/' + project_id )
    sessions = ref.get()
    sess_list = []
    for session, value in sessions.items():
        if value['allen'] != 'Not Yet Converted' and value['type'] == "Ecephys" and value['dandi'] == 'Not Yet Uploaded':
            sess_list.append(session)
    return sess_list


def get_ecephys_upload_sessions(project_id):
    """Reconverts all uploaded sessions of a project

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    sess_list: list
    A list of all the sessions
    """
    ref = db.reference('/Sessions/' + project_id )
    sessions = ref.get()
    sess_list = []
    for session, value in sessions.items():
        if value['allen'] == 'Uploaded' and value['type'] == "Ecephys":
            update_session_status(project_id, session, "Converting")
            sess_list.append(session)
    return sess_list


def get_ophys_uploaded_sessions(project_id):
    """Returns all ophys sessions with all their files on LIMS

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    sess_list: list
    A list of all the sessions
    """
    ref = db.reference('/Sessions/' + project_id )
    sessions = ref.get()
    sess_list = []
    for session, value in sessions.items():
        if value['workflow'] == 'uploaded' and value['type'] == "Ophys" and value['dandi'] == 'Not Yet Uploaded':
            sess_list.append(session)
    return sess_list    


def update_queue_list(session_id):
    """Updates all the queue  to add the current sess

    Parameters
    ----------
    session_id: str
    The sessions's ID value
    Returns
    -------
    """
    ref = db.reference('/Jobs')
    sessions = ref.get()    
    sess_list = []
    if sessions is not None:
        for session in sessions:
            sess_list.append(session)
    if session_id not in sess_list:
        sess_list.append(session_id)

        ref.update(sess_list)



def update_ephys_statuses(projectID):
    """Updates all initalized statuses to converting

    Parameters
    ----------
    projectID: str
    The project's ID value
    Returns
    -------
    session_list: list
    A list of the sessions that need to be converted
    """
    ref = db.reference('/Sessions/' + projectID)
    sessions = ref.get()
    session_list = []
    for session, value in sessions.items():
        if value['status']['status'] == "Initialized" and value['type'] == "Ecephys":
            update_session_status(projectID, session, "Converting")
    for session, value in sessions.items():
        if value['status']['status'] == "Converting" and value['type'] == "Ecephys":
            session_list.append(session)
    return session_list


def update_ophys_statuses(projectID):
    """Updates all initalized statuses to converting

    Parameters
    ----------
    projectID: str
    The project's ID value
    Returns
    -------
    session_list: list
    A list of the sessions that need to be converted
    """
    ref = db.reference('/Sessions/' + projectID)
    sessions = ref.get()
    session_list = []
    for session, value in sessions.items():
        if value['status']['status'] == "Initialized" and value['type'] == "Ophys":
            update_session_status(projectID, session, "Converting")
    for session, value in sessions.items():
        if value['status']['status'] == "Converting" and value['type'] == "Ophys":
            session_list.append(session)
    return session_list


def get_curr_job():
    """Gets the current job id
    We use this to feed it to slurm
    to handle job scheduling

    Parameters
    ----------
    Returns
    -------
    """
    ref = db.reference('/Job/id')
    job_id = ref.get()
    job_id = job_id
    return job_id


def update_curr_job(id):
    """Updates the current job id

    Parameters
    ----------
    id: str
    The job's ID value
    Returns
    -------
    """
    print("INPUT", id)
    ref = db.reference('/Job/id')
    ref.update({"id": id})


def update_ophys_RAW_statuses(projectID):
    """Updates all initalized statuses to converting

    Parameters
    ----------
    projectID: str
    The project's ID value
    Returns
    -------
    session_list: list
    A list of the sessions that need to be converted
    """
    ref = db.reference('/Sessions/' + projectID)
    sessions = ref.get()
    session_list = []
    for session, value in sessions.items():
        if value['status']['status'] == "RAW_Initialized" and value['type'] == "Ophys":
            update_session_status(projectID, session, "RAW_Converting")
    for session, value in sessions.items():
        if value['status']['status'] == "RAW_Converting" and value['type'] == "Ophys":
            session_list.append(session)
    return session_list


def get_dandi_statuses(projectID):
    """Grabs all sessions that are ready to be uploaded to dandi

    Parameters
    ----------
    projectID: str
    The project's ID value
    Returns
    -------
    session_list: list
    A list of the sessions that need to be converted
    """
    ref = db.reference('/Sessions/' + projectID)
    sessions = ref.get()
    session_list = []
    for session, value in sessions.items():
        if value['status']['status'] == "Initializing Upload" and value['type'] == "Ecephys":
            session_list.append(session, value['nwb_location'])
    return session_list
