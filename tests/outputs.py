import os
import subprocess
import warnings
import logging
import hashlib
import sys

import openscopenwb.create_module_input_json as osnjson
from openscopenwb.utils import script_functions as sf
from openscopenwb.utils import parse_project_parameters as ppp

warnings.filterwarnings("ignore", message="numpy.dtype size changed")

logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG,
                    filemode='a')


def align_times(session_params, input_json, output_json):
    module = "allensdk.brain_observatory.ecephys.align_timestamps"
    probes = session_params['probe_list']
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


def stimulus_table(session_params, input_json, output_json):
    module = "allensdk.brain_observatory.ecephys.stimulus_table"
    probes = session_params['probe_list']
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
    probes = session_params['probe_list']
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


def run_tests():
    dir = os.path.dirname(__file__)
    project_parameter_json = os.path.join(dir, "project_json",
                                        "test_project_parameter_json.json")
    project_params = ppp.parse_json(project_parameter_json)
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
                try:
                    align_times(session_params, input_json, output_json)
                except Exception:
                    pass
            elif module == "allensdk.brain_observatory.ecephys.stimulus_table":
                try:
                    stimulus_table(session_params, input_json, output_json)
                except Exception:
                    pass
            elif module == "allensdk.brain_observatory.extract_running_speed":
                try:
                    running_speed(session_params, input_json, output_json)
                except Exception:
                    pass
            elif module == "allensdk.brain_observatory.ecephys.write_nwb":
                try:
                    write_nwb(session_params, input_json, output_json)
                except Exception:
                    pass
    assert check_hash(sha256sum(time_stamps_file), input_times_hash)
    assert check_hash(sha256sum(stimulus_file), input_stim_hash)
    assert check_hash(sha256sum(running_speed_file), input_running_hash)
    assert check_hash(sha256sum(nwb_json_file), input_nwb_hash)
    assert check_hash(sha256sum(nwb_file), nwb_hash)
