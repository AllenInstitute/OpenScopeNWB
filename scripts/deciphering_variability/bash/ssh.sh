#!/usr/bin/bash

ssh ahad.bawany@hpc-login "sbatch /allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/scripts/deciphering_variability/bash/job.sh"
echo "hello world"
exit 1