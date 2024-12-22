import glob
from pyrs.algorithm import rs_image
import numpy as np
from osgeo import gdal, osr
import cv2


def save_global_image(array_data, save_path):
    # 创建一个新的GeoTIFF文件
    driver = gdal.GetDriverByName('GTiff')
    data_set = driver.Create(save_path, array_data.shape[1], array_data.shape[0], 1, gdal.GDT_Float32)

    data_set.GetRasterBand(1).WriteArray(array_data)

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


def nan2zero(array):
    nan_pos = np.isnan(array)
    array[nan_pos] = 0
    return array


file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\crop_production_26\\'
image_path_list = glob.glob(file + '*.tif')

total_image = np.zeros((len(image_path_list), 2160, 4320))

for i in range(0, len(image_path_list), 1):
    image_array = nan2zero(rs_image.Image(image_path_list[i]).get_array(True, 1))
    total_image[i, :, :] = image_array

total_image = np.sum(total_image, axis=0)
total_image = cv2.resize(total_image, (8016, 4008), interpolation=cv2.INTER_NEAREST)

save_global_image(total_image, 'D:\\Drought_and_heat_wave_coupling\\data\\water\\crop_production_26\\total_crop.tif')