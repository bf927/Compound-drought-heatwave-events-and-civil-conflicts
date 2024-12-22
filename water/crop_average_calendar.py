import numpy as np
import pandas as pd
from osgeo import gdal, osr
import glob
import os
from pyrs.algorithm import rs_image
import glob


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

    del data_set


path = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\kc2\\irritated\\no_BIS\\'
path_list = glob.glob(path + '*.tif')
average_image = np.zeros((365, 360, 720))
for i in range(0, len(path_list), 1):
    print(i)
    array = rs_image.Image(path_list[i]).get_array(True, 1)
    average_image += array

average_image = average_image / len(path_list)
grow_num = np.sum(average_image != 0.5, axis=0)
grow_percent = grow_num / 365
save_global_image(grow_percent,
                  'D:\\Drought_and_heat_wave_coupling\\data\\water\\kc2\\irritated\\average_grow_percent.tif')