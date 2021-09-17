import pytest
import math
from pathlib import Path

import openscopenwb.cli.argexample as ae


@pytest.fixture
def file_fixture(tmpdir):
    """creates a file with some content
    """
    file_path = tmpdir / "mytmpfile.txt"
    with open(file_path, "w") as f:
        f.write("some content")
    yield str(file_path)


def test_hash_my_file(file_fixture):
    """tests that the file gets hashed into a string

    Notes
    -----
    normally, a good unit test would check that the return value is correct.
    In this simple case, I am only testing the return type of the function.

    """
    hashstr = ae.hash_my_file(file_fixture)
    assert isinstance(hashstr, str)


@pytest.mark.parametrize(
        "x, expected",
        [
            (1.0, math.pi - 1.0),
            (0.0, math.pi - 0.0),
            (-1.0, math.pi + 1.0)])
def test_my_diff(x, expected):
    """tests the the function my_diff provides the expected result.
    """
    mydiff = ae.my_diff(x)
    assert mydiff == expected


def test_ArgExample(file_fixture, tmpdir):
    output_path = Path(tmpdir / "example_output.json")
    input_args = {
            "my_file": file_fixture,
            "my_float": 1.0,
            "output_json": str(output_path)}
    argex = ae.ArgExample(input_data=input_args, args=[])
    argex.run()
    assert output_path.exists()
