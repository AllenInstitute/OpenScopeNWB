from psycopg2 import connect
import json
import os


def get_cred_location():
    dir = os.path.dirname(__file__)
    cred_json = os.path.join(dir, "cred", "post_gres.json")
    return cred_json


def get_psql_cursor(cred_json):
    """Initializes a connection to the postgres database

    Parameters
    ----------
    cred_json: str
    A path to the credential json, which stores the following info:
    dbname: str
    The database name
    user: str
    The username
    host: str
    Host location of the database
    password: str
    The password for the database
    post: int
    The port to connect to

    Returns
    -------
    con: connect
    A connection to the postgres database
    """
    cred_file = open(cred_json)
    cred_info = json.load(cred_file)
    cred_file.close()
    dbname = cred_info['dbname']
    user = cred_info['user']
    host = cred_info['host']
    password = cred_info['password']
    port = cred_info['port']
    con = connect(dbname=dbname, user=user, host=host, password=password,
                  port=port)
    con.set_session(readonly=True, autocommit=True)
    return con.cursor()


def get_ses_all(session_id):
    """Gets all info associated with an ophys sessions

    Parameters
    ----------
    session_id: int
    The sessions's id value

    Returns
    -------
    info_list: str
    The session's info
    """
    OPHYS_SESSION_QRY = """
    SELECT *
    FROM ophys_sessions os
    WHERE os.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = OPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list


def get_sess_directory(session_id):
    """Gets a specific session's filepath

    Parameters
    ----------
    session_id: int
    The sessions's id value

    Returns
    -------
    path: str
    The session's file path
    """    
    OPHYS_SESSION_QRY = """
    SELECT os.storage_directory
    FROM ophys_sessions os
    WHERE os.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = OPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list


def get_sess_info(session_id):
    """Gets a specific session's information

    Parameters
    ----------
    session_id: int
    The sessions's id value

    Returns
    -------
    meta_dict: dict
    A dictionary including all relevant metadata
    """
    OPHYS_SESSION_QRY = """
    SELECT os.id,
        os.name,
        os.specimen_id,
        os.equipment_id,
        os.stimulus_name,
        os.date_of_acquisition,
        os.operator_id,
    os.imaging_depth_id
    FROM ophys_sessions os
    WHERE os.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = OPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
        print(info_list)

    meta_dict = {}
    meta_dict['name'] = info_list[1]
    meta_dict['date'] = info_list[5]
    meta_dict['mouse'] = info_list[2]
    meta_dict['stim'] = info_list[4]
    meta_dict['img'] = info_list[7]
    meta_dict['operator'] = info_list[6]
    meta_dict['equip'] = info_list[3]
    meta_dict['id'] = info_list[0]
    meta_dict['path'] = get_sess_directory(session_id)

    return meta_dict


def get_proj_info(project_id):
    """Gets a specific project's information

    Parameters
    ----------
    project_id: int
    The project's id value

    Returns
    -------
    meta_dict: dict
    A dictionary including all relevant metadata, currently just the sessions
    """
    LIST_OF_SESSION_QRY = """
    SELECT os.id
    FROM ophys_sessions os
        JOIN projects p ON p.id = os.project_id
        JOIN specimens sp ON sp.id = os.specimen_id
        WHERE p.code =  '{}'
        AND os.workflow_state = 'uploaded'
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = LIST_OF_SESSION_QRY.format(project_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(project_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    meta_dict = {}
    meta_dict['sessions'] = []
    for session in info_list:
        meta_dict['sessions'].append(session)
    return meta_dict
