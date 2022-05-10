import slurm_job
import slurm_temp
import sys

slurm_job.generate_ephys_nwb(slurm_temp.get_text())