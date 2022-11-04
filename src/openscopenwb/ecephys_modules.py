import datetime
import pandas as pd
import numpy as np
import re
import os
import json
import logging
import pickle
from openscopenwb.utils import clean_up_functions as cuf
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import allen_functions as allen

from os.path import join
from glob import glob
from datetime import datetime


logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG,
                    filemode='a')


def stimulus_table(module_params):
    """Returns the dict for the stimulus path

    Parameters
    ----------
    module_params: dict
    Session or probe unique information, used by each module

    Returns
    -------
    module_params: dict
    Session or probe unique information, used by each module
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """
    # trim_discontiguous_frame_times = module_params['trim']
    output_directory = module_params['output_path']
    try:
        pkl_path = glob(join(module_params['base_directory'],
                             "*.stim.pkl"))[0]
    except IndexError:
        pkl_path = glob(join(module_params['base_directory'],
                             "**",
                             "*.stim.pkl"))[0]
    try:
        sync_path = glob(join(module_params['base_directory'],
                              "*.sync"))[0]
    except IndexError:
        sync_path = glob(join(module_params['base_directory'],
                              "**",
                              "*.sync"))[0]

    input_json_write_dict = \
        {
            'stimulus_pkl_path': pkl_path,
            'sync_h5_path': sync_path,
            'output_stimulus_table_path':
                os.path.join(output_directory,
                             "stim_table_allensdk.csv"),
            'output_frame_times_path':
                os.path.join(output_directory,
                             "frame_times.npy"),
            # 'trim_discontiguous_frame_times': trim_discontiguous_frame_times,
            "log_level": 'INFO'
        }
    return module_params, input_json_write_dict


def ecephys_gaze_mapping(module_params):
    """Returns the dict for the Gaze json

    Parameters
    ----------
    module_params: dict
    Session or probe unique information, used by each module

    Returns
    -------
    module_params: dict
    Session or probe unique information, used by each module
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """
    try:
        elipse_path = glob(join(module_params['base_directory'], 'eye_tracking',
                                     '*_ellipse.h5'))[0]
    except IndexError:
        elipse_path = glob(join(module_params['base_directory'], 
                                     '**', 'eye_tracking','*_ellipse.h5'))[0] 
    try:
        platform_path = glob(join(module_params['base_directory'], '*',
                                     '*_platformD1.json'))[0]
    except IndexError:
        platform_path = glob(join(module_params['base_directory'], '**',
                                     '*_platformD1.json'))[0]
    try:
        eye_path = glob(join(module_params['base_directory'], '*',
                                     '*.eye.mp4'))[0]
    except IndexError:
        eye_path = glob(join(module_params['base_directory'], '**',
                                     '*.eye.mp4'))[0]
    param_file = open(platform_path)
    platform_dict = json.load(param_file)
    param_file.close()
    eye_info = platform_dict['HardwareConfiguration']['eye_camera_position']
    led_info = platform_dict['HardwareConfiguration']['eye_led_position']
    monitor_info = platform_dict['HardwareConfiguration']['screen_position']
    equipment = "Allen Institute OpenScope Rig"
    date = platform_dict['ProbeInsertionCompleteTime']

    input_json_write_dict = \
    {
        'session_sync_file': module_params['sync_path'],
        'input_file': elipse_path,
        'output_file': module_params['output_path'] + 'gaze.h5',
        'monitor_position_x_mm': monitor_info['center_x_mm'],
        'monitor_position_y_mm': monitor_info['center_y_mm'],
        'monitor_position_z_mm': monitor_info['center_z_mm'],
        'monitor_rotation_x_deg': monitor_info['rotation_x_deg'],
        'monitor_rotation_y_deg': monitor_info['rotation_y_deg'],
        'monitor_rotation_z_deg': monitor_info['rotation_z_deg'],
        'camera_rotation_x_deg': eye_info['rotation_x_deg'],
        'camera_rotation_y_deg': eye_info['rotation_y_deg'],
        'camera_rotation_z_deg': eye_info['rotation_z_deg'],
        'camera_position_x_mm': eye_info['center_x_mm'],
        'camera_position_y_mm': eye_info['center_y_mm'],
        'camera_position_z_mm': eye_info['center_z_mm'],
        'led_position_x_mm': led_info['center_x_mm'],
        'led_position_y_mm': led_info['center_y_mm'],
        'led_position_z_mm': led_info['center_z_mm'],
        'equipment': equipment,
        'date_of_acquisition': date,
        'eye_video_file': eye_path
    }
    return module_params, input_json_write_dict



