import numpy as np
from pyrs.algorithm import rs_image
import pandas as pd
from osgeo import gdal, osr

CROP_ID = 26


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


class Stage:
    def __init__(self, start, end):
        self.start = int(start)
        self.end = int(end)


def nan2zero(array):
    nan_pos = np.isnan(array)
    array[nan_pos] = 0
    return array


def get_region_stage(region_stage_array):
    stage_list = []
    if np.sum(region_stage_array[0:3]) != 0:
        stage1 = Stage(region_stage_array[1], region_stage_array[2])
        stage_list.append(stage1)
    if np.sum(region_stage_array[3:6]) != 0:
        stage2 = Stage(region_stage_array[4], region_stage_array[5])
        stage_list.append(stage2)
    if np.sum(region_stage_array[6:9]) != 0:
        stage3 = Stage(region_stage_array[7], region_stage_array[8])
        stage_list.append(stage3)

    return stage_list


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


def get_year_kc_array(crop_area_array, calender_region_array, kc_table, stage_table, day_last, day_first,
                      crop_4stage_table, is_BIS):
    if is_BIS:
        kc_array = np.zeros((366, crop_area_array.shape[0], crop_area_array.shape[1]))
    else:
        kc_array = np.zeros((365, crop_area_array.shape[0], crop_area_array.shape[1]))

    crop_list = stage_table[:, 1]  # 生长期表格中的作物类型列
    crop_pos = np.where(crop_list == CROP_ID)[0]  # 找到特定作物的列索引

    stage_start_month_array = crop_4stage_table[:, 0]  # 同一个作物在不同种植月份拥有不同生长期长度
    stage_4length_array = crop_4stage_table[:, 1:5]

    kc_crop_id_array = kc_table[:, 0]
    kc_pos = np.where(kc_crop_id_array == CROP_ID)[0][0]
    kc_list = kc_table[kc_pos, 1:]  # 特定作物的三个kc
    for i in range(0, crop_pos.shape[0], 1):  # 遍历全部存在特定作物的区域
        region_info = stage_table[crop_pos[i], :]  # 某一区域的全部信息
        region_id = region_info[0]  # 区域id
        region_stage_list = get_region_stage(region_info[3:])  # 区域特定作物生长期列表

        intersection_pos = np.where((calender_region_array == region_id) & (crop_area_array > 0))  # 特定区域特定作物位置
        no_growing = np.ones((kc_array.shape[0])) * 0.5  # 非生长季kc设置为0.5
        kc_array[:, intersection_pos[0], intersection_pos[1]] = no_growing[:, None]  # kc矩阵的特定区域起始全设置为0.5

        for j in range(0, len(region_stage_list), 1):  # 遍历全部生长期
            start = region_stage_list[j].start  # 生长期起始月份
            end = region_stage_list[j].end  # 生长期结束月份
            stage_length = calculate_days(start, end, is_BIS)  # 总时长

            stage_pos = np.where(stage_start_month_array == start)[0][0]
            stage_list = stage_4length_array[stage_pos, :]  # 生长期四个时期的长度

            # 生长期的全部kc值
            crop_kc_function_value = calculate_segmented_function(int(stage_length), list(stage_list), list(kc_list))

            start_doy_index = day_first[start - 1]  # 起始月份第一天的在一年内的索引
            end_doy_index = day_last[end - 1]  # 结束月份最后一天的在一年内的索引
            if start < end:
                kc_array[start_doy_index:end_doy_index + 1, intersection_pos[0], intersection_pos[1]] = \
                    crop_kc_function_value[:, None]
            else:
                crop_kc_function_value1 = crop_kc_function_value[0:day_last[-1] - start_doy_index + 1]  # 起始月份到年末的kc
                crop_kc_function_value2 = crop_kc_function_value[day_last[-1] - start_doy_index + 1:]  # 年初到结束月份的kc
                kc_array[start_doy_index:, intersection_pos[0], intersection_pos[1]] = crop_kc_function_value1[:, None]
                kc_array[0:end_doy_index + 1, intersection_pos[0], intersection_pos[1]] = \
                    crop_kc_function_value2[:, None]

    return kc_array


def make_kc(crop_area_path, calender_region_path, kc_table_path, stage_table_path, crop_4stage_table_pah,
            no_BIS_kc_path, BIS_kc_path):
    crop_area_dataset = rs_image.Image(crop_area_path)
    crop_area_array = crop_area_dataset.get_array(True, 1)
    crop_area_array = nan2zero(crop_area_array)

    calender_region_dataset = rs_image.Image(calender_region_path)
    calender_region_array = calender_region_dataset.get_array(True, 1)
    calender_region_array = nan2zero(calender_region_array)

    kc_table = pd.read_excel(kc_table_path)
    kc_table = np.array(kc_table)

    stage_table = pd.read_excel(stage_table_path)
    stage_table = np.array(stage_table)
    stage_table = nan2zero(stage_table)

    crop_4stage_table = pd.read_excel(crop_4stage_table_pah)
    crop_4stage_table = np.array(crop_4stage_table)

    month_days = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    month_days_BIS = np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])

    # 转化为索引
    day_last = np.cumsum(month_days)
    day_last_BIS = np.cumsum(month_days_BIS)
    day_first = day_last - month_days + 1
    day_first_BIS = day_last_BIS - month_days_BIS + 1

    # 非闰年
    kc_array = get_year_kc_array(crop_area_array,
                                 calender_region_array,
                                 kc_table,
                                 stage_table,
                                 day_last - 1,
                                 day_first - 1,
                                 crop_4stage_table,
                                 False)

    # 闰年
    kc_array_BIS = get_year_kc_array(crop_area_array,
                                     calender_region_array,
                                     kc_table,
                                     stage_table,
                                     day_last_BIS - 1,
                                     day_first_BIS - 1,
                                     crop_4stage_table,
                                     True)

    save_global_image(kc_array, no_BIS_kc_path)
    save_global_image(kc_array_BIS, BIS_kc_path)


if __name__ == '__main__':
    formatted = "{:02}".format(int(CROP_ID))
    crop_area = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\crop_area\\rainfall\\' \
                'annual_area_harvested_rfc_crop' + formatted + '_ha_30mn1.tif'
    calender_region = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\unit_code1.tif'
    kc = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\water\\kc.xlsx'
    stage = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\water\\irritated_calendar.xlsx'
    crop_4stage = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\water\\stage\\' + \
                  str(CROP_ID) + '.xlsx'
    no_BIS = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\kc\\rainfall\\no_BIS\\' + formatted + '.tif'
    BIS = 'D:\\Drought_and_heat_wave_coupling\\data\\water\\kc\\rainfall\\BIS\\' + formatted + '.tif'
    make_kc(crop_area, calender_region, kc, stage, crop_4stage, no_BIS, BIS)
