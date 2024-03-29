from datetime import date, datetime
from psycopg2 import connect
import json
import os
import re

from openscopenwb.utils import allen_functions as allen


def get_cred_location():
    """Gets content of firebase credential file
        Files are ignored and not committed to the repository

    Parameters
    ----------

    Returns
    -------
    cred_json: str
        path to json file storing credential information

    """
    dir = os.path.dirname(__file__)
    cred_json = os.path.join(dir, ".cred", "post_gres.json")
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
    print(cred_json)
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


def get_o_sess_all(session_id):
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


def get_e_sess_all(session_id):
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

    EPHYS_SESSION_QRY = """
    SELECT *
    FROM ecephys_sessions es
    WHERE es.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = EPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list


def get_o_sess_directory(session_id):
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
        path = info_list[0]
    return path


def get_e_sess_directory(session_id):
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
    EPHYS_SESSION_QRY = """
    SELECT es.storage_directory
    FROM ecephys_sessions es
    WHERE es.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = EPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
        path = info_list[0]
    return path[0]


def get_sess_donor(session_id):
    """Gets a specific session's donor

    Parameters
    ----------
    session_id: int
        The sessions's id value

    Returns
    -------
    info_list: str
        A list of the session's passing probes
    """
    EPHYS_DONOR_QRY = '''
    SELECT es.external_name
    FROM ecephys_sessions es
    WHERE es.id = {}
    GROUP BY es.id
    '''
    cur = get_psql_cursor(get_cred_location())
    lims_query = EPHYS_DONOR_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list


def get_sess_probes(session_id):
    """Gets a specific session's probes and workflow states

    Parameters
    ----------
    session_id: int
        The sessions's id value

    Returns
    -------
    info_list: str
        A list of the session's passing probes
    """
    EPHYS_PROBE_QRY = '''
    SELECT es.workflow_state,
        ARRAY_AGG(ep.id ORDER BY ep.id) AS ephys_probe_ids
    FROM ecephys_sessions es
        LEFT JOIN ecephys_probes ep ON ep.ecephys_session_id = es.id
    WHERE es.id = {}
    GROUP BY es.id
    '''
    PROBE_ID_QRY = '''
    SELECT ep.name,
        ep.workflow_state,
        ep.storage_directory
    FROM ecephys_probes ep
        JOIN ecephys_sessions es ON es.id = ep.ecephys_session_id
    WHERE ep.id = {}
    '''
    cur = get_psql_cursor(get_cred_location())
    lims_query = EPHYS_PROBE_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
        probes_list = []
        probes_id_list = info_list[0][1]
        for probe_id in probes_id_list:
            probe_query = PROBE_ID_QRY.format(probe_id)
            cur.execute(probe_query)
            if cur.rowcount == 0:
                raise Exception("No data was found for ID {}".format(
                                session_id))
            else:
                probe_name_status = cur.fetchall()
                probe_status = probe_name_status[0][1]
                probe_name = probe_name_status[0][0]
                probe_storage = probe_name_status[0][2]
                if (probe_status == 'passed' or probe_status ==
                        'created') and probe_storage is not None:
                    if (probe_status) == 'passed':
                        print(probe_name)
                    else:
                        print(probe_name + " is created, but not passed")
                    probes_list.append(probe_name)
        return probes_list


def get_sess_experiments(session_id):
    """Gets a specific session's experiments and workflow states

    Parameters
    ----------
    session_id: int
        The sessions's id value

    Returns
    -------
    info_list: str
        A list of the session's passing experiments
    """
    OPHYS_SESSION_QRY = """
    SELECT os.workflow_state,
        ARRAY_AGG(oe.id ORDER BY oe.id) AS ophys_experiment_ids
    FROM ophys_sessions os
        LEFT JOIN ophys_experiments oe on oe.ophys_session_id = os.id
    WHERE os.id = {}
    GROUP by os.id
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = OPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
        if info_list[0][0] == "uploaded" or info_list[0][1] == "passed":
            info_list = info_list[0][1]
    return info_list


def get_o_exp_plane(experiment_id):
    """Gets a specific experiment's plane

    Parameters
    ----------
    experiment_id: int
        The experiment's id value

    Returns
    -------
    info_list: list
        The experiment's plane
    """
    OPHYS_PLANE_QRY = """
            SELECT oe.id as ophys_experiment_id, pg.group_order AS plane_group
            FROM  ophys_experiments oe
            JOIN ophys_sessions os ON oe.ophys_session_id = os.id
            JOIN  ophys_imaging_plane_groups pg
                ON pg.id = oe.ophys_imaging_plane_group_id
            WHERE os.id = (
                SELECT oe.ophys_session_id
                FROM ophys_experiments oe
                WHERE oe.id = {}
            )
    """
    cur = get_psql_cursor(get_cred_location())
    if experiment_id == ('created', [None]):
        return "No planes were found for this session"
    elif experiment_id == ('failed', [None]):
        return "No planes were found for this session"
    lims_query = OPHYS_PLANE_QRY.format(experiment_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(experiment_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
        res = str(info_list).strip('[]')
        return res


def get_e_sess_spec_info(session_id):
    """Gets a specific ephys session's specimen info

    Parameters
    ----------
    session_id: int
        The session's id value

    Returns
    -------
    info_list: list
        The session's specimen info
    """
    EPHYS_SESSION_QRY = """
    SELECT es.specimen_id
    FROM ecephys_sessions es
    WHERE es.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = EPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list


