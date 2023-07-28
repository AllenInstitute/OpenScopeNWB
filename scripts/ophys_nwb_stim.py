import pandas as pd
import numpy as np
from pathlib import Path, PurePath
from typing import Any, Dict, List, Tuple
from pynwb import NWBHDF5IO
from allensdk.brain_observatory.behavior.data_objects.stimuli.presentations \
    import \
    Presentations
from allensdk.brain_observatory.nwb import (
    add_stimulus_ophys_timestamps,
)

STIM_TABLE_RENAMES_MAP = {"Start": "start_time", "End": "stop_time"}


def read_stimulus_table(path: str,
                        column_renames_map: Dict[str, str]=None,
                        columns_to_drop: List[str]=None) -> pd.DataFrame:
    """ Loads from a CSV on disk the stimulus table for this session.
    Optionally renames columns to match NWB epoch specifications.
    Parameters
    ----------
    path : str
        path to stimulus table csv
    column_renames_map : Dict[str, str], optional
        If provided, will be used to rename columns from keys -> values.
        Default renames: ('Start' -> 'start_time') and ('End' -> 'stop_time')
    columns_to_drop : List, optional
        A list of column names to drop. Columns will be dropped BEFORE
        any renaming occurs. If None, no columns are dropped.
        By default None.
    Returns
    -------
    pd.DataFrame :
        stimulus table with applied renames
    """
    if column_renames_map is None:
        column_renames_map = STIM_TABLE_RENAMES_MAP

    ext = PurePath(path).suffix

    if ext == ".csv":
        stimulus_table = pd.read_csv(path)
    else:
        raise IOError(f"unrecognized stimulus table extension: {ext}")

    if columns_to_drop:
        stimulus_table = stimulus_table.drop(errors='ignore',
                                             columns=columns_to_drop)

    return stimulus_table.rename(columns=column_renames_map, index={})


def add_stim_to_nwb(
    stim_path,
    nwb_path
):
    """Adds Stim info to an NWB

    Parameters
    ----------
    stim_path: str
    The stim's location
    nwb_path: str
    The current nwb's location

    Returns
    -------
    """
    stimulus_columns_to_drop = [
        "colorSpace", "depth", "interpolate", "pos", "rgbPedestal", "tex",
        "texRes", "flipHoriz", "flipVert", "rgb", "signalDots"
    ]
    stimulus_table = Presentations.from_path(
        path=stim_path,
        exclude_columns=stimulus_columns_to_drop,
        columns_to_rename=STIM_TABLE_RENAMES_MAP,
        sort_columns=False
    )
    with NWBHDF5IO(nwb_path, "r+", load_namespaces=True) as nwbfile:
        input_nwb = nwbfile.read()
        nwb_temp = stimulus_table.to_nwb(nwbfile=input_nwb)
        nwb_temp = add_stimulus_ophys_timestamps(
            nwb_temp, stimulus_table.value['start_time'].values)
        nwbfile.write(nwb_temp)
