import dandi.dandiapi.DandiAPIClient as dandi
import dandi.files.LocalAsset as dandi_file
import argparse
import os 
import json


def get_creds():
    cred_json = json.load(r'/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/src/openscopenwb/utils/.cred/dandi.json')
    return cred_json['api_key']



def set_env():
    os.environ['DANDI_API_KEY'] = get_creds()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dandi_url', type=int)
    parser.add_argument('--dandi_file', type=str)
    args = parser.parse_args()
    dandi_set = dandi(args.dandi_url)
    dandi_set.authenticate()
    file = dandi_file(args.dandi_file)
    file.upload(dandi_set)