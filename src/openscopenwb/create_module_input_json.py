import io
import json
import openscopenwb.ecephys_modules as ephys_mod


def create_module_input(module, session_parameters, input_json_path):
    """Writes an input json and calls the run_module based on the input module

    Parameters
    ----------
    session_parameters: dict
    Session unique information, used by each module
    module: str
    The specific module that will be used
    input_json_path: str
    The path to write the input json to

    Returns
    -------
    session_parameters: dict
    Session unique information, used by each module, updated by the module
    """
    session_parameters, input_json_write_dict = run_module(module, 
                                                           session_parameters)

    with io.open(input_json_path, 'w', encoding='utf-8') as file_handle:
        file_handle.write(json.dumps(input_json_write_dict,
                                     ensure_ascii=False,
                                     sort_keys=True,
                                     indent=4))

    return session_parameters


def run_module(module, session_parameters):
    """ Creates a dictionary for an input json with information 
    that is used by each module
    
    Parameters
    ----------

    module: str
    The specific module that will be used
    session_parameters: dict
    Session unique information, used by each module

    Returns
    -------
    session_parameters: dict
    Session unique information, used by each module
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """
    if module == 'allensdk.brain_observatory.ecephys_optotagging_table':
        session_parameters, input_json_write_dict =  \
            ephys_mod.ecephys_optotagging_table(session_parameters)
    if module == 'allensdk.brain_observatory.ecephys_write_nwb':
        session_parameters, input_json_write_dict =  \
            ephys_mod.ecephys_write_nwb(session_parameters)
    if module == 'allensdk.brain_observatory.ecephys_lfp_subsampling':
        session_parameters, input_json_write_dict = \
            ephys_mod.ecephys_lfp_subsampling(session_parameters)
    return session_parameters, input_json_write_dict