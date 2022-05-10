import os
import slurm_job 
import slurm_temp
import subprocess
from openscopenwb.utils import firebase_sync as fire_sync
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import postgres_functions as postgres


dir = os.path.dirname(__file__)
cred_json = os.path.join(dir, 'cred', 'openscopetest-d7614-firebase-adminsdk-bwzou-b9942c1cd6.json')


#ephys_list = fb.update_ephys_statuses()
slurm_temp.set_text(762602078)
subprocess.call('./bash/ecephys.sh')
