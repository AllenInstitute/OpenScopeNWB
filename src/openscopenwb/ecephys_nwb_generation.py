import os
import subprocess
import warnings
from create_input_JSON import createEcephysJSON

warnings.filterwarnings("ignore", message="numpy.dtype size changed")


# TODO: Generate info_list from parameter JSON
# TODO: Clarify purpose of some code using comments
# TODO: Implement function from util to parse parameter JSON
info_list = ''
directories = info_list.directories
JSON_directory = info_list.JSON_directory
modules = info_list.modules
output_directory = info_list.output_directory
last_unit_id = info_list.last_unit_id

for directory in directories:

    session_id = os.path.basename(os.path.dirname(directory))

    for module in modules:

        input_json = os.path.join(JSON_directory, session_id + '-' + module
                                  + '-input.json')
        output_json = os.path.join(JSON_directory, session_id + '-' + module
                                   + '-output.json')

        info, last_unit_id = createEcephysJSON(directory,
                                               module,
                                               input_json,
                                               last_unit_id)

        print('Running ' + module + ' for session id ' + session_id)

        command_string = ["python", "-W", "ignore", "-m", module,
                          "--input_json", input_json,
                          "--output_json", output_json]

        subprocess.check_call(command_string)
