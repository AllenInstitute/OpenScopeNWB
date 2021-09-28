import os
import subprocess
import warnings
import openscopenwb as osn
import openscopenwb.create_module_input_json as osnjson
from openscopenwb.utils import parse_project_parameters as ppp

warnings.filterwarnings("ignore", message="numpy.dtype size changed")

project_parameter_json = "path to project file"
# project_parameters = ppp.parse_json(project_parameter_json)
# sessions = ppp.get_session_ids(project_parameters)
# modules = ppp.get_modules(project_parameters)


# Settings, currently being used for testing
sessions = ['721123822']
modules = ['allensdk.brain_observatory.ecephys.align_timestamps',
           'allensdk.brain_observatory.ecephys.stimulus_table',
           'allensdk.brain_observatory.extract_running_speed',
           'allensdk.brain_observatory.ecephys.write_nwb']
for session in sessions:
    # session_params = ppp.generate_session_params(project_parameters,
    #                                                     session)
    session_params = {
        'session_id': '721123822',
        'base_directory': "S:\\721123822_NWB",
        'last_unit_id': 1,
        'probes': ['ProbeA', 'ProbeB', 'ProbeC', 'ProbeD', 'ProbeE', 'ProbeF'],
        'final_probe': 'ProbeF',
        'probe_dict_list': [],
        'trim': False
    }
    for module in modules:
        #json_directory = ppp.get_input_json_directory(project_parameters)
        json_directory = session_params['base_directory'] + '\\JSON'
        input_json = os.path.join(json_directory, session + '-' + module
                                  + '-input.json')
        output_json = os.path.join(json_directory, session + '-' + module
                                   + '-output.json')
        session_params = osnjson.create_module_input(module, session_params, input_json)

        command_string = ["python", "-W", "ignore", "-m", module,
                          "--input_json", input_json,
                          "--output_json", output_json]

        subprocess.check_call(command_string)
