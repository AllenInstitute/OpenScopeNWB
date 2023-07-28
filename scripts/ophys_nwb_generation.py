#!/usr/bin/env python
import argparse
import os
import warnings
import logging
import sys
import json
import subprocess
import sys
import ecephys_nwb_eye_tracking as eye_tracking
import ophys_nwb_raw as raw_nwb
import ophys_nwb_stim as stim


from datetime import datetime
from os.path import join
from glob import glob

from allensdk.brain_observatory.behavior.ophys_experiment import \
    OphysExperiment as ophys
from pynwb import NWBHDF5IO
from pynwb.file import Subject
from pynwb.ophys import OpticalChannel

from openscopenwb.utils import script_functions as sf
from openscopenwb.utils import allen_functions as allen
from openscopenwb.utils import postgres_functions as postgres
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils.slurm_utils import slurm_jobs as slurm_job
from openscopenwb.utils.generate_json import generate_ophys_json

warnings.filterwarnings("ignore", message="numpy.dtype size changed")

sys.stdout = open('std.log', 'a')
logging.basicConfig(filename="std.log",
                    format='%(asctime)s %(message)s',
                    level=logging.DEBUG,
                    filemode='a')
dir = os.path.dirname(__file__)


def gen_ophys(experiment_id, file_path):
    """Calls functions to write ophys NWB

    Parameters
    ----------
    experiment_id: int
    The experiment_id for the plane
    file_path: str
    The output nwb's location

    Returns
    -------
    """
    key = experiment_id
    ophys_experiment_id = int(key)
    ophys_nwb = ophys.from_lims(ophys_experiment_id=ophys_experiment_id,
                                skip_eye_tracking=True)
    ophys_nwb = ophys_nwb.to_nwb()
    with NWBHDF5IO(file_path, mode='w') as io:
        io.write(ophys_nwb)


def add_data_to_nwb(csv_path, nwb_path):
    """Adds Stim info to an NWB

    Parameters
    ----------
    csv_path: str
    The stim's location
    nwb_path: str
    The current nwb's location

    Returns
    -------
    """
    stim.add_stim_to_nwb(csv_path, nwb_path)


def add_plane_to_nwb(nwb_path):
    """Writes plane for metadata if missing in NWB

    Parameters
    ----------
    nwb_path: str
    The current nwb's location

    Returns
    -------
    """
    with NWBHDF5IO(nwb_path, mode='a') as io:
        # Read the NWB file
        nwbfile = io.read()
        structure = nwbfile.surgery.split(":")
        structure = structure[1].strip()

        fov_height = str(
            nwbfile.lab_meta_data["metadata"].field_of_view_height)
        fov_width = str(nwbfile.lab_meta_data["metadata"].field_of_view_width)
        depth = str(nwbfile.lab_meta_data["metadata"].imaging_depth)
        description = "(" + fov_height + ", " + fov_width + \
            ") field of view in " + structure + " at depth " + depth + " um"

        # Check if imaging_plane_1 exists
        if 'imaging_plane_1' in nwbfile.imaging_planes:
            print("imaging_plane_1 already exists in the NWB file.")
        else:
            # Create Optical Channel
            optical_channel = OpticalChannel(
                name='channel_1',
                description='PLACEHOLDER OPTICAL CHANNEL',
                emission_lambda=0.0)

            # Create imaging_plane_1
            imaging_plane = nwbfile.create_imaging_plane(
                name='imaging_plane_1',
                description=description,
                device=nwbfile.devices['MESO.2'],
                excitation_lambda=910.0,
                imaging_rate=10.0,
                indicator='GCaMP6f',
                location=structure,
                optical_channel=optical_channel
            )

            print(imaging_plane)
            # Save the modified NWB file
            io.write(nwbfile)

            print("imaging_plane_1 has been created in the NWB file.")


def add_subject_to_nwb(session_id, experiment_id, nwb_path):
    """Adds Stim info to an NWB

    Parameters
    ----------
    session_id: str
    The 10 digit session id
    nwb_path: str
    The current nwb's location

    Returns
    -------
    """
    subject_info = allen.lims_o_subject_info(session_id)
    subject_dob = datetime.strptime(subject_info['dob'][:10], '%Y-%m-%d')
    subject_date = postgres.get_o_sess_info(session_id)['date']
    subject_date = datetime.strptime(subject_date[:10], '%Y-%m-%d')
    specimen_id = postgres.get_o_sess_donor_info(session_id)
    duration = subject_date - subject_dob
    duration = duration.total_seconds()
    duration = divmod(duration, 86400)
    days = (duration[0])
    days = 'P' + str(days) + 'D'
    subject = {
        'age': days,
        'genotype': subject_info['genotype'],
        'sex': subject_info['gender'],
        'strain': "Transgenic",
        'stimulus_name': 'Ophys Dendrite',
        'species': 'Mus musculus',
        'subject_id': subject_info['name']
    }
    with NWBHDF5IO(nwb_path, "r+", load_namespaces=True) as nwbfile:
        input_nwb = nwbfile.read()
        input_nwb.subject = Subject(
            subject_id=str(subject_info['name']),
            age=subject['age'],
            species='Mus musculus',
            sex=subject['sex'],
            genotype=subject['genotype'],
            description=("external: " + str(subject_info['name']) +
                         " donor_id: " +
                         str(subject_info['id']) +
                         " specimen_id: " + str(specimen_id))
        )
        input_nwb.surgery = " Structure: " + \
            postgres.get_o_targeted_struct(experiment_id)
        nwbfile.write(input_nwb)


