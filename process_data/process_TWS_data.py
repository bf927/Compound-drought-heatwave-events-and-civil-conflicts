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
    data_set = driver.Create(save_path, array_data.shape[2], array_data.shape[1], array_data.shape[0], gdal.GDT_Float32)

    for i in range(0, array_data.shape[0], 1):
        data_set.GetRasterBand(i + 1).WriteArray(array_data[i, :, :])

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
    x_resolution = (x_max - x_min) / float(array_data.shape[2])
    y_resolution = (y_max - y_min) / float(array_data.shape[1])

    data_set.SetGeoTransform([x_min, x_resolution, 0, y_max, 0, -y_resolution])


def array_trans(global_array):
    left = global_array[:, 0:global_array.shape[1] // 2]
    right = global_array[:, global_array.shape[1] // 2:]
    new_array = np.append(right, left, axis=1)
    return new_array


file = 'D:\\Drought_and_heat_wave_coupling\\data\\TWS\\CSR\\CSR-based GTWS-MLrec TWS.nc'
save_file = 'D:\\Drought_and_heat_wave_coupling\\data\\TWS\\CSR\\year\\'

dataset = nc.Dataset(file)
all_vars = dataset.variables.keys()
# print(all_vars)

# 获取所有变量信息
all_vars_info = dataset.variables.items()
# print(all_vars_info)
all_vars_info = list(all_vars_info)

array = dataset.variables['TWSA'][:]
# print(array.shape)

start = (2000 - 1940 + 1) * 12
end = (2020 - 1940 + 1) * 12
total_array = array[start:end, :, :]
print(total_array.shape)

year = 2001
for i in range(0, 240, 12):
    year_array = total_array[i:i + 12, :, :]

    if year % 4 != 0:  # 判断是否为闰年
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # 初始化一个新的数组，用于存放每天的数据
    tws_daily = np.ones((sum(days_in_month), total_array.shape[1], total_array.shape[2]), dtype=year_array.dtype)

    # 记录上一个月份结束时的累积天数
    sum_days = 0
    for month, days in enumerate(days_in_month):
        tws_daily[sum_days: sum_days + days] = np.repeat(year_array[month][np.newaxis, ...],
                                                         days, axis=0)  # 将当前月份的数据复制到daily_data数组中
        sum_days += days  # 更新累积天数

    # 创建一个空的输出数组，形状为 (365, 360, 720)
    output_array = np.empty((sum(days_in_month), 360, 720))

    # 对每一天进行重采样
    for j in range(sum(days_in_month)):
        # 使用 cv2.resize 对每一天的二维数组进行重采样
        output_array[j] = cv2.resize(tws_daily[j], (720, 360), interpolation=cv2.INTER_NEAREST)

    output_path = save_file + str(year) + '.tif'
    save_global_image(output_array, output_path)

    year += 1
