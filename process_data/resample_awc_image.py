from pyrs.algorithm import rs_image
import numpy as np
from osgeo import gdal, osr
import cv2


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


path = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\awc\\AWC_CLASS.tif'
data = rs_image.Image(path)
array = data.get_array(True, 1)

nan_pos = np.isnan(array)
array[nan_pos] = 0

array = cv2.resize(array, (720, 360), interpolation=cv2.INTER_NEAREST)

array = np.where(array == -1, 0, array)
array = np.where(array == 1, 150, array)
array = np.where(array == 2, 125, array)
array = np.where(array == 3, 100, array)
array = np.where(array == 4, 75, array)
array = np.where(array == 5, 50, array)
array = np.where(array == 6, 15, array)
array = np.where(array == 7, 0, array)


output_path = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\awc\\awc.tif'
save_global_image(array, output_path)