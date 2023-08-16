from openscopenwb.utils import postgres_functions as post_gres
from openscopenwb.utils import firebase_functions as firebase


def compare_o_session(project_id, session_id):
    """Compares a specific session's information between postgres and firebase

    Parameters
    ----------
    project_id: int
    The project's id value
    session_id: int
    The session's id value

    Returns
    -------
    difference_list: list
    A list of the differences between the postgres and firebase,
    ordered by info type and the information reported by the postgres
    """
    post_gres_info = post_gres.get_o_sess_info(session_id)
    firebase_info = firebase.view_session(project_id, session_id)
    difference_list = []
    for i in post_gres_info:
        if i not in firebase_info:
            difference_list.append(i)
            continue
        if post_gres_info[i] != firebase_info[i]:
            difference_list.append(i)
    return difference_list


def compare_o_sessions(project_id):
    """Compares which sessions are associated with a project's
    postgres and firebase

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    new_sessions: list
    A list of the sessions which are not present in the firebase
    """
    post_gres_sessions = post_gres.get_o_proj_info(project_id)
    post_gres_sessions = post_gres_sessions['sessions']
    firebase_sessions = firebase.get_sessions(project_id)
    new_sessions = []
    for session in post_gres_sessions:
        if session not in firebase_sessions:
            new_sessions.append(session)
    return new_sessions


def compare_session(project_id, session_id):
    """Compares a specific session's information between postgres and firebase

    Parameters
    ----------
    project_id: int
    The project's id value
    session_id: int
    The session's id value

    Returns
    -------
    difference_list: list
    A list of the differences between the postgres and firebase,
    ordered by info type and the information reported by the postgres
    """
    post_gres_info = post_gres.get_e_sess_info(session_id)
    firebase_info = firebase.view_session(project_id, session_id)
    difference_list = []
    for i in post_gres_info:
        if i not in firebase_info:
            difference_list.append(i)
            continue
        if post_gres_info[i] != firebase_info[i]:
            difference_list.append(i)
    return difference_list


def compare_sessions(project_id):
    """Compares which sessions are associated with a project's
    postgres and firebase

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    new_sessions: list
    A list of the sessions which are not present in the firebase
    """
    print(project_id)
    post_gres_sessions = post_gres.get_e_proj_info(project_id)
    post_gres_sessions = post_gres_sessions['sessions']
    firebase_sessions = firebase.get_sessions(project_id)
    new_sessions = []

    for session in post_gres_sessions:
        if session not in firebase_sessions:
            new_sessions.append(session)
    return new_sessions


def create_sessions(project_id, new_sessions):
    """Creates the new sessions for a project in firebase

    Parameters
    ----------
    project_id: int
    The project's id value
    new_sessions: list
    A list of the sessions which are not present in the firebase

    Returns
    -------
    """
    for session in new_sessions:
        firebase.init_session(project_id, session)


def update_session_status(project_id, sessions):
    """Updates the conversion status of sessions for a project

    Parameters
    ----------
    project_id: int
    The project's id value
    sessions: list
    A list of the sessions which are to be updated and their statuses

    Returns
    -------
    """
    for session in sessions:
        firebase.update_session_status(project_id,
                                       session_id=session[0],
                                       status=session[1])
