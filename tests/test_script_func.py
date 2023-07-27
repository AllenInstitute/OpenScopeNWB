import pytest
from openscopenwb.utils import script_functions as sf


@pytest.fixture
def module_prep():
    conda_environment = 'openscopenwb'
    module = 'test_module_name'
    input_json = '/path/to/input.json'
    output_json = '/path/to/output.json'
    expected_cmd = [
        '/allen/programs/mindscope/workgroups/openscope/ahad/Conda_env/openscopenwb/bin/python',
        '-W', 'ignore', '-m', 'test_module_name',
        '--input_json', '/path/to/input.json',
        '--output_json', '/path/to/output.json'
    ]

    yield expected_cmd

def test_script_module(module_prep):
    module = 'test_module_name'
    input_json = '/path/to/input.json'
    output_json = '/path/to/output.json'
    assert sf.generate_module_cmd(module, input_json, output_json) == module_prep