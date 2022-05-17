#!/usr/bin/env python
import logging
import os
import subprocess
import warnings
import argparse
import ecephys_nwb_trials

from glob import glob
from os.path import join

import openscopenwb.create_module_input_json as osnjson
import sys
import generate_json as gen_json

from pynwb import NWBHDF5IO
import pynwb

from openscopenwb.utils import parse_ephys_project_parameters as ppp
from openscopenwb.utils import script_functions as sf

def convert_session(session_id):
    warnings.filterwarnings("ignore", message="numpy.dtype size changed")

    logging.basicConfig(filename="std.log",
                        format='%(asctime)s %(message)s',
                        level=logging.DEBUG,
                        filemode='a')

    dir = os.path.dirname(__file__)
    # project_parameter_json = os.path.join(dir, "project_json",
    #                                      "test_ephys_project_parameter_json.json")
    # project_params = ppp.parse_json(project_parameter_json)
    #project_csv_json = os.path.join(dir, "project_json",
    #                                "test_ecephys_csv_json.json")
    project_csv_json = gen_json.generate_ephys_json(session_id)
    project_params = ppp.parse_json(project_csv_json)
    session_param_list = ppp.generate_all_session_params(project_params)
    modules = ppp.get_modules(project_params)
    session_modules, probe_modules = ppp.get_module_types(project_params)
    old_last_unit = -1

    default_stimulus_renames = {
        "": "spontaneous",

        "natural_movie_1": "natural_movie_one",
        "natural_movie_3": "natural_movie_three",
        "Natural Images": "natural_scenes",
        "flash_250ms": "flashes",
        "gabor_20_deg_250ms": "gabors",
        "drifting_gratings": "drifting_gratings",
        "static_gratings": "static_gratings",

        "contrast_response": "drifting_gratings_contrast",
        "natural_movie_1_more_repeats": "natural_movie_one",
        "natural_movie_shuffled": "natural_movie_one_shuffled",
        "motion_stimulus": "dot_motion",
        "drifting_gratings_more_repeats": "drifting_gratings_75_repeats",

        "signal_noise_test_0_200_repeats": "test_movie_one",

        "signal_noise_test_0": "test_movie_one",
        "signal_noise_test_1": "test_movie_two",
        "signal_noise_session_1": "dense_movie_one",
        "signal_noise_session_2": "dense_movie_two",
        "signal_noise_session_3": "dense_movie_three",
        "signal_noise_session_4": "dense_movie_four",
        "signal_noise_session_5": "dense_movie_five",
        "signal_noise_session_6": "dense_movie_six",
    }

    default_column_renames = {
        "Contrast": "contrast",
        "Ori":	"orientation",
        "SF": "spatial_frequency",
        "TF": "temporal_frequency",
        "Phase": "phase",
        "Color": "color",
        "Image": "frame",
        "Pos_x": "x_position",
        "Pos_y": "y_position"
    }


    for session_params in session_param_list:
        session = session_params["session_id"]
        probes = session_params['probes']
        for module in modules:
            json_directory = ppp.get_input_json_directory(project_params)
            json_directory = os.path.join(json_directory, session)
            input_json = os.path.join(json_directory, session + '-' + module
                                    + '-input.json')
            output_json = os.path.join(json_directory, session + '-' + module
                                    + '-output.json')
            if module in session_modules:
                module_params = session_params
                module_params = osnjson.create_module_input(
                    module, module_params, input_json)

                command_string = sf.generate_module_cmd(
                                    module,
                                    input_json,
                                    output_json
                )
                logging.debug("Starting Session Level Module: " + module)
                logging.debug(command_string)
                subprocess.check_call(command_string)
                logging.debug("Finished Session Level Module: " + module)
            elif module in probe_modules:
                for probe in probes:
                    session_params['last_unit_id'] = old_last_unit + 1
                    module_params = session_params
                    module_params['current_probe'] = probe
                    module_params['id'] = probes.index(probe)
                    module_params = osnjson.create_module_input(
                        module, module_params, input_json)
                    command_string = sf.generate_module_cmd(
                                        module,
                                        input_json,
                                        output_json
                    )
                    old_last_unit = module_params['last_unit_id']
                logging.debug("Starting Probe Level Module:: " + module)
                subprocess.check_call(command_string)
                logging.debug("Finished Probe Level Module: " + module)
    return join(module_params['nwb_path'])
'''
                if module == 'allensdk.brain_observatory.ecephys.write_nwb':
                    stimulus_pkl_path = glob(join(module_params['base_directory'],
                                            "*.stim.pkl"))[0]
                    sync_h5_path = glob(join(module_params['base_directory'],
                                            "*.sync"))[0]
                    output_stimulus_table_path = join(
                                                module_params['output_path'],
                                                "manual_stim_table_allensdk.csv")
                    frame_time_strategy = "use_photodiode"
                    minimum_spontaneous_activity_duration = sys.float_info.epsilon
                    maximum_expected_spontaneous_activity_duration = 1225.02541
                    extract_const_params_from_repr = True
                    drop_const_params = ["name", "maskParams", "win",
                                        "autoLog", "autoDraw"]
                    fail_on_negative_duration = False
                    column_name_map = default_column_renames
                    stimulus_name_map = default_stimulus_renames
                    output_nwb_path = module_params['nwb_path']

                    trial_params = {
                            "stimulus_pkl_path": stimulus_pkl_path,
                            "sync_h5_path": sync_h5_path,
                            "output_stimulus_table_path":
                            output_stimulus_table_path,
                            "frame_time_strategy": frame_time_strategy,
                            "minimum_spontaneous_activity_duration":
                            minimum_spontaneous_activity_duration,
                            "maximum_expected_spontaneous_activity_duration":
                            maximum_expected_spontaneous_activity_duration,
                            "extract_const_params_from_repr":
                            extract_const_params_from_repr,
                            "drop_const_params": drop_const_params,
                            "fail_on_negative_duration": fail_on_negative_duration,
                            "column_name_map": column_name_map,
                            "stimulus_name_map": stimulus_name_map,
                            "output_nwb_path": output_nwb_path
                    }

                #ecephys_nwb_trials.add_trials_to_nwb(trial_params)
'''
def write_subject_to_nwb(nwb_path):
    write_nwb_path = nwb_path.replace("spike_times.nwb", "spike_times_re.nwb")
    io = NWBHDF5IO(nwb_path, "a", load_namespaces=True)
    input_nwb = io.read()
    
    subject = pynwb.file.Subject(
        age="P90D", 
        description="Placeholder", 
        genotype="Placeholder", 
        sex="M", 
        subject_id="Placeholder", 
        strain="Placeholder"
    )
    input_nwb.subject = subject
    io.write(input_nwb)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--session_id', type=int)
    args = parser.parse_args()
    write_subject_to_nwb(
        convert_session(session_id = args.session_id)
    )
