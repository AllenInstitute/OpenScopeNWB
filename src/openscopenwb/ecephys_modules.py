import datetime
import pandas as pd
import numpy as np
from openscopenwb.utils import clean_up_functions as cuf
import os


from os.path import join
from glob import glob


def stimulus_table(session_params):
    """Returns the dict for the stimulus path

    Parameters
    ----------
    session_params: dict
    Session unique information, used by each module
    trim: bool
    Whether or not to trim values

    Returns
    -------
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """    
    trim_discontiguous_frame_times = session_params['trim']

    input_json_write_dict = \
        {
            'stimulus_pkl_path': glob(join(session_params['base_directory'],
                                      "*.stim.pkl"))[0],
            'sync_h5_path': glob(join(session_params['base_directory'],
                                 "*.sync"))[0],
            'output_stimulus_table_path':
                os.path.join(session_params['base_directory'],
                             "stim_table_allensdk.csv"),
            'output_frame_times_path':
                os.path.join(session_params['base_directory'],
                             "frame_times.npy"),
            #'trim_discontiguous_frame_times': trim_discontiguous_frame_times,
            "log_level": 'INFO'
        }
    return session_params, input_json_write_dict


def ecephys_align_timestamps(probe_idx, session_params):
    """Returns the dict for the timestamps json

    Parameters
    ----------
    probe_idx: str
    The name/id of the current probe
    session_params: dict
    Session unique information, used by each module


    Returns
    -------
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """  
    spike_times = []
    base_directory = glob(os.path.join(session_params['base_directory'], '*' + probe_idx + '*_sorted'))[0]
    events_directory = glob(os.path.join(base_directory, 'events', 'Neuropix*', 'TTL*'))[0]
    probe_directory = glob(os.path.join(base_directory, 'continuous', 'Neuropix*'))[0]
    print(probe_directory)
    timestamp_files = []

    timestamp_files.append({
            'name': 'spike_timestamps',
            'input_path': join(probe_directory,     'spike_times.npy'),
            'output_path': join(probe_directory, 'spike_times_master_clock.npy')
        }
    )

    try:
        spike_times = np.load(join(probe_directory, 'spike_times.npy'))
    except FileNotFoundError:
        print(' Spikes not found for ' + probe_directory)
    else:

        probe_dict = {
            'name': probe_idx,
            'sampling_rate': 30000.,
            'lfp_sampling_rate': 2500.,
            'barcode_channel_states_path': join(events_directory,
                                                'channel_states.npy'),
            'barcode_timestamps_path': join(
                events_directory,
                'event_timestamps.npy'),
            'mappable_timestamp_files': timestamp_files,
        }

        session_params['probe_dict_list'].append(probe_dict)
        if probe_idx != session_params['final_probe']:
            return session_params, probe_dict
        else:
            dictionary = {
                'sync_h5_path': glob(join(
                               session_params['base_directory'],
                                '*.sync'))[0],
                "probes": session_params['probe_dict_list']
            }
            return session_params, dictionary


