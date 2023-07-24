#!/usr/bin/bash
while getopts "s:p:e:r:v:f:" arg; do
  case "$arg" in
    s) Session=$OPTARG;;
    p) Project=$OPTARG;;
    e) Experiment=$OPTARG;;
    r) Raw=$OPTARG;;
    v) Val=$OPTARG;;
    f) Final=$OPTARG;;

  esac
done
echo $Session
echo $Project
echo $Experiment
echo $Raw
echo $Val
echo $Final
python "/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/src/openscopenwb/utils/slurm_utils/slurm_ophys_job.py" $Project $Session $Experiment $Raw $Val $Final
exit 1