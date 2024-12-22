import netCDF4 as nc
import cv2
import numpy as np
from osgeo import gdal, osr
import os
from pyrs.algorithm import rs_image


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


def array_trans(global_array):
    left = global_array[:, 0:global_array.shape[1] // 2]
    right = global_array[:, global_array.shape[1] // 2:]
    new_array = np.append(right, left, axis=1)
    return new_array


def nan2zero(array):
    nan_pos = np.isnan(array)
    array[nan_pos] = 0
    return array


os.environ['PROJ_LIB'] = 'C:\\Python\\Lib\\site-packages\\osgeo\\data\\proj'
gdal.PushErrorHandler("CPLQuietErrorHandler")

file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\gdhy_v1.2_v1.3_20190128\\maize\\yield_'
area_path = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\crop_area\\maize_HarvestedAreaHectares.tif'
area_array = rs_image.Image(area_path).get_array(True, 1)
area_array = np.where(area_array < 0, 0, area_array)
area_array = np.where(area_array == np.min(area_array), 0, area_array)
area_array = nan2zero(area_array)


for i in range(0, 36, 1):
    file_path = file + str(i + 1981) + '.nc4'
    dataset = nc.Dataset(file_path)
    all_vars = dataset.variables.keys()
    image_array = np.array(dataset.variables['var'])
    new_array = nan2zero(image_array)
    trans_array = array_trans(new_array)
    yield_array = np.flipud(trans_array)
    yield_array = cv2.resize(yield_array, (4320, 2160), interpolation=cv2.INTER_NEAREST)
    yield_array = np.where(yield_array < 0, 0, yield_array)
    total_yield_array = yield_array * area_array
    total_yield = np.sum(total_yield_array)
    print(str(i + 1981) + ': ' + str(total_yield))

    output_path = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\crop_area_yield\\maize\\' + str(i + 1981) + '.tif'
    save_global_image(total_yield_array, output_path)