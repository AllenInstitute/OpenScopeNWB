#!/usr/bin/bash
while getopts "c:d:s:p:e:r:v:f:" arg; do
  case "$arg" in
    c) Conda=$OPTARG;;
    d) Directory=$OPTARG;;
    s) Session=$OPTARG;;
    p) Project=$OPTARG;;
    e) Experiment=$OPTARG;;
    r) Raw=$OPTARG;;
    v) Val=$OPTARG;;
    f) Final=$OPTARG;;

  esac
done
echo $Conda
echo $Directory
echo $Session
echo $Project
echo $Experiment
echo $Raw
echo $Val
echo $Final
$Conda $Directory $Project $Session $Experiment $Raw $Val $Final
exit 1