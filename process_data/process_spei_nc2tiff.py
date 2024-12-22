import netCDF4 as nc
import cv2
import numpy as np
from osgeo import gdal, osr
import os


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


os.environ['PROJ_LIB'] = 'C:\\Python\\Lib\\site-packages\\osgeo\\data\\proj'
gdal.PushErrorHandler("CPLQuietErrorHandler")

file = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\SPEI_data\\spei01.nc'
output_file = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\SPEI_data\\spei\\'

dataset = nc.Dataset(file)
all_vars = dataset.variables.keys()
# print(all_vars)

# 获取所有变量信息
all_vars_info = dataset.variables.items()
# print(all_vars_info)
all_vars_info = list(all_vars_info)

array = dataset.variables['spei'][:]
print(array.shape)
start_year_index = (1989 - 1901) * 12
array2 = array[start_year_index:, :, :]

for i in range(1989, 2023, 1):
    for j in range(1, 13, 1):
        start = (i - 1989) * 12 + j - 1
        print(start)
        month_array = array2[start, :, :]
        month_array = np.flipud(month_array)

        formatted_month = "{:02}".format(j)
        month_spei_save_path = output_file + str(i) + '\\' + str(formatted_month) + '.tiff'
        save_global_image(month_array, month_spei_save_path)