import os
import subprocess
import shlex
import matplotlib.pyplot as plt

from requests import post
from openscopenwb.utils import firebase_sync as fire_sync
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import postgres_functions as postgres
from openscopenwb.utils import allen_functions as allen
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
print(curr_dir)
print("directory")
print(dir)
# ephys_list = fb.update_ephys_statuses()
#session_id = 1172129291
# session_id = 762602078
# cmd = './bash/ecephys.sh ' + "-s " + str(session_id)
# subprocess.call(shlex.split(cmd))
# OpenScopeIllusion

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
    print(conversion_list)
    '''
    for session in conversion_list:
        print("Sanity Checking")
        allen_path = postgres.get_e_sess_directory(session)
        if allen.sanity_check(allen_path, session):
            print("sanity check passed for: " + session)
        else:
            print("sanity check failed for: " + session)
            conversion_list.remove(session)
    '''
    print("List of Sessions to convert: ")
    print(conversion_list)
    for session in conversion_list:
        cmd = dir + '/bash/ecephys.sh ' + "-s " + str(session) +" -p " + project
        print(shlex.split(cmd))
        subprocess.call(shlex.split(cmd))
        fb.update_session_status(project, session, "Conversion Running")
    dandi_list = fb.get_dandi_statuses(project)
    print(dandi_list)
    for session in dandi_list:
        cmd = dir + '/bash/dandi.sh ' + "-d " + proj_dandi_value
        subprocess.call(shlex.split(cmd))
        fb.update_session_status(project, session, "Conversion Running")

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

# 1202394917
exp_list = postgres.get_sess_experiments('1214523350')
# for experiment in exp_list:
#    if experiment == 1211453853:
#    cmd = dir + '/bash/ophys.sh ' + "-s " + '1214523350 '+ "-e " + str(experiment)
#    subprocess.call(shlex.split(cmd))