if __name__ == "__main__":
    """Calls functions to write and upload ophys NWB

    Parameters
    ----------
    experiment_id: int
    The experiment_id for the plane
    file_path: str
    The output nwb's location
    session_id: int
    The session_id for the session
    project: str
    The project's LIMS ID
    raw_flag: bool
    Whether or not to process raw data
    final: bool
    Whether or not to upload to dandi
    val: int
    The dandiset's id

    Returns
    -------
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--project_id', type=str)
    parser.add_argument('--session_id', type=int)
    parser.add_argument('--experiment_id', type=int)
    parser.add_argument('--raw', type=str)
    parser.add_argument('--val', type=int)
    parser.add_argument('--final', type=str)
    args = parser.parse_args()
    session_id = args.session_id
    experiment_id = args.experiment_id
    experiment_id = int(experiment_id)
    raw_flag = args.raw
    final = args.final
    val = args.val
    json_in = generate_ophys_json(experiment_id)
    input_json = (r'/allen/programs/mindscope/workgroups/openscope/' +
                  'ahad/ophys_no_behavior_nwb/' +
                  str(experiment_id) + "_in.json")
    output_json = (r'/allen/programs/mindscope/workgroups/openscope/' +
                   'ahad/ophys_no_behavior_nwb/' +
                   str(experiment_id) + "_out.json")
    with open(input_json, "w") as outfile:
        outfile.write(json_in)
    command_string = sf.generate_module_cmd(
        'allensdk.brain_observatory.ecephys.stimulus_table',
        input_json,
        output_json,
    )
    subprocess.check_call(command_string)
    file_path = (r'/allen/programs/mindscope/workgroups/openscope/' +
                 'ahad/ophys_no_behavior_nwb')
    file_folder = file_path
    if raw_flag is True:
        file_path = file_path + '/' + str(experiment_id) + 'raw_data.nwb'
    else:
        file_path = file_path + '/' + str(experiment_id) + '.nwb'
    gen_ophys(experiment_id, file_path)
    json_in = json.loads(json_in)
    main_dir = postgres.get_o_sess_directory(session_id)
    main_dir = main_dir[0]
    ellipse_path = glob(join(main_dir, "eye_tracking", "*_ellipse.h5"))[0]

    data_json_path = glob(join(main_dir, "*_Behavior_*.json"))[0]
    sync_path = glob(join(main_dir, "*.h5"))
    if 'full_field' in sync_path[0]:
        sync_path = sync_path[1]
    else:
        sync_path = sync_path[0]
    motion_path = glob(
        join(
            main_dir,
            'ophys_experiment_' +
            str(experiment_id),
            'processed',
            '*_suite2p_motion_output.h5'))[0]
    tracking_params = {
        'ellipse_path': ellipse_path,
        'sync_path': sync_path,
        'nwb_path': file_path,
        'data_json': data_json_path
    }
    subject_info = allen.lims_o_subject_info(session_id)
    subject_id = subject_info['name']
    add_data_to_nwb(json_in['output_stimulus_table_path'], file_path)
    add_subject_to_nwb(session_id, experiment_id, file_path)
    eye_tracking.add_tracking_to_ophys_nwb(tracking_params)
    add_plane_to_nwb(file_path)
    raw_params = {
        'nwb_path': file_path,
        'suite_2p': motion_path,
        'time': postgres.get_o_sess_info(session_id)['date'],
        'plane': str(experiment_id),
        'final': final
    }
    print("SLURM ID")
    print(os.environ.get('SLURM_JOBID'), flush=True)

    slurm_id = os.environ.get('SLURM_JOBID')
    fb.start(fb.get_creds())
    fb.update_curr_job(slurm_id)

    dandi_url = r'https://dandiarchive.org/dandiset/' + str(val)

    if raw_flag == "True":
        raw_flag = True
    else:
        raw_flag = False

    if raw_flag is True:
        print("Processing Raw")
        raw_nwb.process_suit2p(raw_params)
        slurm_job.dandi_ophys_upload(
            file=file_folder,
            session_id=session_id,
            experiment_id=experiment_id,
            subject_id=subject_id,
            raw=True,
            final=final,
            dandi_set_id=val
        )
    else:
        print("Processing without RAW")
        slurm_job.dandi_ophys_upload(
            file=file_folder,
            session_id=session_id,
            experiment_id=experiment_id,
            subject_id=subject_id,
            raw=True,
            final=final,
            dandi_set_id=val
        )
