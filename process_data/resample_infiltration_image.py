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


path = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\HWSD\\texture.tif'
data = rs_image.Image(path)
array = data.get_array(True, 1)
array = cv2.resize(array, (720, 360), interpolation=cv2.INTER_NEAREST)

# 1 clay(heavy)
# 2 silty clay
# 3 clay (light)
# 4 silty clay loam
# 5 clay loam
# 6 silt
# 7 silt loam
# 8 sandy clay
# 9 loam
# 10 sandy clay loam
# 11 sandy loam
# 12 loamy sand
# 13 sand

print(np.unique(array))
array = np.where(array == 1, 1.5 * 24, array)
array = np.where(array == 2, 1.5 * 24, array)
array = np.where(array == 3, 1.5 * 24, array)
array = np.where(array == 4, 1.5 * 24, array)
array = np.where(array == 5, 1.5 * 24, array)
array = np.where(array == 6, 5.1 * 24, array)
array = np.where(array == 7, 7.6 * 24, array)
array = np.where(array == 8, 1.5 * 24, array)
array = np.where(array == 9, 7.6 * 24, array)
array = np.where(array == 10, 5.1 * 24, array)
array = np.where(array == 11, 20.3 * 24, array)
array = np.where(array == 12, 20.3 * 24, array)
array = np.where(array == 13, 41.4 * 24, array)

output_path = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\infiltration_rate\\infiltration.tif'
save_global_image(array, output_path)