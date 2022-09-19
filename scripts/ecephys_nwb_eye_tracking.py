from requests import NullHandler
from allensdk.brain_observatory.behavior.data_objects.eye_tracking.eye_tracking_table import (
    EyeTrackingTable
)
from allensdk.brain_observatory import sync_utilities
from allensdk.brain_observatory.behavior.data_files import SyncFile
from allensdk.brain_observatory.behavior.data_files.eye_tracking_file import \
    EyeTrackingFile
from allensdk.brain_observatory.behavior.data_objects import DataObject
from allensdk.brain_observatory.behavior.data_objects.base \
    .readable_interfaces import \
    NwbReadableInterface, DataFileReadableInterface
from allensdk.brain_observatory.behavior.data_objects.base \
    .writable_interfaces import \
    NwbWritableInterface
from allensdk.brain_observatory.behavior.eye_tracking_processing import \
    process_eye_tracking_data, determine_outliers, determine_likely_blinks, \
    compute_elliptical_area, compute_circular_area, load_eye_tracking_hdf, EyeTrackingError
from allensdk.brain_observatory.nwb.eye_tracking.ndx_ellipse_eye_tracking \
    import \
    EllipseSeries, EllipseEyeTracking
from allensdk.brain_observatory.sync_dataset import Dataset
from pathlib import Path
import json
import pandas as pd
import numpy as np
# from openscopenwb.utils import clean_up_functions as cuf
# from os.path import join
import pynwb
from pynwb import NWBFile, TimeSeries
from pynwb import NWBHDF5IO


def add_eye_tracking_nwb(eye_tracking_df, nwb_file):
        eye_tracking_df = eye_tracking_df.value
        eye_tracking = EllipseSeries(
            name='eye_tracking',
            reference_frame='nose',
            data=eye_tracking_df[['eye_center_x', 'eye_center_y']].values,
            area=eye_tracking_df['eye_area'].values,
            area_raw=eye_tracking_df['eye_area_raw'].values,
            width=eye_tracking_df['eye_width'].values,
            height=eye_tracking_df['eye_height'].values,
            angle=eye_tracking_df['eye_phi'].values,
            timestamps=eye_tracking_df['timestamps'].values
        )

        pupil_tracking = EllipseSeries(
            name='pupil_tracking',
            reference_frame='nose',
            data=eye_tracking_df[['pupil_center_x', 'pupil_center_y']].values,
            area=eye_tracking_df['pupil_area'].values,
            area_raw=eye_tracking_df['pupil_area_raw'].values,
            width=eye_tracking_df['pupil_width'].values,
            height=eye_tracking_df['pupil_height'].values,
            angle=eye_tracking_df['pupil_phi'].values,
            timestamps=eye_tracking
        )

        corneal_reflection_tracking = EllipseSeries(
            name='corneal_reflection_tracking',
            reference_frame='nose',
            data=eye_tracking_df[['cr_center_x', 'cr_center_y']].values,
            area=eye_tracking_df['cr_area'].values,
            area_raw=eye_tracking_df['cr_area_raw'].values,
            width=eye_tracking_df['cr_width'].values,
            height=eye_tracking_df['cr_height'].values,
            angle=eye_tracking_df['cr_phi'].values,
            timestamps=eye_tracking
        )
        print("TEST")
        print(eye_tracking_df['likely_blink'].values)
        print(eye_tracking_df['likely_blink'])
        print(eye_tracking_df['likely_blink'].dtype)
        print(eye_tracking_df['likely_blink'].values.dtype)
        for i in range(0,len(eye_tracking_df['likely_blink'].values)):
            if eye_tracking_df['likely_blink'].values[i] is np.nan:
                print(i)
                eye_tracking_df['likely_blink'].values[i] = True
        print(eye_tracking_df['likely_blink'].values.dtype)
        eye_tracking_np = eye_tracking_df['likely_blink'].to_numpy(dtype=bool)
        print(eye_tracking_np)
        print(eye_tracking_np.dtype)
        likely_blink = TimeSeries(timestamps=eye_tracking,
                                  data=eye_tracking_np,
                                  name='likely_blink',
                                  description='blinks',
                                  unit='N/A')

        ellipse_eye_tracking = EllipseEyeTracking(
            eye_tracking=eye_tracking,
            pupil_tracking=pupil_tracking,
            corneal_reflection_tracking=corneal_reflection_tracking,
            likely_blink=likely_blink
        )
        nwb_file.add_acquisition(ellipse_eye_tracking)
        return nwb_file

