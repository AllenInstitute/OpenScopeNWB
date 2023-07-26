import os
import re

import fsspec
import h5py
import pandas as pd
import json
import shutil
import time


from pathlib import Path
from dandi import dandiapi
from fsspec.implementations.cached import CachingFileSystem
from pynwb import NWBHDF5IO
from pynwb.base import Images
from glob import glob
from os.path import join
from shutil import rmtree


from dandi.dandiapi import DandiAPIClient as dandi
# from pynwb.base import ImageReferences
from dandi.organize import organize as dandi_organize
from dandi.download import download as dandi_download
from dandi.upload import upload as dandi_upload


def get_creds():
    """
    Gets DANDI API key from .cred file

    Returns
    -------
    str
        DANDI API key
    """
    cred_file_path = (
        "/allen/programs/mindscope/workgroups/openscope/"
        "ahad/test_cron/OpenScopeNWB-feature-firebase_testing/"
        "src/openscopenwb/utils/.cred/dandi.json"
    )
    with open(cred_file_path) as cred_file:
        cred_json = json.load(cred_file)
    return cred_json["api_key"]


def set_env():
    '''Sets DANDI API key as environment variable

    Parameters
    ----------
    Returns
    ----------
    '''
    os.environ['DANDI_API_KEY'] = get_creds()


def rename_sessions(Raw, dandi_id):
    """Downloads, renames, and reuploads sessions on dandi

    Parameters
    ----------
    Raw: bool
        If True, only RAW files will be renamed
    dandi_id: str
        Dandi ID of the dandiset to be renamed
    Returns
    -------
    """
    # set up dandi client
    set_env()
    dandiset_id = dandi_id
    authenticate = True
    dandi_api_key = os.environ['DANDI_API_KEY']
    my_dandiset = dandiapi.DandiAPIClient(
        token=dandi_api_key).get_dandiset(dandiset_id)

    # set up streaming filesystem
    fs = fsspec.filesystem("http")

    nwb_table = []
    for file in my_dandiset.get_assets():
        path = file.path
        # skip files that aren't main session files
        if raw:
            if "raw" not in file.path or "exp" not in file.path:
                continue
        else:
            if "exp" not in file.path:
                continue

        print(f"Examining file {file.identifier}")
        print(file.path)

        # get file url
        base_url = file.client.session.head(file.base_download_url)
        file_url = base_url.headers['Location']
        selected_path = path
        filename = selected_path.split("/")[-1]
        file = my_dandiset.get_asset_by_path(selected_path)

        # grab relevant IDs from file path
        match = re.search(r'sub_(\d+)', selected_path)
        if match:
            specimen_number = match.group(1)
        match = re.search(r'sess_(\d+)', selected_path)
        if match:
            session_number = match.group(1)
        match = re.search(r'exp_(\d+)', selected_path)
        if match:
            exp_number = match.group(1)

        # Rename session if raw
        if raw:
            session_number = session_number + "_acq-" + exp_number + "-raw"
        else:
            session_number = session_number + "_acq-" + exp_number

        base_path = ("/allen/programs/mindscope/workgroups/openscope/" +
                     "openscopedata2022/ophys")
        directory_path = os.path.join(base_path, session_number)
        dandi_path = os.path.abspath(directory_path)
        dandi_path_set = dandi_path + "/" + dandiset_id
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            os.makedirs(dandi_path_set)
        file.download(f"{directory_path}/{filename}")

        downloaded_files = glob(join(directory_path, "*.nwb"))[0]
        file_path = Path(downloaded_files)
        dandi_download(urls='https://dandiarchive.org/dandiset/000336/draft',
                       output_dir=str(dandi_path),
                       get_metadata=True,
                       get_assets=False)
        dandi_organize(paths=directory_path,
                       dandiset_path=dandi_path_set)
        dst = directory_path + '/' + "sub-" + specimen_number
        src = (directory_path + "/" + dandiset_id +
               "/" + "sub-" + specimen_number)
        shutil.move(src, dst)

        organized_files = glob(
            join(dandi_path_set,  "sub-" + specimen_number, "*.nwb"))
        print(dandi_path_set, flush=True)
        print(join(dandi_path_set,  "sub-" + specimen_number) +
              "-exp-" + exp_number, flush=True)
        print(organized_files, flush=True)
        for organized_nwbfile in organized_files:
            file_path = Path(organized_nwbfile)
            if "ses" not in file_path.stem:
                print("SESS")
                with NWBHDF5IO(path=file_path, mode="r+",
                               load_namespaces=True) as io:
                    nwbfile = io.read()
                    session_id = session_number
                dandi_stem = file_path.stem
                dandi_stem_split = dandi_stem.split("_")
                dandi_stem_split.insert(1, f"ses-{session_id}")
                corrected_name = "_".join(dandi_stem_split) + ".nwb"
                file_path.rename(file_path.parent / corrected_name)
        organized_nwbfiles = glob(
            join(dandi_path_set,  "sub-" + specimen_number, "*.nwb"))
        print(organized_nwbfiles, flush=True)
        dandi_upload(paths=[str(x)
                     for x in organized_nwbfiles],
                     dandi_instance='dandi')

        # The sleep is needed to prevent the dandi server
        # from rejecting the upload
        time.sleep(600)

        rmtree(path=directory_path)

if __name__ == '__main__':
    rename_sessions(True, "000336")