def ecephys_align_timestamps(module_params):
    """Returns the dict for the timestamps json

    Parameters
    ----------
    module_params: dict
    Session or probe unique information, used by each module

    Returns
    -------
    module_params: dict
    Session or probe unique information, used by each module
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """
    file_in_base_folder = False
    probe_idx = module_params['current_probe']
    print(module_params['base_directory'])
    print(probe_idx)
    print(glob(os.path.join(
        module_params['base_directory'], '*' + probe_idx + '*_sorted')))
    base_directory = glob(os.path.join(
        module_params['base_directory'], '*' + probe_idx + '*_sorted'))
    queue_directory = []
    if base_directory != []:
        base_directory = base_directory[0]
        events_directory = glob(os.path.join(
            base_directory, 'events', 'Neuropix*', 'TTL*'))[0]
        probe_directory = glob(os.path.join(
            base_directory, 'continuous', 'Neuropix*'))[0]
        queue_directory = glob(os.path.join(
            base_directory, 'EUR_QUEUE*', 'continuous', 'Neuropix*'))
        file_in_base_folder = True

    alt_probe_directory = glob(join(module_params['base_directory'],
                                    "**", '*'+ probe_idx,
                                    'continuous',
                                    'Neuropix*'))
    print(alt_probe_directory)
    test_probe_directory = glob(join(module_params['base_directory'],
                                    "**", '*'+ probe_idx))
    print(test_probe_directory)
    if alt_probe_directory != []:
        alt_probe_directory = alt_probe_directory[0]

    if queue_directory != []:
        queue_directory = queue_directory[0]

    output_directory = module_params['output_path']
    spike_directory = ""
    if file_in_base_folder:
        logging.debug("Current directory is: " + probe_directory)
    timestamp_files = []

    file_found = False
    file_in_probe_folder = False
    file_in_parent_folder = False
    file_in_queue_folder = False
    if file_in_base_folder:
        try:
            np.load(join(probe_directory, 'spike_times.npy'))
            file_found = True
            file_in_probe_folder = True
        except FileNotFoundError:
            logging.debug(' Spikes not found for ' + probe_directory)
            file_found = False
            file_in_probe_folder = False

    if alt_probe_directory != []:
        try:
            print(alt_probe_directory)
            print(glob(join(alt_probe_directory, "spike_times.npy")))
            np.load(glob(join(module_params['base_directory'],
                                    "**", '*'+ probe_idx,
                                    'continuous',
                                    'Neuropix*',
                                    'spike_times.npy'))[0])
            spike_directory = glob(join(module_params['base_directory'],
                                    "**", '*'+ probe_idx,
                                    'continuous',
                                    'Neuropix*',
                                    'spike_times.npy'))[0]
#            np.load(glob(join(alt_probe_directory,
#                    "spike_times.npy"))[0])
#            spike_directory = glob(join(
 #                                  alt_probe_directory,
#                                   "spike_times.npy"))[0]
            print(alt_probe_directory)
            print(spike_directory)
            try:
                events_directory = glob(join(module_params['base_directory'],
                                        '*', "*" + probe_idx, 'events',
                                             'Neuropix*', 'TTL*'))[0]
            except IndexError:
                events_directory = glob(os.path.join(
                                   base_directory, 'events', 'Neuropix*',
                                   'TTL*'))[0]
            print(events_directory)
            file_found = True
            file_in_parent_folder = True

        except FileNotFoundError:
            logging.debug(' Spikes not found for ' +
                          join(module_params['base_directory'],
                               module_params['session_id'] +
                               "_" +
                               probe_idx +
                               "_aligned_" +
                               "spike_times.npy"))
            file_found = False
            file_in_parent_folder = False

    if(queue_directory != []) and not file_in_parent_folder:
        try:
            np.load(join(queue_directory, 'spike_times.npy'))
            alt_spike_directory = glob(join(queue_directory,
                                            "spike_times.npy"))[0]
            file_found = True
            file_in_queue_folder = True

        except FileNotFoundError:
            logging.debug(' Spikes not found for ' + queue_directory)
            file_found = False
            file_in_queue_folder = False

    if(file_in_probe_folder):
        timestamp_files.append({
            'name': 'spike_timestamps',
            'input_path': join(probe_directory,     'spike_times.npy'),
            'output_path': join(output_directory, probe_idx,
                                'spike_times_master_clock.npy')
        })

    elif(file_in_parent_folder):
        timestamp_files.append({
            'name': 'spike_timestamps',
            'input_path': spike_directory,
            'output_path': join(output_directory, probe_idx,
                                'spike_times_master_clock.npy')
        })

    elif(file_in_queue_folder):
        timestamp_files.append({
            'name': 'spike_timestamps',
            'input_path': alt_spike_directory,
            'output_path': join(output_directory, probe_idx,
                                'spike_times_master_clock.npy')
        })
    try:
        lfp_directory = glob(join(module_params['base_directory'],
                                           '*',
                                           '*_' +
                                           probe_idx,
                                           'continuous'
                                           "Neuropix*100.1"))[0]
    except IndexError:
        lfp_directory = glob(join(module_params['base_directory'], 
                                           "**",
                                           "*_" +
                                           probe_idx,
                                           'continuous',
                                           '**'
                                           "Neuropix*100.1"))[0]

    timestamp_files.append({
        'name': 'lfp_timestamps',
        'input_path': join(lfp_directory, 'lfp_timestamps.npy'),
        'output_path': join(module_params['output_path'], probe_idx + '_lfp_timestamps.npy')
    })
    print("File was found: " + str(file_found))
    if(file_found):
        probe_dict = {
            'name': probe_idx,
            'sampling_rate': 30000.,
            'lfp_sampling_rate': 2500.,
            'barcode_channel_states_path': join(events_directory,
                                                'channel_states.npy'),
            'barcode_timestamps_path': join(
                events_directory,
                'event_timestamps.npy'),
            'mappable_timestamp_files': timestamp_files
        }

        module_params['probe_dict_list'].append(probe_dict)
        if probe_idx != module_params['final_probe']:
            print(module_params, probe_dict)
            return module_params, probe_dict
        else:
            print(module_params['base_directory'])
            print(glob(join(
                    module_params['base_directory'], '**',
                    '*.sync')))
            print(glob(join(
                    module_params['base_directory'], '*',
                    '*.sync')))
            print(glob(join(
                    module_params['base_directory'],
                    '*.sync')))

            try:
                sync_path = glob(join(
                    module_params['base_directory'],
                    '*.sync'))[0]
            except IndexError:
                sync_path = glob(join(
                    module_params['base_directory'], '**',
                    '*.sync'))[0]
            input_json_write_dict = {
                'sync_h5_path': sync_path,
                "probes": module_params['probe_dict_list']
            }
            module_params['sync_path'] = sync_path
            module_params['probe_dict_list'] = []
            print(module_params, input_json_write_dict)
            return module_params, input_json_write_dict


