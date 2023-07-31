#!/usr/bin/env python
import logging
import os
import subprocess
import warnings
import argparse
import ecephys_nwb_eye_tracking

from openscopenwb.utils.slurm_utils import slurm_jobs as slurm_job
from openscopenwb.utils import parse_ephys_project_parameters as ppp
from openscopenwb.utils import script_functions as sf
from openscopenwb.utils import firebase_functions as fb
from openscopenwb.utils import generate_json as gen_json
import openscopenwb.create_module_input_json as osnjson


def convert_session(session_id, project):
    """Calls functions to write ephys NWB session

    Parameters
    ----------
    session_id: str
    The session_id for the session
    project: str
    The project's LIMS ID

    Returns
    -------
    module_params: dict
    Session unique information, used by each module
    """

    warnings.filterwarnings("ignore", message="numpy.dtype size changed")

    project_csv_json, _ = gen_json.generate_ephys_json(session_id, project)
    project_params = ppp.parse_json(project_csv_json)
    session_param_list = ppp.generate_all_session_params(project_params)
    modules = ppp.get_modules(project_params)
    session_modules, probe_modules = ppp.get_module_types(project_params)
    old_last_unit = -1
    log_out = session_param_list[0]['output_path']
    logging.basicConfig(filename=log_out + "/std.log",
                        format='%(asctime)s %(message)s',
                        level=logging.DEBUG,
                        filemode='a')

    for session_params in session_param_list:
        session = session_params["session_id"]
        probes = session_params['probes']
        for module in modules:
            json_directory = ppp.get_input_json_directory(project_params)
            json_directory = os.path.join(json_directory, session)
            input_json = os.path.join(json_directory, session + '-' + module +
                                      '-input.json')
            output_json = os.path.join(json_directory, session + '-' + module +
                                       '-output.json')
            if module in session_modules:
                module_params = session_params
                module_params = osnjson.create_module_input(
                    module, module_params, input_json)

                command_string = sf.generate_module_cmd(
                    module,
                    input_json,
                    output_json
                )
                logging.debug("Starting Session Level Module: " + module)
                logging.debug(command_string)
                subprocess.check_call(command_string)
                logging.debug("Finished Session Level Module: " + module)
            elif module in probe_modules:
                for probe in probes:
                    session_params['last_unit_id'] = old_last_unit + 1
                    module_params = session_params
                    module_params['current_probe'] = probe
                    module_params['id'] = probes.index(probe)
                    module_params = osnjson.create_module_input(
                        module, module_params, input_json)
                    command_string = sf.generate_module_cmd(
                        module,
                        input_json,
                        output_json
                    )
                    old_last_unit = module_params['last_unit_id']
                logging.debug("Starting Probe Level Module:: " + module)
                subprocess.check_call(command_string)
                logging.debug("Finished Probe Level Module: " + module)
    return module_params


def write_subject_to_nwb(session_id, module_params, dandi_id):
    """Writes subject table information to nwb

    Parameters
    ----------
    session_id: str
    The session_id for the session
    module_params: dict
    Session unique information, used by each module

    Returns
    -------
    """

    ecephys_nwb_eye_tracking.add_tracking_to_nwb(module_params)
    fb.update_session_dir(
        module_params['project'], session_id, module_params['nwb_path'])
    slurm_job.upload_ephys_nwb(
        session_id, module_params['project'],
        module_params['nwb_path'],
        dandi_id)


if __name__ == "__main__":
    """Calls functions to write ephys NWB session

    Parameters
    ----------
    session_id: str
    The session_id for the session
    project: str
    The project's LIMS ID

    Returns
    -------
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--session_id', type=str)
    parser.add_argument('--project', type=str)
    parser.add_argument('--dandi_id', type=str)
    args = parser.parse_args()
    print(args.project)
    write_subject_to_nwb(
        module_params=convert_session(
            session_id=args.session_id, project=args.project),
        session_id=args.session_id,
        dandi_id=args.dandi_id
    )
