import pytest
import datetime
from openscopenwb.utils import postgres_functions as postgres


@pytest.fixture
def gres_sess_prep():
    test_dict = {
        "name": "20211029_594315_SN2",
        "date": '2021-10-29T15:07:27.150000',
        "mouse": '594315',
        "stim": 'SNR_2',
        "img": None,
        "operator": 51,
        "equip": 1053461091
    }
    yield test_dict


def test_sessions(gres_sess_prep):
    info_list = postgres.get_o_sess_info(1137276124)
    mouse = info_list['mouse']
    name = info_list['name']
    date = info_list['date']
    stim = info_list['stim']
    img = info_list['img']
    operator = info_list['operator']
    equip = info_list['equip']
    assert mouse == gres_sess_prep['mouse']
    assert name == gres_sess_prep['name']
    assert date == gres_sess_prep['date']
    assert stim == gres_sess_prep['stim']
    assert img == gres_sess_prep['img']
    assert operator == gres_sess_prep['operator']
    assert equip == gres_sess_prep['equip']