def get_o_sess_spec_info(session_id):
    """Gets a specific session's specimen info

    Parameters
    ----------
    session_id: int
        The session's id value

    Returns
    -------
    info_list: list
        The session's specimen info
    """
    OPHYS_SESSION_QRY = """
    SELECT os.specimen_id
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


def get_e_sess_donor_info(session_id):
    """Gets a specific session's donor info

    Parameters
    ----------
    session_id: int
        The sessions's id value

    Returns
    -------
    info_list: list
        The session's donor info
    """
    EPHYS_SESSION_QRY = """
    SELECT sp.donor_id
    FROM ecephys_sessions es
        JOIN specimens sp ON sp.id = es.specimen_id
    WHERE es.id = {}
    """
    DONOR_NAME_QRY = """
    SELECT d.external_donor_name
    FROM donors d
    WHERE d.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = EPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
        cur = get_psql_cursor(get_cred_location())
        info_list = [item for item, in info_list]
        lims_query = DONOR_NAME_QRY.format(info_list[0])
        cur.execute(lims_query)
        if cur.rowcount == 0:
            raise Exception("No data was found for ID {}".format(session_id))
        elif cur.rowcount != 0:
            info_list = cur.fetchall()
            info_list = [item for item, in info_list]
            return info_list


def get_o_sess_donor_info(session_id):
    """Gets a specific session's donor info

    Parameters
    ----------
    session_id: int
        The sessions's id value

    Returns
    -------
    info_list: str
        The session's donor info
    """
    OPHYS_SESSION_QRY = """
    SELECT sp.donor_id
    FROM ophys_sessions os
        JOIN specimens sp ON sp.id = os.specimen_id
    WHERE os.id = {}
    """
    DONOR_NAME_QRY = """
    SELECT d.external_donor_name
    FROM donors d
    WHERE d.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = OPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
        cur = get_psql_cursor(get_cred_location())
        info_list = [item for item, in info_list]
        lims_query = DONOR_NAME_QRY.format(info_list[0])
        cur.execute(lims_query)
        if cur.rowcount == 0:
            raise Exception("No data was found for ID {}".format(session_id))
        elif cur.rowcount != 0:
            info_list = cur.fetchall()
            info_list = [item for item, in info_list]
            return info_list


def get_o_sess_dff(session_id):
    """Gets a specific session's dff file

    Parameters
    ----------
    session_id: int
        The sessions's id value

    Returns
    -------
    info_list: str
        The session's dff file
    """
    QRY = """
    SELECT wkf.storage_directory || wkf.filename AS dff_file
    FROM ophys_experiments oe
                JOIN well_known_files wkf ON wkf.attachable_id = oe.id
                JOIN well_known_file_types wkft
                ON wkft.id = wkf.well_known_file_type_id
    WHERE wkft.name = 'OphysDffTraceFile'
    AND oe.id = {};"""
    cur = get_psql_cursor(get_cred_location())
    lims_query = QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list


def get_avg_pic(exp_id):
    """Gets the average project image for an experiment

    Parameters
    ----------
    exp_id: int
        The experiment's id value

    Returns
    -------
    info_list: str
        The average image's filepath
    """
    query = """
            SELECT
                wkf.storage_directory || wkf.filename AS filepath,
                wkft.name as wkfn
            FROM ophys_experiments oe
            JOIN well_known_files wkf ON wkf.attachable_id = oe.id
            JOIN well_known_file_types wkft
            ON wkft.id = wkf.well_known_file_type_id
            WHERE wkf.attachable_type = 'OphysExperiment'
            AND wkft.name IN ('OphysMaxIntImage',
                                'OphysAverageIntensityProjectionImage')
            AND oe.id = {};"""
    cur = get_psql_cursor(get_cred_location())
    lims_query = query.format(exp_id)
    cur.execute(lims_query)
    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(exp_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list


def get_e_sess_info(session_id):
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
    EPHYS_SESSION_QRY = """
        SELECT es.name,
        es.date_of_acquisition,
        es.stimulus_name,
        sp.external_specimen_name,
        isi.id AS isi_experiment_id,
        e.name AS rig,
        es.workflow_state
    FROM ecephys_sessions es
        JOIN specimens sp ON sp.id = es.specimen_id
        LEFT JOIN isi_experiments isi ON isi.id = es.isi_experiment_id
        LEFT JOIN equipment e ON e.id = es.equipment_id
    WHERE es.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    session_id = str(session_id)
    session_id = ''.join((c for c in session_id if c.isdigit()))
    lims_query = EPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    tmp = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    for i in info_list:
        for j in i:
            tmp.append(j)
    info_list = tmp
    meta_dict = {}
    if isinstance(info_list[1], (datetime, date)):
        info_list[1] = info_list[1].isoformat()

    subject = allen.lims_subject_info(session_id)

    meta_dict['name'] = info_list[0]
    meta_dict['date'] = info_list[1]
    meta_dict['stimulus'] = info_list[2]
    meta_dict['mouse'] = info_list[3]
    meta_dict['exp_id'] = info_list[4]
    meta_dict['rig'] = info_list[5]
    meta_dict['workflow'] = info_list[6]
    meta_dict['path'] = get_e_sess_directory(session_id)
    meta_dict['specimen'] = get_e_sess_spec_info(session_id)[0][0]
    meta_dict['type'] = 'Ecephys'
    meta_dict['status'] = {'status': 'Not Converted'}
    meta_dict['notes'] = 'none'
    meta_dict['dandi'] = 'Not Yet Uploaded'
    meta_dict['allen'] = 'Not Yet Converted'
    meta_dict['genotype'] = subject['genotype']
    try:
        meta_dict['probes'] = get_sess_probes(session_id)
    except Exception:
        meta_dict['probes'] = ['no probe info']
    return meta_dict


