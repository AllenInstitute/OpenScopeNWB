import io
import json
from os.path import join
from glob import glob
import numpy as np
import os
import pandas as pd
import datetime

from utils import cleanUpNanAndInf


# TODO: Work on parameterJSON info more to work on parsing the relevant modules
# NOTE: This example is based on the “deciphering variability” project example
# NOTE: Each project will have a unique create_input_JSON.py
# NOTE: Will need to rework how the returned dictionaries are assigned
# CONT: to the createEcephys function
# NOTE: Utils will have a function where the parameter JSON is parsed
def runModules(input_list):
    # This is not being parsed currently
    # Included for demonstration on how functionality will work
    # TODO: Implement a python-based switch case for this
    session_id = input_list.session_Id
    local_path = 'S:\\DV_NWB\\LFP\\'
    for module_name in input_list.modules:
        module = module_name
        if module == 'allensdk.brain_observatory.ecephys.align_timestamps':
            try:
                spike_times = np.load(join(input_list.probe_directory,
                                      'spike_times.npy'))
            except FileNotFoundError:
                print(' Spikes not found for ' + input_list.probe_directory)
            else:
                probe_dict = {
                    'name': input_list.probe_name,
                    'sampling_rate': 30000.,
                    'lfp_sampling_rate': 2500.,
                    'barcode_channel_states_path': join(
                        input_list.events_directory,
                        'channel_states.npy'),
                    'barcode_timestamps_path': join(
                        input_list.events_directory,
                        'event_timestamps.npy'),
                    'mappable_timestamp_files': input_list.timestamp_files,
                }

                input_list.spike_times.append(spike_times)
                input_list.probes.append(probe_dict)

        elif module == 'allensdk.brain_observatory.ecephys.lfp_subsampling':

            probe_dict = {
                'name': input_list.probe_name,
                'lfp_sampling_rate': 2500.,
                'lfp_input_file_path': join(
                    input_list.lfp_directory,
                    'continuous.dat'),
                'lfp_timestamps_input_path': join(
                    input_list.lfp_directory,
                    'lfp_timestamps_master_clock.npy'),
                'lfp_data_path': join(
                    local_path,
                    session_id +
                    '_' +
                    input_list.probe_name +
                    '_lfp.dat'),
                'lfp_timestamps_path': join(
                    local_path,
                    session_id +
                    '_' +
                    input_list.probe_name +
                    '_timestamps.npy'),
                'lfp_channel_info_path': join(
                    local_path,
                    session_id +
                    '_' +
                    input_list.probe_name +
                    '_channels.npy'),
                'surface_channel': input_list.probe_info['surface_channel'],
                'reference_channels': [191]}

            input_list.probes.append(probe_dict)

        # NOTE: This is using my local file path
        # NOTE: This will be changed to use a file path specified
        # CONT: by the parameter JSON
        # TODO: Specify input path using the parameter JSON
        elif module == 'allensdk.brain_observatory.ecephys.write_nwb':
            try:
                channel_info = pd.read_csv(join(input_list.probe_directory,
                                           'ccf_regions.csv'), index_col=0)
            except FileNotFoundError:
                pass
            else:

                lfp_dict = {
                    'input_data_path': join(local_path, str(session_id)
                                            + '_' + input_list.probe_name
                                            + '_lfp.dat'),
                    'input_timestamps_path': join(local_path, str(session_id)
                                                  + '_' + input_list.probe_name
                                                  + '_timestamps.npy'),
                    'input_channels_path': join(local_path, str(session_id)
                                                + '_' + input_list.probe_name
                                                + '_channels.npy'),
                    'output_path': join(local_path, str(session_id)
                                        + '_' + input_list.probe_name
                                        + '.lfp.nwb'),
                }
                input_list.lfp_dict = lfp_dict

                channels = []

                for idx, channel_row in channel_info.iterrows():

                    structure_acronym = channel_row['region']

                    channel_dict = {
                        'id': idx + input_list.probe_idx * 1000,
                        'valid_data': True,
                        # channel_row['is_valid'],
                        'probe_id': input_list.probe_idx,
                        'local_index': idx,
                        'probe_vertical_position': -1,
                        # channel_row['vertical_position'],
                        'probe_horizontal_position': -1,
                        # channel_row['horizontal_position'],
                        'manual_structure_id': -1,
                        'manual_structure_acronym': structure_acronym,
                        # 'cortical_layer': cortical_layer,
                        'anterior_posterior_ccf_coordinate': -1,
                        # channel_row['A/P'],
                        'dorsal_ventral_ccf_coordinate': -1,
                        # channel_row['D/V'],
                        'left_right_ccf_coordinate': -1,
                        # channel_row['M/L'],
                        # 'cortical_depth': channel_row['cortical_depth']
                    }

                    channels.append(channel_dict)

                unit_info = pd.read_csv(join(input_list.probe_directory,
                                             'metrics.csv'), index_col=0)
                quality_info = pd.read_csv(join(input_list.probe_directory,
                                                'cluster_group.tsv.v2'),
                                           sep='\t', index_col=0)

                spike_clusters = np.load(join(input_list.probe_directory,
                                              'spike_clusters.npy'))

                units = []

                for idx, unit_row in unit_info.iterrows():

                    if quality_info.loc[unit_row.cluster_id].group == 'good':

                        spike_count = np.sum(spike_clusters ==
                                             unit_row['cluster_id'])
                        for i in unit_row:
                            unit_row[i] = cleanUpNanAndInf(i)
                        unit_dict = {
                            'id': input_list.last_unit_id,
                            'peak_channel_id': unit_row['peak_channel'] +
                            input_list.probe_idx * 1000,
                            'local_index': idx,
                            'cluster_id': unit_row['cluster_id'],
                            'quality': unit_row['quality'],
                            'firing_rate': unit_row['firing_rate'],
                            'snr': unit_row['snr'],
                            'isi_violations': unit_row['isi_viol'],
                            'presence_ratio': unit_row['presence_ratio'],
                            'amplitude_cutoff': unit_row['amplitude_cutoff'],
                            'isolation_distance': unit_row['isolation_ \
                                                            distance'],
                            'l_ratio': unit_row['l_ratio'],
                            'd_prime': unit_row['d_prime'],
                            'nn_hit_rate': unit_row['nn_hit_rate'],
                            'nn_miss_rate': unit_row['nn_miss_rate'],
                            'max_drift': unit_row['max_drift'],
                            'cumulative_drift': unit_row['cumulative_drift'],
                            'silhouette_score': unit_row['silhouette_score'],
                            'waveform_duration': unit_row['duration'],
                            'waveform_halfwidth': unit_row['halfwidth'],
                            'PT_ratio': unit_row['PT_ratio'],
                            'repolarization_slope': unit_row['repolarization_\
                                                             slope'],
                            'recovery_slope': unit_row['recovery_slope'],
                            'amplitude': unit_row['amplitude'],
                            'spread': unit_row['spread'],
                            'velocity_above': unit_row['velocity_above'],
                            'velocity_below': unit_row['velocity_below']
                        }

                        input_list.spike_times_index += spike_count
                        input_list.spike_amplitudes_index += spike_count

                        units.append(unit_dict)

                        input_list.last_unit_id += 1

                probe_dict = {
                    'id': input_list.probe_idx,
                    'name': input_list.probe_name,
                    'spike_times_path': join(input_list.probe_directory,
                                             'spike_times_master_clock.npy'),
                    'spike_clusters_file': join(input_list.probe_directory,
                                                'spike_clusters.npy'),
                    'spike_amplitudes_path': join(input_list.probe_directory,
                                                  'amplitudes.npy'),
                    'mean_waveforms_path': join(input_list.probe_directory,
                                                'mean_waveforms.npy'),
                    'spike_templates_path': join(input_list.probe_directory,
                                                 'spike_templates.npy'),
                    'templates_path': join(input_list.probe_directory,
                                           'templates.npy'),
                    'inverse_whitening_matrix_path': {
                        join(input_list.probe_directory,
                             'whitening_mat_inv.npy')
                    },
                    'channels': channels,
                    'units': units,
                    'lfp': None  # lfp_dict
                }

                input_list.probes.append(probe_dict)

    if module == 'allensdk.brain_observatory.ecephys.align_timestamps':

        dictionary = \
            {
                'sync_h5_path': glob(join(input_list.directory, '*.sync'))[0],
                "probes": input_list.probes,
            }

    elif module == 'allensdk.brain_observatory.ecephys.stimulus_table':

        if False:
            trim_discontiguous_frame_times = True
        else:
            trim_discontiguous_frame_times = False

        dictionary = {
            'stimulus_pkl_path': glob(
                join(
                    input_list.directory,
                    '*.stim.pkl'))[0],
            'sync_h5_path': glob(
                join(
                    input_list.directory,
                    '*.sync'))[0],
            'output_stimulus_table_path': os.path.join(
                        input_list.directory,
                        'stim_table_allensdk.csv'),
            'output_frame_times_path': os.path.join(
                input_list.directory,
                'frame_times.npy'),
            'trim_discontiguous_frame_times': trim_discontiguous_frame_times,
            "log_level": 'INFO'}

    elif module == 'allensdk.brain_observatory.extract_running_speed':

        if False:
            trim_discontiguous_frame_times = True
        else:
            trim_discontiguous_frame_times = False

        dictionary = \
            {
                'stimulus_pkl_path': glob(join(input_list.directory,
                                               '*.stim.pkl'))[0],
                'sync_h5_path': glob(join(input_list.directory, '*.sync'))[0],

                'output_path': join(input_list.directory, 'running_speed.h5'),
                'trim_discontiguous_frame_times': {
                    trim_discontiguous_frame_times
                },
                "log_level": 'INFO'
            }

    elif module == 'allensdk.brain_observatory.ecephys.lfp_subsampling':

        dictionary = \
            {
                'lfp_subsampling': {'temporal_subsampling_factor': 2, },
                "probes": input_list.probes,
            }

    elif module == 'allensdk.brain_observatory.ecephys.optotagging_table':

        dictionary = {
            'opto_pickle_path': glob(
                join(
                    input_list.directory,
                    '*.opto.pkl'))[0],
            'sync_h5_path': glob(
                join(
                    input_list.directory,
                    '*.sync'))[0],
            'output_opto_table_path': join(
                        input_list.directory,
                'optotagging_table.csv')}

    elif module == 'allensdk.brain_observatory.ecephys.write_nwb':

        # session_string = os.path.basename(sync_file)
        YYYY = 2021  # int(session_string[17:21])
        MM = 6  # int(session_string[21:23])
        DD = 16  # int(session_string[23:25])

        dictionary = \
            {
                'invalid_epochs': [{'id': 0,
                                    'type': 'none',
                                    'label': 'LABEL',
                                    'start_time': 0.0,
                                    'end_time': 0.0}, ],
                "log_level": 'INFO',
                "output_path": input_list.nwb_output_path,
                "session_id": int(session_id),
                "session_start_time": datetime.datetime(YYYY, MM, DD,
                                                        0, 0, 0).isoformat(),
                "stimulus_table_path": os.path.join(input_list.directory,
                                                    'stim_table_allensdk.csv'),
                "probes": input_list.probes,
                "session_sync_path": input_list.sync_file,
                # ,
                "running_speed_path": join(input_list.directory,
                                           'running_speed.h5')
                # "optotagging_table_path": join(directory,
                #                                'optotagging_table.csv')
            }
    input_list.dictionary = dictionary
    return input_list


