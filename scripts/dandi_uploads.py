#!/usr/bin/env python
import dandi
from  dandi.dandiapi import DandiAPIClient as dandi
from dandi import validate as validate
import argparse
import os 
import json


def get_creds():
    cred_file = open(r'/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/src/openscopenwb/utils/.cred/dandi.json')
    cred_json = json.load(cred_file)
    print(cred_json['api_key'])
    print('cred')
    return cred_json['api_key']



def set_env():
    os.environ['DANDI_API_KEY'] = get_creds()


if __name__ == "__main__":
    print("Uploading")
    parser = argparse.ArgumentParser()
    parser.add_argument('--dandi_url', type=str)
    parser.add_argument('--dandi_file', type=str)
    parser.add_argument('--dandi_val', type=str)
    parser.add_argument('--sess_id', type=str)
    parser.add_argument('--exp_id', type=str)
    parser.add_argument('--raw', type=str)
    args = parser.parse_args()
    set_env()
    validate.validate(args.dandi_file)
    dandi_set = dandi()
    dandi_set.dandi_authenticate()
    dandi_dataset = dandi_set.get_dandiset('000' + args.dandi_val)
    raw = args.raw


    #TODO: Implement a flag check for if file exists and then use replace if it does 
    if raw == 'True':
        status = dandi_dataset.iter_upload_raw_asset(args.dandi_file, asset_metadata = {'path': args.sess_id + '/' + args.sess_id + '/' + args.exp_id  + '_raw.nwb', "dandiset": str(dandi_dataset)} )
    else:
        status = dandi_dataset.iter_upload_raw_asset(args.dandi_file, asset_metadata = {'path': args.sess_id + '/' + args.exp_id  + '.nwb', "dandiset": str(dandi_dataset)} )
    print("STATUS")
    print(list(status))
    #file = dandi_file(args.dandi_file, args.dandi_file)
    #file.upload(dandiset = dandi_set.get_dandiset(args.dandi_val), metadata = {})