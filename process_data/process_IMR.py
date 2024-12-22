import numpy as np
from pyrs.algorithm import rs_image


image_path = 'D:\\Drought_and_heat_wave_coupling\\data\\neonatal_infant\\' \
             'IHME_LMICS_U5M_2000_2017_Q_UNDER5_MEAN_Y2019M10D16.TIF'
save_file = 'D:\\Drought_and_heat_wave_coupling\\data\\under5_image\\'
data = rs_image.Image(image_path)
array = data.get_array(True, 0)
for i in range(1, array.shape[0], 1):
    year_array = array[i, :, :]
    save_path = save_file + str(i + 2000) + '.tif'
    data.save(save_path, year_array)