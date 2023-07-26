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
    StimulusFile


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
    json_data = {
        "log_level": "INFO",
        "output_frame_times_path": "/allen/programs/mindscope/workgroups/" +
                                   "openscope/ahad/" +
                                   "ophys_no_behavior_nwb/" +
                                   str(experiment_id) +
                                   "frame_times.npy",
        "output_stimulus_table_path": "/allen/programs/mindscope/workgroups/" +
                                      "openscope/ahad/" +
                                      "ophys_no_behavior_nwb/" +
                                      str(experiment_id) +
                                      "allen_sdk.csv",
        "stimulus_pkl_path": stimulus_file.filepath,
        "sync_h5_path": sync_path,
    }
    json_out = json.dumps(json_data)
    return json_out
