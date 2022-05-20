import pytest
from scripts.generate_json import generate_ephys_json as gen_e_json



@pytest.fixture
def gres_sess_prep():
    test_dict = {
        "modules": ["allensdk.brain_observatory.ecephys.align_timestamps",
            "allensdk.brain_observatory.ecephys.stimulus_table",
            "allensdk.brain_observatory.extract_running_speed",
            "allensdk.brain_observatory.ecephys.write_nwb"]
    }
    yield test_dict


def test_sessions(gres_sess_prep):
    info_list = gen_e_json(1172129291)
    assert gres_sess_prep['modules'] == info_list['modules']