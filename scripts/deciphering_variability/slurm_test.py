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
print(python_path)
