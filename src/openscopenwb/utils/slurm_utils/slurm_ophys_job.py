import slurm_job
import sys

if __name__ == '__main__':
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
    try:
        print("SLURN OPHYS JOB")
        print("arguments")
        print(sys.argv)
        slurm_job.generate_ophys_nwb(
            sys.argv[1],
            sys.argv[2],
            sys.argv[3],
            False,
            sys.argv[4],
            sys.argv[5])
    except Exception as e:
        print("An error occurred:", str(e))
