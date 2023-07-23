import slurm_jobs
import sys

if __name__ == '__main__':
    """Calls functions to submit ephys NWB session jobs

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
    """
    print("arguments")
    print(sys.argv)
    slurm_jobs.generate_ephys_nwb(sys.argv[1], sys.argv[2], sys.argv[3])
