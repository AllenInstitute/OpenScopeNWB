#!/usr/bin/env python
import dandi
from dandi.dandiapi import DandiAPIClient as dandi
from dandi import validate as validate

import argparse
import os
import json

from openscopenwb.utils import firebase_functions as fb
 

def get_creds():
    cred_file = open(
        r'/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/src/openscopenwb/utils/.cred/dandi.json')
    cred_json = json.load(cred_file)
    return cred_json['api_key']


def set_env():
    os.environ['DANDI_API_KEY'] = get_creds()


if __name__ == "__main__":
    """Uploads an NWB to dandi 

    Parameters
    ----------
    dandi_url: str
    The dandiset's location
    dandi_file: str
    The current nwb's location
    dandi_val: str
    The dandi set's id
    project_id: str
    The project name for the data 
    sess_id: str
    The 10 digit session id for our data
    exp_id: str
    The experiment id for the session's plane
    subject_id: str
    The mouse id for the session
    raw: str
    Whether to include RAW data
    final: str
    Whether this is the final plane for the sess

    Returns
    -------
    """
    print("Uploading")
    parser = argparse.ArgumentParser()
    parser.add_argument('--dandi_url', type=str)
    parser.add_argument('--dandi_file', type=str)
    parser.add_argument('--dandi_val', type=str)
    parser.add_argument('--project_id', type=str)
    parser.add_argument('--subject_id', type=str)
    parser.add_argument('--sess_id', type=str)
    parser.add_argument('--exp_id', type=str)
    parser.add_argument('--raw', type=str)
    parser.add_argument('--final', type=str)
    args = parser.parse_args()
    set_env()
    validate.validate(args.dandi_file)
    dandi_set = dandi()
    dandi_set.dandi_authenticate()
    dandi_dataset = dandi_set.get_dandiset('000' + args.dandi_val)
    raw = args.raw
    if raw == 'True':
        status = dandi_dataset.iter_upload_raw_asset(
            args.dandi_file,
            asset_metadata={
                'path': 'sub_' + args.subject_id + '/' 'sub_' + args.subject_id + 'sess_' + args.sess_id + '/' +  'sub_' + args.subject_id + 'sess_' + args.sess_id  + 'exp_' + args.exp_id + 'raw_ophys.nwb',
                "dandiset": str(dandi_dataset)})
    else:
        status = dandi_dataset.iter_upload_raw_asset(
            args.dandi_file,
            asset_metadata={
                'path': 'sub_' + args.subject_id + '/' 'sub_' + args.subject_id + 'sess_' + args.sess_id + '/' +  'sub_' + args.subject_id + 'sess_' + args.sess_id  + 'exp_' + args.exp_id + 'ophys.nwb',
                "dandiset": str(dandi_dataset)})
    print("STATUS")
    print(list(status))
    os.remove(args.dandi_file)
    fb.start(fb.get_creds())


    if args.final == 'True':
        fb.update_session_dandi(args.project_id, args.sess_id, "sub_" + args.subject_id + '/' + args.sess_id)
    fb.update_session_status(args.project_id, args.sess_id, "Uploaded")