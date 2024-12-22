from pyrs.algorithm import rs_image
import numpy as np
import cv2
import pandas as pd
from osgeo import gdal, osr


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
    nan_pos = np.isnan(array)
    array[nan_pos] = 0
    return array


def negative2zero(array):
    array = np.where(array < 0, 0, array)
    return array


etp_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\etp\\rainfall\\GW\\'
eta_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\eta\\rainfall\\GW\\'
rainfall_area_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\crop_area\\rainfall\\'
rainfall_max_yield_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\HarvestedAreaYield175Crops_Geotiff\\' \
                          'yield_26\\'
ky_path = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\HarvestedAreaYield175Crops_Geotiff\\ky.xlsx'
energy_path = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\HarvestedAreaYield175Crops_Geotiff\\Calories.xlsx'

save_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\HarvestedAreaYield175Crops_Geotiff\\' \
            'total_yield_pre\\'
ky_array = np.array(pd.read_excel(ky_path)).flatten()
energy_array = np.array(pd.read_excel(energy_path)['type'])

for year in range(2001, 2021, 1):
    print(year)
    total_array = np.zeros((360, 720))
    for i in range(1, 27, 1):
        np.seterr(all="ignore")
        formatted = "{:02}".format(int(i))

        etp_path = etp_file + formatted + '\\' + str(year) + '.tif'
        eta_path = eta_file + formatted + '\\' + str(year) + '.tif'
        rainfall_area_path = rainfall_area_file + '\\annual_area_harvested_rfc_crop' + formatted + '_ha_30mn1.tif'
        rainfall_max_yield_path = rainfall_max_yield_file + formatted + '.tif'

        etp = rs_image.Image(etp_path).get_array(True, 1)
        eta = rs_image.Image(eta_path).get_array(True, 1)
        rainfall_area = nan2zero(rs_image.Image(rainfall_area_path).get_array(True, 1))
        rainfall_max_yield = nan2zero(rs_image.Image(rainfall_max_yield_path).get_array(True, 1))
        print(np.sum(rainfall_max_yield))

        rainfall_max_yield_resample = cv2.resize(rainfall_max_yield, (720, 360), interpolation=cv2.INTER_NEAREST)

        ks = eta / etp
        new_ks = nan2zero(ks)

        ky = ky_array[i - 1]
        yield_act = rainfall_max_yield_resample * (1 + ky * (new_ks - 1))

        rainfall_yield_act = np.where(rainfall_area == 0, 0, yield_act)
        rainfall_yield_act_filter = np.where(rainfall_yield_act < 0, 0, rainfall_yield_act)
        total_array += rainfall_yield_act_filter

    save_path = save_file + str(year) + '.tif'
    save_global_image(total_array, save_path)