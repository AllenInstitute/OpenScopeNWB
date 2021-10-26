import os
import subprocess
import warnings
import hashlib
import openscopenwb.create_module_input_json as osnjson
from openscopenwb.utils import script_functions as sf
from openscopenwb.utils import parse_project_parameters as ppp
import logging
import json
import pytest

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
            "725254892":  ["probeA"]
        },
        "modules": [
            "allensdk.brain_observatory.ecephys.align_timestamps",
            "allensdk.brain_observatory.ecephys.stimulus_table",
            "allensdk.brain_observatory.extract_running_speed",
            "allensdk.brain_observatory.ecephys.write_nwb"
        ],
        "sessions": {"725254892": os.path.join(os.path.dirname(__file__),
                        "../samples/ephys_session_725254892_demo/")},
        "lims": ["test"],
        "output_path": str(tmpdir),
        "nwb_path": os.path.join(str(tmpdir), "spike_times.nwb"),
        "input_json": str(tmpdir),
        "output_json": str(tmpdir),
        "session_dir": os.path.join(os.path.dirname(__file__),
                        "../samples/ephys_session_725254892_demo/"),
        "trim_discontiguous_frame_times": False,
        "last_unit_id": 1,
        "string": "Hello World"
        }

    print(project_parameter_json)
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
        os.mkdir(tmpdir.join(str(725254892)))
        os.mkdir(tmpdir.join(str(725254892), 'probeA'))
    except:
        logging.INFO('Output folders already created')

    project_params = ppp.parse_json(project_param_json_path)
    session_param_list = ppp.generate_all_session_params(project_params)
    modules = ppp.get_modules(project_params)

    input_times_hash = ""
    input_running_hash = ""
    input_stim_hash = ""
    input_nwb_hash = ""
    nwb_hash = ""

    time_stamps_file = ""
    running_speed_file = ""
    stimulus_file = ""
    nwb_json_file = ""
    nwb_file = ""

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
            elif module == "allensdk.brain_observatory.ecephys.stimulus_table":
                stimulus_table(session_params, input_json, output_json)
            elif module == "allensdk.brain_observatory.extract_running_speed":
                running_speed(session_params, input_json, output_json)
            elif module == "allensdk.brain_observatory.ecephys.write_nwb":
                write_nwb(session_params, input_json, output_json)

    assert check_hash(sha256sum(time_stamps_file), input_times_hash)
    assert check_hash(sha256sum(stimulus_file), input_stim_hash)
    assert check_hash(sha256sum(running_speed_file), input_running_hash)
    assert check_hash(sha256sum(nwb_json_file), input_nwb_hash)
    assert check_hash(sha256sum(nwb_file), nwb_hash)
