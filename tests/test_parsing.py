import pytest
import os
import json
from openscopenwb.utils import parse_project_parameters as ppp


@pytest.fixture
def json_prep(tmpdir):
    test_json = {
        "probes": [
            "probeA"
        ],
        "modules": [
            "module"
        ],
        "sessions": [
            "session"
        ],
        "lims": [
            "test"
        ],
        "nwb_path": "nwb_path",
        "input_json": "input_path",
        "output_json": "output_path",
        "session_dir": "session_dir",
        "trim_discontiguous_frame_times": False,
        "last_unit_id": 1,
    }
    json_path = os.path.join(tmpdir, "test.json")
    with open(json_path, 'w') as json_file:
        json.dump(test_json, json_file)
    yield json_path


def test_parsing(json_prep, tmpdir):
    test_dict = ppp.parse_json(json_prep)
    test_probes = ppp.get_probes(test_dict)
    test_ids = ppp.get_session_ids(test_dict)
    test_modules = ppp.get_modules(test_dict)
    test_input = ppp.get_input_json_directory(test_dict)
    test_output = ppp.get_output_json_directory(test_dict)
    test_lims = ppp.get_lims_path(test_dict)
    test_nwb = ppp.get_output_nwb_path(test_dict)
    test_sess_dir = ppp.get_session_dir(test_dict)
    test_trim = ppp.get_trim(test_dict)
    assert test_probes == ["probeA"]
    assert test_ids == ["session"]
    assert test_modules == ["module"]
    assert test_input == "input_path"
    assert test_output == "output_path"
    assert test_lims == ["test"]
    assert test_nwb == "nwb_path"
    assert test_sess_dir == "session_dir"
    assert test_trim is False
