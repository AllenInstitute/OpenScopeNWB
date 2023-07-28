from allensdk.brain_observatory.sync_dataset import \
    Dataset
import allensdk.brain_observatory.ecephys.stimulus_sync as sync
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.use('WebAgg')

# Get sync dataset object for one of the bad sessions
syncdata = Dataset(
    r'/allen/programs/mindscope/production/openscope/prod0/' +
    'specimen_1194090570/ecephys_session_1208667752/1208964113/' +
    '1208667752_637484_20220908.sync')

# Grab the stim running line that tells us when visual stimuli were on the
# screen
stim_running_r, stim_running_f = (syncdata.get_rising_edges('stim_running', 
                                                            'seconds'),
                                  syncdata.get_falling_edges('stim_running', 
                                                             'seconds'))
stim_running_f = stim_running_f[stim_running_f > stim_running_r[0]]
# Get vsyncs that tell us when the graphics card buffer was flipped
vsyncs = syncdata.get_falling_edges('vsync_stim', units='seconds')
vsyncs = vsyncs[(stim_running_r[0] <= vsyncs) & (vsyncs < stim_running_f[0])]
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
# find the first diode edges after each flip_vsync
nearest_diode_edges = np.searchsorted(photodiode_times_on_off, flip_vsyncs)
# get the monitor lag between the vsync and the diode edge
lags = photodiode_times_on_off[nearest_diode_edges] - flip_vsyncs
# Plot histogram of lags, these should be tight around 20-21 ms

plt.figure()
plt.hist(lags, bins=1000)
# Plot the diode/vsyncs together
fig, ax = plt.subplots(2, 1, sharex=True)
ys = np.ones(len(photodiode_times))
ys[::2] = 0
ax[0].step(photodiode_times, ys)
ys = np.ones(len(photodiode_times_fixed))
ys[::2] = 0
ax[0].step(photodiode_times_fixed, ys)
ax[0].plot(vsyncs, np.ones(len(vsyncs)) * 0.5, 'k|')
ax[0].plot(flip_vsyncs, np.ones(len(flip_vsyncs)) * 0.5, 'r|', ms=10, )
ax[1].plot(photodiode_times[:-1], np.diff(photodiode_times))
ax[0].legend(['raw diode', 'fixed diode', 'vsyncs', 'flip vsyncs'])
ax[1].legend(['raw diode edge intervals'])
plt.show()