def ecephys_write_nwb(module_params):
    """Writes the input json for the nwb modules

    Parameters
    ----------
    module_params: dict
    Session or probe unique information, used by each module

    Returns
    -------
    module_params: dict
    Session or probe unique information, used by each module
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """
    probes = []
    probe_idx = module_params['current_probe']
    probe_id = module_params['probes'].index(probe_idx)
    probe_directory = ''
    base_directory = glob(os.path.join(
            module_params['base_directory'], '*' + probe_idx + '*_sorted'))
    if base_directory != []:
        base_directory = base_directory[0]
        probe_directory = glob(os.path.join(base_directory,
                                            'continuous',
                                            'Neuropix*'))[0]
    alt_probe_directory = glob(join(module_params['base_directory'],
                                    '*', "*" + probe_idx,
                                    'continuous',
                                    'Neuropix*'))
    if alt_probe_directory != []:
        alt_probe_directory = alt_probe_directory[0]
    output_directory = module_params['output_path']
    channel_in_parent = True
    channel_in_child = False
    channel_in_queue = False
    need_placeholder = False
    search_child = False
    search_queue = False
    region = ''
    master_clock_path = ''

    try:
        channel_info = pd.read_csv(join(probe_directory,
                                        'ccf_regions.csv'),
                                   index_col=0)
    except FileNotFoundError:
        channel_in_parent = False
        search_child = True
        pass

    if search_child:
        child_neuropix = glob(join(module_params['base_directory'],
                                   '*', "*" + probe_idx,
                                   'continuous',
                                   'Neuropix*',
                                   "ccf_regions.csv"))
        if child_neuropix != []:
            try:
                channel_info = pd.read_csv(glob(join(
                                           module_params['base_directory'],
                                           '*', "*" + probe_idx,
                                           'continuous',
                                           'Neuropix*',
                                           "ccf_regions.csv"))[0])
                channel_in_child = True

            except FileNotFoundError:
                channel_in_child = False
    if channel_in_child is False and channel_in_parent is False:
        search_queue = True

    if search_queue:
        if base_directory == []:
            base_directory = glob(os.path.join(
                            module_params['base_directory'], '*', '*' +
                            probe_idx + '*_sorted'))
        if base_directory != []:
            base_directory = base_directory[0]
        if base_directory == []:
            queue_neuropix = []
            skip_queue = True
        if not skip_queue:
            queue_neuropix = glob(os.path.join(
                              base_directory, 'EUR_QUEUE*',
                              'continuous', 'Neuropix*',
                              "ccf_regions.csv"))
        if queue_neuropix != []:
            try:
                channel_info = pd.read_csv(queue_neuropix[0])
                channel_in_queue = True
            except FileNotFoundError:
                channel_in_queue = False
                pass
    if not channel_in_child and not channel_in_parent and not channel_in_queue:
        need_placeholder = True
        base_directory = "/allen/programs/mindscope/workgroups/openscope/" + \
                         "openscopedata2022/placeholdercsvs"
        neuropix = glob(os.path.join(
                        base_directory, "ccf_regions.csv"))
        channel_info = pd.read_csv(neuropix[0])

    if channel_in_parent:
        probe_directory = probe_directory
        region = 'region'
        channels = []
        master_clock_path = join(output_directory, probe_idx,
                                 'spike_times_master_clock.npy')
    elif channel_in_child:
        probe_directory = glob(join(module_params['base_directory'],
                                    '*', "*" + probe_idx,
                                    'continuous',
                                    'Neuropix*',))[0]
        region = 'structure_acronym'
        channels = []
        master_clock_path = join(output_directory, probe_idx,
                                 'spike_times_master_clock.npy')
    elif channel_in_queue:
        probe_directory = glob(os.path.join(
                              base_directory, 'EUR_QUEUE*',
                              'continuous', 'Neuropix*'))[0]
        region = 'structure_acronym'
        channels = []
        master_clock_path = join(output_directory, probe_idx,
                                 'spike_times_master_clock.npy')

    elif need_placeholder:
        probe_directory = glob(os.path.join(
                           module_params['base_directory'], "**", "*" +
                           probe_idx, 'continuous',
                           'Neuropix*',
                          ))[0]
        region = 'region'
        channels = []
        master_clock_path = join(output_directory, probe_idx,
                                 'spike_times_master_clock.npy')
    try:
        elipse_path = glob(join(module_params['base_directory'], 'eye_tracking',
                                     '*_ellipse.h5'))[0]
    except IndexError:
        elipse_path = glob(join(module_params['base_directory'], 
                                     '**', 'eye_tracking','*_ellipse.h5'))[0] 
    module_params['ellipse_path'] = elipse_path
    for idx, channel_row in channel_info.iterrows():
        structure_acronym = channel_row[region]
        #numbers = re.findall(r'\d+', structure_acronym)
        logging.debug(channel_row)


        #if (len(numbers) > 0):
        #    structure_acronym = structure_acronym.split(numbers[0])[0]

        channel_dict = {
            'id': idx + probe_id * 1000,
            'valid_data': True,
            'probe_id': probe_id,
            'local_index': idx,
            'probe_vertical_position': channel_row['vertical_position'],
            'probe_horizontal_position': channel_row['horizontal_position'],
            'manual_structure_id': channel_row['structure_id'],
            'manual_structure_acronym': structure_acronym,
            'anterior_posterior_ccf_coordinate': channel_row['A/P'] * 1000,
            'dorsal_ventral_ccf_coordinate': channel_row['D/V'] * 1000 ,
            'left_right_ccf_coordinate': channel_row['M/L'] * 1000
        }
        channels.append(channel_dict)
    metrics = glob(join(module_params['base_directory'],
                                    "**/*", 
                                    'metrics.csv'), recursive=True)
    for probe in metrics:
        if probe_idx in probe:
            current_metric = probe
    print('current-metric')
    print(current_metric)
    unit_info =   pd.read_csv(current_metric, index_col=0)

