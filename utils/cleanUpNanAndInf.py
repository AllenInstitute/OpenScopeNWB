import numpy as np

def cleanUpNanAndInf(value):
    if np.isnan(value) or np.isinf(value):
        return -1
    else:
        return value