# TODO: Implement better log in method(?)
# TODO: Fix some formatting for Linting
# NOTE: Ths goal is to have this function be as general as possible and handle
# CONT: changes in the runModules function specifically
def createEcephysJSON(output_directory, row, output_file, last_unit_id,
                      probe_list):

    session_id = str(row.session_id)
    description = 'Neuropixels experiment in visual cortex'
    sync_file = glob(join(row.local_path, '*.sync'))[0]
    nwb_output_path = join(output_directory, 'mouse' + str(row['name']) +
                           '.spikes.nwb')
    stimulus_table_path = join(row.local_path, 'stim_table.csv')

    probe_directories = []
    available_probes = []
    for probe in probe_list:
        if isinstance(row[probe], str):

            probe_directories.append(row[probe])
            available_probes.append(probe)

    # Printing out possible directories for testing purposes
    print(probe_directories)
    print(available_probes)
    probes = []
    probe_idx = -1
    spike_times_index = 0
    spike_amplitudes_index = 0

    for probe_name, probe_directory in zip(
            available_probes, probe_directories):

        print(probe_name)
        probe_idx += 1

        base_directory = glob(os.path.join(row.local_path, '*' + probe_name +
                              '*_sorted'))[0]
        lfp_directory = glob(os.path.join(base_directory, 'continuous',
                             'Neuropix*100.1'))[0]
        events_directory = glob(os.path.join(base_directory, 'events',
                                'Neuropix*', 'TTL*'))[0]

        # We will only be using PXI moving forward but
        # we will keep this for now for legacy purposes
        if probe_directory.find('PXI') > -1:
            probe_type = 'PXI'
        else:
            probe_type = '3a'

        timestamp_files = []

        timestamp_files.append(
            {
                'name': 'spike_timestamps',
                'input_path': join(probe_directory, 'spike_times.npy'),
                'output_path': join(probe_directory,
                                    'spike_times_master_clock.npy'),
            }
        )

        timestamp_files.append(
            {
                'name': 'lfp_timestamps',
                'input_path': join(lfp_directory, 'lfp_timestamps.npy'),
                'output_path': join(lfp_directory,
                                    'lfp_timestamps_master_clock.npy'),
            }
        )
        dictionary = ''
        input_list = {
            session_id,
            probes,
            probe_idx,
            probe_type,
            probe_directory,
            events_directory,
            timestamp_files,
            spike_amplitudes_index,
            spike_times_index,
            sync_file,
            description,
            nwb_output_path,
            stimulus_table_path
        }
        input_list = runModules(input_list)

    with io.open(output_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(dictionary, ensure_ascii=False, sort_keys=True,
                           indent=4))

    # TODO: Update appropriately
    return dictionary, last_unit_id