#    unit_info = pd.read_csv(join(probe_directory,
#                                 'metrics.csv'),
#                            index_col=0)

    quality_check = glob(join(module_params['base_directory'],
                                    "**", 
                                    'cluster_group.tsv'), recursive=True)
    tmp_index = 0
    if quality_check != []:
        for index, quality in enumerate(quality_info):
            if probe_idx in quality:
                tmp_index = index
        quality_info = pd.read_csv(join(quality_check[index],
                                   sep='\t',
                                   index_col=0))
    else:
        quality_info = []
    spike_clusters = glob(join(module_params['base_directory'],
                                    "**", 
                                    'spike_clusters.npy'), recursive=True)
    for index, cluster in enumerate(spike_clusters):
        if probe_idx in cluster:
            tmp_index = index
    spike_clusters = np.load(spike_clusters[tmp_index])


    units = []
    spike_times_index = 0
    spike_amplitudes_index = 0
    unit_keys = [
        'peak_channel',
        'cluster_id',
        'quality',
        'firing_rate',
        'snr',
        'isi_viol',
        'presence_ratio',
        'amplitude_cutoff',
        'isolation_distance',
        'l_ratio',
        'd_prime',
        'nn_hit_rate',
        'nn_miss_rate',
        'max_drift',
        'cumulative_drift',
        'silhouette_score',
        'duration',
        'halfwidth',
        'PT_ratio',
        'repolarization_slope',
        'recovery_slope',
        'amplitude',
        'spread',
        'velocity_above',
        'velocity_below'
    ]
    j = -1
    for i in unit_keys:
        j += 1
        move_on = False
        try:
            unit_info[i]
        except Exception:
            if i == 'peak_channel':
                try:
                    unit_info['peak_chan']
                except Exception:
                    pass
                else:
                    unit_info.rename(columns={'peak_chan':
                                              'peak_channel'}, inplace=True)
                    move_on = True
            if i == 'cluster_id':
                try:
                    unit_info['cluster_ids']
                except Exception:
                    pass
                else:
                    unit_info.rename(columns={'cluster_ids':
                                              'cluster_id'}, inplace=True)
                    move_on = True
            if i == 'quality':
                try:
                    unit_info['unit_quality']
                except Exception:
                    pass
                else:
                    unit_info.rename(columns={'unit_quality':
                                              'quality'}, inplace=True)
                    move_on = True
            if not move_on:
                row_count = unit_info.shape[0]
                i_list = []
                logging.debug("Adding a placeholder value for : " + i)
                for x in range(row_count):
                    i_list.append(-1)
                unit_info.insert(loc=j, column=i, value=i_list)
                unit_info[i] = i_list
    for idx, unit_row in unit_info.iterrows():
        if quality_info == []:

            spike_count = np.sum(spike_clusters ==
                                 unit_row['cluster_id'])

            unit_dict = {
                'id': module_params['last_unit_id'],
                'peak_channel_id': unit_row['peak_channel'] +
                probe_id * 1000,
                'local_index': idx,
                'cluster_id': unit_row['cluster_id'],
                'quality': unit_row['quality'],
                'firing_rate': cuf.clean_up_nan_and_inf(
                                unit_row['firing_rate']),
                'snr': cuf.clean_up_nan_and_inf(unit_row['snr']),
                'isi_violations': cuf.clean_up_nan_and_inf(
                                    unit_row['isi_viol']),
                'presence_ratio': cuf.clean_up_nan_and_inf(
                                    unit_row['presence_ratio']),
                'amplitude_cutoff': cuf.clean_up_nan_and_inf(
                                    unit_row['amplitude_cutoff']),
                'isolation_distance': cuf.clean_up_nan_and_inf(
                                        unit_row['isolation_distance']),
                'l_ratio': cuf.clean_up_nan_and_inf(
                            unit_row['l_ratio']),
                'd_prime': cuf.clean_up_nan_and_inf(
                            unit_row['d_prime']),
                'nn_hit_rate': cuf.clean_up_nan_and_inf(
                                unit_row['nn_hit_rate']),
                'nn_miss_rate': cuf.clean_up_nan_and_inf(
                                unit_row['nn_miss_rate']),
                'max_drift': cuf.clean_up_nan_and_inf(
                                unit_row['max_drift']),
                'cumulative_drift': cuf.clean_up_nan_and_inf(
                                    unit_row['cumulative_drift']),
                'silhouette_score': cuf.clean_up_nan_and_inf(
                                    unit_row['silhouette_score']),
                'waveform_duration': cuf.clean_up_nan_and_inf(
                                        unit_row['duration']),
                'waveform_halfwidth': cuf.clean_up_nan_and_inf(
                                        unit_row['halfwidth']),
                'PT_ratio': cuf.clean_up_nan_and_inf(
                                unit_row['PT_ratio']),
                'repolarization_slope': cuf.clean_up_nan_and_inf(
                                        unit_row['repolarization_slope']),
                'recovery_slope': cuf.clean_up_nan_and_inf(
                                    unit_row['recovery_slope']),
                'amplitude': cuf.clean_up_nan_and_inf(
                                unit_row['amplitude']),
                'spread': cuf.clean_up_nan_and_inf(
                            unit_row['spread']),
                'velocity_above': cuf.clean_up_nan_and_inf(
                                    unit_row['velocity_above']),
                'velocity_below': cuf.clean_up_nan_and_inf(
                                    unit_row['velocity_below'])
            }
            spike_times_index += spike_count
            spike_amplitudes_index += spike_count

            units.append(unit_dict)
            module_params['last_unit_id'] += 1
        else:
            if quality_info.loc[unit_row.cluster_id].group == 'good':
                spike_count = np.sum(spike_clusters ==
                                     unit_row['cluster_id'])

                unit_dict = {
                    'id': module_params['last_unit_id'],
                    'peak_channel_id': unit_row['peak_channel'] +
                    probe_id * 1000,
                    'local_index': idx,
                    'cluster_id': unit_row['cluster_id'],
                    'quality': unit_row['quality'],
                    'firing_rate': cuf.clean_up_nan_and_inf(
                                    unit_row['firing_rate']),
                    'snr': cuf.clean_up_nan_and_inf(unit_row['snr']),
                    'isi_violations': cuf.clean_up_nan_and_inf(
                                        unit_row['isi_viol']),
                    'presence_ratio': cuf.clean_up_nan_and_inf(
                                        unit_row['presence_ratio']),
                    'amplitude_cutoff': cuf.clean_up_nan_and_inf(
                                        unit_row['amplitude_cutoff']),
                    'isolation_distance': cuf.clean_up_nan_and_inf(
                                            unit_row['isolation_distance']),
                    'l_ratio': cuf.clean_up_nan_and_inf(
                                unit_row['l_ratio']),
                    'd_prime': cuf.clean_up_nan_and_inf(
                                unit_row['d_prime']),
                    'nn_hit_rate': cuf.clean_up_nan_and_inf(
                                    unit_row['nn_hit_rate']),
                    'nn_miss_rate': cuf.clean_up_nan_and_inf(
                                    unit_row['nn_miss_rate']),
                    'max_drift': cuf.clean_up_nan_and_inf(
                                    unit_row['max_drift']),
                    'cumulative_drift': cuf.clean_up_nan_and_inf(
                                        unit_row['cumulative_drift']),
                    'silhouette_score': cuf.clean_up_nan_and_inf(
                                        unit_row['silhouette_score']),
                    'waveform_duration': cuf.clean_up_nan_and_inf(
                                            unit_row['duration']),
                    'waveform_halfwidth': cuf.clean_up_nan_and_inf(
                                            unit_row['halfwidth']),
                    'PT_ratio': cuf.clean_up_nan_and_inf(
                                    unit_row['PT_ratio']),
                    'repolarization_slope': cuf.clean_up_nan_and_inf(
                                            unit_row['repolarization_slope']),
                    'recovery_slope': cuf.clean_up_nan_and_inf(
                                        unit_row['recovery_slope']),
                    'amplitude': cuf.clean_up_nan_and_inf(
                                    unit_row['amplitude']),
                    'spread': cuf.clean_up_nan_and_inf(
                                unit_row['spread']),
                    'velocity_above': cuf.clean_up_nan_and_inf(
                                        unit_row['velocity_above']),
                    'velocity_below': cuf.clean_up_nan_and_inf(
                                        unit_row['velocity_below'])
                }
                spike_times_index += spike_count
                spike_amplitudes_index += spike_count

                units.append(unit_dict)
                module_params['last_unit_id'] += 1
    lfp_directory = module_params['lfp_path']
    output = module_params['nwb_path'].replace('spike_times.nwb', '')
    lfp_dict = {
        'input_data_path': join(module_params['output_path'], probe_idx+ '_lfp.dat'),
        'input_timestamps_path': join(module_params['output_path'],  probe_idx +'_timestamps.npy'),
        'input_channels_path': join(module_params['output_path'], probe_idx +'_channels.npy'),
        'output_path': join(output, probe_idx + '_lfp.nwb')
    }
    print(glob(join(module_params['base_directory'], '**/*', 'spike_clusters.npy'), recursive=True))
    spike_clusters = glob(join(module_params['base_directory'], '**/*', 'spike_clusters.npy'), recursive=True)
    spike_amplitudes = glob(join(module_params['base_directory'], '**/*', 'amplitudes.npy'), recursive=True)
    mean_waveforms = glob(join(module_params['base_directory'], '**/*','mean_waveforms.npy'), recursive=True)
    spike_templates =  glob(join(module_params['base_directory'], '**/*',
                                     'spike_templates.npy'), recursive=True)
    templates_path =  glob(join(module_params['base_directory'], '**/*','templates.npy'), recursive=True)
    inverse_whitening = glob(join(module_params['base_directory'], '**',
                                              'whitening_mat_inv.npy'), recursive=True)
    spike_info = {
        'spike_clusters': spike_clusters, 
        'spike_amplitudes': spike_amplitudes, 
        'mean_waveforms': mean_waveforms, 
        'spike_templates': spike_templates, 
        'templates_path': templates_path, 
        'whitening': inverse_whitening}
    for info in spike_info:
        for probe in spike_info[info]:
            if probe_idx in probe:
                tmp = probe
                spike_info[info] = tmp 
                break
    probe_dict = {
        'id': module_params['id'],
        'name': probe_idx,
        'spike_times_path': master_clock_path,
        'spike_clusters_file': spike_info['spike_clusters'],
        'spike_amplitudes_path': spike_info['spike_amplitudes'],
        'mean_waveforms_path': spike_info['mean_waveforms'],
        'spike_templates_path': spike_info['spike_templates'],
        'templates_path': spike_info['templates_path'],
        'inverse_whitening_matrix_path': spike_info['whitening'],
        'channels': channels,
        'units': units,
        'lfp': lfp_dict
    }
    module_params['probe_dict_list'].append(probe_dict)
    input_json_write_dict = probe_dict
    new_date = False
    session_id = module_params['session_id']
    nwb_path = module_params['nwb_path']
    subject_info = allen.lims_subject_info(session_id)
    if probe_idx == module_params['first_probe']:
        fb.start(fb.get_creds())
    session_date = fb.view_session(module_params['project'], session_id)
    session_date = session_date['date']
    session_date = datetime.strptime(session_date[:10], '%Y-%m-%d')
    subject_dob = datetime.strptime(subject_info['dob'][:10],'%Y-%m-%d' )
    duration = session_date - subject_dob
    duration = duration.total_seconds()
    duration = divmod(duration, 86400)
    days = (duration[0])
    subject = {
        'age_in_days': days,
        'specimen_name': subject_info['name'],
        'full_genotype': subject_info['genotype'],
        'sex': subject_info['gender'],
        'strain': "Transgenic",
        'stimulus_name': module_params['project'],
        'species': 'Mus musculus',
        'donor_id': subject_info['id']
    }
    if probe_idx != module_params['final_probe']:
        return module_params, input_json_write_dict
    else:
        sync_file = glob(
            join(module_params['base_directory'], '*.sync'))
        if sync_file != []:
            sync_file = sync_file[0]
        else:
            sync_file = glob(
                        join(module_params['base_directory'], "**",
                             '*.sync'))[0]
            new_date = True
        sync_string = os.path.basename(sync_file)
        try:
            data_json = glob(join(module_params['base_directory'], "*",
                             '*.behavior.json'))[0]
        except IndexError:
            data_json = glob(join(module_params['base_directory'], "**",
                             '*.behavior.json'))[0]
        module_params['data_json'] = data_json
        if not new_date:
            YYYY = int(sync_string[17:21])
            MM = int(sync_string[21:23])
            DD = int(sync_string[23:25])
        elif new_date:
            YYYY = int(sync_string[18:22])
            MM = int(sync_string[22:24])
            DD = int(sync_string[24:26])
        probes = module_params['probe_dict_list']

        input_json_write_dict = \
            {
                'invalid_epochs': [{'id': 0,
                                    'type': 'none',
                                    'label': 'LABEL',
                                    'start_time': 0.0,
                                    'end_time': 0.0}, ],
                "log_level": 'INFO',
                "output_path": module_params['nwb_path'],
                "session_id": module_params['session_id'],
                "session_start_time": datetime(
                                    YYYY, MM, DD,
                                    0, 0, 0).isoformat(),
                "stimulus_table_path": os.path.join(
                                    output_directory,
                                    'stim_table_allensdk.csv'),
                "optotagging_table_path": os.path.join(
                                    output_directory,
                                    'optotagging_table.csv'),
                "session_metadata": subject,
                "probes": probes,
                "session_sync_path": sync_file,
                "running_speed_path": join(output_directory,
                                           'running_speed.h5')
            }

    return module_params, input_json_write_dict


