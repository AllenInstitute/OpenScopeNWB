#!/usr/bin/bash
while getopts "s:p:e:r" arg; do
  case $arg in
    s) Session=$OPTARG;;
    p) Project=$OPTARG;;
    e) Experiment=$OPTARG;;
    r) Raw=$OPTATRG;;
  esac
done
echo $Session
echo $Project
echo $Experiment
ssh ahad.bawany@hpc-login "/allen/programs/mindscope/workgroups/openscope/ahad/Conda_env/openscopenwb/bin/python /allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/scripts/slurm_ophys_job.py" $Session $Experiment $Raw
exit 1