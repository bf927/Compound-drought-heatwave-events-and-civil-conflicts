import numpy as np
import pandas as pd
from osgeo import gdal, osr
import glob
import os

os.environ['PROJ_LIB'] = 'C:\\Python\\Lib\\site-packages\\osgeo\\data\\proj'
gdal.PushErrorHandler("CPLQuietErrorHandler")


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


def save_list(array_list, save_file):
    for i in range(0, 26, 1):
        formatted = "{:02}".format(int(i + 1))
        save_path = save_file + formatted + '.tif'
        save_global_image(array_list[i], save_path)


def nan2zero(array):
    nan_pos = np.isnan(array)
    array[nan_pos] = 0
    return array


def calculate_days(start_month, end_month, is_BIS):
    # Define a list of days in each month
    if is_BIS:
        days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # Calculate the total number of days
    if start_month <= end_month:
        total_days = sum(days_in_month[start_month - 1:end_month])
    else:
        total_days = sum(days_in_month[start_month - 1:]) + sum(days_in_month[:end_month])

    return total_days


def calculate_segmented_function(stage_length, stage_list, kc_list):
    # 计算stage_list的总长度
    total_stage_length = sum(stage_list)

    # 根据比例计算每个时间段在stage数组中的实际长度
    actual_stage_lengths = [int((s / total_stage_length) * stage_length) for s in stage_list]

    # 累积每个时间段的实际长度，以确定每个时间段在stage数组中的范围
    cumulative_stage_lengths = np.cumsum(actual_stage_lengths)

    # 创建一个空的y值数组，用于存储计算结果
    y_values = np.zeros(stage_length)

    # 第一段函数值恒定为kc_list的第一个数
    y_values[:actual_stage_lengths[0]] = kc_list[0]

    # 第二段函数值为一次函数，左端值为kc_list中第一个值，右端值为kc_list中第二个值
    y_values[actual_stage_lengths[0]:cumulative_stage_lengths[1]] = np.linspace(kc_list[0], kc_list[1],
                                                                                actual_stage_lengths[1], endpoint=False)

    # 第三段函数值恒定为kc_list中第二个数
    y_values[cumulative_stage_lengths[1]:cumulative_stage_lengths[2]] = kc_list[1]

    # 第四段函数值为一次函数，左端值为kc_list中第二个值，右端值为kc_list中第三个值
    y_values[cumulative_stage_lengths[2]:] = np.linspace(kc_list[1], kc_list[2],
                                                         stage_length - cumulative_stage_lengths[2])

    y_values = np.array(y_values)
    return y_values


