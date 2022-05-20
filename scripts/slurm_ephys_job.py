import slurm_job
import sys

if __name__ == '__main__':
    """ 
    Currently, only runs the ephys nwb conversion step. In the future
    This will do additional steps, such as uploading to dandi
    """
    for i in sys.argv:
        print(i)
    slurm_job.generate_ephys_nwb(sys.argv[1])
