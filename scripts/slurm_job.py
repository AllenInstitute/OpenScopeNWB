import os
from time import time
import warnings
import logging
import sys
import inspect 
print(os.path.dirname(inspect.getfile(inspect))+"/site-packages") 

# from openscopenwb.utils import parse_ophys_project_parameters as popp
# from allensdk.brain_observatory.behavior.ophys_experiment import \
# OphysExperiment as ophys
from simple_slurm import Slurm

warnings.filterwarnings("ignore", message="numpy.dtype size changed")

sys.stdout = open('std.log', 'a')
logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG,
                    filemode='a')
dir = os.path.dirname(__file__)

'''
def generate_ophys_nwb(session_id):
    project_parameter_json = gen_json(session_id)
    project_info = popp.parse_json(project_parameter_json)
    ophys_experiment_ids = popp.get_ids(project_info)
    for key in ophys_experiment_ids:
        ophys_experiment_id = int(key)
        ophys_session_id = int(ophys_experiment_ids[key])
        ophys_nwb = ophys.from_lims(ophys_experiment_id=ophys_experiment_id,
                    skip_eye_tracking=True)
        ophys_nwb = ophys_nwb.to_nwb()
        file_path = r"//allen/programs/braintv/production/openscope/"
                    openscopedata2022/" + str(session_id) +  '/'
        file_path = os.path.join(file_path, str(ophys_experiment_id) + \
                    'raw_data.nwb')
        with NWBHDF5IO(file_path, mode='w') as io:
            io.write(ophys_nwb)


'''

def generate_ephys_nwb(session_id, project):
    conda_environment = 'openscopenwb'

    python_path = os.path.join(
        '/allen',
        'programs',
        'mindscope',
        'workgroups',
        'openscope',
        'ahad',
        'Conda_env',
        conda_environment,
        'bin',
        'python'
    )
    print(session_id)

    slurm = Slurm(
        array=range(3, 4),
        cpus_per_task=12,
        job_name='openscope_test',
        dependency=dict(after=65541, afterok=34987),
        mem='128gb',
        partition = 'braintv',
        time = "06:00:00",
        output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out'
    )
    dir = os.path.dirname(__file__)
    print(dir)

    slurm.sbatch(python_path+
                r' /allen/programs/mindscope/workgroups/openscope/ahad/'+
                r'test_cron/OpenScopeNWB-feature-firebase_testing/' +
                r'scripts/ecephys_nwb_generation.py'
                ' --session_id {}'.format(session_id) +
                ' --project {}'.format(project))


def generate_ophys_nwb(session_id, experiment_id, raw, val):
    conda_environment = 'ophys_nwb'

    python_path = os.path.join(
        '/allen',
        'programs',
        'mindscope',
        'workgroups',
        'openscope',
        'ahad',
        'Conda_env',
        conda_environment,
        'bin',
        'python'
    )

    slurm = Slurm(
        array=range(3, 4),
        cpus_per_task=12,
        job_name='openscope_test',
        dependency=dict(after=65541, afterok=34987),
        mem='128gb',
        partition = 'braintv',
        time = "01:50:00",
        output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out'
    )
    dir = os.path.dirname(__file__)
    print(dir)
    print(raw)
    slurm.sbatch(python_path+
                r' /allen/programs/mindscope/workgroups/openscope/ahad/'+
                r'test_cron/OpenScopeNWB-feature-firebase_testing/' +
                r'scripts/ophys_nwb_generation.py'
                ' --session_id {}'.format(session_id) +
                ' --experiment_id {}'.format(experiment_id) +
                ' --raw {}'.format(raw) +
                ' --val {}'.format(val))

def dandi_ophys_upload(file, session_id, experiment_id, raw, val):
    conda_environment = 'openscopenwb'

    python_path = os.path.join(
        '/allen',
        'programs',
        'mindscope',
        'workgroups',
        'openscope',
        'ahad',
        'Conda_env',
        conda_environment,
        'bin',
        'python'
    )

    slurm = Slurm(
        array=range(3, 4),
        cpus_per_task=12,
        job_name='openscope_test',
        dependency=dict(after=65541, afterok=34987),
        mem='128gb',
        partition = 'braintv',
        time = "01:50:00",
        output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out'
    )
    dir = os.path.dirname(__file__)
    print(dir)
    print(raw)
    slurm.sbatch(python_path+
                r' /allen/programs/mindscope/workgroups/openscope/ahad/'+
                r'test_cron/OpenScopeNWB-feature-firebase_testing/' +
                r'scripts/dandi_uploads.py'
                ' --sess_id {}'.format(session_id) +
                ' --dandi_file {}'.format(file) +
                ' --exp_id {}'.format(experiment_id) +
                ' --raw {}'.format(raw) +
                ' --dandi_val {}'.format(val))