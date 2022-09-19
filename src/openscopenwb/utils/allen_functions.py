from openscopenwb.utils import postgres_functions as post_gres
import os
import numpy as np
from os.path import join
from glob import glob
import requests
import json


def lims_subject_info(session_id):
    gender = ""
    genotype = ""
    dob = ""
    donor_name = post_gres.get_e_sess_donor_info(session_id)[0]
    print(donor_name)
    donor_info = requests.get('http://lims2/donors/info/details.json?external_donor_name=' + donor_name)
    donor_json = json.loads(donor_info.text)
    genotype = donor_json[0]['full_genotype']
    if donor_json[0]['gender_id'] == 2:
        gender = "F"
    else:
        gender = "M"
    dob = donor_json[0]['date_of_birth'] 
    id = donor_json[0]['id']
    info = {
        'gender': gender,
        'genotype': genotype,
        'dob': dob,
        'name': donor_name,
        'id': id
    }
    return info 


def lims_o_subject_info(session_id):
    gender = ""
    genotype = ""
    dob = ""
    donor_name = post_gres.get_o_sess_donor_info(session_id)[0]
    print(donor_name)
    donor_info = requests.get('http://lims2/donors/info/details.json?external_donor_name=' + donor_name)
    donor_json = json.loads(donor_info.text)
    genotype = donor_json[0]['full_genotype']
    if donor_json[0]['gender_id'] == 2:
        gender = "F"
    else:
        gender = "M"
    dob = donor_json[0]['date_of_birth'] 
    id = donor_json[0]['id']
    info = {
        'gender': gender,
        'genotype': genotype,
        'dob': dob,
        'name': donor_name,
        'id': id
    }
    return info 

def sanity_check(allen_path, session_id):
    probes = post_gres.get_sess_probes(session_id)
    for current_probe in probes:
        file_in_base_folder = False
        probe_idx = current_probe
        print(allen_path)
        print(probe_idx)
        print(glob(os.path.join(
            allen_path, '*' + probe_idx + '*_sorted')))
        base_directory = glob(os.path.join(
            allen_path, '*' + probe_idx + '*_sorted'))
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

        alt_probe_directory = glob(join(allen_path,
                                        '*', "*" + probe_idx,
                                        'continuous',
                                        'Neuropix*'))
        if alt_probe_directory != []:
            alt_probe_directory = alt_probe_directory[0]


        if queue_directory != []:
            queue_directory = queue_directory[0]

        spike_directory = ""
        if file_in_base_folder:
            print("File in base folder")

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
                print(' Spikes not found for ' + probe_directory)
                file_found = False
                file_in_probe_folder = False

        if alt_probe_directory != []:
            try:
                np.load(glob(join(alt_probe_directory,
                        "spike_times.npy"))[0])
                spike_directory = glob(join(
                                    alt_probe_directory,
                                    "spike_times.npy"))[0]
                print(alt_probe_directory)
                print(spike_directory)
                try:
                    events_directory = glob(join(allen_path,
                                            '*', "*" + probe_idx, 'events',
                                            'Neuropix*', 'TTL*'))[0]
                except IndexError:
                    events_directory = glob(os.path.join(
                                    base_directory, 'events', 'Neuropix*', 'TTL*'))[0]
                print(events_directory)
                file_found = True
                file_in_parent_folder = True

            except FileNotFoundError:
                print(' Spikes not found for ' +
                            join(allen_path,
                                session_id+
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
                print(' Spikes not found for ' + queue_directory)
                file_found = False
                file_in_queue_folder = False

        if(file_in_probe_folder):
            print("file_in_probe_folder")

        elif(file_in_parent_folder):
            print("file_in_parent_folder")

        elif(file_in_queue_folder):
            print("file_in_queue_folder")

        if(file_found):
            return True