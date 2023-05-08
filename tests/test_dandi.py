import pytest
import dandi 
import os
import shlex
import subprocess

from dandi.download import download as dandi_download
from openscopenwb.utils import clean_up_functions as cuf



@pytest.fixture
def dandi_prep():
    test_dict = {
        "file_path": os.path.join(
                        os.path.dirname(__file__),
                        "../samples/test_dandi_download/"),
        "dandiset_id": '000150',
        "session_id": '000150',   
        "project_id": 'test',
        'subject_id': 'test'
    }
    yield test_dict

def test_dandi_download(dandi_prep):
    os.environ['DANDI_API_KEY'] = cuf.get_creds()

    dandi_download(urls=r'https://dandiarchive.org/dandiset/' + dandi_prep['dandiset_id']
                   + '/draft/', output_dir=str(dandi_prep['file_path'])
                   , get_metadata=True, get_assets=True)
    assert os.path.exists(dandi_prep['file_path'] + dandi_prep['session_id'])


def test_dandi_upload(dandi_prep):
    os.environ['DANDI_API_KEY'] = cuf.get_creds()
    cmd = "./scripts/dandi_ephys_uploads.py --nwb_folder_path " + dandi_prep['file_path'] + \
          " --dandiset_id " + dandi_prep['dandiset_id'] + " --sess_id " + \
          dandi_prep['session_id'] + " --project_id " + dandi_prep['project_id'] + \
          " --subject_id " + dandi_prep['subject_id']
    subprocess.run(shlex.split(cmd))
    assert os.path.exists(dandi_prep['file_path'] + dandi_prep['session_id'] + "/" +
                          dandi_prep['dandiset_id'] + "sub-{subject_id}}")

