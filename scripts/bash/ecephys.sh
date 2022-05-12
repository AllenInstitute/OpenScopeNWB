#!/usr/bin/bash
while getopts "s:" arg; do
  case $arg in
    s) Session=$OPTARG;;
  esac
done
echo $Session
ssh ahad.bawany@hpc-login "/allen/programs/mindscope/workgroups/openscope/ahad/Conda_env/openscopenwb/bin/python /allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/scripts/slurm_ephys_job.py" $Session
exit 1