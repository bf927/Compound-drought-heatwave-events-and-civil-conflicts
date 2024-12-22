import numpy as np
import glob
from pyrs.algorithm import rs_image

file = 'D:\\Drought_and_heat_wave_coupling\\data\\Tmax_data\\'
output1 = 'D:\\Drought_and_heat_wave_coupling\\data\\percentiles\\25.tiff'
output2 = 'D:\\Drought_and_heat_wave_coupling\\data\\percentiles\\75.tiff'
output3 = 'D:\\Drought_and_heat_wave_coupling\\data\\percentiles\\95.tiff'
ex_path = 'D:\\Drought_and_heat_wave_coupling\\data\\Tmax_data\\2010\\201001\\01.tiff'
part_1 = 'D:\\Drought_and_heat_wave_coupling\\data\\split\\part1.npy'
part_2 = 'D:\\Drought_and_heat_wave_coupling\\data\\split\\part2.npy'
part_3 = 'D:\\Drought_and_heat_wave_coupling\\data\\split\\part3.npy'

part_1_array = np.load(part_1)
print(part_1_array.shape)
part_2_array = np.load(part_2)
print(part_2_array.shape)
part_3_array = np.load(part_3)
print(part_3_array.shape)

# 使用内存映射文件创建一个空的数组，用于存储最终组合的数据
output_shape = (part_1_array.shape[0] + part_2_array.shape[0] + part_3_array.shape[0],
                part_1_array.shape[1], part_1_array.shape[2])
output_dtype = np.float32
output_filename = 'D:\\Drought_and_heat_wave_coupling\\data\\percentiles\\compos.dat'
total_image = np.memmap(output_filename, dtype=output_dtype, mode='w+', shape=output_shape)

# total_image = np.zeros((part_1_array.shape[0] + part_2_array.shape[0] + part_3_array.shape[0],
#                         part_1_array.shape[1], part_1_array.shape[2]), dtype=np.float32)
total_image[0:part_1_array.shape[0], :, :] = part_1_array
total_image[part_1_array.shape[0]:part_1_array.shape[0] + part_2_array.shape[0], :, :] = part_2_array
total_image[part_1_array.shape[0] + part_2_array.shape[0]:part_1_array.shape[0] + part_2_array.shape[0] + part_3_array.shape[0], :,
:] = part_3_array

ex_image = rs_image.Image(ex_path)
# total_image = np.array([ex_image.get_array(True, 1)])
# total_image = np.append(part_1_array, part_2_array, axis=0)
# total_image = np.append(total_image, part_3_array, axis=0)


# year_path_list = glob.glob(file + '*')
# for i in range(0, len(year_path_list), 1):
#     print(i+1989)
#     print(total_image.shape)
#     month_path_list = glob.glob(year_path_list[i] + '\\*')
#     for j in range(0, len(month_path_list), 1):
#         day_path_list = glob.glob(month_path_list[j] + '\\*.tiff')
#         for k in range(0, len(day_path_list), 1):
#             dataset = rs_image.Image(day_path_list[k])
#             array = np.array([dataset.get_array(True, 1)])
#             total_image = np.append(total_image, array, axis=0)
#
# np.save(part_1, total_image)
# print(total_image.shape)
#
# image_25 = np.percentile(total_image, 25, axis=0)
# image_75 = np.percentile(total_image, 75, axis=0)
image_90 = np.percentile(total_image, 95, axis=0)

# ex_image.save(output1, image_25)
# ex_image.save(output2, image_75)
ex_image.save(output3, image_90)
