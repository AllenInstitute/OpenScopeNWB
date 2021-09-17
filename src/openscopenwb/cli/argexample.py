import argschema
import hashlib
import math
from pathlib import Path
from typing import Union

from openscopenwb.cli.schemas import (
        ArgExampleInputSchema, ArgExampleOutputSchema)


def hash_my_file(file_path: Union[Path, str]) -> str:
    """computes the sha256 hash of a file

    Parameters
    ----------
    file_path: str or Path
        the path to the file for hashing

    Returns
    -------
    hexhash: str
        the hexadecimal hash of file_path

    """
    with open(file_path, "rb") as f:
        bytes = f.read()
        hexhash = hashlib.sha256(bytes).hexdigest()
    return hexhash


def my_diff(x: float) -> float:
    """difference function, computes pi - x

    Parameters
    ----------
    x: float
        arg to difference

    Returns
    -------
    diff: float
        the difference

    """
    diff = math.pi - x
    return diff


class ArgExample(argschema.ArgSchemaParser):
    default_schema = ArgExampleInputSchema
    default_output_schema = ArgExampleOutputSchema

    def run(self):
        self.logger.info("computing hash of input file "
                         f"{self.args['my_file']}")
        hexhash = hash_my_file(self.args["my_file"])

        self.logger.info("computing difference from pi")
        diff = my_diff(self.args['my_float'])

        output_dict = {
                "my_file_hash": hexhash,
                "my_float_diff_from_pi": diff}

        self.output(output_dict, indent=2)
        self.logger.info(f"wrote output {self.args['output_json']}")


if __name__ == "__main__":  # pragma: no cover
    ae = ArgExample()
    ae.run()
