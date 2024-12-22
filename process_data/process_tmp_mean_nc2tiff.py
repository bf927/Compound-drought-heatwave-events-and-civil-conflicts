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

file = 'C:\\Users\\Administrator\\Desktop\\cru_ts4.08.2001.2010.tmp.dat.nc'
output_file = 'C:\\Users\\Administrator\\Desktop\\tmp_mean\\'

dataset = nc.Dataset(file)
all_vars = dataset.variables.keys()
# print(all_vars)

# 获取所有变量信息
all_vars_info = dataset.variables.items()
# print(all_vars_info)
all_vars_info = list(all_vars_info)

array = dataset.variables['tmp'][:]
print(array.shape)

for i in range(2001, 2011, 1):
    year_array = np.zeros((360, 720), dtype=np.float32)
    for j in range(1, 13, 1):
        start = (i - 2001) * 12 + j - 1
        # print(start)
        month_array = array[start, :, :]
        month_array = np.flipud(month_array)
        nan_pos = np.isnan(month_array)
        month_array[nan_pos] = 0
        max_value = np.max(month_array)
        print(max_value)
        year_array += month_array

    mean_year_array = year_array / 12
    max_value = np.max(mean_year_array)
    mean_year_array = np.where(mean_year_array == max_value, 0, mean_year_array)
    print(mean_year_array.max())
    mean_year_save_path = output_file + str(i) + '.tif'
    save_global_image(mean_year_array, mean_year_save_path)