def get_o_exp_info(exp_id):
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
    OPHYS_EXPERIMENT_QRY = """
    SELECT oe.workflow_state
    FROM ophys_experiments oe
    WHERE oe.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = OPHYS_EXPERIMENT_QRY.format(exp_id)
    cur.execute(lims_query)
    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(exp_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list


def get_o_sess_info(session_id):
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
        sp.external_specimen_name,
        os.equipment_id,
        os.stimulus_name,
        os.date_of_acquisition,
        os.operator_id,
        os.imaging_depth_id,
        os.workflow_state
    FROM ophys_sessions os
        JOIN specimens sp ON sp.id = os.specimen_id
    WHERE os.id = {}
    """
    cur = get_psql_cursor(get_cred_location())
    session_id = str(session_id)
    session_id = ''.join((c for c in session_id if c.isdigit()))
    lims_query = OPHYS_SESSION_QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    tmp = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()

    for i in info_list:
        for j in i:
            tmp.append(j)
    info_list = tmp
    meta_dict = {}
    if isinstance(info_list[5], (datetime, date)):
        info_list[5] = info_list[5].isoformat()
    subject = allen.lims_o_subject_info(session_id)
    flags, fails, overrides, flag_notes, override_notes = allen.ophys_tag_info(
        session_id)
    meta_dict['name'] = info_list[1]
    meta_dict['date'] = info_list[5]
    meta_dict['mouse'] = info_list[2]
    meta_dict['stim'] = info_list[4]
    meta_dict['img'] = info_list[7]
    meta_dict['operator'] = info_list[6]
    meta_dict['equip'] = info_list[3]
    meta_dict['id'] = info_list[0]
    meta_dict['workflow'] = info_list[8]
    meta_dict['dandi'] = 'Not Yet Uploaded'
    meta_dict['path'] = get_o_sess_directory(session_id)[0]
    meta_dict['specimen'] = get_o_sess_spec_info(session_id)[0][0]
    meta_dict['type'] = 'Ophys'
    meta_dict['notes'] = 'none'
    meta_dict['genotype'] = subject['genotype']
    meta_dict['experiments'] = get_sess_experiments(session_id)
    meta_dict['planes'] = get_o_exp_plane(get_sess_experiments(session_id)[0])
    meta_dict['status'] = {'status': 'Not Converted'}
    meta_dict['fails'] = fails
    meta_dict['flags'] = flags
    meta_dict['overrides'] = overrides
    meta_dict['flag_notes'] = flag_notes
    meta_dict['override_notes'] = override_notes

    return meta_dict


