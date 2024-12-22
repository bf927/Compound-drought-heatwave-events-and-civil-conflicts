import netCDF4 as nc
import cv2
import numpy as np
from osgeo import gdal, osr
import os
import glob


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

file = 'D:\\Drought_and_heat_wave_coupling\\data\\Tmax_data\\'

year_path_list = glob.glob(file + '*')
for i in range(0, len(year_path_list), 1):
    month_path_list = glob.glob(year_path_list[i] + '\\*')
    for j in range(0, len(month_path_list), 1):
        day_path_list = glob.glob(month_path_list[j] + '\\*.nc')
        for k in range(0, len(day_path_list), 1):
            dataset = nc.Dataset(day_path_list[k])
            all_vars = dataset.variables.keys()
            array = dataset.variables['Temperature_Air_2m_Max_24h'][:][0]
            resample_array = cv2.resize(array, (720, 360), interpolation=cv2.INTER_NEAREST)

            day = k + 1
            formatted_day = "{:02}".format(day)
            output_path = month_path_list[j] + '\\' + formatted_day + '.tiff'
            save_global_image(resample_array, output_path)