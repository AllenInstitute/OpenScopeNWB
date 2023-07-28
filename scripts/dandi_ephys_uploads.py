#!/usr/bin/env python
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import clean_up_functions as cuf
from glob import glob
from os.path import join

import argparse
import os
import shutil


from dandi.dandiapi import DandiAPIClient as dandi
from dandi.organize import organize as dandi_organize
from dandi.download import download as dandi_download
from dandi.upload import upload as dandi_upload
from pathlib import Path
from pynwb import NWBHDF5IO


if __name__ == "__main__":
    """Uploads all probes from a session

    Parameters
    ----------
    nwb_folder_path: str
    The path to the folder containing the nwb files
    dandiset_id: str
    The dandiset's id value
    sess_id: str
    The session's id value
    project_id: str
    The project's id string from LIMS (e.g. 'OpenScopeDendriteCoupling')
    subject_id: str
    The subject's SIX DIGIT DONOR id value

    Returns
    -------
    sess_list: list
    A list of all the sessions
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--nwb_folder_path', type=str)
    parser.add_argument('--dandiset_id', type=str)
    parser.add_argument('--sess_id', type=str)
    parser.add_argument('--project_id', type=str)
    parser.add_argument('--subject_id', type=str)
    args = parser.parse_args()
    dandi_api_key = os.getenv("DANDI_API_KEY")
    if dandi_api_key is not None:
        print("DANDI_API_KEY is set")
    else:
        os.environ['DANDI_API_KEY'] = cuf.get_creds()
    nwb_folder_path = args.nwb_folder_path
    dandiset_id = args.dandiset_id
    dandi_set = dandi()
    dandi_set.dandi_authenticate()
    dandi_dataset = dandi_set.get_dandiset(dandiset_id)
    session_id = args.sess_id
    project_id = args.project_id
    subject_id = args.subject_id

    dandiset_path = nwb_folder_path
    assert os.getenv("DANDI_API_KEY"), (
        "Unable to find environment variable 'DANDI_API_KEY'. "
        "Please retrieve your token from DANDI"
        "and set this environment variable."
    )

    # Create the session directory
    directory_path = os.path.join(nwb_folder_path)
    dandi_path = os.path.abspath(directory_path)
    dandi_path_set = directory_path + "/" + dandiset_id
    print("PATHS: ", directory_path, dandi_path, dandi_path_set)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        os.makedirs(dandi_path_set)

    # Rename the nwb file to include the session id
    src = os.path.join(nwb_folder_path,  "spike_times.nwb")
    dst = os.path.join(directory_path, session_id + ".nwb")

    # Move the nwb file to the session directory
    shutil.move(src, dst)

    dandi_download(urls=r'https://dandiarchive.org/dandiset/' + dandiset_id +
                   '/draft/', output_dir=str(dandi_path),
                   get_metadata=True, get_assets=False)
    dandi_organize(paths=str(directory_path),
                   dandiset_path=str(dandi_path_set))

    # We need to add ses to file names manually when using dandi_organize
    organized_nwbfiles = glob(
        join(directory_path, dandiset_id,  'sub-*',  "*.nwb"))
    for organized_nwbfile in organized_nwbfiles:
        file_path = Path(organized_nwbfile)
        if "ses" not in file_path.stem:
            with NWBHDF5IO(path=file_path, mode="r",
                           load_namespaces=True) as io:
                nwbfile = io.read()
                session_id = session_id
            dandi_stem = file_path.stem
            dandi_stem_split = dandi_stem.split("_")

            dandi_stem_split.insert(1, f"ses-{session_id}")
            corrected_name = "_".join(dandi_stem_split) + ".nwb"
            file_path.rename(file_path.parent / corrected_name)
    # Verify that the files are organized correctly
    organized_nwbfiles = glob(
        join(directory_path, dandiset_id,  'sub-*',  "*.nwb"))
    print("ORGANIZED: ", organized_nwbfiles, flush=True)
    dandi_upload(paths=[str(x)
                        for x in organized_nwbfiles], dandi_instance='dandi')
    print(organized_nwbfiles)

    # Update the session status in firebase
    fb.update_session_status(args.project_id, args.sess_id, "Uploaded")
