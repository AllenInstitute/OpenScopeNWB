import json
import os
from openscopenwb.utils import postgres_functions as postgres
from datetime import datetime
from glob import glob
from os.path import join

from allensdk.core.auth_config import LIMS_DB_CREDENTIAL_MAP
from allensdk.internal.api import db_connection_creator

from allensdk.brain_observatory.behavior.data_objects.metadata\
    .ophys_experiment_metadata.ophys_session_id import \
    OphysSessionId
from allensdk.brain_observatory.behavior.data_files import \
    BehaviorStimulusFile


def get_path(session_id):
    path = postgres.get_sess_directory(session_id)
    return path


def get_probes(path):
    probes = ["ProbeA", "ProbeB", "ProbeC", "ProbeD", "ProbeE", "ProbeF"]
    for probe_idx in probes:
        existence_list = glob(os.path.join(path, '*' + probe_idx + '*_sorted'))
        print(existence_list)


def generate_ophys_json(experiment_id):

    lims_db = db_connection_creator(
        fallback_credentials=LIMS_DB_CREDENTIAL_MAP
    )
    sess_id = OphysSessionId.from_lims(
        ophys_experiment_id=experiment_id, lims_db=lims_db
    )
    stimulus_file = StimulusFile.from_lims(
        behavior_session_id=sess_id.value, db=lims_db
    )
    sync_path = postgres.get_o_sess_directory(str(sess_id.value))
    sync_path = glob(join(sync_path[0], str(sess_id.value) + "_*.h5"))[0]
    behavior_path = ("/allen/programs/mindscope/workgroups/openscope/" +
                     "ahad/ophys_no_behavior_nwb/")
    json_data = {
        "log_level": "INFO",
        "output_frame_times_path":
            behavior_path +
            str(experiment_id) +
            "frame_times.npy",
        "output_stimulus_table_path":
            behavior_path +
            str(experiment_id) +
            "allen_sdk.csv",
        "stimulus_pkl_path": stimulus_file.filepath,
        "sync_h5_path": sync_path
    }
    json_out = json.dumps(json_data)
    return json_out


def generate_ephys_json(session_id, project):
    date = datetime.today().strftime('%Y-%m-%d-%H-%M')
    json_data = {}
    json_data['modules'] = [
        "allensdk.brain_observatory.ecephys.align_timestamps",
        "allensdk.brain_observatory.ecephys.stimulus_table",
        "allensdk.brain_observatory.extract_running_speed",
        'allensdk.brain_observatory.ecephys.lfp_subsampling',
        'allensdk.brain_observatory.ecephys.optotagging_table',
        "allensdk.brain_observatory.ecephys.write_nwb"
    ]
    output_path = r"/allen/programs/mindscope/workgroups/openscope/" + \
                  "openscopedata2022/" + \
                  str(session_id) + '/' + date + '/outputs'
    nwb_path = r"/allen/programs/mindscope/workgroups/openscope/" + \
               "openscopedata2022/" + str(session_id) + '/' + date + \
               '/nwb_path'
    json_path = r"/allen/programs/mindscope/workgroups/openscope/" + \
                "openscopedata2022/" + str(session_id) + \
                '/' + date + '/json'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.exists(nwb_path):
        os.makedirs(nwb_path)
    if not os.path.exists(json_path):
        os.makedirs(json_path)

    path_list = [output_path, json_path]

    json_data['output_path'] = output_path
    json_data['nwb_path'] = nwb_path
    json_data['input_json'] = json_path
    json_data['output_json'] = json_path
    json_data['trim_discontiguous_frame_times'] = False
    json_data['last_unit_id'] = 0
    json_data['project'] = project
    json_data['lims'] = True
    json_data['probes'] = {session_id: postgres.get_sess_probes(session_id)}
    json_data['sessions'] = {session_id: postgres.get_e_sess_directory(
                             session_id)}
    json_out = json.dumps(json_data)
    probe_list = postgres.get_sess_probes(session_id)
    for probe in probe_list:
        for input_path in path_list:
            probe_path = os.path.join(input_path, str(session_id), probe)
            if not os.path.exists(probe_path):
                os.makedirs(probe_path)
    input_ecephys_json = output_path + '/ecephys.json'
    with open(input_ecephys_json, "w") as myfile:
        myfile.write(json_out)
    return input_ecephys_json
