#!/usr/bin/env python
import argparse
import os
import warnings
import logging
import sys
import subprocess
import json
from datetime import datetime

# import openscopenwb.create_module_input_json as osnjson
# from openscopenwb.utils import script_functions as sf
import ophys_nwb_stim as stim
from openscopenwb.utils import parse_ophys_project_parameters as popp
from allensdk.brain_observatory.behavior.ophys_experiment import \
     OphysExperiment as ophys
from pynwb import NWBHDF5IO
from openscopenwb.utils import script_functions as sf
from openscopenwb.utils import allen_functions as allen
from openscopenwb.utils import postgres_functions as postgres
from generate_json import generate_ophys_json
from pynwb.file import Subject

warnings.filterwarnings("ignore", message="numpy.dtype size changed")

sys.stdout = open('std.log', 'a')
logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG,
                    filemode='a')
# dir = os.path.dirname(__file__)
# project_parameter_json = os.path.join(dir, "project_json",
#                                      "test_ophys_project_parameter_json.json")

# project_parameter_json = r'/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/scripts/deciphering_variability/project_json/test_ophys_project_parameter_json.json'
# project_info = popp.parse_json(project_parameter_json)
# ophys_experiment_ids = popp.get_ids(project_info)

def gen_ophys(experiment_id, file_path):
    key = experiment_id
    ophys_experiment_id = int(key)
    ophys_nwb = ophys.from_lims(ophys_experiment_id=ophys_experiment_id,
                                skip_eye_tracking=True)
    ophys_nwb = ophys_nwb.to_nwb()
    print(file_path)
    with NWBHDF5IO(file_path, mode='w') as io:
        io.write(ophys_nwb)


def add_data_to_nwb(csv_path, nwb_path):
    stim.add_stim_to_nwb(csv_path, nwb_path)  


def add_subject_to_nwb(session_id, experiment_id, nwb_path):
    subject_info = allen.lims_o_subject_info(session_id)
    # TODO: Calculate mouse age 
    subject_dob = datetime.strptime(subject_info['dob'][:10],'%Y-%m-%d')
    subject_date = postgres.get_o_sess_info['date']
    subject_date = datetime.strptime(subject_date[:10], '%Y-%m-%d')
    duration = subject_date - subject_dob
    duration = duration.total_seconds()
    duration = divmod(duration, 86400)
    days = (duration[0])
    days = 'P' + str(days) + 'D'
    subject = {
        'age_in_days': days,
        'specimen_name': subject_info['name'],
        'full_genotype': subject_info['genotype'],
        'sex': subject_info['gender'],
        'strain': "Transgenic",
        'stimulus_name': 'Ophys Dendrite',
        'species': 'Mus musculus',
        'donor_id': subject_info['id']
    }
    with NWBHDF5IO(nwb_path, "r+", load_namespaces=True) as nwbfile:
        input_nwb = nwbfile.read()
        input_nwb.subject = Subject(
            subject_id= str(experiment_id),
            age = subject['age_in_days'],
            species = 'Mus musculus',
            sex = subject['sex'],
            genotype = subject['full_genotype'],
            description = 'Dendrite'
        )
        nwbfile.write(input_nwb)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session_id', type=int)
    parser.add_argument('--experiment_id', type=int)
    args = parser.parse_args()
    session_id = args.session_id
    experiment_id = args.experiment_id
    experiment_id = int(experiment_id)
    json_in = generate_ophys_json(experiment_id)
    input_json =  r'/allen/programs/mindscope/workgroups/openscope/ahad/ophys_no_behavior_nwb/' + str(experiment_id) + "_in.json"
    output_json = r'/allen/programs/mindscope/workgroups/openscope/ahad/ophys_no_behavior_nwb/' + str(experiment_id) + "_out.json"
    with open(input_json, "w") as outfile:
        outfile.write(json_in)
    command_string = sf.generate_module_cmd(
        'allensdk.brain_observatory.ecephys.stimulus_table',
        input_json,
        output_json,
    )
    subprocess.check_call(command_string)
    file_path = r'/allen/programs/mindscope/workgroups/openscope/ahad/ophys_no_behavior_nwb'
    file_path =  file_path + '/' + str(experiment_id) + 'raw_data.nwb'
    gen_ophys(experiment_id, file_path)
    json_in = json.loads(json_in)
    add_data_to_nwb(json_in['output_stimulus_table_path'],file_path)
    add_subject_to_nwb(session_id, experiment_id, file_path)
