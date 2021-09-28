import pytest
import openscopenwb.ecephys_modules as ecephys_mod
import os

@pytest.fixture
def session_param_prep(tmpdir):
    session_parameters = {
        'base_directory': tmpdir
    }
    opto_pkl_path = os.path.join(session_parameters['base_directory'],
                                 'test.opto.pkl')
    sync_path = os.path.join(session_parameters['base_directory'],
                             'test.sync')
    opto_table_path = os.path.join(session_parameters['base_directory'],
                                   'test.optotagging_table.csv')
    open(opto_pkl_path, mode='w').close()
    open(sync_path, mode='w').close()
    open(opto_table_path, mode='w').close()
    yield session_parameters


def test_ecephys_optotagging(session_param_prep, tmpdir):
    test_json = ecephys_mod.ecephys_optotagging_table(session_param_prep)
    assert test_json['opto_pickle_path'] == os.path.join(session_param_prep['base_directory'],
                                                         'test.opto.pkl')
    assert test_json['sync_h5_path'] == os.path.join(session_param_prep['base_directory'],
                                                     'test.sync')
    assert test_json['output_opto_table_path'] == os.path.join(session_param_prep['base_directory'],
                                                               'optotagging_table.csv')