def includes_meta_data(data_json):
    video_file_name = \
        data_json['RecordingReport']['VideoOutputFileName'].lower()
    video_file_name = Path(video_file_name)

    return video_file_name.suffix == '.mp4' or \
        'mvr' in video_file_name.name


def trim_meta_data(data_file):
    data_file = data_file[1:]
    return data_file


def proc_eye_tracking(eye_data, frame_times, z_threshold, dilation_frames):
    n_sync = len(frame_times)
    n_eye_frames = len(eye_data.index)

    # If n_sync exceeds n_eye_frames by <= 15,
    # just trim the excess sync pulses from the end
    # of the timestamps array.
    if n_eye_frames < n_sync <= n_eye_frames + 15:
        frame_times = frame_times[:n_eye_frames]
        n_sync = len(frame_times)

    if n_sync != n_eye_frames:
        raise EyeTrackingError(f"Error! The number of sync file frame times "
                               f"({len(frame_times)}) does not match the "
                               f"number of eye tracking frames "
                               f"({len(eye_data.index)})!")

    cr_areas = (eye_data[["cr_width", "cr_height"]]
                .apply(compute_elliptical_area, axis=1))
    eye_areas = (eye_data[["eye_width", "eye_height"]]
                 .apply(compute_elliptical_area, axis=1))
    pupil_areas = (eye_data[["pupil_width", "pupil_height"]]
                   .apply(compute_circular_area, axis=1))

    # only use eye and pupil areas for outlier detection
    area_df = pd.concat([eye_areas, pupil_areas], axis=1)
    outliers = determine_outliers(area_df, z_threshold=z_threshold)

    likely_blinks = determine_likely_blinks(eye_areas,
                                            pupil_areas,
                                            outliers,
                                            dilation_frames=dilation_frames)

    # remove outliers/likely blinks `pupil_area`, `cr_area`, `eye_area`
    pupil_areas_raw = pupil_areas.copy()
    cr_areas_raw = cr_areas.copy()
    eye_areas_raw = eye_areas.copy()

    for i in range(0, len(likely_blinks)):
        if likely_blinks[i] == True:            
            pupil_areas[i] = np.nan
            cr_areas[i] = np.nan
            eye_areas[i] = np.nan

    eye_data.insert(0, "timestamps", frame_times)
    eye_data.insert(1, "cr_area", cr_areas)
    eye_data.insert(2, "eye_area", eye_areas)
    eye_data.insert(3, "pupil_area", pupil_areas)
    eye_data.insert(4, "likely_blink", likely_blinks)
    eye_data.insert(5, "pupil_area_raw", pupil_areas_raw)
    eye_data.insert(6, "cr_area_raw", cr_areas_raw)
    eye_data.insert(7, "eye_area_raw", eye_areas_raw)

    return eye_data


def from_data_file(ellipse_file, sync_file, data_json_path):
    frame_times = sync_utilities.get_synchronized_frame_times(
        session_sync_file=sync_file,
        sync_line_label_keys=Dataset.EYE_TRACKING_KEYS,
        trim_after_spike=False)
    json_file = open(data_json_path)
    data_json = json.load(json_file)
    json_file.close()
    data_file = load_eye_tracking_hdf(ellipse_file)
    if(includes_meta_data(data_json)):
        data_file = trim_meta_data(data_file)
    print(data_file)
    eye_tracking_data = proc_eye_tracking(
                                        data_file,
                                        frame_times,
                                        z_threshold = 3.0,
                                        dilation_frames = 2)

    return EyeTrackingTable(eye_tracking=eye_tracking_data)

def add_tracking_to_nwb(tracking_params):
    ellipse_file = tracking_params['ellipse_path']
    sync_file = tracking_params['sync_path']
    nwb_file = tracking_params['nwb_path']
    write_nwb_path = nwb_file.replace("spike_times.nwb", "spike_times_re.nwb")
    data_json_path = tracking_params['data_json']
   #eye_df = EyeTrackingTable.from_data_file(ellipse_file, sync_file)
    eye_df = from_data_file(ellipse_file, sync_file, data_json_path)
    io = NWBHDF5IO(nwb_file, "r+", load_namespaces=True)
    input_nwb = io.read()
    input_nwb = add_eye_tracking_nwb(eye_df, input_nwb)
    io.write(input_nwb)