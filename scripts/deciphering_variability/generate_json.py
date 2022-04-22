import json
from openscopenwb.utils import postgres_functions as postgres
import os
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




print(postgres.get_sess_experiments(1137276124))
print(postgres.get_sess_probes(829720705))
print(generate_ophys_json(1137276124))