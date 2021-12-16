import csv
import functools
import numpy as np
import pandas as pd

from pynwb import NWBHDF5IO
import pynwb

from allensdk.brain_observatory.ecephys.file_io.ecephys_sync_dataset import (
    EcephysSyncDataset,
)
from allensdk.brain_observatory.ecephys.file_io.stim_file import (
    CamStimOnePickleStimFile,
)

from allensdk.brain_observatory.ecephys.stimulus_table import (
    ephys_pre_spikes,
    naming_utilities,
    output_validation,
)
from openscopenwb.utils import clean_up_functions as cuf
from os.path import join

from pynwb.file import NWBFile

loc_stim_file = ""


def add_trials_to_nwb(trial_params):
    stim_file = CamStimOnePickleStimFile.factory(trial_params['stimulus_pkl_path'])

    sync_dataset = EcephysSyncDataset.factory(trial_params['sync_h5_path'])
    frame_times = sync_dataset.extract_frame_times(
                strategy=trial_params['frame_time_strategy'])
    update_glob_stim(stim_file)
    stimulus_tabler, spon_tabler = create_partial_funcs(trial_params, stim_file)

    stim_table_full = ephys_pre_spikes.create_stim_table(
        stim_file.stimuli, stimulus_tabler, spon_tabler
    )
    stim_table_full = ephys_pre_spikes.apply_frame_times(
        stim_table_full, frame_times, stim_file.frames_per_second, True
    )

    output_validation.validate_epoch_durations(
        stim_table_full,
        fail_on_negative_durations=trial_params['fail_on_negative_duration'])
    output_validation.validate_max_spontaneous_epoch_duration(
        stim_table_full,
        trial_params['maximum_expected_spontaneous_activity_duration']
    )

    stim_table_full = naming_utilities.collapse_columns(stim_table_full)
    stim_table_full = naming_utilities.drop_empty_columns(stim_table_full)
    stim_table_full = naming_utilities.standardize_movie_numbers(
        stim_table_full)
    stim_table_full = naming_utilities.add_number_to_shuffled_movie(
        stim_table_full)
    stim_table_full = naming_utilities.map_stimulus_names(
        stim_table_full,
        trial_params['stimulus_name_map']
    )
    stim_table_full = naming_utilities.map_column_names(stim_table_full,
                                                        trial_params['column_name_map'])

    stim_table_full.to_csv(trial_params['output_stimulus_table_path'], index=False)
    write_trials_to_nwb(trial_params['output_stimulus_table_path'],
                        trial_params['output_nwb_path'])


def update_glob_stim(stim_file):
    global loc_stim_file
    loc_stim_file = stim_file


def write_trials_to_nwb(csv_path, nwb_path):
    write_nwb_path = nwb_path.replace("spike_times.nwb", "spike_times_re.nwb")
    io = NWBHDF5IO(nwb_path, "r+", load_namespaces=True)
    input_nwb = io.read()
    stim_list = []

    csv_info = pd.read_csv(csv_path)

    for i, row in csv_info.iterrows():
        input_nwb.add_trial(start_time=row['Start'],
                            stop_time=row['End'],
                            )
    for i in csv_info:
        if i == 'Start' or i == 'End':
            continue
        stim_list.append(i)
        data_list = []
        for j in csv_info[i]:
            data_list.append(j)
        input_nwb.add_trial_column(name=i, description=i, data=data_list)
    with NWBHDF5IO(write_nwb_path, mode='w') as export_io:
        export_io.export(src_io=io, nwbfile=input_nwb)


def create_partial_funcs(trial_params, stim_file):

    minimum_spontaneous_activity_duration = (
            trial_params['minimum_spontaneous_activity_duration'] /
            stim_file.frames_per_second
    )

    stimulus_tabler = functools.partial(
        ephys_pre_spikes.build_stimuluswise_table,
        seconds_to_frames=seconds_to_frames,
        extract_const_params_from_repr=trial_params['extract_const_params_from_repr'],
        drop_const_params=trial_params['drop_const_params'],
    )
    spon_tabler = functools.partial(
        ephys_pre_spikes.make_spontaneous_activity_tables,
        duration_threshold=minimum_spontaneous_activity_duration,
    )

    return stimulus_tabler, spon_tabler


def seconds_to_frames(seconds):
    return  \
        (np.array(seconds) + loc_stim_file.pre_blank_sec) * \
        loc_stim_file.frames_per_second
