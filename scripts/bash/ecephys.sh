#!/usr/bin/bash
while getopts "c:s:p:l:d:v:" arg; do
  case $arg in
    c) Conda=$OPTARG;;
    s) Session=$OPTARG;;
    p) Project=$OPTARG;;
    l) Long=$OPTARG;;
    d) Directory=$OPTARG;;
    v) Value=$OPTARG;;
  esac
done
echo $Session
echo $Project
$Conda $Directory $Session $Project $Long $Value
exit 1