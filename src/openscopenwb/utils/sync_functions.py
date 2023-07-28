from allensdk.brain_observatory.sync_dataset import \
    Dataset
import allensdk.brain_observatory.ecephys.stimulus_sync as sync
from openscopenwb.utils import postgres_functions as postgres
from glob import glob
from os.path import join
import numpy as np
import os
import matplotlib
matplotlib.use('WebAgg')


def sync_test(session_id):
    """Tests the sync file for a session for long frames

    Parameters
    ----------
    session_id: str
        The session_id for the session

    Returns
    -------
    long_flag: bool
        True if there are long frames, False otherwise
    """
    long_flag = False
    sync_file = postgres.get_e_sess_sync(session_id)
    sync_exists = os.path.isfile(sync_file)
    if sync_exists:
        try:
            syncdata = Dataset(sync_file)
        except Exception:
            sync_file = postgres.get_e_sess_directory(session_id)
            print("DIRECTORY", sync_file)
            sync_file = glob(
                join(sync_file, '**/**', '*.sync'), recursive=True)
            print("SYNC: ", sync_file)
            syncdata = Dataset(max(sync_file, key=os.path.getmtime))
    else:
        sync_file = postgres.get_e_sess_directory(session_id)
        print("DIRECTORY", sync_file)
        sync_file = glob(join(sync_file, '**/**', '*.sync'), recursive=True)
        print("SYNC: ", sync_file)
        syncdata = Dataset(sync_file[0])
    # Grab the stim running line that tells us when visual stimuli were on the
    # screen
    stim_running_r, stim_running_f = (syncdata.get_rising_edges(
                                        'stim_running', 'seconds'),
                                      syncdata.get_falling_edges(
                                        'stim_running', 'seconds'))

    # Filter out any falling edges from before the first rising
    stim_running_f = stim_running_f[stim_running_f > stim_running_r[0]]

    # Get vsyncs that tell us when the graphics card buffer was flipped
    vsyncs = syncdata.get_falling_edges('vsync_stim', units='seconds')
    print("Syncs")
    print(vsyncs)
    vsyncs = vsyncs[(stim_running_r[0] <= vsyncs) &
                    (vsyncs < stim_running_f[0])]
    # These are the vsyncs that are associated with a diode flip
    flip_vsyncs = vsyncs[::60]
    print("VSYNCS")
    print(vsyncs)
    # Get diode edges
    photodiode_times = np.sort(np.concatenate([
        syncdata.get_rising_edges('stim_photodiode', 'seconds'),
        syncdata.get_falling_edges('stim_photodiode', 'seconds')
    ]))
    photodiode_times = photodiode_times[
        (stim_running_r[0] <= photodiode_times) &
        (photodiode_times < stim_running_f[0])
    ]
    # removes blinking at beginning and end of each stimulus
    photodiode_times_trimmed = sync.trim_border_pulses(
        photodiode_times, vsyncs
    )
    # correcting for on/off photodiode asymmetry
    photodiode_times_on_off = sync.correct_on_off_effects(
        photodiode_times_trimmed
    )
    # fix blips in the line: THIS IS THE FUNCTION THAT GOES HAYWIRE
    photodiode_times_fixed = sync.fix_unexpected_edges(
        photodiode_times_on_off, cycle=60)

    # fix blips in the line: THIS version accounts for long times
    photodiode_times_fixed_no_long = sync.fix_unexpected_edges_no_long(
        photodiode_times_on_off, cycle=60)
    # find the first diode edges after each flip_vsync
    nearest_diode_edges = np.searchsorted(photodiode_times_on_off, flip_vsyncs)

    diode_list = list(zip(photodiode_times_fixed,
                      photodiode_times_fixed_no_long))
    for i in diode_list:
        if i[0] != i[1]:
            print(i)
            long_flag = True
    return (long_flag)
