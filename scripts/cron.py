import os
import subprocess
import shlex
import h5py
import matplotlib.pyplot as plt

from requests import post
from openscopenwb.utils import firebase_sync as fire_sync
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import postgres_functions as postgres
from openscopenwb.utils import allen_functions as allen
from openscopenwb.utils import sync_functions as sync
from pathlib import Path
from ecephys_nwb_generation import write_subject_to_nwb

from datetime import date, datetime
import pynwb
from pynwb import NWBFile, TimeSeries
from pynwb import NWBHDF5IO
from glob import glob
from os.path import join


dir = os.path.dirname(__file__) or '.'
curr_dir = Path(__file__).parent

e_proj_list = ["OpenScopeIllusion", "OpenScopeGlobalLocalOddball"]
o_proj_list = ["OpenScopeDendriteCoupling"]

fb.start(fb.get_creds())
for project in e_proj_list:
    if project == "OpenScopeIllusion":
        proj_dandi_value = "000248"
    elif project == "OpenScopeGlobalLocalOddBall":
        proj_dandi_value = "000253"
    missing_list = fire_sync.compare_sessions(project)
    print("List of sessions to upload: ")
    print(missing_list)
    for session in missing_list:
        fb.init_session(project, session)
    update_list = []
    long_conversion_list = []
    tmp_update_list = postgres.get_e_proj_info(project)['sessions']
    for sess in tmp_update_list:
        tmp_val = fire_sync.compare_session(project, sess)
        if tmp_val != []:
            update_list.append(sess)
    print("List of Sessions to Update: ")
    print(update_list)
    for session in update_list:
        fb.update_session(project, session)
    conversion_list = fb.update_ephys_statuses(project)
    print("List of pre-sanity checked sessions: ")
    for session in conversion_list:
        flag = sync.sync_test(session)
        if flag:
            print("Long Frame!")
            print(session)
            long_conversion_list.append(session)
            conversion_list.remove(session)
    print(conversion_list)
    print("List of Sessions to convert: ")
    print(conversion_list)
    for session in conversion_list:
        cmd = dir + '/bash/ecephys.sh ' + "-s " + \
            str(session) + " -p " + project
        print(shlex.split(cmd))
        subprocess.call(shlex.split(cmd))
        fb.update_session_status(project, session, "Conversion Running")
    dandi_list = fb.get_ecephys_upload_sessions(project)
    print(dandi_list)
    print("List of Long Frame Sessions to convert: ")
    for session in long_conversion_list:
        cmd = dir + '/bash/long_ecephys.sh ' + "-s " + \
            str(session) + " -p " + project
        print(shlex.split(cmd))
        subprocess.call(shlex.split(cmd))
        fb.update_session_status(project, session, "Conversion Running")        
    # for session in dandi_list:
    #    cmd = dir + '/bash/dandi.sh ' + "-d " + proj_dandi_value
    #    subprocess.call(shlex.split(cmd))
    #    fb.update_session_status(project, session, "Conversion Running")

for project in o_proj_list:
    if project == 'OpenScopeDendriteCoupling':
        proj_dandi_value = '000336'
    missing_list = fire_sync.compare_o_sessions(project)
    print("List of sessions to upload: ")
    print(missing_list)
    for session in missing_list:
        fb.init_o_session(project, session)
    update_list = []
    tmp_update_list = postgres.get_o_proj_info(project)['sessions']
    for sess in tmp_update_list:
        tmp_val = fire_sync.compare_o_session(project, sess)
        if tmp_val != []:
            update_list.append(sess)
    print("List of Sessions to Update: ")
    print(update_list)
    for session in update_list:
        fb.update_o_session(project, session)
    conversion_list = fb.update_ophys_statuses(project)
    print("List of Sessions to convert: ")
    print(conversion_list)
    for session in conversion_list:
        exp_list = fb.get_experiments(project, session)
        for experiment in exp_list:
            cmd = dir + '/bash/ophys.sh ' + "-s " + \
                str(session) + " -p " + project + " -e " + \
                str(experiment) + ' -v ' + str(proj_dandi_value)
            print(shlex.split(cmd))
            subprocess.call(shlex.split(cmd))
            fb.update_session_status(project, session, "Conversion Running")
    raw_conversion_list = fb.update_ophys_RAW_statuses(project)
    print("List of RAW Sessions to convert: ")
    print(raw_conversion_list)
    for session in raw_conversion_list:
        print(session)
        exp_list = fb.get_experiments(project, session)
        for experiment in exp_list:
            if experiment == exp_list[-1]:
                cmd = dir + '/bash/raw_ophys.sh ' + "-s " + str(session) + " -p " + project + " -e " + str(
                    experiment) + ' -v ' + str(proj_dandi_value) + ' -f ' + "final"
            else:
                cmd = dir + '/bash/raw_ophys.sh ' + "-s " + str(session) + " -p " + project + " -e " + str(
                    experiment) + ' -v ' + str(proj_dandi_value) + ' -f ' + 'not_final'
            print(shlex.split(cmd))
            subprocess.call(shlex.split(cmd))
            fb.update_session_status(
                project, session, "Raw Conversion Running")
