import slurm_job
import sys

if __name__ == '__main__':
    # Some doc to explain this stpe
    slurm_job.generate_ephys_nwb(sys.argv[1])
