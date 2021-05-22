import math

import scipy


def calc_expected_value(counts_dict):
    """Returns the expected value of the histogram of the counts provided as a dict, if the results can be
    interpreted as binary numbers """
    result = 0
    for key in counts_dict.keys():
        result += int(key, 2) * counts_dict[key]
    return result


def calc_standard_deviation(counts_dict, expected_value):
    """Returns the standard deviation of the histogram of the counts provided as a dict, if the results can be
     interpreted as binary numbers"""
    sum = 0
    for key in counts_dict.keys():
        sum += ((int(key, 2) - expected_value) ** 2) * counts_dict[key]
    return math.sqrt(sum)


def calc_percentage_error(counts_sim, counts_real):
    """Returns the percentage errors for each count provided in the dict"""
    result = {}
    for key in counts_sim.keys():
        if key in counts_real.keys():
            error = (counts_sim[key] - counts_real[key]) / counts_sim[key]
            result[key] = abs(error)
    return result


def calc_intersection(counts_sim, counts_real, shots):
    """Returns the histogram intersection value for the two histograms of simulator and quantum computer"""
    intersection = 0
    for key in counts_real.keys():
        # add missing keys from quantum computer to simulator
        if key not in counts_sim.keys():
            counts_sim[key] = 0
    for key in counts_sim.keys():
        # add missing keys from simulator to quantum computer
        if key not in counts_real.keys():
            counts_real[key] = 0
        # calculate histogram intersection
        intersection = intersection + min(counts_sim[key], counts_real[key])
    return intersection / shots


def calc_chi_square_distance(counts_sim, counts_real):
    """Returns the chi-square-distance for the two histograms of simulator and quantum computer"""
    coefficient = 0
    for key in counts_real.keys():
        # add missing keys from quantum computer to simulator
        if key not in counts_sim.keys():
            counts_sim[key] = 0
    for key in counts_sim.keys():
        # add missing keys from simulator to quantum computer
        if key not in counts_real.keys():
            counts_real[key] = 0
        # calculate chi square distance
        coefficient = coefficient + ((counts_real[key] - counts_sim[key]) ** 2 / (counts_real[key] + counts_sim[key]))
    return coefficient / 2


def calc_correlation(counts_sim, counts_real, shots):
    """Returns the correlation between the two histograms of the simulator and quantum computer"""
    for key in counts_real.keys():
        # add missing keys from quantum computer to simulator
        if key not in counts_sim.keys():
            counts_sim[key] = 0
    for key in counts_sim.keys():
        # add missing keys from simulator to quantum computer
        if key not in counts_real.keys():
            counts_real[key] = 0
    # calculate correlation value for the two histogram
    sum_combined = 0
    sum_sim = 0
    sum_real = 0
    h_sim = shots / len(counts_sim)
    h_real = shots / len(counts_real)
    for key in counts_real.keys():
        sum_real = sum_real + ((counts_real[key] - h_real) ** 2)
    for key in counts_sim.keys():
        sum_sim = sum_sim + ((counts_sim[key] - h_sim) ** 2)
        sum_combined = sum_combined + ((counts_sim[key] - h_sim) * (counts_real[key]- h_real))
    if sum_sim == 0 or sum_real == 0:
        return None
    correlation = sum_combined / (math.sqrt(sum_sim * sum_real))

    return correlation
