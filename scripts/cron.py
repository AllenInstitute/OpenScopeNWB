import os
import subprocess
import shlex
from openscopenwb.utils import firebase_sync as fire_sync
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import postgres_functions as postgres
from pathlib import Path

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

proj_list = ["OpenScopeIllusion", "OpenScopeGlobalLocalOddball"]

fb.start(fb.get_creds())
for project in proj_list:
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
    print("List of Sessions to convert: ")
    print(conversion_list)
    for session in conversion_list:
        cmd = dir + '/bash/ecephys.sh ' + "-s " + str(session)
        subprocess.call(shlex.split(cmd))
        fb.update_session_status(project, session, "Conversion Running")
