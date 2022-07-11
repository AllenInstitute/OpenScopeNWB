#!/usr/bin/bash
while getopts "d:" arg; do
  case $arg in
    d) DandiID=$OPTARG;;
  esac
done
echo $DandiID
dandi download "https://dandiarchive.org/dandiset/{}/draft" $DandiID
cd $DandiID
dandi organize $DandiID -f dry
dandi organize $DandiID
dandi upload