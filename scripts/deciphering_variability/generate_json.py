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
        json_data['Session_ids'] = {experiment: session_id}
    json_out = json.dumps(json_data)
    return json_out


def generate_ephys_json(session_id):
    date = datetime.today().strftime('%Y-%m-%d')
    json_data = {}
    json_data['modules'] = [
    "allensdk.brain_observatory.ecephys.align_timestamps",
    "allensdk.brain_observatory.ecephys.stimulus_table",
    "allensdk.brain_observatory.extract_running_speed",
    "allensdk.brain_observatory.ecephys.write_nwb"
    ]
    json_data['output_path'] = r"//allen/programs/braintv/production/openscope/openscopedata2022/" + str(session_id) +  '/' + date + '/outputs'
    json_data['nwb_path'] = r"//allen/programs/braintv/production/openscope/openscopedata2022/" + str(session_id) +  '/' + date + '/nwb_path'
    json_data['input_json'] = r"//allen/programs/braintv/production/openscope/openscopedata2022/" + str(session_id) +  '/' + date + '/json'
    json_data['output_json'] = r"//allen/programs/braintv/production/openscope/openscopedata2022/" + str(session_id) +  '/' + date + '/json'
    json_data['trim_discontiguous_frame_times'] = False
    json_data['last_unit_id'] = 0
    json_data['probes'] = {session_id: postgres.get_sess_probes(session_id)}
    json_data['sessions']={session_id: postgres.get_e_sess_directory(session_id)}
    json_out = json.dumps(json_data)
    return json_out


print(postgres.get_sess_experiments(1137276124))
print(postgres.get_sess_probes(829720705))
print(generate_ophys_json(1137276124))
print(generate_ephys_json(829720705))
