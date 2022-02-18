import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


def __init__(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://openscopetest-d7614-default-rtdb.firebaseio.com/'
    })


def upload_session(project_id, session_id):
    "TODO: Upload information about a session to a project"
    ref = db.reference('/Sessions')
    sessions = ref.get()
    # NOTE: Instead of numerical indices, might be a good idea to use a dictionary
    meta_dict = post_gres.get_sess_info(project_id, session_id)

    for key in sessions.items():
        if key == session_id:
            print("editing session info")
            for i in meta_dict:
                ref.child(key).update({i[0]: {'session_date': i[8], 
                                   'session_mouse': i[1],
                                   'session_notes': i[2], 
                                   'session_pass': i[3],
                                   'session_stimulus_type': i[4],
                                   'session_img_depth': i[5],
                                   'session_operator': i[6],
                                   'session_equipment': i[7], 
                                   'session_type': 'Ophys'}})


def upload_project(project_id):
    "TODO: Add a new project to the firebase"
    ref = db.reference('/Sessions')
    sessions = ref.get()
    # NOTE: Structure meta_dict in the manner we want to structure the realtime database
    meta_dict = post_gres.get_proj_info(project_id)
    for key in sessions.items():
        if key == project_id:
            for session in meta_dict['sessions']:
                upload_session(project_id, session)
    ref = db.reference('/Projects')
    projects = ref.get()
    for key in projects.items():
        if key == project_id:
            ref.child(key).update({meta_dict})


def init_project(project_id):
    "TODO: Add the project id to the /Projects section of firebase"


def init_session(project_id, session_id):
    "TODO: Add the session id to the /Sessions section of firebase"


def update_project_status():
    "TODO: Update the status of a project to represent its nwb conversion state"



def update_session_status():
    "TODO: Update the status of a session to represent its nwb conversion state"


def view_session():
    "TODO: Show all the associated metadata of a session"


def view_proj_sessions():
    "TODO: Show all session(s) metadata for a project"


def view_project():
    "TODO: Show all the associated metadata of a project"


def update_session():
    "TODO: Update information for a session"


def update_project():
    "TODO: Update information for a project"


def update_users():
    "TODO: Updated the associated users for a project"


def get_sessions():
    "TODO: Get sessions associated with a project"
