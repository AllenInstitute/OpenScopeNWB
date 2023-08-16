import pytest
from openscopenwb.utils import allen_functions as af


@pytest.fixture
def get_e_donor_prep():
    sess_id = 1170425945
    info = {
        'gender': 'F',
        'genotype': 'Sst-IRES-Cre/wt;Ai32(RCL-ChR2(H134R)_EYFP)/wt',
        'dob': '2022-02-14T16:00:00.000-08:00',
        'name': '621891',
        'id': sess_id
    }
    yield info


@pytest.fixture
def get_o_donor_prep():
    sess_id = 1199275030
    info = {
        'gender': 'F',
        'genotype': "Cux2-CreERT2/wt;Camk2a-tTA/wt;Ai93(TITL-GCaMP6f)/wt",
        'dob': '2022-06-20T17:00:00.000-07:00',
        'name': '638955',
        'id': sess_id
    }
    yield info


def test_get_e_donor(get_e_donor_prep):
    sess_id = '1179909741'
    info = af.lims_subject_info(sess_id)
    assert info == get_e_donor_prep


def test_get_o_donor(get_o_donor_prep):
    sess_id = '1226237853'
    info = af.lims_o_subject_info(sess_id)
    assert info == get_o_donor_prep
