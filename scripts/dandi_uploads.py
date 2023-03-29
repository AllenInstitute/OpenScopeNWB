#!/usr/bin/env python
import dandi
from dandi.dandiapi import DandiAPIClient as dandi
from dandi import validate as validate
from dandi.organize import organize as dandi_organize
from dandi.download import download as dandi_download
from dandi.upload import upload as dandi_upload
from pathlib import Path

from pynwb import NWBHDF5IO

import argparse
import os
import json

from os.path import join
from glob import glob




from openscopenwb.utils import firebase_functions as fb
 

def get_creds():
    cred_file = open(
        r'/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/src/openscopenwb/utils/.cred/dandi.json')
    cred_json = json.load(cred_file)
    return cred_json['api_key']


def set_env():
    os.environ['DANDI_API_KEY'] = get_creds()
def automatic_dandi_upload(
    #dandiset_id: str,
    #nwb_folder_path: str,
    #dandiset_folder_path: str,
    #version: str = "draft",
    #staging: bool = False,
    #cleanup: bool = False,
):
    """
    Fully automated upload of NWBFiles to a DANDISet.
    Requires an API token set as an envrinment variable named DANDI_API_KEY.
    To set this in your bash terminal in Linux or MacOS, run
        export DANDI_API_KEY=...
    or in Windows
        set DANDI_API_KEY=...
    DO NOT STORE THIS IN ANY PUBLICLY SHARED CODE.
    Parameters
    ----------
    dandiset_id : str
        Six-digit string identifier for the DANDISet the NWBFiles will be uploaded to.
    nwb_folder_path : folder path
        Folder containing the NWBFiles to be uploaded.
    dandiset_folder_path : folder path, optional
        A separate folder location within which to download the dandiset.
        Used in cases where you do not have write permissions for the parent of the 'nwb_folder_path' directory.
        Default behavior downloads the DANDISet to a folder adjacent to the 'nwb_folder_path'.
    version : {None, "draft", "version"}
        The default is "draft".
    staging : bool, default: False
        Is the DANDISet hosted on the staging server? This is mostly for testing purposes.
        The default is False.
    cleanup : bool, default: False
        Whether to remove the dandiset folder path and nwb_folder_path.
        Defaults to False.
    """
    set_env()
    dandiset_path = r'/allen/programs/mindscope/workgroups/openscope/openscopedata2022/1189887297/2023-02-01-11-02/nwb_path/1189887297'
    assert os.getenv("DANDI_API_KEY"), (
        "Unable to find environment variable 'DANDI_API_KEY'. "
        "Please retrieve your token from DANDI and set this environment variable."
    )

    #url_base = "https://gui-staging.dandiarchive.org" if staging else "https://dandiarchive.org"
    #dandiset_url = f"{url_base}/dandiset/{dandiset_id}/{version}"


    #dandi_organize(paths=str(dandiset_path), dandiset_path=str(dandiset_path)))
    organized_nwbfiles = glob(join(dandiset_path, 'sub-1177693335',  "*.nwb" ))
    dandi_download(urls=r'https://dandiarchive.org/dandiset/000248/draft/', output_dir=str(dandiset_path), get_metadata=True, get_assets=False)
    print(organized_nwbfiles)
    for organized_nwbfile in organized_nwbfiles:
        file_path = Path(organized_nwbfile)
        if "ses" not in file_path.stem:
            with NWBHDF5IO(path=file_path, mode="r", load_namespaces=True) as io:
                nwbfile = io.read()
                session_id = nwbfile.session_id
            dandi_stem = file_path.stem
            dandi_stem_split = dandi_stem.split("_")
            dandi_stem_split.insert(1, f"ses-{session_id}")
            corrected_name = "_".join(dandi_stem_split) + ".nwb"
            file_path.rename(file_path.parent / corrected_name)
    organized_nwbfiles = glob(join(dandiset_path, 'sub-1177693335',  "*.nwb" ))
    print(organized_nwbfiles)
    dandi_upload(paths=[str(x) for x in organized_nwbfiles], dandi_instance='dandi')
    #organized_nwbfiles = dandiset_path.rglob("*.nwb")
   # print(organized_nwbfiles)

   

if __name__ == '__main__':
    automatic_dandi_upload()

'''
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
                'path': 'sub_' + args.subject_id + '/' 'sub_' + args.subject_id + 'sess_' + args.sess_id + '/' + 'sub_' + args.subject_id + '+sess_' + args.sess_id + 'exp_' + args.exp_id + '+raw_ophys.nwb',
                "dandiset": str(dandi_dataset)})
    else:
        status = dandi_dataset.iter_upload_raw_asset(
            args.dandi_file,
            asset_metadata={
                'path': 'sub_' + args.subject_id + '/' 'sub_' + args.subject_id + 'sess_' + args.sess_id + '/' +  'sub_' + args.subject_id + '+sess_' + args.sess_id + 'exp_' + args.exp_id + 'ophys.nwb',
                "dandiset": str(dandi_dataset)})
    print("STATUS")
    print(list(status))
    os.remove(args.dandi_file)
    npy_files = glob(args.subject_id + "*.npy")
    print(npy_files)
    fb.start(fb.get_creds())


    if args.final == 'True':
        fb.update_session_dandi(args.project_id, args.sess_id, "sub_" + args.subject_id + '/' + args.sess_id)
    fb.update_session_status(args.project_id, args.sess_id, "Uploaded")
'''
