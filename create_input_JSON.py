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


# TODO: Work on InputJSON info more to work on parsing the relevant modules
def runModules(inputJson):
    "Placeholder"


# TODO: Implement better log in method(?)
# TODO: Fix formatting for Linting
def createEphys(output_directory, row, intputJSON, output_file, last_unit_id,
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

        # I have to speak with Josh about this, not sure if this is specific
        # to an experiment or general
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
