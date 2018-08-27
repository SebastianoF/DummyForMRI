import numpy as np


def generate_dummy_labels_descriptor():
    # TODO
    pass

def intensity_segmentation(in_array, num_levels=5):
    """
    Simplest way of getting an intensity based segmentation.
    :param in_array: image data in a numpy array.
    :param num_levels: maximum allowed 65535 - 1.
    :return: segmentation of the result in levels levels based on the intensities of the in_data.
    """
    segm = np.zeros_like(in_array, dtype=np.uint16)
    min_data = np.min(in_array)
    max_data = np.max(in_array)
    h = (max_data - min_data) / float(int(num_levels))
    for k in range(0, num_levels):
        places = (min_data + k * h <= in_array) * (in_array < min_data + (k + 1) * h)
        np.place(segm, places, k)
    places = in_array == max_data
    np.place(segm, places, num_levels-1)
    return segm