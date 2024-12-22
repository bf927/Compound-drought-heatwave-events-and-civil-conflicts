import numpy as np
from pyrs.algorithm import rs_image
import glob
from osgeo import gdal, osr
import cv2


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


file_path = 'D:\\Drought_and_heat_wave_coupling\\data\\SPI_data\\spi\\'
save_file = 'D:\\Drought_and_heat_wave_coupling\\data\\SPI_data\\year\\'

for year in range(2001, 2021, 1):
    spei_year_file = file_path + str(year)
    spei_path_list = glob.glob(spei_year_file + '\\*.tif')
    # print(spei_path_list)

    spei_month = np.zeros((12, 360, 720), np.float32)  # 构造特定年的月度pet数组
    for j in range(0, len(spei_path_list), 1):
        image = rs_image.Image(spei_path_list[j])
        image_array = image.get_array(True, 1, np.float32)
        image_array = cv2.resize(image_array, (720, 360), interpolation=cv2.INTER_NEAREST)
        spei_month[j, :, :] = image_array

    if year % 4 != 0:  # 判断是否为闰年
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # 初始化一个新的数组，用于存放每天的数据
    spei_daily = np.ones((sum(days_in_month), 360, 720), dtype=spei_month.dtype)

    # 记录上一个月份结束时的累积天数
    sum_days = 0
    for month, days in enumerate(days_in_month):
        spei_daily[sum_days: sum_days + days] = np.repeat(spei_month[month][np.newaxis, ...],
                                                          days, axis=0)  # 将当前月份的数据复制到daily_data数组中
        sum_days += days  # 更新累积天数

    output_path = save_file + str(year) + '.tif'
    save_global_image(spei_daily, output_path)