def get_o_targeted_struct(exp_id):
    """Gets a specific experiment's information

    Parameters
    ----------
    exp_id: int
        The experiments's id value

    Returns
    -------
    info_list: str
        The experiment's info
    """
    QRY = """
            SELECT st.acronym
            FROM ophys_experiments oe
            LEFT JOIN structures st ON st.id = oe.targeted_structure_id
            WHERE oe.id = {};
            """.format(exp_id)
    cur = get_psql_cursor(get_cred_location())
    lims_query = QRY.format(exp_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(exp_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list[0][0]


def get_sess_specimen(dir):
    """Gets a specific specimen id from a session's path.

    Parameters
    ----------
    dir : str
        The session's internal file path.

    Returns
    -------
    specimen_id : str or None
        A string representation of the specimen id,
        or None if no match is found.
    """
    match = re.search(r'/specimen_(\d+)/', dir)
    if match:
        specimen_id = match.group(1)
        return specimen_id
    else:
        return None


def get_e_sess_sync(session_id):
    """Gets a specific session's sync file path

    Parameters
    ----------
    session_id: int
        The sessions's id value

    Returns
    -------
    info_list: str
        The session's sync file path
    """
    QRY = f"""
    SELECT wkf.storage_directory || wkf.filename AS sync_file
    FROM ecephys_sessions es
    JOIN well_known_files wkf ON wkf.attachable_id = es.id
    JOIN well_known_file_types wkft
    ON wkft.id = wkf.well_known_file_type_id
    AND wkft.name = 'EcephysRigSync'
    AND es.id = {session_id}
    """

    cur = get_psql_cursor(get_cred_location())
    lims_query = QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list[0][0]


def get_o_sess_sync(session_id):
    """Gets a specific session's sync file path

    Parameters
    ----------
    session_id: int
        The sessions's id value

    Returns
    -------
    info_list: str
        The session's sync file path
    """
    QRY = f"""
        SELECT wkf.storage_directory || wkf.filename AS sync_file
        FROM ophys_sessions os
        JOIN well_known_files wkf ON wkf.attachable_id = os.id
        JOIN well_known_file_types wkft
        ON wkft.id = wkf.well_known_file_type_id
        WHERE wkf.attachable_type = 'OphysSession'
        AND wkft.name = 'OphysRigSync'
        AND os.id = {session_id}
    """
    cur = get_psql_cursor(get_cred_location())
    lims_query = QRY.format(session_id)
    cur.execute(lims_query)

    info_list = []
    if cur.rowcount == 0:
        raise Exception("No data was found for ID {}".format(session_id))
    elif cur.rowcount != 0:
        info_list = cur.fetchall()
    return info_list


def get_e_proj_info(project_id):
    """Gets a specific project's information

    Parameters
    ----------
    project_id: int
        The project's id value

    Returns
    -------
    meta_dict: dict
        A dictionary including all relevant metadata,
        currently just the sessions
    """
    LIST_OF_SESSION_QRY = """
    SELECT es.id
    FROM ecephys_sessions es
        JOIN projects p ON p.id = es.project_id
        JOIN specimens sp ON sp.id = es.specimen_id
        WHERE p.code =  '{}'
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
        session = str(session)
        session = ''.join((c for c in session if c.isdigit()))
        meta_dict['sessions'].append(session)
    return meta_dict


def get_o_proj_info(project_id):
    """Gets a specific project's information

    Parameters
    ----------
    project_id: int
        The project's id value

    Returns
    -------
    meta_dict: dict
        A dictionary including all relevant metadata,
        currently just the sessions
    """
    LIST_OF_SESSION_QRY = """
    SELECT os.id
    FROM ophys_sessions os
        JOIN projects p ON p.id = os.project_id
        JOIN specimens sp ON sp.id = os.specimen_id
        WHERE p.code =  '{}'
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
        session = str(session)
        session = ''.join((c for c in session if c.isdigit()))
        meta_dict['sessions'].append(session)
    return meta_dict
