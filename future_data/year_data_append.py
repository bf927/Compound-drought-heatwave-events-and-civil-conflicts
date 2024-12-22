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


year_data_file = 'E:\\CDHW_conflict\\future_climate\\t_mean\\year\\ssp370_model1\\'
path_list = glob.glob(year_data_file + '*.tif')
array_list = []

for i in range(0, len(path_list), 1):
    array_list.append(rs_image.Image(path_list[i]).get_array(True, 0))

total_array = np.concatenate(array_list, axis=0)
print(total_array.shape)

save_global_image2(total_array,
                   'E:\\CDHW_conflict\\future_climate\\t_mean\\total_data\\ssp370_1941_2100_model1.tif')