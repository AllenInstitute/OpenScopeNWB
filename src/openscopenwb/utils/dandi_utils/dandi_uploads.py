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

import shutil


from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import clean_up_functions as cuf
 



def set_env():
    x = cuf.get_creds()
    os.environ["DANDI_API_KEY"] = x
def automatic_dandi_upload(
    dandiset_id: str,
    nwb_folder_path: str,
    session_id,
    experiment_id,
    subject_id,
    raw, 
    final
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
    dandiset_path = nwb_folder_path
    assert os.getenv("DANDI_API_KEY"), (
        "Unable to find environment variable 'DANDI_API_KEY'. "
        "Please retrieve your token from DANDI and set this environment variable."
    )

    #url_base = "https://gui-staging.dandiarchive.org" if staging else "https://dandiarchive.org"
    #dandiset_url = f"{url_base}/dandiset/{dandiset_id}/{version}"

    directory_path = os.path.join(nwb_folder_path, experiment_id)
    dandi_path = os.path.abspath(directory_path)
    dandi_path_set = directory_path  + "/" + dandiset_id
    print("PATHS: ", directory_path, dandi_path, dandi_path_set)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        os.makedirs(dandi_path_set)


    src = os.path.join(nwb_folder_path, experiment_id + "raw_data.nwb")
    dst = os.path.join(directory_path, experiment_id + ".nwb")

    # Move the nwb file to the session directory
    shutil.move(src, dst)
    

    dandi_download(urls=r'https://dandiarchive.org/dandiset/000336/draft/', output_dir=str(dandi_path), get_metadata=True, get_assets=False)
    dandi_organize(paths=str(directory_path), dandiset_path=str(dandi_path_set))
    organized_nwbfiles = glob(join(directory_path, dandiset_id,  'sub-' + subject_id,  "*.nwb" ))
    print("ORIGINAL ORGANIZED: ", organized_nwbfiles, flush=True)
    print(organized_nwbfiles)
    for organized_nwbfile in organized_nwbfiles:
        file_path = Path(organized_nwbfile)
        if "ses" not in file_path.stem:
            with NWBHDF5IO(path=file_path, mode="r", load_namespaces=True) as io:
                nwbfile = io.read()
                session_id = session_id
            dandi_stem = file_path.stem
            dandi_stem_split = dandi_stem.split("_")
            if raw == True:
                dandi_stem_split.insert(1, f"ses-{session_id}-acq-{experiment_id}raw")
            else:
                dandi_stem_split.insert(1, f"ses-{session_id}-acq-{experiment_id}raw")
            corrected_name = "_".join(dandi_stem_split)  + ".nwb"
            file_path.rename(file_path.parent / corrected_name)
    organized_nwbfiles = glob(join(directory_path, dandiset_id,  'sub-' + subject_id,  "*.nwb" ))
    print("ORGANIZED: ", organized_nwbfiles, flush=True)
    dandi_upload(paths=[str(x)
                     for x in organized_nwbfiles], dandi_instance='dandi')
    print(organized_nwbfiles)
   # dandi_upload(paths=[str(x) for x in organized_nwbfiles], dandi_instance='dandi')
    fb.start(fb.get_creds())
    if args.final == True:
        fb.update_session_dandi("OpenScopeDendriteCoupling", session_id, "sub_" + args.subject_id + '/' + session_id)
    fb.update_session_status("OpenScopeDendriteCoupling", args.session_id, "Uploaded")
    #organized_nwbfiles = dandiset_path.rglob("*.nwb")
   # print(organized_nwbfiles)

   

if __name__ == '__main__':
    """Uploads an NWB to dandi 

    Parameters
    ----------

    nwb_folder_path: str
    The current nwb's location
    dandiset_id: str
    The dandi set's id
    session_id: str
    The 10 digit session id for our data
    experiment_id: str
    The experiment id for the session's plane
    subject_id: str
    The external donor id for the session
    raw: bool
    Whether to include RAW data
    final: bool
    Whether this is the final plane for the sess

    Returns
    -------
    print("Uploading")
    parser = argparse.ArgumentParser()
    parser.add_argument('--nwb_folder_path', type=str)
    parser.add_argument('--dandiset_id', type=str)
    parser.add_argument('--subject_id', type=str)
    parser.add_argument('--session_id', type=str)
    parser.add_argument('--experiment_id', type=str)
    parser.add_argument('--raw', type=bool)
    parser.add_argument('--final', type=str)
    args = parser.parse_args()
    nwb_folder_path = args.nwb_folder_path
    dandiset_id = args.dandiset_id
    subject_id = args.subject_id
    session_id = args.session_id
    experiment_id = args.experiment_id
    raw = args.raw
    final = args.final
    automatic_dandi_upload(nwb_folder_path = nwb_folder_path, dandiset_id = dandiset_id, subject_id = subject_id, session_id = session_id, experiment_id = experiment_id, raw = raw, final = final)
