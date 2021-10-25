import pytest
import openscopenwb.ecephys_modules as ecephys_mod
import os
from glob import glob
from os.path import join


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

    stim_pkl_path = os.path.join(session_parameters['base_directory'],
                                 "test.stim.pkl")
    stim_h5_path = os.path.join(session_parameters['base_directory'],
                                "test.sync")
    stim_table_path = os.path.join(
                        session_parameters['base_directory'],
                        "stim_table_allensdk.csv")
    stim_frame_times_path = os.path.join(
                        session_parameters['base_directory'],
                        "frame_times.npy")
    open(stim_pkl_path, mode='w').close()
    open(stim_h5_path, mode='w').close()
    open(stim_table_path, mode='w').close()
    open(stim_frame_times_path, mode='w').close()

    run_h5_path = os.path.join(session_parameters['base_directory'],
                               "running_speed.h5")
    open(run_h5_path, mode='w').close()

    yield session_parameters


def test_ecephys_optotagging(session_param_prep, tmpdir):
    _, test_json = ecephys_mod.ecephys_optotagging_table(session_param_prep)

    assert test_json['opto_pickle_path'] == \
        os.path.join(session_param_prep['base_directory'],
                     'test.opto.pkl')
    assert test_json['sync_h5_path'] == \
        os.path.join(session_param_prep['base_directory'],
                     'test.sync')
    assert test_json['output_opto_table_path'] == \
        os.path.join(session_param_prep['base_directory'],
                     'optotagging_table.csv')


def test_ecephys_stim_table(session_param_prep, tmpdir):
    params, test_json = ecephys_mod.stimulus_table(session_param_prep)
    assert test_json['stimulus_pkl_path'] == \
        os.path.join(session_param_prep['base_directory'],
                     "test.stim.pkl")
    assert test_json['sync_h5_path'] == \
        os.path.join(session_param_prep['base_directory'],
                     "test.sync")
    assert test_json['output_stimulus_table_path'] == \
        os.path.join(session_param_prep['base_directory'],
                     "stim_table_allensdk.csv")
    assert test_json['output_frame_times_path'] == \
        os.path.join(session_param_prep['base_directory'],
                     "frame_times.npy")


def test_running_speed(session_param_prep, tmpdir):
    params, test_json = ecephys_mod.extract_running_speed(session_param_prep)
    assert test_json['stimulus_pkl_path'] == \
        os.path.join(session_param_prep['base_directory'],
                     "test.stim.pkl")
    assert test_json['sync_h5_path'] == \
        os.path.join(session_param_prep['base_directory'],
                     "test.sync")
    assert test_json['output_path'] == \
        os.path.join(session_param_prep['base_directory'],
                     "running_speed.h5")
