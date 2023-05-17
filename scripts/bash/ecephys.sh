#!/usr/bin/bash
while getopts "s:p:l:" arg; do
  case $arg in
    s) Session=$OPTARG;;
    p) Project=$OPTARG;;
    l) Long=$OPTARG;;
  esac
done
echo $Session
echo $Project
ssh ahad.bawany@hpc-login "/allen/programs/mindscope/workgroups/openscope/ahad/Conda_env/openscopenwb/bin/python /allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/scripts/slurm_ephys_job.py" $Session $Project $Long
exit 1