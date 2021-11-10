import os
import subprocess
import warnings
import logging
import sys

import openscopenwb.create_module_input_json as osnjson
from openscopenwb.utils import script_functions as sf
from openscopenwb.utils import parse_project_parameters as ppp

warnings.filterwarnings("ignore", message="numpy.dtype size changed")

sys.stdout = open('std.log', 'a')
logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG,
                    filemode='a')
dir = os.path.dirname(__file__)
project_parameter_json = os.path.join(dir, "project_json",
                                      "test_project_parameter_json.json")
project_params = ppp.parse_json(project_parameter_json)
session_param_list = ppp.generate_all_session_params(project_params)
modules = ppp.get_modules(project_params)
session_modules, probe_modules = ppp.get_module_types(project_params)

for session_params in session_param_list:
    session = session_params["session_id"]
    probes = session_params['probes']
    for module in modules:
        json_directory = ppp.get_input_json_directory(project_params)
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
            subprocess.check_call(command_string)
            logging.debug("Finished Session Level Module: " + module)
        elif module in probe_modules:
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
                logging.debug("Starting Probe Level Module:: " + module)
                subprocess.check_call(command_string)
                logging.debug("Finished Probe Level Module: " + module)
