#!/usr/bin/env python
from dandi.dandiapi import DandiAPIClient as dandi
from dandi.files import LocalAsset as dandi_file
from dandi import validate as validate
from openscopenwb.utils import firebase_functions as fb
from glob import glob
from os.path import join
from os.path import dirname
import argparse
import os
import json
import shutil


def get_creds():
    cred_file = open(
        r'/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/src/openscopenwb/utils/.cred/dandi.json')
    cred_json = json.load(cred_file)
    print(cred_json['api_key'])
    print('cred')
    return cred_json['api_key']


def set_env():
    os.environ['DANDI_API_KEY'] = get_creds()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dandi_url', type=str)
    parser.add_argument('--dandi_file', type=str)
    parser.add_argument('--dandi_val', type=str)
    parser.add_argument('--sess_id', type=str)
    parser.add_argument('--project_id', type=str)
    parser.add_argument('--subject_id', type=str)
    args = parser.parse_args()
    set_env()
    print(validate.validate(args.dandi_file))
    dandi_set = dandi()
    dandi_set.dandi_authenticate()
    dandi_dataset = dandi_set.get_dandiset(args.dandi_val)

    status_probes = []
    path = 'sub_' + args.subject_id + '/' 'sub_' + args.subject_id + 'sess_' + args.sess_id + '/' +  'sub_' + args.subject_id + '+sess_' + args.sess_id + '_ecephys.nwb'
    status = dandi_dataset.iter_upload_raw_asset(
        args.dandi_file,
        asset_metadata={
            'path': path,
            "dandiset": str(dandi_dataset)})
    dir = os.path.dirname(args.dandi_file)
    probes = ["probeA", 'probeB', 'probeC', 'probeD', 'probeE', 'probeF']
    for i in glob(join(dir, "*" + 'probe' + "*.nwb")):
        for probe in probes:
            if probe in i:
                print(i, probe)
                status_probes.append(
                    dandi_dataset.iter_upload_raw_asset(
                        i,
                        asset_metadata={
                            'path': 'sub_' + args.subject_id + '/' 'sub_' + args.subject_id + 'sess_' + args.sess_id + '/' +  'sub_' + args.subject_id + '+sess_' + args.sess_id + '+' + probe + '_ecephys.nwb',
                            "dandiset": str(dandi_dataset)}))
    print(list(status))
    for i in status_probes:
        print(list(i))

    fb.start(fb.get_creds())
    fb.update_session_status(args.project_id, args.sess_id, "Uploaded")
    fb.update_session_dandi(args.project_id, args.sess_id, path)
    base_dir = dirname(dirname(dirname(args.dandi_file)))
    output_dir = join(base_dir,"outputs")
    shutil.rmtree(output_dir)