import os
import numpy as np

dir = os.path.dirname(__file__)

path_folder = os.path.join(dir, '725254892_388523_20180726_probeA_sorted',
                           'continuous', 'Neuropix-3a-100.0')

all_files = os.listdir(path_folder)
nb_spike_times = np.load(os.path.join(path_folder, 'spike_times.npy')).shape[0]
nb_units = np.load(os.path.join(path_folder, 'templates.npy')).shape[0]
replace = True
max_nb_spikes_times = 10000

for indiv_files in all_files:
    local_path = os.path.join(path_folder, indiv_files)

    if '.npy' in local_path:
        local_array = np.load(local_path)
        local_shape = local_array.shape
        index = np.where(np.array(local_shape) == nb_spike_times)

        if len(index[0])>0:
            index = index[0][0]
            local_array = local_array[0:max_nb_spikes_times, :]
            if replace:
                new_file = indiv_files
            else:
                new_file = indiv_files.split('.')[0]\
                    + '_new.'+indiv_files.split('.')[1]
            new_path = os.path.join(path_folder, new_file)
            np.save(new_path, local_array)
