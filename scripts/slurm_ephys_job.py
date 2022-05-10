import slurm_job
import sys

if __name__ == '__main__':
    slurm_job.generate_ephys_nwb(sys.argv[1])
