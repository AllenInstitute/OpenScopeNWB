import os
import warnings
import logging
import sys

# import openscopenwb.create_module_input_json as osnjson
# from openscopenwb.utils import script_functions as sf
from openscopenwb.utils import parse_ophys_project_parameters as popp
from allensdk.brain_observatory.behavior.ophys_experiment import OphysExperiment as ophys
from pynwb import NWBHDF5IO

warnings.filterwarnings("ignore", message="numpy.dtype size changed")

sys.stdout = open('std.log', 'a')
logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG,
                    filemode='a')
dir = os.path.dirname(__file__)
project_parameter_json = os.path.join(dir, "project_json",
                                      "test_ophys_project_parameter_json.json")

project_info = popp.parse_json(project_parameter_json)
ophys_experiment_ids = popp.get_ids(project_info)
# ophys_experiment_id = 1137365310
for key in ophys_experiment_ids:
    ophys_experiment_id = int(key)
    ophys_session_id = int(ophys_experiment_ids[key])
    ophys_nwb = ophys.from_lims(ophys_experiment_id=ophys_experiment_id, skip_eye_tracking=True)
    ophys_nwb = ophys_nwb.to_nwb()
    file_path = r'\\allen\programs\mindscope\workgroups\openscope\ahad\ophys_no_behavior_nwb'
    file_path = os.path.join(file_path, str(ophys_experiment_id) + 'raw_data.nwb')
    with NWBHDF5IO(file_path, mode='w') as io:
        io.write(ophys_nwb)
