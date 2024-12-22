import numpy as np
from pyrs.algorithm import rs_image


def nan2zero(array):
    nan_pos = np.isnan(array)
    array[nan_pos] = 0
    return array


etp_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\etp\\rainfall\\GW\\'
eta_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\eta\\rainfall\\GW\\'
ks_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\etp\\rainfall\\ks\\'

for i in range(0, 26, 1):
    formatted = "{:02}".format(int(i + 1))
    for j in range(0, 20, 1):
        np.seterr(all="ignore")

        year = str(j + 2001)
        etp_path = etp_file + formatted + '\\' + year + '.tif'
        eta_path = eta_file + formatted + '\\' + year + '.tif'
        ks_path = ks_file + formatted + '\\' + year + '.tif'

        etp = rs_image.Image(etp_path).get_array(True, 1)
        eta = rs_image.Image(eta_path).get_array(True, 1)

        ks = eta / etp
        new_ks = nan2zero(ks)

        rs_image.Image(etp_path).save(ks_path, new_ks)