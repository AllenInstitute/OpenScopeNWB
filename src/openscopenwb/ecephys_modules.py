from os.path import join
from glob import glob


def ecephys_write_nwb(session_parameters):
    """Writes the input json for the nwb modules

    Parameters
    ----------

    session_parameters: dict
    Session unique information, used by each module


    Returns
    -------
    None
    """

def ecephys_optotagging_table(session_parameters):
    """ Writes the relevant optotagging information to the input json

    Parameters
    ----------

    session_parameters: dict
    Session unique information, used by each module


    Returns
    -------
    input_json_write_dict: dict
    A dictionary representing the values that will be written to the input json
    """
    input_json_write_dict = {
        'opto_pickle_path': glob(
            join(session_parameters['base_directory'], '*.opto.pkl'))[0],
        'sync_h5_path': glob(
            join(session_parameters['base_directory'], '*.sync'))[0],
        'output_opto_table_path': join(session_parameters['base_directory'],
                                       'optotagging_table.csv')
        }
    return input_json_write_dict


def ecephys_lfp_subsampling(session_parameters):
    """ Writes the lfp sampling information to the input json

    Parameters
    ----------

    session_parameters: dict
    Session unique information, used by each module

    Returns
    -------

    None
    """