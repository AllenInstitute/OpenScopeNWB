import io
import json
from os.path import join, basename
from glob import glob
import numpy as np
import os
import pwd
import pandas as pd
import datetime
import re


def cleanUpNanAndInf(value):
    if np.isnan(value) or np.isinf(value):
        return -1
    else:
        return value


# TODO: Work on parameterJSON info more to work on parsing the relevant modules
# TODO: Make the input for this command shorter by creating an array which contains relevant into
# TODO: Run an parameter JSON parse function to obtain info such as session id
# TODO: Fix linting issues 
# NOTE: This example is based on the “deciphering variability” project example by Josh
# NOTE: This will be refactored as this current code file should be project specific
# NOTE: Each project will have a unique create_input_JSON.py
# TODO: Change return type to return the appropriate dictionary
# NOTE: Will need to rework how the returned dictionaries are assigned to the createEcephys function
def runModules(parameterJSON, probe_directory, probe_name, events_directory, timestamp_files,
               lfp_directory, session_id,probe_info, probes, probe_idx ):
    # This is not being parsed currently
    # Included for demonstration on how functionality will work
    # TODO: Implement a python-based switch case for this
    for module_name in parameterJSON:
        module = module_name
        if module == 'allensdk.brain_observatory.ecephys.align_timestamps':
            try:
                spike_times = np.load(join(probe_directory, 'spike_times.npy'))
            except FileNotFoundError:
                print(' Spikes not found for ' + probe_directory)
            else:

                probe_dict = {
                    'name' : probe_name,
                    'sampling_rate' : 30000.,
                    'lfp_sampling_rate' : 2500.,
                    'barcode_channel_states_path' : join(events_directory, 'channel_states.npy'),
                    'barcode_timestamps_path' : join(events_directory, 'event_timestamps.npy'),
                    'mappable_timestamp_files' : timestamp_files,
                }

                probes.append(probe_dict)
        elif module == 'allensdk.brain_observatory.ecephys.lfp_subsampling':

            probe_dict = {
                'name' : probe_name,
                'lfp_sampling_rate' : 2500.,
                'lfp_input_file_path' : join(lfp_directory, 'continuous.dat'),
                'lfp_timestamps_input_path' : join(lfp_directory, 'lfp_timestamps_master_clock.npy'),
                'lfp_data_path' : join('S:\\DV_NWB\\LFP\\', session_id + '_' + probe_name + '_lfp.dat'),
                'lfp_timestamps_path' : join('S:\\DV_NWB\\LFP\\', session_id + '_' + probe_name + '_timestamps.npy'),
                'lfp_channel_info_path' : join('S:\\DV_NWB\\LFP\\', session_id + '_' + probe_name + '_channels.npy'),
                'surface_channel' : probe_info['surface_channel'],
                'reference_channels' : [191]

            }

            probes.append(probe_dict)


        # NOTE: This is using the file path I used when generating files on my machine
        # NOTE: This will be changed to use a file path specific by the parameter JSON
        # TODO: Specify input path using the parameter JSON
        elif module == 'allensdk.brain_observatory.ecephys.write_nwb':
            try:
                channel_info = pd.read_csv(join(probe_directory, 'ccf_regions.csv'), index_col=0)
            except FileNotFoundError:
                pass
            else:
                lfp_dict = {
                'input_data_path' : join('S:\\DV_NWB\\LFP\\', str(session_id) + '_' + probe_name + '_lfp.dat'),
                'input_timestamps_path' : join('S:\\DV_NWB\\LFP\\', str(session_id) + '_' + probe_name + '_timestamps.npy'),
                'input_channels_path' : join('S:\\DV_NWB\\LFP\\', str(session_id) + '_' + probe_name + '_channels.npy'),
                'output_path' : join('S:\\DV_NWB\\LFP\\', str(session_id) + '_' + probe_name + '.lfp.nwb'),
                }


                channels = []

                for idx, channel_row in channel_info.iterrows():

                    structure_acronym = channel_row['region']
                    #numbers = re.findall(r'\d+', structure_acronym)
                        
                    #if (len(numbers) > 0 and structure_acronym[:2] != 'CA'):
                    #    structure_acronym = structure_acronym.split(numbers[0])[0]
                    #if    cortical_layer = '/'.join(numbers)
                    # else:
                    #     cortical_layer = 'none'

                    channel_dict = {
                        'id' : idx + probe_idx * 1000,
                        'valid_data' : True, #channel_row['is_valid'],
                        'probe_id' : probe_idx,
                        'local_index' : idx,
                        'probe_vertical_position' : -1, #channel_row['vertical_position'],
                        'probe_horizontal_position' : -1, #channel_row['horizontal_position'],
                        'manual_structure_id' : -1,
                        'manual_structure_acronym' : structure_acronym,
                        #'cortical_layer' : cortical_layer,
                        'anterior_posterior_ccf_coordinate' : -1, #channel_row['A/P'],
                        'dorsal_ventral_ccf_coordinate' : -1, #channel_row['D/V'],
                        'left_right_ccf_coordinate' : -1, #channel_row['M/L'],
                        # 'cortical_depth' : channel_row['cortical_depth']
                    }

                    channels.append(channel_dict)

            
                unit_info = pd.read_csv(join(probe_directory, 'metrics.csv'), index_col=0)
                quality_info = pd.read_csv(join(probe_directory, 'cluster_group.tsv.v2'), sep='\t', index_col=0)

                spike_clusters = np.load(join(probe_directory, 'spike_clusters.npy'))

                units = []

                for idx, unit_row in unit_info.iterrows():

                    if quality_info.loc[unit_row.cluster_id].group == 'good':

                        spike_count = np.sum(spike_clusters == unit_row['cluster_id'])

                        unit_dict = {
                            'id' : last_unit_id,
                            'peak_channel_id' : unit_row['peak_channel'] + probe_idx * 1000,
                            'local_index' : idx,
                            'cluster_id' : unit_row['cluster_id'],
                            'quality' : unit_row['quality'],
                            'firing_rate' : cleanUpNanAndInf(unit_row['firing_rate']), 
                            'snr' : cleanUpNanAndInf(unit_row['snr']),
                            'isi_violations' : cleanUpNanAndInf(unit_row['isi_viol']),
                            'presence_ratio' : cleanUpNanAndInf(unit_row['presence_ratio']),
                            'amplitude_cutoff' : cleanUpNanAndInf(unit_row['amplitude_cutoff']),
                            'isolation_distance' : cleanUpNanAndInf(unit_row['isolation_distance']),
                            'l_ratio' : cleanUpNanAndInf(unit_row['l_ratio']),
                            'd_prime' : cleanUpNanAndInf(unit_row['d_prime']),
                            'nn_hit_rate' : cleanUpNanAndInf(unit_row['nn_hit_rate']),
                            'nn_miss_rate' : cleanUpNanAndInf(unit_row['nn_miss_rate']),
                            'max_drift' : cleanUpNanAndInf(unit_row['max_drift']),
                            'cumulative_drift' : cleanUpNanAndInf(unit_row['cumulative_drift']),
                            'silhouette_score' : cleanUpNanAndInf(unit_row['silhouette_score']),
                            'waveform_duration' : cleanUpNanAndInf(unit_row['duration']),
                            'waveform_halfwidth' : cleanUpNanAndInf(unit_row['halfwidth']),
                            'PT_ratio' : cleanUpNanAndInf(unit_row['PT_ratio']),
                            'repolarization_slope' : cleanUpNanAndInf(unit_row['repolarization_slope']),
                            'recovery_slope' : cleanUpNanAndInf(unit_row['recovery_slope']),
                            'amplitude' : cleanUpNanAndInf(unit_row['amplitude']),
                            'spread' : cleanUpNanAndInf(unit_row['spread']),
                            'velocity_above' : cleanUpNanAndInf(unit_row['velocity_above']),
                            'velocity_below' : cleanUpNanAndInf(unit_row['velocity_below'])
                        }

                        spike_times_index += spike_count
                        spike_amplitudes_index += spike_count

                        units.append(unit_dict)
                        
                        last_unit_id += 1

                probe_dict = {
                    'id' : probe_idx,
                    'name' : probe_name,
                    'spike_times_path' : join(probe_directory, 'spike_times_master_clock.npy'),
                    'spike_clusters_file' : join(probe_directory, 'spike_clusters.npy'),
                    'spike_amplitudes_path' : join(probe_directory, 'amplitudes.npy'),
                    'mean_waveforms_path' : join(probe_directory, 'mean_waveforms.npy'),
                    'spike_templates_path' : join(probe_directory, 'spike_templates.npy'),
                    'templates_path' : join(probe_directory, 'templates.npy'),
                    'inverse_whitening_matrix_path' : join(probe_directory, 'whitening_mat_inv.npy'),
                    'channels' : channels,
                    'units' : units,
                    'lfp' : None #lfp_dict
                }

                probes.append(probe_dict)


    if module == 'allensdk.brain_observatory.ecephys.align_timestamps':

        dictionary = \
        {
            'sync_h5_path' : glob(join(directory, '*.sync'))[0],
            "probes" : probes,
        }

    elif module == 'allensdk.brain_observatory.ecephys.stimulus_table':

        if False:
            trim_discontiguous_frame_times = True
        else:
            trim_discontiguous_frame_times = False

        dictionary = \
        {

            'stimulus_pkl_path' : glob(join(directory, '*.stim.pkl'))[0],
            'sync_h5_path' : glob(join(directory, '*.sync'))[0],
            'output_stimulus_table_path' : os.path.join(directory, 'stim_table_allensdk.csv'),
            'output_frame_times_path' : os.path.join(directory, 'frame_times.npy'),
            'trim_discontiguous_frame_times' : trim_discontiguous_frame_times,

            "log_level" : 'INFO'
        }

    elif module == 'allensdk.brain_observatory.extract_running_speed':

        if False:
            trim_discontiguous_frame_times = True
        else:
            trim_discontiguous_frame_times = False

        dictionary = \
        {
            'stimulus_pkl_path' : glob(join(directory, '*.stim.pkl'))[0],
            'sync_h5_path' : glob(join(directory, '*.sync'))[0],

            'output_path' : join(directory, 'running_speed.h5'),
            'trim_discontiguous_frame_times' : trim_discontiguous_frame_times,

            "log_level" : 'INFO'
        }

    elif module == 'allensdk.brain_observatory.ecephys.lfp_subsampling':

        dictionary = \
        {
            'lfp_subsampling' : {'temporal_subsampling_factor' : 2,},
            "probes" : probes,
        }

    elif module == 'allensdk.brain_observatory.ecephys.optotagging_table':

        dictionary = \
        {
            'opto_pickle_path' : glob(join(directory, '*.opto.pkl'))[0],
            'sync_h5_path' : glob(join(directory, '*.sync'))[0],
            'output_opto_table_path' : join(directory, 'optotagging_table.csv')
        }

    elif module == 'allensdk.brain_observatory.ecephys.write_nwb':

        #session_string = os.path.basename(sync_file)
        YYYY = 2021 #int(session_string[17:21])
        MM = 6 #int(session_string[21:23])
        DD = 16 #int(session_string[23:25])

        dictionary = \
        {
            'invalid_epochs' : [{'id' : 0,
                                'type' : 'none',
                                'label' : 'LABEL',
                                'start_time' : 0.0,
                                'end_time' : 0.0}, ],
            "log_level" : 'INFO',
            "output_path" : nwb_output_path,
            "session_id" : int(session_id),
            "session_start_time" : datetime.datetime(YYYY, MM, DD, 0, 0, 0).isoformat(),
            "stimulus_table_path" : os.path.join(directory, 'stim_table_allensdk.csv'),
            "probes" : probes,
            "session_sync_path" : sync_file,
            "running_speed_path" : join(directory, 'running_speed.h5')#,
            # "optotagging_table_path" : join(directory, 'optotagging_table.csv')
        }




