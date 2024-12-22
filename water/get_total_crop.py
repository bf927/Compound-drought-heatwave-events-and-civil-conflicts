import numpy as np
from pyrs.algorithm import rs_image
from osgeo import gdal, osr
import cv2


def nan2zero(array):
    nan_pos = np.isnan(array)
    array[nan_pos] = 0
    return array


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


etp_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\etp\\rainfall\\GW\\'
eta_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\eta\\rainfall\\GW\\'
ks_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\etp\\rainfall\\ks\\'
gw_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\total_crop\\staple_gw\\'
new_ks_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\total_crop\\staple_ks\\'

for i in range(0, 20, 1):
    np.seterr(all="ignore")

    year = str(i + 2001)
    year_total_crop_eta = np.zeros((11, 360, 720))
    year_total_crop_ks = np.zeros((11, 360, 720))
    num = 0
    for j in range(0, 17, 1):
        if (j == 8) or (j == 11) or (j == 12) or (j == 13) or (j == 14) or (j == 15):
            continue
        else:
            formatted = "{:02}".format(int(j + 1))

            eta_path = eta_file + formatted + '\\' + year + '.tif'
            ks_path = ks_file + formatted + '\\' + year + '.tif'

            eta = rs_image.Image(eta_path).get_array(True, 1)
            ks = rs_image.Image(ks_path).get_array(True, 1)

            year_total_crop_eta[num, :, :] = eta
            year_total_crop_ks[num, :, :] = ks

            num += 1

    total_eta = np.sum(year_total_crop_eta, axis=0)
    total_ks = np.sum(year_total_crop_ks, axis=0) / np.sum(year_total_crop_eta > 0, axis=0)
    new_ks = nan2zero(total_ks)

    # total_eta = cv2.resize(total_eta, (8016, 4008), interpolation=cv2.INTER_NEAREST)
    # new_ks = cv2.resize(new_ks, (8016, 4008), interpolation=cv2.INTER_NEAREST)

    gw_path = gw_file + year + '.tif'
    new_ks_path = new_ks_file + year + '.tif'

    save_global_image(total_eta, gw_path)
    save_global_image(new_ks, new_ks_path)