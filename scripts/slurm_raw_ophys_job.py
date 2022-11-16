import slurm_job
import sys

if __name__ == '__main__':
    """
    Currently, only runs the ophys nwb conversion step. In the future
    This will do additional steps, such as uploading to dandi
    """
    print("arguments")
    print(sys.argv)
    slurm_job.generate_ophys_nwb(
        sys.argv[1],
        sys.argv[2],
        sys.argv[3],
        'True',
        sys.argv[4],
        sys.argv[5])
