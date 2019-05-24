import numpy as np


def ceil_to_base(x, base=5):
    return base * np.ceil(x / base)
