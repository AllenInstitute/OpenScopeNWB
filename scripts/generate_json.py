import json
import os
from openscopenwb.utils import postgres_functions as postgres
from datetime import datetime
from glob import glob


def get_path(session_id):
    path = postgres.get_sess_directory(session_id)
    return path


def get_probes(path):
    probes = ["ProbeA", "ProbeB", "ProbeC", "ProbeD", "ProbeE", "ProbeF"]
    for probe_idx in probes:
        existence_list = glob(os.path.join(path, '*' + probe_idx + '*_sorted'))
        print(existence_list)

def generate_ophys_json(session_id):
    json_data = {}
    for experiment in postgres.get_sess_experiments(session_id):    
        json_data['Session_ids'] = {experiment : session_id}
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
    output_path = r"/allen/programs/mindscope/workgroups/openscope/openscopedata2022/" + str(session_id) +  '/' + date + '/outputs'
    nwb_path = r"/allen/programs/mindscope/workgroups/openscope/openscopedata2022/" + str(session_id) +  '/' + date + '/nwb_path'
    json_path = r"/allen/programs/mindscope/workgroups/openscope/openscopedata2022/" + str(session_id) +  '/' + date + '/json'
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
    json_data['probes'] = {session_id:postgres.get_sess_probes(session_id)}
    json_data['sessions']={session_id:postgres.get_e_sess_directory(session_id)}
    json_out = json.dumps(json_data)
    probe_list = postgres.get_sess_probes(session_id)
    for probe in probe_list:
        for input_path in path_list:
            probe_path = os.path.join(input_path, str(session_id), probe)
            if not os.path.exists(probe_path):
                os.makedirs(probe_path)
    with open(r'/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/scripts/deciphering_variability/inputs/ecephys.json', "w") as myfile:
        myfile.write(json_out)
    return r'/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/scripts/deciphering_variability/inputs/ecephys.json'

