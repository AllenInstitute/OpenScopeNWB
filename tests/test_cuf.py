import pytest
import numpy as np
from openscopenwb.utils import clean_up_functions as cuf


@pytest.fixture
def cuf_prep():
    test_list = [-2, 7, np.nan]
    yield test_list


def test_clean_up(cuf_prep):
    assert cuf.clean_up_nan_and_inf(cuf_prep[0]) == -2
    assert cuf.clean_up_nan_and_inf(cuf_prep[1]) == 7
    assert cuf.clean_up_nan_and_inf(cuf_prep[2]) == -1