def ecephys_optotagging_table(module_params):
    """ Writes the relevant optotagging information to the input json

    Parameters
    ----------
    module_params: dict
    Session or probe unique information, used by each module

    Returns
    -------
    module_params: dict
    Session or probe unique information, used by each module
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """
    if module_params['project'] == 'OpenScopeGlobalLocalOddball':
        print("GLO")
        conditions = {
            "0": {
                "duration": 1.0,
                "name": "fast_pulses",
                "condition": "2.5 ms pulses at 10 Hz"
            },
            "1": {
                "duration": 0.005,
                "name": "pulse",
                "condition": "a single square pulse"
            },
            "2": {
                "duration": 0.01,
                "name": "pulse",
                "condition": "a single square pulse"
            },
            "3": {
                "duration": 1.0,
                "name": "raised_cosine",
                "condition": "half-period of a cosine wave"
            },
            "4": {
                "duration": 1.0,
                "name": "5 hz pulse train",
                "condition": "Each pulse is 10 ms wide"
            }, 
            "5": {
                "duration": 1.0,
                "name": "40 hz pulse train",
                "condition": "Each pulse is 6 ms wide"        
            }
        } 
    elif module_params['project'] == 'OpenScopeIllusion':
        conditions = {
            "0": {
                "duration": 1,
                "name": "fast_pulses",
                "condition": "2 ms pulses at 1 Hz"
            },
            "1": {
                "duration": 1,
                "name": "pulse",
                "condition": "a single 10ms pulse"
            },
            "2": {
                "duration": .2,
                "name": "pulse",
                "condition": "1 second of 5Hz pulse train. Each pulse is 2 ms wide"
            },
            "3": {
                "duration": .1,
                "name": "raised_cosine",
                "condition": "half-period of a cosine wave"
            },
            "4": {
                "duration": .05,
                "name": "5 hz pulse train",
                "condition": "Each pulse is 10 ms wide"
            }, 
            "5": {
                "duration": .033,
                "name": "40 hz pulse train",
                "condition": "Each pulse is 6 ms wide"        
            },
            "6": {
                "duration": .025,
                "name": "fast_pulses",
                "condition": "1 second of 40 Hz pulse train. Each pulse is 2 ms wide"
            },
            "7": {
                "duration": 0.02,
                "name": "pulse",
                "condition": "a single square pulse"
            },
            "8": {
                "duration": 0.0167,
                "name": "pulse",
                "condition": "a single square pulse"
            },
            "9": {
                "duration": .0125,
                "name": "raised_cosine",
                "condition": "half-period of a cosine wave"
            },
            "10": {
                "duration": .01,
                "name": "100 hz pulse train",
                "condition": "1 second of 100 Hz pulse train. Each pulse is 2 ms wide"
            }, 
            "11": {
                "duration": 1.0,
                "name": "Square Pulse",
                "condition": "1 second square pulse: continuously on for 1s"        
            }
        }
    try:
        opto_pickle_path = glob(join(module_params['base_directory'], 
                                     '*.opto.pkl'))[0]
    except IndexError:
        opto_pickle_path = glob(join(module_params['base_directory'], 
                                     '**', '*.opto.pkl'))[0]
    try:
        sync_path = glob(join(module_params['base_directory'],
                                      "*.sync"))[0]
    except IndexError:
        sync_path = glob(join(module_params['base_directory'],
                                      "**",
                                      "*.sync"))[0]
    input_json_write_dict = {
        'opto_pickle_path': opto_pickle_path,
        'sync_h5_path': sync_path,
        'output_opto_table_path': join(module_params['output_path'],
                                       'optotagging_table.csv'),
        'conditions': conditions

    }
    print(input_json_write_dict)
    return module_params, input_json_write_dict


