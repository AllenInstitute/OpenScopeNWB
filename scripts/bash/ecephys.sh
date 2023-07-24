#!/usr/bin/bash
while getopts "s:p:l:r:" arg; do
  case $arg in
    s) Session=$OPTARG;;
    p) Project=$OPTARG;;
    l) Long=$OPTARG;;
  esac
done
echo $Session
echo $Project
python /allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/src/utils/slurm_utils/slurm_ephys_job.py" $Session $Project $Long
exit 1