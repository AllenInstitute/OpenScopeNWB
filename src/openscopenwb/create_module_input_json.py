import io
import json
import openscopenwb.ecephys_modules as ephys_mod


def create_module_input(module, module_params, input_json_path):
    """Writes an input json and calls the run_module based on the input module

    Parameters
    ----------
    module: str
    The specific module that will be used
    module_params: dict
    Session unique information, used by each module
    input_json_path: str
    The path to write the input json to

    Returns
    -------
    session_params: dict
    Session unique information, used by each module, updated by the module
    """
    
    module_params, input_json_write_dict = \
        write_module_dict(module, module_params)

    with io.open(input_json_path, 'w', encoding='utf-8') as file_handle:
        file_handle.write(json.dumps(input_json_write_dict,
                                     ensure_ascii=False,
                                     sort_keys=True,
                                     indent=4))

    return module_params


def write_module_dict(module, module_params):
    """ Creates a dictionary for an input json with information
    that is used by each module

    Parameters
    ----------

    module: str
    The specific module that will be used
    module_params: dict
    Session unique information, used by each module

    Returns
    -------
    session_params: dict
    Session unique information, used by each module
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """
    input_json_write_dict = {}
    if module == 'allensdk.brain_observatory.ecephys_optotagging_table':
        session_params, input_json_write_dict =  \
            ephys_mod.ecephys_optotagging_table(module_params)
    if module == 'allensdk.brain_observatory.ecephys_write_nwb':
        session_params, input_json_write_dict =  \
            ephys_mod.ecephys_write_nwb(module_params)
    if module == 'allensdk.brain_observatory.ecephys_lfp_subsampling':
        session_params, input_json_write_dict = \
            ephys_mod.ecephys_lfp_subsampling(module_params)
    if module == 'allensdk.brain_observatory.extract_running_speed':
        session_params, input_json_write_dict = \
            ephys_mod.extract_running_speed(module_params)
    if module == 'allensdk.brain_observatory.ecephys.align_timestamps':
        session_params, input_json_write_dict = \
            ephys_mod.ecephys_align_timestamps(module_params)
    if module == 'allensdk.brain_observatory.ecephys.stimulus_table':
        session_params, input_json_write_dict = \
            ephys_mod.stimulus_table(module_params)
    return session_params, input_json_write_dict
