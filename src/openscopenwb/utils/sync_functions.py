from allensdk.brain_observatory.sync_dataset import \
    Dataset
import allensdk.brain_observatory.ecephys.stimulus_sync as sync
from openscopenwb.utils import postgres_functions as postgres
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('WebAgg')


def sync_test(session_id):
    long_flag = False
    syncdata = Dataset(postgres.get_e_sess_sync(session_id))
    print(postgres.get_e_sess_sync(session_id))
    # syncdata = Dataset(r'/allen/programs/mindscope/workgroups/np-exp/1213341633_637908_20220922/1213341633_637908_20220922.sync')
    # Grab the stim running line that tells us when visual stimuli were on the
    # screen
    stim_running_r, stim_running_f = (syncdata.get_rising_edges('stim_running', 'seconds'),
                                      syncdata.get_falling_edges('stim_running', 'seconds'))
    # Get vsyncs that tell us when the graphics card buffer was flipped
    vsyncs = syncdata.get_falling_edges('vsync_stim', units='seconds')
    vsyncs = vsyncs[(stim_running_r[0] <= vsyncs) &
                    (vsyncs < stim_running_f[0])]
    # These are the vsyncs that are associated with a diode flip
    flip_vsyncs = vsyncs[::60]
    # Get diode edges
    photodiode_times = np.sort(np.concatenate([
        syncdata.get_rising_edges('stim_photodiode', 'seconds'),
        syncdata.get_falling_edges('stim_photodiode', 'seconds')
    ]))
    photodiode_times = photodiode_times[(stim_running_r[0] <= photodiode_times) & (
        photodiode_times < stim_running_f[0])]
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

    photodiode_times_fixed_no_long = sync.fix_unexpected_edges_no_long(
        photodiode_times_on_off, cycle=60)
    # find the first diode edges after each flip_vsync
    nearest_diode_edges = np.searchsorted(photodiode_times_on_off, flip_vsyncs)
    # get the monitor lag between the vsync and the diode edge
    lags = photodiode_times_on_off[nearest_diode_edges] - flip_vsyncs

    diode_list = list(zip(photodiode_times_fixed,
                      photodiode_times_fixed_no_long))
    for i in diode_list:
        if i[0] != i[1]:
            print(i)
            long_flag = True
    print(long_flag)