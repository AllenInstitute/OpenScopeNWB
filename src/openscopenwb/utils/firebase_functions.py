from curses import meta
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
                ref.child(key).update({i[0]: {
                                   'session_date': i[8],
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
    init_project(project_id)
    ref = db.reference('/Sessions')
    sessions = ref.get()
    # NOTE: Structure meta_dict in the manner we want to structure the realtime database
    meta_dict = post_gres.get_proj_info(project_id)
    for key in sessions.items():
        if key == project_id:
            for session in meta_dict['sessions']:
                upload_session(project_id, session)



def init_project(project_id):
    "TODO: Add the project id to the /Projects section of firebase"
    ref = db.reference('/Projects')
    meta_dict = post_gres.get_proj_info(project_id)
    ref.update({project_id: meta_dict})


def init_session(project_id, session_id):
    "TODO: Add the session id to the /Sessions section of firebase"
    ref = db.reference('/Sessions')
    meta_dict = post_gres.get_sess_info(session_id)
    ref.update({project_id: meta_dict})


def update_project_status(project_id, status):
    "TODO: Update the status of a project to represent its nwb conversion state"
    ref = db.reference('/Statuses')
    ref.update({project_id: {"Status": status}})


def update_session_status(project_id, session_id, status):
    "TODO: Update the status of a session to represent its nwb conversion state"
    ref = db.reference('/Statuses')
    ref.update({project_id: {session_id: {"Status": status}}})


def view_session(project_id, session_id):
    "TODO: Show all the associated metadata of a session"
    ref = db.reference('/Sessions/' + project_id + '/' + session_id)
    meta_dict = ref.get()
    return meta_dict


def view_proj_sessions(project_id):
    "TODO: Show all session(s) metadata for a project"
    ref = db.reference('/Sessions/' + project_id)
    sess_dict_list = []
    for session in ref:
        if session != "Metadata":
            sess_dict_list.append(view_session(project_id,session))
    return sess_dict_list


def view_project(project_id):
    "TODO: Show all the associated metadata of a project"
    ref = db.reference('/Sessions/' + project_id + '/' + 'Metadata')
    meta_dict = ref.get()
    return meta_dict


def get_sessions(project_id):
    "TODO: Get sessions associated with a project"
    ref = db.reference('/Sessions/' + project_id)
    sess_list = []
    for session in ref:
        if session != "Metadata":
            sess_list.append(session)
    return sess_list