def get_year_kc_array(stage_table, kc_table, day_last, day_first, crop_4stage_table, is_BIS):
    if is_BIS:
        kc_array_rainfall_list = []
        kc_array_irritated_list = []
        for i in range(0, 26, 1):
            kc_array_rainfall_list.append(np.ones((366, 360, 720)) * 0.5)
            kc_array_irritated_list.append(np.ones((366, 360, 720)) * 0.5)
    else:
        kc_array_rainfall_list = []
        kc_array_irritated_list = []
        for i in range(0, 26, 1):
            kc_array_rainfall_list.append(np.ones((365, 360, 720)) * 0.5)
            kc_array_irritated_list.append(np.ones((365, 360, 720)) * 0.5)

    crop_list = stage_table[:, 5]  # 生长期表格中的作物类型列

    for i in range(0, crop_list.shape[0], 1):
        print(i)
        row = int(stage_table[i, 1] - 1)  # 像元行号
        column = int(stage_table[i, 2] - 1)  # 像元列号
        crop_id = int(crop_list[i])  # 像元作物类别
        start = int(stage_table[i, -2])  # 起始
        end = int(stage_table[i, -1])  # 结束

        if crop_id > 26:
            flag = 'rainfall'
            crop_id = crop_id - 26
        else:
            flag = 'irritated'

        stage_list = crop_4stage_table[crop_id - 1, 1:] * 100  # 生长期四个时期的长度

        kc_list = kc_table[crop_id - 1, 1:]  # 特定作物的三个kc

        stage_length = calculate_days(start, end, is_BIS)  # 生长期总长度

        # 生长期的全部kc值
        crop_kc_function_value = calculate_segmented_function(int(stage_length), list(stage_list), list(kc_list))

        start_doy_index = day_first[start - 1]  # 起始月份第一天的在一年内的索引
        end_doy_index = day_last[end - 1]  # 结束月份最后一天的在一年内的索引

        if start < end:
            if flag == 'rainfall':
                kc_array_rainfall_list[crop_id - 1][start_doy_index:end_doy_index + 1, row, column] = \
                    crop_kc_function_value
            if flag == 'irritated':
                kc_array_irritated_list[crop_id - 1][start_doy_index:end_doy_index + 1, row, column] = \
                    crop_kc_function_value
        else:
            crop_kc_function_value1 = crop_kc_function_value[0:day_last[-1] - start_doy_index + 1]  # 起始月份到年末的kc
            crop_kc_function_value2 = crop_kc_function_value[day_last[-1] - start_doy_index + 1:]  # 年初到结束月份的kc
            if flag == 'rainfall':
                kc_array_rainfall_list[crop_id - 1][start_doy_index:, row, column] = \
                    crop_kc_function_value1
                kc_array_rainfall_list[crop_id - 1][0:end_doy_index + 1, row, column] = \
                    crop_kc_function_value2
            if flag == 'irritated':
                kc_array_irritated_list[crop_id - 1][start_doy_index:, row, column] = \
                    crop_kc_function_value1
                kc_array_irritated_list[crop_id - 1][0:end_doy_index + 1, row, column] = \
                    crop_kc_function_value2

    # print(np.sum(kc_array_rainfall_list[0]))
    return kc_array_rainfall_list, kc_array_irritated_list


def make_kc(stage_table_path, kc_table_path, crop_4stage_table_path, save_file):
    stage_table = pd.read_excel(stage_table_path)
    stage_table = np.array(stage_table)

    kc_table = pd.read_excel(kc_table_path)
    kc_table = np.array(kc_table)

    crop_4stage_table = pd.read_excel(crop_4stage_table_path)
    crop_4stage_table = np.array(crop_4stage_table)

    month_days = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    month_days_BIS = np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

    # 转化为索引
    day_last = np.cumsum(month_days)
    day_last_BIS = np.cumsum(month_days_BIS)
    day_first = day_last - month_days + 1
    day_first_BIS = day_last_BIS - month_days_BIS + 1

    rainfall_file = save_file + 'rainfall\\no_BIS\\'
    rainfall_BIS_file = save_file + 'rainfall\\BIS\\'
    irritated_file = save_file + 'irritated\\no_BIS\\'
    irritated_BIS_file = save_file + 'irritated\\BIS\\'

    # 非闰年
    # kc_array_rainfall_list, kc_array_irritated_list = get_year_kc_array(stage_table,
    #                                                                     kc_table,
    #                                                                     day_last - 1,
    #                                                                     day_first - 1,
    #                                                                     crop_4stage_table,
    #                                                                     False)
    #
    # save_list(kc_array_rainfall_list, rainfall_file)
    # save_list(kc_array_irritated_list, irritated_file)

    # 闰年
    kc_array_rainfall_BIS_list, kc_array_irritated_BIS_list = get_year_kc_array(stage_table,
                                                                                kc_table,
                                                                                day_last_BIS - 1,
                                                                                day_first_BIS - 1,
                                                                                crop_4stage_table,
                                                                                True)

    save_list(kc_array_rainfall_BIS_list, rainfall_BIS_file)
    save_list(kc_array_irritated_BIS_list, irritated_BIS_file)


if __name__ == '__main__':
    pixel_stage = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\water\\pixel_calendar.xlsx'
    kc = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\water\\kc2.xlsx'
    crop_4stage = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\water\\4stage_length.xlsx'
    path = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\kc2\\'
    make_kc(pixel_stage, kc, crop_4stage, path)
