from simple_slurm import Slurm
import os

conda_environment = 'openscopenwb'

python_path = os.path.join(
    'allen',
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
    cpus_per_task=6,
    job_name='openscope_test',
    dependency=dict(after=65541, afterok=34987),
    mem='8gb',
    output=f'{Slurm.JOB_ARRAY_MASTER_ID}_{Slurm.JOB_ARRAY_ID}.out'
)

slurm.sbatch(r'/allen/programs/mindscope/workgroups/openscope/ahad/' +
             r'test_script/OpenScopeNWB-feature-ephys_write_stim/' +
             r'scripts/deciphering_variability/ecephys_nwb_generation.py')
