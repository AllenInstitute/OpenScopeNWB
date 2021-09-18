import numpy as np


def clean_up_nan_and_inf(value):
    """ Replaces Nan and inf values with -1

    Parameters
    ----------
    value: float
    A floating point value

    Returns
    -------
    value: float
    A floating point value, -1 if the original value was nan or inf
    """
    if np.isnan(value) or np.isinf(value):
        return -1
    else:
        return value
