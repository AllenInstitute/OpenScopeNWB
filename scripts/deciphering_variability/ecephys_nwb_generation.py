import os
import subprocess
import warnings
import openscopenwb as osn
from openscopenwb.utils import parse_project_parameters as ppp

warnings.filterwarnings("ignore", message="numpy.dtype size changed")

project_parameter_json = "path to project file"
project_parameters = ppp.parse_json(project_parameter_json)
sessions = ppp.get_session_ids(project_parameters)
modules = ppp.get_modules(project_parameters)

for session in sessions:
    session_parameters = ppp.generate_session_parameters(project_parameters, session)

    for module in modules:
        json_directory = ppp.get_input_json_directory(project_parameters)
        input_json = os.path.join(json_directory, session + '-' + module
                                  + '-input.json')
        output_json = os.path.join(json_directory, session + '-' + module
                                   + '-output.json')
        session_parameters = osn.create_module_input(input_json, session_parameters)

        command_string = ["python", "-W", "ignore", "-m", module,
                          "--input_json", input_json,
                          "--output_json", output_json]

        subprocess.check_call(command_string)


