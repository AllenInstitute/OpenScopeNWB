import os
import subprocess
import warnings
import openscopenwb as osn
import logging
import openscopenwb.create_module_input_json as osnjson
from openscopenwb.utils import parse_project_parameters as ppp

warnings.filterwarnings("ignore", message="numpy.dtype size changed")

project_parameter_json = "path to project file"
project_params = ppp.parse_json(project_parameter_json)
sessions = ppp.get_session_ids(project_params)
session_param_list = ppp.generate_all_session_params(project_params)
modules = ppp.get_modules(project_params)
session_modules, probe_modules = ppp.get_module_types(project_params)


'''
Test Settings
sessions = ['725254892']
modules = ['allensdk.brain_observatory.ecephys.align_timestamps',
           'allensdk.brain_observatory.ecephys.stimulus_table',
           'allensdk.brain_observatory.extract_running_speed',
           'allensdk.brain_observatory.ecephys.write_nwb']

session_modules = ['allensdk.brain_observatory.ecephys.align_timestamps']
probe_modules = ['allensdk.brain_observatory.ecephys.stimulus_table',
                 'allensdk.brain_observatory.extract_running_speed',
                 'allensdk.brain_observatory.ecephys.write_nwb']
'''
for session_params in session_param_list:
    # for module in session_modules
    # for module in probe_modules
    # session_params = ppp.generate_session_params(project_params,
    #     
    #                                                session)
    '''
    Test session_params
    session_params = {
        'session_id': '725254892',
        'base_directory': "C:\\Users\\ahad.bawany\\Documents\\ephys_session_725254892_demo\\ephys_session_725254892_demo",
        'last_unit_id': 1,
        'probes': ['probeA'],
        'final_probe': 'probeA',
        'probe_dict_list': [],
        'trim': False
    }
    '''
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

            command_string = ["python", "-W", "ignore", "-m", module,
                              "--input_json", input_json,
                              "--output_json", output_json]
            logging.debug("Starting Session Level Module")
            subprocess.check_call(command_string)
            logging.debug("Finished Session Level Module")
        elif module in probe_modules:
            for probe in probes:
                module_params = session_params
                module_params['current_probe'] = probe
                module_params = osnjson.create_module_input(
                    module, module_params, input_json)
                command_string = ["python", "-W", "ignore", "-m", module,
                                  "--input_json", input_json,
                                  "--output_json", output_json]
            logging.debug("Starting Probe Level Module")
            subprocess.check_call(command_string)
            logging.debug("Finished Probe Level Module")
            