def ecephys_write_nwb(probe_idx, session_params):
    """Writes the input json for the nwb modules

    Parameters
    ----------
    probe_idx: str,
    The id of the current probe
    session_params: dict
    Session unique information, used by each module


    Returns
    -------
    None
    """
    probes = []
    probe_directory = glob(os.path.join(session_params['base_directory'] + '\\' + probe_idx + '_sorted')[0],
                           'continuous', 'Neuropix*')[0]

    try:
        channel_info = pd.read_csv(join(probe_directory,
                                   'ccf_regions.csv'),
                                   index_col = 0)
    except FileNotFoundError:
        pass

    else:
        channels = []

        for idx, channel_row in channel_info.iterrows():
            structure_acronym = channel_row['region']
            channel_dict = {
                'id': idx + probe_idx * 1000,
                'valid_data': True,
                'probe_id': idx,
                'probe_vertical_position': -1,
                'probe_horizontal_position': -1,
                'manual_structure_id': -1,
                'manual_structure_acronym': -1,
                'anterior_posterior_ccf_coordinate': -1,
                'dorsal_ventral_ccf_coordinate': -1,
                'left_right_ccf_coordinate': -1
            }
            channels.append(channel_dict)

            unit_info = pd.read_csv(join(probe_directory,
                                    'metrics.csv'),
                                    index_col=0)
            quality_info = pd.read_csv(join(probe_directory,
                                       'cluster_group.tsv.v2'),
                                       sep='\t',
                                       index_col=0)

            spike_clusters = np.load(join(probe_directory,
                                     'spike_clusters.npy'))
            
            units = []
            spike_times_index = 0
            spike_amplitudes_index = 0

            for idx, unit_row in unit_info.iterrows():
                if quality_info.loc[unit_row.cluster_id].group == 'good':
                    spike_count = np.sum(spike_clusters ==
                                         unit_row['cluster_id'])
                    unit_dict = {
                        'id': session_params['last_unit_id'],
                        'peak_channel_id': unit_row['peak_channel'] +
                        probe_idx * 100,
                        'local_index': idx,
                        'cluster_id': unit_row['cluster_id'],
                        'quality': unit_row['quality'],
                        'firing_rate': cuf.clean_up_nan_and_inf(unit_row['firing_rate']), 
                        'snr': cuf.clean_up_nan_and_inf(unit_row['snr']),
                        'isi_violations': cuf.clean_up_nan_and_inf(unit_row['isi_viol']),
                        'presence_ratio': cuf.clean_up_nan_and_inf(unit_row['presence_ratio']),
                        'amplitude_cutoff': cuf.clean_up_nan_and_inf(unit_row['amplitude_cutoff']),
                        'isolation_distance': cuf.clean_up_nan_and_inf(unit_row['isolation_distance']),
                        'l_ratio': cuf.clean_up_nan_and_inf(unit_row['l_ratio']),
                        'd_prime': cuf.clean_up_nan_and_inf(unit_row['d_prime']),
                        'nn_hit_rate': cuf.clean_up_nan_and_inf(unit_row['nn_hit_rate']),
                        'nn_miss_rate': cuf.clean_up_nan_and_inf(unit_row['nn_miss_rate']),
                        'max_drift': cuf.clean_up_nan_and_inf(unit_row['max_drift']),
                        'cumulative_drift': cuf.clean_up_nan_and_inf(unit_row['cumulative_drift']),
                        'silhouette_score': cuf.clean_up_nan_and_inf(unit_row['silhouette_score']),
                        'waveform_duration': cuf.clean_up_nan_and_inf(unit_row['duration']),
                        'waveform_halfwidth': cuf.clean_up_nan_and_inf(unit_row['halfwidth']),
                        'PT_ratio': cuf.clean_up_nan_and_inf(unit_row['PT_ratio']),
                        'repolarization_slope': cuf.clean_up_nan_and_inf(unit_row['repolarization_slope']),
                        'recovery_slope': cuf.clean_up_nan_and_inf(unit_row['recovery_slope']),
                        'amplitude': cuf.clean_up_nan_and_inf(unit_row['amplitude']),
                        'spread': cuf.clean_up_nan_and_inf(unit_row['spread']),
                        'velocity_above': cuf.clean_up_nan_and_inf(unit_row['velocity_above']),
                        'velocity_below': cuf.clean_up_nan_and_inf(unit_row['velocity_below'])
                    }
                    spike_times_index += spike_count
                    spike_amplitudes_index += spike_count
                    
                    units.append(unit_dict)
                    session_params['last_unit_id'] += 1

                probe_dict = {
                    'id': probe_idx,
                    'name': probe_idx,
                    'spike_times_path': join(probe_directory, 'spike_times_master_clock.npy'),
                    'spike_clusters_file': join(probe_directory, 'spike_clusters.npy'),
                    'spike_amplitudes_path': join(probe_directory, 'amplitudes.npy'),
                    'mean_waveforms_path': join(probe_directory, 'mean_waveforms.npy'),
                    'spike_templates_path': join(probe_directory, 'spike_templates.npy'),
                    'templates_path': join(probe_directory, 'templates.npy'),
                    'inverse_whitening_matrix_path': join(probe_directory, 'whitening_mat_inv.npy'),
                    'channels': channels,
                    'units': units,
                    'lfp': None
                }
                session_params['probe_dict_list'].append(probe_dict)
        if probe_idx != session_params['final_probe']:
            return session_params
        else:
            sync_file = glob(join(session_params['base_directory'], '*.sync'))[0]
            YYYY = 2021 #int(session_string[17:21])
            MM = 6 #int(session_string[21:23])
            DD = 16 #int(session_string[23:25])

            dictionary = \
            {
                'invalid_epochs': [{'id': 0,
                                    'type': 'none',
                                    'label': 'LABEL',
                                    'start_time': 0.0,
                                    'end_time': 0.0}, ],
                "log_level": 'INFO',
                "output_path": session_params['base_directory'],
                "session_id": session_params['session_id'],
                "session_start_time": datetime.datetime(YYYY, MM, DD, 0, 0, 0).isoformat(),
                "stimulus_table_path": os.path.join(session_params['base_directory'],
                                                    'stim_table_allensdk.csv'),
                "probes": probes,
                "session_sync_path": sync_file,
                "running_speed_path": join(session_params['base_directory'],
                                           'running_speed.h5')
            }
        return dictionary


def ecephys_optotagging_table(session_params):
    """ Writes the relevant optotagging information to the input json

    Parameters
    ----------
    session_params: dict
    Session unique information, used by each module

    Returns
    -------
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """
    input_json_write_dict = {
        'opto_pickle_path': glob(
            join(session_params['base_directory'], '*.opto.pkl'))[0],
        'sync_h5_path': glob(
            join(session_params['base_directory'], '*.sync'))[0],
        'output_opto_table_path': join(session_params['base_directory'],
                                       'optotagging_table.csv')
        }
    return input_json_write_dict


def ecephys_lfp_subsampling(session_params):
    """ Writes the lfp sampling information to the input json

    Parameters
    ----------
    session_params: dict
    Session unique information, used by each module

    Returns
    -------
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """


def extract_running_speed(session_params):
    """Writes the stimulus and pkl paths to the input json

    Parameters
    ----------
    session_params: dict
    Session unique information, used by each module

    Returns
    -------
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """

    trim_discontiguous_frame_times = session_params['trim']

    input_json_write_dict = \
        {
            'stimulus_pkl_path': glob(join(session_params['base_directory'],
                                      "*.stim.pkl"))[0],
            'sync_h5_path': glob(join(session_params['base_directory'],
                                      "*.sync"))[0],
            'output_path': join(session_params['base_directory'],
                                "running_speed.h5"),
            'trim_discontiguous_frame_times': trim_discontiguous_frame_times,
            "log_level": 'INFO'
        }
    return input_json_write_dict, session_params
