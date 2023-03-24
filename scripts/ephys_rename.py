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
#from pynwb.base import ImageReferences
from dandi.organize import organize as dandi_organize
from dandi.download import download as dandi_download
from dandi.upload import upload as dandi_upload


def get_creds():
    '''Gets DANDI API key from .cred file
    
    Parameters
    ----------
    Returns
    ----------
    cred_json['api_key']: str
        DANDI API key
    '''
    cred_file = open(
        r'/allen/programs/mindscope/workgroups/openscope/ahad/test_cron/OpenScopeNWB-feature-firebase_testing/src/openscopenwb/utils/.cred/dandi.json')
    cred_json = json.load(cred_file)
    return cred_json['api_key']


def set_env():
    '''Sets DANDI API key as environment variable
    
    Parameters
    ----------
    Returns
    ----------
    '''
    os.environ['DANDI_API_KEY'] = get_creds()


def rename_sessions(probe=False, dandi_id):
    """Downloads, renames, and reuploads sessions on dandi

    Parameters
    ----------
    probe: bool
        If True, only probe files will be renamed
    dandi_id: str
        Dandi ID of the dandiset to be renamed
    Returns
    -------
    """
    set_env()
    dandiset_id = dandi_id
    dandi_api_key = os.environ['DANDI_API_KEY']
    my_dandiset = dandiapi.DandiAPIClient(token=dandi_api_key).get_dandiset(dandiset_id)

    nwb_table = []
    for file in my_dandiset.get_assets():
        path = file.path
        if probe and 'probe' not in path:
            continue
        print(f"Examining file {file.identifier}")
        print(file.path)

        # Get the file URL
        base_url = file.client.session.head(file.base_download_url)
        file_url = base_url.headers['Location']
        selected_path = path
        filename = selected_path.split("/")[-1]
        file = my_dandiset.get_asset_by_path(selected_path)

        specimen_number = None
        session_number = None
        probe_letter = None

        # Get the relevant IDs from the path
        match = re.search(r'sub_(\d+)', selected_path)
        if match:
            specimen_number = match.group(1)

        match = re.search(r'sess_(\d+)', selected_path)
        if match:
            session_number = match.group(1)

        match = re.search(r'exp_(\d+)', selected_path)
        if match:
            exp_number = match.group(1)

        # Check if a probe letter is present
        match = re.search(r'probe([A-Za-z])', selected_path)
        if match:
            probe_letter = match.group(1)

        session_number = session_number
        base_path = "/allen/programs/mindscope/workgroups/openscope/openscopedata2022/ephys"
        directory_path = os.path.join(base_path, session_number)
        dandi_path = os.path.abspath(directory_path)
        dandi_path_set = os.path.join(dandi_path, dandiset_id)

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            os.makedirs(dandi_path_set)

        file.download(os.path.join(directory_path, filename))
        downloaded_files = glob(os.path.join(directory_path, "*.nwb"))[0]

        dandi_download(urls='https://dandiarchive.org/dandiset/000253/draft', 
                       output_dir=dandi_path, get_metadata=True, get_assets=False)
        dandi_organize(paths=directory_path, dandiset_path=dandi_path_set)

        dst = os.path.join(directory_path, dandi_id, "dandiset.yaml")
        src = glob(os.path.join(dandi_path_set, "*.yaml"))[0]

        # Move the dandiset.yaml file to the correct location
        shutil.move(src, dst)

        organized_files = glob(os.path.join(dandi_path_set, "sub-*", "*.nwb"))
        print(dandi_path_set, flush=True)
        print(os.path.join(dandi_path_set, f"sub-{specimen_number}"), flush=True)
        print(organized_files, flush=True)

        for organized_nwbfile in organized_files:
            file_path = Path(organized_nwbfile)

            if "ses" not in file_path.stem:
                with NWBHDF5IO(path=file_path, mode="r+", load_namespaces=True) as io:
                    nwbfile = io.read()
                    session_id = session_number

            dandi_stem = file_path.stem
            dandi_stem_split = dandi_stem.split("_")
            dandi_stem_split.insert(1, f"ses-{session_id}")
            corrected_name = "_".join(dandi_stem_split) + ".nwb"

            # Make sure conventions are followed
            if probe:
                corrected_name = corrected_name.replace("_ecephys.nwb", '')
                file_path.rename(file_path.parent /
                                (corrected_name + "_" + "probe-" + probe_letter + '_ecephys.nwb'))
            else:
                file_path.rename(file_path.parent / corrected_name)

        organized_nwbfiles = glob(join(dandi_path_set,  "sub-*", "*.nwb"))
        print(organized_nwbfiles, flush=True)
        dandi_upload(paths=[str(x) for x in organized_nwbfiles], dandi_instance='dandi')

        # The sleep is needed to prevent the dandi server from rejecting the upload
        time.sleep(600)

        rmtree(path=directory_path)





if __name__ == '__main__':
    rename_session(True, "000253")