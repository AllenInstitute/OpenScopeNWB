import os
import subprocess
import warnings
import hashlib
import logging
import json
import pytest
import h5py
import openscopenwb.create_module_input_json as osnjson

from openscopenwb.utils import script_functions as sf
from openscopenwb.utils import parse_project_parameters as ppp
from pynwb import NWBHDF5IO

warnings.filterwarnings("ignore", message="numpy.dtype size changed")


def align_times(session_params, input_json, output_json):
    module = "allensdk.brain_observatory.ecephys.align_timestamps"
    probes = session_params['probes']

    for probe in probes:
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
        subprocess.check_call(command_string)


@pytest.fixture
def project_param_json_path(tmpdir):
    project_parameter_json = \
        tmpdir.join("test_ephys_demo_project_parameter.json")
    project_parameter = {
        "probes": {
            "746083955":  ["probeA"]
        },
        "modules": [
            "allensdk.brain_observatory.ecephys.align_timestamps",
            "allensdk.brain_observatory.ecephys.stimulus_table",
            "allensdk.brain_observatory.extract_running_speed",
            "allensdk.brain_observatory.ecephys.write_nwb"
        ],
        "sessions": {"746083955": os.path.join(
                        os.path.dirname(__file__),
                        "../samples/ephys_session_746083955_demo_reduced/"
                        )
                     },
        "lims": ["test"],
        "output_path": str(tmpdir),
        "nwb_path": os.path.join(str(tmpdir), "spike_times.nwb"),
        "input_json": str(tmpdir),
        "output_json": str(tmpdir),
        "session_dir": os.path.join(
                    os.path.dirname(__file__),
                    "../samples/ephys_session_746083955_demo_reduced/"
                    ),
        "trim_discontiguous_frame_times": False,
        "last_unit_id": 0,
        "string": "Hello World"
        }

    with open(project_parameter_json, 'w+') as file_handle:
        json.dump(project_parameter, file_handle)

    return project_parameter_json


def stimulus_table(session_params, input_json, output_json):
    module = "allensdk.brain_observatory.ecephys.stimulus_table"
    probes = session_params['probes']
    for probe in probes:
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
        subprocess.check_call(command_string)


def running_speed(session_params, input_json, output_json):
    module = "allensdk.brain_observatory.extract_running_speed"
    module_params = session_params
    module_params = osnjson.create_module_input(
        module, module_params, input_json)

    command_string = sf.generate_module_cmd(
                        module,
                        input_json,
                        output_json
    )
    logging.debug("Starting Session Level Module: " + module)
    subprocess.check_call(command_string)


def write_nwb(session_params, input_json, output_json):
    module = "allensdk.brain_observatory.ecephys.write_nwb"
    probes = session_params['probes']
    for probe in probes:
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

        subprocess.check_call(command_string)


def sha256sum(file):
    hasher = hashlib.sha256()
    bytes = bytearray(128*1024)
    mem_view = memoryview(bytes)
    with open(file, 'rb', buffering=0) as file_name:
        for n in iter(lambda: file_name.readinto(mem_view), 0):
            hasher.update(mem_view[:n])
    return hasher.hexdigest()


def check_hash(file, hash):
    return file == hash


def test_run_modules(project_param_json_path, tmpdir):

    # This is to prepare the output folder
    try:
        os.mkdir(tmpdir.join(str(746083955)))
        os.mkdir(tmpdir.join(str(746083955), 'probeA'))
    except Exception:
        logging.INFO('Output folders already created')

    project_params = ppp.parse_json(project_param_json_path)
    session_param_list = ppp.generate_all_session_params(project_params)
    modules = ppp.get_modules(project_params)

    input_times_hash = \
        "8822152955287f73018e61f3ecbcef6d8aaea80dd6440e4f7dab775c1fb5f0d2"
    stim_hash = \
        "1a6e60d546e79576c5907a18b324bab400d61bb77c3362d683eb61231114fcc5
    running_hash = \
        "61e2a3c666e02340603a437fedf0d71c316ee530e422ddb0e442936318b13643"
    nwb_hash = \
        "452459f1e5290248bee395b2912e0843517fa0d6adcc90cb9599db66fdb6d206"

    for session_params in session_param_list:
        session = session_params["session_id"]
        for module in modules:
            json_directory = ppp.get_input_json_directory(project_params)
            input_json = os.path.join(json_directory, session + '-' + module
                                      + '-input.json')
            output_json = os.path.join(json_directory, session + '-' + module
                                       + '-output.json')
            if module == "allensdk.brain_observatory.ecephys.align_timestamps":
                align_times(session_params, input_json, output_json)
                data_out = json.load(open(input_json, 'r'))
                probes = data_out['probes'][0]
                time_stamps_link = probes['mappable_timestamp_files'][0]
                time_stamps_file = time_stamps_link['output_path']

            elif module == "allensdk.brain_observatory.ecephys.stimulus_table":
                stimulus_table(session_params, input_json, output_json)
                data_out = json.load(open(input_json, 'r'))

                stimulus_file = data_out['output_stimulus_table_path']

            elif module == "allensdk.brain_observatory.extract_running_speed":
                running_speed(session_params, input_json, output_json)
                data_out = json.load(open(input_json, 'r'))

                running_speed_file = data_out['output_path']
                running_h5 = h5py.File(running_speed_file, "r")
                running_speed_info = str(running_h5['running_speed'].values)

            elif module == "allensdk.brain_observatory.ecephys.write_nwb":
                path_nwb = write_nwb(session_params, input_json, output_json)
                data_out = json.load(open(input_json, 'r'))
                path_nwb = data_out["output_path"]
                nwb_file = NWBHDF5IO(path_nwb, "r", load_namespaces=True)
                nwb_info = nwb_file.read()
                nwb_info = str(nwb_info.units['max_drift'][:])

        assert check_hash(sha256sum(time_stamps_file), input_times_hash)
        print("timestamps successful")
        assert check_hash(sha256sum(stimulus_file), stim_hash)
        print("stimulus succesful")
        assert check_hash(hashlib.sha256(running_speed_info.encode('utf-8'))
                          .hexdigest(),
                          running_hash)
        print("running speed check successful")
        # assert check_hash(sha256sum(path_nwb), nwb_hash)
        assert check_hash(hashlib.sha256(nwb_info.encode('utf-8'))
                          .hexdigest(),
                          nwb_hash)
