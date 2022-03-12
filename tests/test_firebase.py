import pytest
import os
from openscopenwb.utils import firebase_functions as fb



@pytest.fixture
def firebase_prep():
    test_dict = {
        "session_1_date": "2/12/2022",
        "session_1_mouse": "408021",
        "session_1_pass": "Pass",
        "session_1_stimulus_type": "Stimuli",
        "session_1_type": "Ophys"
    }
    yield test_dict

def test_sess_meta(firebase_prep):
    dir = os.path.dirname(__file__)
    cred_json = os.path.join  (dir, 'openscopetest-d7614-firebase-adminsdk-bwzou-b9942c1cd6.json')
    fb.start(cred_json)
    session_meta = fb.view_session("Project_test_id", 758519303)
    assert session_meta['session_type'] == firebase_prep['session_1_type']
    assert session_meta['session_date'] == firebase_prep['session_1_date']
    assert session_meta['session_pass'] == firebase_prep['session_1_pass']
    assert session_meta['session_stimulus_type'] == firebase_prep['session_1_stimulus_type']
    assert session_meta['session_mouse'] == firebase_prep['session_1_mouse']