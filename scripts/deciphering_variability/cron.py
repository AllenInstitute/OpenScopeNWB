import os
import slurm_job 
import subprocess
from openscopenwb.utils import firebase_sync as fire_sync
from openscopenwb.utils import firebase_functions as fb


dir = os.path.dirname(__file__)
cred_json = os.path.join(dir, 'cred', 'openscopetest-d7614-firebase-adminsdk-bwzou-b9942c1cd6.json')
lister = [1137276124]
for i in lister:
    subprocess.call("./bash/ssh.sh")
