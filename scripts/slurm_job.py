from simple_slurm import Slurm
import os
from time import time
import warnings
import logging
import sys
import inspect
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import postgres_functions as postgres


# from openscopenwb.utils import parse_ophys_project_parameters as popp
# from allensdk.brain_observatory.behavior.ophys_experiment import \
# OphysExperiment as ophys

warnings.filterwarnings("ignore", message="numpy.dtype size changed")

sys.stdout = open('std.log', 'a')
logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG,
                    filemode='a')
dir = os.path.dirname(__file__)


def generate_ephys_nwb(session_id, project, long):
    if long == "True":
        conda_environment = 'long_nwb'
    else:
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
    print(project)

    slurm = Slurm(
        array=range(3, 4),
        cpus_per_task=12,
        job_name='openscope_ephys_nwb',
        dependency=dict(after=65541, afterok=34987),
        mem='128gb',
        partition='braintv',
        time="06:00:00",
        output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out'
    )
    dir = os.path.dirname(__file__)
    print(dir)

    slurm.sbatch(python_path +
                 r' /allen/programs/mindscope/workgroups/openscope/ahad/' +
                 r'test_cron/OpenScopeNWB-feature-firebase_testing/' +
                 r'scripts/ecephys_nwb_generation.py'
                 ' --session_id {}'.format(session_id) +
                 ' --project {}'.format(project))


def generate_ophys_nwb(project_id, session_id, experiment_id, raw, val, final):
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
    experiments = postgres.get_sess_experiments(session_id)
    fb.start(fb.get_creds())
    slurm_id_old = fb.get_curr_job()['id']
    slurm = Slurm(
        array=range(3, 4),
        cpus_per_task=12,
        job_name='openscope_ophys_nwb',
        dependency=dict(after=slurm_id_old),
        mem='128gb',
        partition='braintv',
        time="01:50:00",
        output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out'
    )
    dir = os.path.dirname(__file__)
    slurm.sbatch(python_path +
                 r' /allen/programs/mindscope/workgroups/openscope/ahad/' +
                 r'test_cron/OpenScopeNWB-feature-firebase_testing/' +
                 r'scripts/ophys_nwb_generation.py'
                 ' --project_id {}'.format(project_id) +
                 ' --session_id {}'.format(session_id) +
                 ' --experiment_id {}'.format(experiment_id) +
                 ' --raw {}'.format(raw) +
                 ' --val {}'.format(val) +
                 ' --final {}'.format(final))


def dandi_ophys_upload(file, session_id, experiment_id, subject_id, raw,  final):
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
        job_name='openscope_dandi_upload',
        mem='128gb',
        partition='braintv',
        time="01:50:00",
        output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out'
    )
    dir = os.path.dirname(__file__)
    slurm.sbatch(python_path +
                 r' /allen/programs/mindscope/workgroups/openscope/ahad/' +
                 r'test_cron/OpenScopeNWB-feature-firebase_testing/' +
                 r'scripts/dandi_uploads.py'
                 ' --session_id {}'.format(session_id) +
                 ' --nwb_folder_path {}'.format(file) +
                 ' --experiment_id {}'.format(experiment_id) +
                 ' --subject_id {}'.format(subject_id) + 
                 ' --raw {}'.format(raw) +
                 ' --final {}'.format(final))

'''
if __name__ == '__main__':
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
        job_name='openscope_fix_nwb',
        dependency=dict(after=65541, afterok=34987),
        mem='128gb',
        partition='braintv',
        time="60:00:00",
        output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out'
    )
    dir = os.path.dirname(__file__)
    slurm.sbatch(python_path +
                 r' /allen/programs/mindscope/workgroups/openscope/ahad/' +
                 r'test_cron/OpenScopeNWB-feature-firebase_testing/' +
                 r'scripts/ephys_rename.py')

'''

if __name__ == '__main__':
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
        job_name='openscope_fix_nwb',
        dependency=dict(after=65541, afterok=34987),
        mem='128gb',
        partition='braintv',
        time="60:00:00",
        output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out'
    )
    dir = os.path.dirname(__file__)
    slurm.sbatch(python_path +
                 r' /allen/programs/mindscope/workgroups/openscope/ahad/' +
                 r'test_cron/OpenScopeNWB-feature-firebase_testing/' +
                 r'scripts/ophys_rename.py')
