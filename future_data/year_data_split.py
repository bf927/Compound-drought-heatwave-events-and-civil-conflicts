from pyrs.algorithm import rs_image
import numpy as np
from osgeo import gdal, osr
import glob


def save_global_image2(array_data, save_path):
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


total_path = 'E:\\CDHW_conflict\\future_climate\\spei\\ssp370_model1_1989_2020_01.tif'
save_file = 'E:\\CDHW_conflict\\future_climate\\spei_year\\ssp370_1989_2020_01\\'
total_array = rs_image.Image(total_path).get_array(True, 0)

year = 1941
for i in range(0, total_array.shape[0], 12):
    year_array = total_array[i:i + 12, :, :]
    save_path = save_file + str(year) + '.tif'
    save_global_image2(year_array, save_path)

    year += 1