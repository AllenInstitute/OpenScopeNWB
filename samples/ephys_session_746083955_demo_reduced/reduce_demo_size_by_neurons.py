<<<<<<< Updated upstream
import os
import numpy as np

dir = os.path.dirname(__file__)

path_folder = os.path.join(dir, '746083955_403407_20180906_probeA_sorted',
                           'continuous', 'Neuropix-3a-100.0')

all_files = os.listdir(path_folder)
nb_spike_times = np.load(os.path.join(path_folder, 'spike_times.npy')).shape[0]
nb_units = np.load(os.path.join(path_folder, 'templates.npy')).shape[0]
ind_clusters = np.load(os.path.join(path_folder, 'spike_clusters.npy'))

replace = True
max_nb_neuron_units = 10

reduce_cluster_times = ind_clusters < max_nb_neuron_units

for indiv_files in all_files:
    local_path = os.path.join(path_folder, indiv_files)

    if '.npy' in local_path:
        local_array = np.load(local_path)
        local_shape = local_array.shape
        # this is for files that are associated with units characterization
        if 'similar_templates.npy' in local_path:
            local_array = local_array[0:max_nb_neuron_units,
                                      0:max_nb_neuron_units]
            if replace:
                new_file = indiv_files
            else:
                new_file = indiv_files.split('.')[0] + '_new.' + indiv_files\
                    .split('.')[1]
            new_path = os.path.join(path_folder, new_file)
            np.save(new_path, local_array)
        else:
            index = np.where(np.array(local_shape) == nb_units)

            if len(index[0]) > 0:
                index = index[0][0]
                try:
                    local_array = local_array[0:max_nb_neuron_units, :]
                except Exception:
                    local_array = local_array[0:max_nb_neuron_units]

                if replace:
                    new_file = indiv_files
                else:
                    new_file = indiv_files.split('.')[0]\
                        + '_new.'+indiv_files.split('.')[1]
                new_path = os.path.join(path_folder, new_file)
                np.save(new_path, local_array)

            index = np.where(np.array(local_shape) == nb_spike_times)

            if len(index[0]) > 0:
                index = index[0][0]
                try:
                    local_array = local_array[reduce_cluster_times, :]
                except Exception:
                    local_array = local_array[reduce_cluster_times]

                if replace:
                    new_file = indiv_files
                else:
                    new_file = indiv_files.split('.')[0]\
                        + '_new.'+indiv_files.split('.')[1]
                new_path = os.path.join(path_folder, new_file)
                np.save(new_path, local_array)
=======
<<<<<<< HEAD
import os
import numpy as np

dir = os.path.dirname(__file__)

path_folder = os.path.join(dir, '746083955_403407_20180906_probeA_sorted',
                           'continuous', 'Neuropix-3a-100.0')

all_files = os.listdir(path_folder)
nb_spike_times = np.load(os.path.join(path_folder, 'spike_times.npy')).shape[0]
nb_units = np.load(os.path.join(path_folder, 'templates.npy')).shape[0]
ind_clusters = np.load(os.path.join(path_folder, 'spike_clusters.npy'))

replace = True
max_nb_neuron_units = 10

reduce_cluster_times = ind_clusters < max_nb_neuron_units

for indiv_files in all_files:
    local_path = os.path.join(path_folder, indiv_files)

    if '.npy' in local_path:
        local_array = np.load(local_path)
        local_shape = local_array.shape
        # this is for files that are associated with units characterization
        if 'similar_templates.npy' in local_path:
            local_array = local_array[0:max_nb_neuron_units,
                                      0:max_nb_neuron_units]
            if replace:
                new_file = indiv_files
            else:
                new_file = indiv_files.split('.')[0] + '_new.' + indiv_files\
                    .split('.')[1]
            new_path = os.path.join(path_folder, new_file)
            np.save(new_path, local_array)
        else:
            index = np.where(np.array(local_shape) == nb_units)

            if len(index[0]) > 0:
                index = index[0][0]
                try:
                    local_array = local_array[0:max_nb_neuron_units, :]
                except Exception:
                    local_array = local_array[0:max_nb_neuron_units]

                if replace:
                    new_file = indiv_files
                else:
                    new_file = indiv_files.split('.')[0]\
                        + '_new.'+indiv_files.split('.')[1]
                new_path = os.path.join(path_folder, new_file)
                np.save(new_path, local_array)

            index = np.where(np.array(local_shape) == nb_spike_times)

            if len(index[0]) > 0:
                index = index[0][0]
                try:
                    local_array = local_array[reduce_cluster_times, :]
                except Exception:
                    local_array = local_array[reduce_cluster_times]

                if replace:
                    new_file = indiv_files
                else:
                    new_file = indiv_files.split('.')[0]\
                        + '_new.'+indiv_files.split('.')[1]
                new_path = os.path.join(path_folder, new_file)
                np.save(new_path, local_array)
=======
import os
import numpy as np

dir = os.path.dirname(__file__)

path_folder = os.path.join(dir, '746083955_403407_20180906_probeA_sorted',
                           'continuous', 'Neuropix-3a-100.0')

all_files = os.listdir(path_folder)
nb_spike_times = np.load(os.path.join(path_folder, 'spike_times.npy')).shape[0]
nb_units = np.load(os.path.join(path_folder, 'templates.npy')).shape[0]
ind_clusters = np.load(os.path.join(path_folder, 'spike_clusters.npy'))

replace = True
max_nb_neuron_units = 10

reduce_cluster_times = ind_clusters < max_nb_neuron_units

for indiv_files in all_files:
    local_path = os.path.join(path_folder, indiv_files)

    if '.npy' in local_path:
        local_array = np.load(local_path)
        local_shape = local_array.shape
        # this is for files that are associated with units characterization
        if 'similar_templates.npy' in local_path:
            local_array = local_array[0:max_nb_neuron_units,
                                      0:max_nb_neuron_units]
            if replace:
                new_file = indiv_files
            else:
                new_file = indiv_files.split('.')[0] + '_new.' + indiv_files\
                    .split('.')[1]
            new_path = os.path.join(path_folder, new_file)
            np.save(new_path, local_array)
        else:
            index = np.where(np.array(local_shape) == nb_units)

            if len(index[0]) > 0:
                index = index[0][0]
                try:
                    local_array = local_array[0:max_nb_neuron_units, :]
                except Exception:
                    local_array = local_array[0:max_nb_neuron_units]

                if replace:
                    new_file = indiv_files
                else:
                    new_file = indiv_files.split('.')[0]\
                        + '_new.'+indiv_files.split('.')[1]
                new_path = os.path.join(path_folder, new_file)
                np.save(new_path, local_array)

            index = np.where(np.array(local_shape) == nb_spike_times)

            if len(index[0]) > 0:
                index = index[0][0]
                try:
                    local_array = local_array[reduce_cluster_times, :]
                except Exception:
                    local_array = local_array[reduce_cluster_times]

                if replace:
                    new_file = indiv_files
                else:
                    new_file = indiv_files.split('.')[0]\
                        + '_new.'+indiv_files.split('.')[1]
                new_path = os.path.join(path_folder, new_file)
                np.save(new_path, local_array)
>>>>>>> fd0d134d40757b1a6fd470fd87f278345f01b284
>>>>>>> Stashed changes
