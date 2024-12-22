from pyrs.algorithm import rs_image
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


production_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\crop_area_yield\\'
save_file = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\crop_production\\'

for i in range(0, 16, 1):
    wheat_file = production_file + 'wheat\\' + str(i + 2001) + '.tif'
    maize_file = production_file + 'maize\\' + str(i + 2001) + '.tif'
    rice_file = production_file + 'rice\\' + str(i + 2001) + '.tif'
    soybean_file = production_file + 'soybean\\' + str(i + 2001) + '.tif'

    wheat_array = rs_image.Image(wheat_file).get_array(True, 1)
    maize_array = rs_image.Image(maize_file).get_array(True, 1)
    rice_array = rs_image.Image(rice_file).get_array(True, 1)
    soybean_array = rs_image.Image(soybean_file).get_array(True, 1)

    total_production = wheat_array + maize_array + rice_array + soybean_array
    # total_production = cv2.resize(total_production, (8016, 4008), interpolation=cv2.INTER_NEAREST)
    save_path = save_file + str(i + 2001) + '.tif'
    save_global_image(total_production, save_path)