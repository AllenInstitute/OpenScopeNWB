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
import dandi
from dandi.dandiapi import DandiAPIClient as dandi
from dandi import validate as validate
from dandi.organize import organize as dandi_organize
from dandi.download import download as dandi_download
from dandi.upload import upload as dandi_upload
from pathlib import Path
from pynwb import NWBHDF5IO


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
    parser.add_argument('--nwb_folder_path', type=str)
    parser.add_argument('--dandiset_id', type=str)
    parser.add_argument('--sess_id', type=str)
    parser.add_argument('--project_id', type=str)
    parser.add_argument('--subject_id', type=str)
    args = parser.parse_args()
    set_env()
    nwb_folder_path = args.nwb_folder_path
    dandiset_id = args.dandiset_id
    dandi_set = dandi()
    dandi_set.dandi_authenticate()
    dandi_dataset = dandi_set.get_dandiset(dandiset_id)
    session_id = args.sess_id
    project_id = args.project_id
    subject_id = args.subject_id
  

    set_env()
    dandiset_path = nwb_folder_path
    assert os.getenv("DANDI_API_KEY"), (
        "Unable to find environment variable 'DANDI_API_KEY'. "
        "Please retrieve your token from DANDI and set this environment variable."
    )

    # Create the session directory
    directory_path = os.path.join(nwb_folder_path)
    dandi_path = os.path.abspath(directory_path)
    dandi_path_set = directory_path  + "/" + dandiset_id
    print("PATHS: ", directory_path, dandi_path, dandi_path_set)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        os.makedirs(dandi_path_set)


    # Rename the nwb file to include the session id
    src = os.path.join(nwb_folder_path,  "spike_times.nwb")
    dst = os.path.join(directory_path, session_id + ".nwb")

    # Move the nwb file to the session directory
    shutil.move(src, dst)
    

    dandi_download(urls=r'https://dandiarchive.org/dandiset/' + dandiset_id + '/draft/', output_dir=str(dandi_path), get_metadata=True, get_assets=False)
    dandi_organize(paths=str(directory_path), dandiset_path=str(dandi_path_set))

    # We need to add ses to file names manually when using dandi_organize
    organized_nwbfiles = glob(join(directory_path, dandiset_id,  'sub-*' ,  "*.nwb" ))
    for organized_nwbfile in organized_nwbfiles:
        file_path = Path(organized_nwbfile)
        if "ses" not in file_path.stem:
            with NWBHDF5IO(path=file_path, mode="r", load_namespaces=True) as io:
                nwbfile = io.read()
                session_id = session_id
            dandi_stem = file_path.stem
            dandi_stem_split = dandi_stem.split("_")
          
            dandi_stem_split.insert(1, f"ses-{session_id}")
            corrected_name = "_".join(dandi_stem_split)  + ".nwb"
            file_path.rename(file_path.parent / corrected_name)
    # Verify that the files are organized correctly
    organized_nwbfiles = glob(join(directory_path, dandiset_id,  'sub-*' ,  "*.nwb" ))
    print("ORGANIZED: ", organized_nwbfiles, flush=True)
    dandi_upload(paths=[str(x)
                     for x in organized_nwbfiles], dandi_instance='dandi')
    print(organized_nwbfiles)

    # Update the session status in firebase
    fb.update_session_status(args.project_id, args.sess_id, "Uploaded")
