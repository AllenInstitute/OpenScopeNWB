import os
import subprocess
import shlex
import re

from openscopenwb.utils import firebase_sync as fire_sync
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import postgres_functions as postgres
from openscopenwb.utils import sync_functions as sync
from openscopenwb.utils.dandi_utils import dandi_functions as dandi
from pathlib import Path


dir = os.path.dirname(__file__) or '.'
curr_dir = Path(__file__).parent


e_proj_list = ["OpenScopeIllusion",
               "OpenScopeGlobalLocalOddball", "OpenScopeTemporalBarcode"]
o_proj_list = ["OpenScopeDendriteCoupling"]


fb.start(fb.get_creds())

for project in e_proj_list:
    current_dir = os.path.abspath(__file__)
    current_dir = current_dir.replace('scripts/cron.py', '')
    utils_dir = str(current_dir) + \
        'src/openscopenwb/utils/slurm_utils/slurm_ephys_job.py'
    conda_environment = 'openscopenwb'
    python_path = os.path.join(
        '/allen',
        'programs',
        'mindscope',
        'workgroups',
        'openscope',
        'ahad',
        'Conda_env',
        conda_environment,
        'bin',
        'python',
    )
    if project == "OpenScopeIllusion":
        proj_dandi_value = "000248"
    elif project == "OpenScopeGlobalLocalOddBall":
        proj_dandi_value = "000253"
    elif project == "OpenScopeTemporalBarcode":
        proj_dandi_value = "000563"

    # Compare sessions between postgres and FB
    missing_list = fire_sync.compare_sessions(project)
    print("List of sessions to upload: ")
    print(missing_list)
    for session in missing_list:
        fb.init_session(project, session)

    update_list = []
    long_conversion_list = []
    # Similarly, find sessions with new info on postgres
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

    # Run our sync check for timings
    print("List of pre-sanity checked sessions: ")
    for session in conversion_list:
        flag = sync.sync_test(session)
        if flag:
            print("Long Frame!")
            print(session)
            long_conversion_list.append(session)
            conversion_list.remove(session)
    print(conversion_list)

    # Trigger Normal Conversions
    print("List of Sessions to convert: ")
    print(conversion_list)
    for session in conversion_list:
        cmd = dir + '/bash/ecephys.sh ' + "-s " + \
            str(session) + " -p " + project + " -l " + False + " -c " + \
            python_path + " -d " + utils_dir + " -v " + proj_dandi_value
        print(shlex.split(cmd))
        subprocess.call(shlex.split(cmd))
        fb.update_session_status(project, session, "Conversion Running")
    dandi_list = fb.get_ecephys_upload_sessions(project)
    print(dandi_list)

    # Trigger conversions for sessions with sync issues
    print("List of Long Frame Sessions to convert: ")
    for session in long_conversion_list:
        cmd = dir + '/bash/ecephys.sh ' + "-s " + \
            str(session) + " -p " + project + " -l " + True + " -c " + \
            python_path + " -d " + utils_dir + " -v " + proj_dandi_value
        print(shlex.split(cmd))
        subprocess.call(shlex.split(cmd))
        fb.update_session_status(project, session, "Conversion Running")

    # Trigger uploads for sessions with upload status
    print("List of sessions to upload")
    upload_list = fb.get_dandi_statuses()
    for session in upload_list:
        dandi_file = fb.view_session(project, sess)['allen']
        match = re.search(r'specimen_(\d+)',
                          fb.view_session(project, sess)['path'])
        if match:
            specimen_number = match.group(1)
        with open("dandi_ephys_uploads.py") as upload:
            code = compile(upload.read(), "dandi_ephys_uploads.py", "exec")
            exec(code, {"dandi_val": proj_dandi_value, "sess_id": session,
                 "dandi_file": dandi_file, "subject_id": specimen_number})
    dandi.find_dandiset_sessions(project, proj_dandi_value)
    fb.update_session_status(project, session, "Conversion Running")

    # Update the dandi locations for the project
    dandi.find_dandiset_sessions(project, proj_dandi_value)


