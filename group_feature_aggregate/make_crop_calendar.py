import netCDF4 as nc
import cv2
from osgeo import gdal, osr
import os
import glob
import numpy as np
from pyrs.algorithm import rs_image
import pandas as pd

os.environ['PROJ_LIB'] = 'C:\\Python\\Lib\\site-packages\\osgeo\\data\\proj'
gdal.PushErrorHandler("CPLQuietErrorHandler")


def save_global_image(array_data, save_path):
    # 创建一个新的GeoTIFF文件
    driver = gdal.GetDriverByName('GTiff')
    data_set = driver.Create(save_path, array_data.shape[1], array_data.shape[0], 1, gdal.GDT_Float32)

    # 设置数组数据
    band = data_set.GetRasterBand(1)
    band.WriteArray(array_data)

    # 添加地理坐标系和全球范围
    projection = osr.SpatialReference()
    projection.ImportFromEPSG(4326)  # WGS 1984坐标系
    data_set.SetProjection(projection.ExportToWkt())

    # 定义全球范围的坐标范围
    x_min = -180
    x_max = 180
    y_min = -90
    y_max = 90

    # 设置全球范围的空间分辨率
    x_resolution = (x_max - x_min) / float(array_data.shape[1])
    y_resolution = (y_max - y_min) / float(array_data.shape[0])

    data_set.SetGeoTransform([x_min, x_resolution, 0, y_max, 0, -y_resolution])

    # 保存数据并关闭文件
    band.FlushCache()


def nan2zero(array):
    nan_index = np.isnan(array)
    array[nan_index] = 0
    return array


crop_file = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\ALL_CROPS_netCDF_5min_filled_2'
start_save_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\crop_calendar\\start.tif'
end_save_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\crop_calendar\\end.tif'
mask_image_path = 'D:\\Drought_and_heat_wave_coupling\\data\\global_population\\resample_mask.tif'
table_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\CDHW_conflict _2001_2020.xlsx'

crop_file_list = glob.glob(crop_file + '\\*')
start_list = []
end_list = []

for i in range(0, len(crop_file_list), 1):
    crop_image_list = glob.glob(crop_file_list[i] + '\\*')
    crop_image_path = crop_image_list[0]
    dataset = nc.Dataset(crop_image_path)
    all_vars = dataset.variables.keys()
    plant_start_array = np.array([dataset.variables['plant.start'][:]])
    # plant_start_array = nan2zero(plant_start_array)
    plant_end_array = np.array([dataset.variables['plant.end'][:]])
    harvest_start_array = np.array([dataset.variables['harvest.start'][:]])
    harvest_end_array = np.array([dataset.variables['harvest.end'][:]])
    # harvest_end_array = nan2zero(harvest_end_array)
    start_list.append(plant_start_array)
    end_list.append(harvest_end_array)

start_array = start_list[0]
end_array = end_list[0]
for i in range(1, len(start_list), 1):
    start_array = np.append(start_array, start_list[i], axis=0)
    end_array = np.append(end_array, end_list[i], axis=0)

start_array = np.where(start_array > 366, 1000, start_array)
end_array = np.where(end_array > 366, 0, end_array)
start_array = np.min(start_array, axis=0)
end_array = np.max(end_array, axis=0)
start_array = np.where(start_array == 1000, 0, start_array)

table = pd.read_excel(table_path)
table = np.array(table)
index = np.unique(table[:, 0])
# print(index)

mask_image = rs_image.Image(mask_image_path)
mask_image_array = mask_image.resample(start_array.shape[0], start_array.shape[1])
new_mask_array = np.copy(mask_image_array)
mask = np.isin(mask_image_array, index, invert=True)
new_mask_array[mask] = -1
# print(np.unique(new_mask_array))
start_array = np.where(new_mask_array == -1, -1, start_array)
end_array = np.where(new_mask_array == -1, -1, end_array)

start_list2 = []
end_list2 = []

for i in range(0, index.shape[0], 1):
    pos = np.where(new_mask_array == index[i])
    mean_start = np.mean(start_array[pos[0], pos[1]])
    mean_end = np.mean(end_array[pos[0], pos[1]])
    start_list2.append(mean_start)
    end_list2.append(mean_end)
    # print(str(index[i]) + ': ' + str(int(mean_start)) + ' ' + str(int(mean_end)))

# save_global_image(start_array, start_save_path)
# save_global_image(end_array, end_save_path)
print(np.mean(np.array(start_list2)))
print(np.mean(np.array(end_list2)))