def ecephys_lfp_subsampling(module_params):
    """ Writes the lfp sampling information to the input json

    Parameters
    ----------
    module_params: dict
    Session or probe unique information, used by each module

    Returns
    -------
    module_params: dict
    Session or probe unique information, used by each module
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """
    probe_idx = module_params['current_probe']
    output_path = module_params['output_path']
    print(module_params['base_directory'])
    print(probe_idx)
    print(glob(join(module_params['base_directory'],
                                           '*',
                                           '*_' + probe_idx)))
    print(glob(join(module_params['base_directory'],
                                           '**',
                                           probe_idx)))
    try:
        lfp_directory = glob(join(module_params['base_directory'],
                                           '*',
                                           '*_' +
                                           probe_idx,
                                           'continuous'
                                           "Neuropix*100.1"))[0]
    except IndexError:
        lfp_directory = glob(join(module_params['base_directory'], 
                                           "**",
                                           "*_" +
                                           probe_idx,
                                           'continuous',
                                           '**'
                                           "Neuropix*100.1"))[0]
    try:
        probe_info_file = glob(join(module_params['base_directory'],
                                           '*'
                                           "probe_info.json"))[0]
    except IndexError:
        probe_info_file= glob(join(module_params['base_directory'], 
                                           "**",
                                           "*_" +
                                           probe_idx,
                                           'probe_info.json'))[0]

    print(probe_info_file)
    with open(probe_info_file) as probe_file:
        probe_info = json.load(probe_file)
    module_params['lfp_path'] = lfp_directory
    input_json_write_dict = {
        'name': module_params['current_probe'],
        'lfp_sampling_rate': 2500.,
        'lfp_input_file_path': join(lfp_directory, 'continuous.dat'),
        'lfp_timestamps_input_path': join(output_path, probe_idx + '_lfp_timestamps.npy'),
        'lfp_data_path': join(output_path, probe_idx+ '_lfp.dat'),
        'lfp_timestamps_path': join(output_path, probe_idx +  '_timestamps.npy'),
        'lfp_channel_info_path': join(output_path, probe_idx +'_channels.npy'),
        'surface_channel': probe_info['surface_channel'],
        'reference_channels': [191]
    }
    if probe_idx != module_params['final_probe']:
        module_params['lfp_list'].append(input_json_write_dict)
        return module_params, input_json_write_dict
    else:
        module_params['lfp_list'].append(input_json_write_dict)
        input_json_write_dict = \
            {
                'lfp_subsampling': {
                    'temporal_subsampling_factor': 2,
                    'channel_stride': 1,
                    'start_channel_offset': 0},
                "probes": module_params['lfp_list'],
            }
        return module_params, input_json_write_dict


def extract_running_speed(module_params):
    """Writes the stimulus and pkl paths to the input json

    Parameters
    ----------
    module_params: dict
    Session or probe unique information, used by each module

    Returns
    -------
    module_params: dict
    Session or probe unique information, used by each module
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """

    # trim_discontiguous_frame_times = module_params['trim']
    output_path = module_params['output_path']
    try:
        pkl_path = glob(join(module_params['base_directory'],
                             "*.stim.pkl"))[0]
    except IndexError:
        pkl_path = glob(join(module_params['base_directory'],
                             "**",
                             "*.stim.pkl"))[0]
    try:
        sync_path = glob(join(module_params['base_directory'],
                              "*.sync"))[0]
    except IndexError:
        sync_path = glob(join(module_params['base_directory'],
                              "**",
                              "*.sync"))[0]
    # TODO: Create a check to see if we want to use a modified version
    # of the stim pkl here
    input_json_write_dict = \
        {
            'stimulus_pkl_path': pkl_path,
            'sync_h5_path': sync_path,
            'output_path': join(output_path,
                                "running_speed.h5"),
            "log_level": 'INFO'
        }
    return module_params, input_json_write_dict