for project in o_proj_list:
    current_dir = os.path.abspath(__file__)
    current_dir = current_dir.replace('scripts/cron.py', '')
    utils_dir = str(current_dir) + \
        'src/openscopenwb/utils/slurm_utils/slurm_ophys_job.py'
    conda_environment = 'ophys_nwb'

    python_path = os.path.join(
        '/allen',
        'programs',
        'mindscope',
        'workgroups',
        'openscope',
        'ahad',
        'Conda_env',
        conda_environment,
        'bin',
        'python',
    )
    if project == 'OpenScopeDendriteCoupling':
        proj_dandi_value = '000336'

    # Find sessions on postgres but not FB
    missing_list = fire_sync.compare_o_sessions(project)
    print("List of sessions to upload: ")
    print(missing_list)
    for session in missing_list:
        fb.init_o_session(project, session)
    update_list = []

    # Find sessions where postgres info has been updated
    tmp_update_list = postgres.get_o_proj_info(project)['sessions']
    for sess in tmp_update_list:
        tmp_val = fire_sync.compare_o_session(project, sess)
        if tmp_val != []:
            update_list.append(sess)
    print("List of Sessions to Update: ")
    print(update_list)
    for session in update_list:
        fb.update_o_session(project, session)

    # Find and convert sessions which are ready
    conversion_list = fb.update_ophys_statuses(project)
    print("List of Sessions to convert: ")
    print(conversion_list)
    missing_normal_list, \
        missing_raw_list, \
        missing_all_list = dandi.find_files_with_missing_raw(
            project, proj_dandi_value)
    for i in missing_normal_list:
        conversion_list.append(i)
    for i in missing_all_list:
        conversion_list.append(i)
    for session in conversion_list:
        exp_list = fb.get_experiments(project, session)
        for experiment in exp_list:
            if experiment != exp_list[-1]:
                cmd = (dir + '/bash/ophys.sh ' + "-s " +
                       str(session) + " -p " + project + " -e " +
                       str(experiment) + ' -v ' +
                       str(proj_dandi_value) + ' -c ' +
                       python_path + ' -f ' + "False" +
                       ' -r ' + "False" +
                       ' -d ' + utils_dir)
            else:
                cmd = (dir + '/bash/ophys.sh ' + "-s " +
                       str(session) + " -p " + project + " -e " +
                       str(experiment) + ' -v ' +
                       str(proj_dandi_value) + ' -c ' +
                       python_path + ' -f ' + "True" +
                       ' -r ' + "False" + ' -d ' + utils_dir)
            print(shlex.split(cmd))
            subprocess.call(shlex.split(cmd))
            fb.update_session_status(project, session, "Conversion Running")

    # Find and convert sessions for RAW which are ready
    raw_conversion_list = fb.update_ophys_RAW_statuses(project)
    print("List of RAW Sessions to convert: ")
    print(raw_conversion_list)
    for i in missing_raw_list:
        raw_conversion_list.append(i)
    for i in missing_all_list:
        raw_conversion_list.append(i)
    for session in raw_conversion_list:
        print(session)
        exp_list = fb.get_experiments(project, session)

        # We check for the final plane to update the
        # FB info on dandi locations
        for experiment in exp_list:
            if experiment == exp_list[-1]:
                cmd = (dir + '/bash/ophys.sh ' + "-s " +
                       str(session) + " -p " +
                       project + " -e " +
                       str(experiment) + ' -v ' +
                       str(proj_dandi_value) + ' -c ' +
                       python_path + ' -f ' + "False" +
                       ' -r ' + "True" + ' -d ' + utils_dir)
            else:
                cmd = (dir + '/bash/ophys.sh ' + "-s " +
                       str(session) + " -p " +
                       project + " -e " +
                       str(experiment) + ' -v ' +
                       str(proj_dandi_value) + ' -c ' +
                       python_path + ' -f ' + "True" +
                       ' -r ' + "True" + ' -d ' + utils_dir)
            print(shlex.split(cmd))
            subprocess.run(shlex.split(cmd))
            fb.update_session_status(
                project, session, "Raw Conversion Running")
    dandi.find_dandiset_sessions(project, proj_dandi_value)
