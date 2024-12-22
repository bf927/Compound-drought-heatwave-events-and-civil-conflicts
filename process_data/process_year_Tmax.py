import numpy as np
from pyrs.algorithm import rs_image
import glob
from osgeo import gdal, osr


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


Tmax_file = 'D:\\Drought_and_heat_wave_coupling\\data\\Tmax_data\\'
save_file = 'D:\\Drought_and_heat_wave_coupling\\data\\Tmax_year\\'

Tmax_year_list = glob.glob(Tmax_file + '*')
for i in range(0, len(Tmax_year_list), 1):
    year = i + 2001
    Tmax_month_list = glob.glob(Tmax_year_list[i] + '\\*')
    if year % 4 != 0:
        days = 365
    else:
        days = 366

    total_day = np.zeros((days, 360, 720))
    day_index = 0
    for j in range(0, len(Tmax_month_list), 1):
        Tmax_day_list = glob.glob(Tmax_month_list[j] + '\\*.tiff')
        for k in range(0, len(Tmax_day_list), 1):
            print(Tmax_day_list[k])
            dataset = rs_image.Image(Tmax_day_list[k])
            array = dataset.get_array(True, 1, np.float32)
            total_day[day_index, :, :] = array
            day_index += 1

    output_path = save_file + str(year) + '.tif'
    # save_global_image(total_day, output_path)