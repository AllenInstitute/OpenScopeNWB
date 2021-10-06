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
        "string": "Hello World"
    }
    json_path = os.path.join(tmpdir, "test.json")
    with open(json_path, 'w') as json_file:
        json.dump(test_json, json_file)
    yield json_path


def test_parsing(json_prep, tmpdir):
    test_dict = ppp.parse_json(json_prep)
    test_probes = ppp.get_probes(test_dict)
    assert test_probes == ["probeA"]
