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
    EyeTrackingError
from allensdk.brain_observatory.nwb.eye_tracking.ndx_ellipse_eye_tracking \
    import \
    EllipseSeries, EllipseEyeTracking
from allensdk.brain_observatory.sync_dataset import Dataset
from pathlib import Path
import json
# from openscopenwb.utils import clean_up_functions as cuf
# from os.path import join

# from pynwb.file import NWBFile

loc_stim_file = ""

def includes_meta_data(data_json):
    video_file_name = \
        data_json['RecordingReport']['VideoOutputFileName'].lower()
    video_file_name = Path(video_file_name)

    return video_file_name.suffix == '.mp4' or \
        'mvr' in video_file_name.name


def from_data_file(ellipse_file, sync_file, data_json):
    frame_times = sync_utilities.get_synchronized_frame_times(
        session_sync_file=sync_file,
        sync_line_label_keys=Dataset.EYE_TRACKING_KEYS,
        trim_after_spike=False)
    data_json = json.load(data_json)
    data_file = EyeTrackingFile.load_data(ellipse_file)
    if(includes_meta_data(data_json))
    eye_tracking_data = process_eye_tracking_data(
                                        data_file,
                                        frame_times,
                                        z_threshold = 3.0,
                                        dilation_frames = 2)

    return EyeTrackingTable(eye_tracking=eye_tracking_data)

def add_tracking_to_nwb(tracking_params):
    ellipse_file = tracking_params['ellipse_path']
    sync_file = tracking_params['sync_path']
    nwb_file = tracking_params['nwb_path']
    data_json = tracking_params['data_json']
   #eye_df = EyeTrackingTable.from_data_file(ellipse_file, sync_file)
    eye_df = from_data_file(ellipse_file, sync_file, data_json)
    eye_df.to_nwb(nwb_file)
