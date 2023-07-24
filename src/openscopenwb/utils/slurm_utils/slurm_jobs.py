from simple_slurm import Slurm
import os
from time import time
import warnings
import logging
import sys
import inspect
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import postgres_functions as postgres


warnings.filterwarnings("ignore", message="numpy.dtype size changed")

sys.stdout = open('std.log', 'a')
logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG,
                    filemode='a')
dir = os.path.dirname(__file__)


def generate_ephys_nwb(session_id, project, long):
    '''Generates an ephys nwb for a given session_id and project
    
    Parameters
    ----------
    session_id: str
        The sessions's id value
    project: str
        The project's name in LIMS
    long: str
        Whether the session has long frames

    Returns
    -------
    '''
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
    '''Generates an ophys nwb for a given experiment
    
    Parameters
    ----------
    session_id: str
        The sessions's id value
    project_d: str
        The project's name in LIMS
    experiment_id: str
        The experiment's id in LIMS
    raw: bool
        Whether the session will have raw data
    val: str
        The project's dandi value
    final: bool
        Whether the experiment is the final of the session

    Returns
    -------
    '''
    conda_environment = 'ophys_nwb'
    print("SLURM JOB")

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
    if final == "True":
        final = True
    else:
        final = False
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


def dandi_ephys_upload():
    '''Generates an ophys nwb for a given session_id and project
    
    Parameters
    ----------
    file: str
        The experiment file's nwb path
    session_id: str
        The sessions's id value
    experiment_id: str
        The experiment's id in LIMS
    subject_id: str
        The subject's DONOR id in LIMS
    raw: bool
        Whether the session will have raw data
    final: bool
        Whether the experiment is the final of the session

    Returns
    -------
    '''
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
                 r'scripts/dandi_ephys_uploads.py'
                 ' --sess_id {}'.format('1274061513') +
                 ' --nwb_folder_path {}'.format(r'/allen/programs/mindscope/workgroups/openscope/openscopedata2022/1274061513/2023-06-13-13-21/nwb_path/1274061513') +
                 ' --dandiset_id {}'.format('000563') +
                 ' --subject_id {}'.format('688000') + 
                 ' --project_id {}'.format('OpenScopeTemporalBarcode'))    

def add_temp_to_nwb():
    '''Adds image templates to an ephys nwb

    Parameters
    ----------

    Returns
    -------
    '''
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
        job_name='Openscope_add_temp_to_nwb',
        mem='24gb',
        partition='braintv',
        time="01:50:00",
        output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out'
    )

    dir = os.path.dirname(__file__)
    slurm.sbatch(python_path +
                 r' /allen/programs/mindscope/workgroups/openscope/ahad/' +
                 r'test_cron/OpenScopeNWB-feature-firebase_testing/' +
                 r'scripts/ecephys_nwb_templates.py')



def dandi_ophys_upload(file, session_id, experiment_id, subject_id, raw,  final):
    '''Generates an ophys nwb for a given session_id and project
    
    Parameters
    ----------
    file: str
        The experiment file's nwb path
    session_id: str
        The sessions's id value
    experiment_id: str
        The experiment's id in LIMS
    subject_id: str
        The subject's DONOR id in LIMS
    raw: bool
        Whether the session will have raw data
    final: bool
        Whether the experiment is the final of the session

    Returns
    -------
    '''
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
                 ' --raw {}'.format(False) +
                 ' --final {}'.format(final))


def nwb_add_templates():
    '''Adds image templates to an ephys nwb

    Parameters
    ----------
    None

    Returns
    -------
    '''

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
        job_name='openscope_fix_nwb_template',
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
                 r'scripts/ecephys_nwb_templates.py')
