from pathlib import Path
import json
import pandas as pd
import numpy as np
# from openscopenwb.utils import clean_up_functions as cuf
# from os.path import join
import pynwb
import h5py
from pynwb import NWBFile
from pynwb.file import TimeSeries
from pynwb.ophys import TwoPhotonSeries, ImagingPlane, OpticalChannel
from pynwb import NWBHDF5IO
from hdmf.backends.hdf5.h5_utils import H5DataIO


def process_suit2p(raw_params):
    """Adds RAW info to an NWB 

    Parameters
    ----------
    raw_params: dict
    Contains the nwb's file path and other data

    Returns
    -------
    """
    print("Processing timeseries data")
    with h5py.File(raw_params['suite_2p'], "r") as suite2p:
        data = suite2p['data']
        wrapped_data = H5DataIO(
            data=data,
            compression='gzip',
            compression_opts=4,
            chunks=True,
            maxshape=(None, 100)
        )
        nwb_file = raw_params['nwb_path']
        io = NWBHDF5IO(nwb_file, "r+", load_namespaces=True)
        input_nwb = io.read()
        try:
            ts = TwoPhotonSeries(
                name='raw_suite2p_motion_corrected',
                imaging_plane=input_nwb.processing['ophys']['image_segmentation']['cell_specimen_table'].imaging_plane,
                data=wrapped_data,
                format='raw',
                unit='SIunit',
                rate=10.71
            )
        except KeyError:
            channel = OpticalChannel(
                name='place_holder Channel',
                description='place_holder Channel',
                emission_lambda=488.0
            )
            plane = input_nwb.create_imaging_plane(
                name='imaging_plane',
                optical_channel=channel,
                description='Failed Cell Segmentation',
                device = input_nwb.devices['MESO.2'],
                excitation_lambda=488.0,
                imaging_rate=10.71,
                indicator='GCaMP6f',
                location='Failed Cell Segmentation',
            )
            ts = TwoPhotonSeries(
                name='raw_suite2p_motion_corrected',
                imaging_plane=plane,
                data=wrapped_data,
                format='raw',
                unit='SIunit',
                rate=10.71
            )
        input_nwb.add_acquisition(ts)
        io.write(input_nwb)
