import os
import slurm_job 
import slurm_temp
import subprocess
import shlex
from openscopenwb.utils import firebase_sync as fire_sync
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import postgres_functions as postgres


dir = os.path.dirname(__file__)
cred_json = fb.get_creds()

#ephys_list = fb.update_ephys_statuses()
session_id = 1172129291
#session_id = 762602078
cmd = './bash/ecephys.sh ' + "-s " + str(session_id)
subprocess.call(shlex.split(cmd))
