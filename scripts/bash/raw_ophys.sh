#!/usr/bin/bash
while getopts "s:p:e:v:f:" arg; do
  case "$arg" in
    s) Session=$OPTARG;;
    p) Project=$OPTARG;;
    e) Experiment=$OPTARG;;
    v) Val=$OPTARG;;
    f) Final=$OPTARG;;
  esac
done
echo $Session
echo $Project
echo $Experiment
echo $Val
ssh ahad.bawany@hpc-login "/allen/programs/mindscope/workgroups/openscope/ahad/Conda_env/openscopenwb/bin/python /allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/scripts/slurm_raw_ophys_job.py" $Project $Session $Experiment $Val $Final
exit 1