# TODO: Implement better log in method(?)
# TODO: Fix some formatting for Linting
# NOTE: Ths goal is to have this function be as general as possible and handle
# NOTE: Changes in the runModules function specifically
def createEcephys(output_directory, row, intputJSON, output_file, last_unit_id,
                  probe_list):

    session_id = str(row.session_id)

    userID = '???'
    description = 'Neuropixels experiment in visual cortex'

    sync_file = glob(join(row.local_path, '*.sync'))[0]

    nwb_output_path = join(output_directory, 'mouse' + str(row['name']) +
                           '.spikes.nwb')

    stimulus_table_path = join(row.local_path, 'stim_table.csv')

    probe_directories = []
    available_probes = []
    for probe in probe_list:
        if type(row[probe]) == str:

            probe_directories.append(row[probe])
            available_probes.append(probe)

    # Printing out possible directories for testing purposes
    print(probe_directories)
    print(available_probes)
    probes = []
    probe_idx = -1
    spike_times_index = 0
    spike_amplitudes_index = 0

    for probe_name, probe_directory in zip(available_probes, probe_directories):

        print(probe_name)
        probe_idx += 1

        base_directory = glob(os.path.join(row.local_path, '*' + probe_name +
                              '*_sorted'))[0]
        lfp_directory = glob(os.path.join(base_directory, 'continuous',
                             'Neuropix*100.1'))[0]
        events_directory = glob(os.path.join(base_directory, 'events',
                                'Neuropix*', 'TTL*'))[0]

        # We will only be using PXI moving forward but
        # I will keep this for now for legacy purposes
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
        dictionary = runModules(intputJSON)

    with io.open(output_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(dictionary, ensure_ascii=False, sort_keys=True,
                           indent=4))

    return dictionary, last_unit_id
