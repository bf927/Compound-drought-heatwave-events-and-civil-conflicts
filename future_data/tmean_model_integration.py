import numpy as np
import glob
import netCDF4 as nc
from osgeo import gdal, osr
import os

os.environ['PROJ_LIB'] = 'C:\\Python\\Lib\\site-packages\\osgeo\\data\\proj'

gdal.PushErrorHandler("CPLQuietErrorHandler")


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


model1_file = 'E:\\CDHW_conflict\\future_climate\\t_mean\\GFDL_ESM4\\history\\'
model2_file = 'E:\\CDHW_conflict\\future_climate\\t_mean\\IPSL_CM6A_MR\\history\\'
model3_file = 'E:\\CDHW_conflict\\future_climate\\t_mean\\MPI_ESM1_2_HR\\history\\'
model4_file = 'E:\\CDHW_conflict\\future_climate\\t_mean\\MRI_ESM2_0\\history\\'
model5_file = 'E:\\CDHW_conflict\\future_climate\\t_mean\\UKESM1_0_LL\\history\\'

year_save_file = 'E:\\CDHW_conflict\\future_climate\\t_mean\\year\\ssp585\\'

model1_path_list = glob.glob(model1_file + '*.nc')
model2_path_list = glob.glob(model2_file + '*.nc')
model3_path_list = glob.glob(model3_file + '*.nc')
model4_path_list = glob.glob(model4_file + '*.nc')
model5_path_list = glob.glob(model5_file + '*.nc')

model_path_list = [model1_path_list, model2_path_list, model3_path_list, model4_path_list, model5_path_list]

model1_corr_path = 'E:\\CDHW_conflict\\future_climate\\t_mean\\GFDL_ESM4\\corr.npy'
model2_corr_path = 'E:\\CDHW_conflict\\future_climate\\t_mean\\IPSL_CM6A_MR\\corr.npy'
model3_corr_path = 'E:\\CDHW_conflict\\future_climate\\t_mean\\MPI_ESM1_2_HR\\corr.npy'
model4_corr_path = 'E:\\CDHW_conflict\\future_climate\\t_mean\\MRI_ESM2_0\\corr.npy'
model5_corr_path = 'E:\\CDHW_conflict\\future_climate\\t_mean\\UKESM1_0_LL\\corr.npy'

model_corr1 = np.mean(np.load(model1_corr_path))
model_corr2 = np.mean(np.load(model2_corr_path))
model_corr3 = np.mean(np.load(model3_corr_path))
model_corr4 = np.mean(np.load(model4_corr_path))
model_corr5 = np.mean(np.load(model5_corr_path))

weight1 = model_corr1 / (model_corr1 + model_corr2 + model_corr3 + model_corr4 + model_corr5)
weight2 = model_corr2 / (model_corr1 + model_corr2 + model_corr3 + model_corr4 + model_corr5)
weight3 = model_corr3 / (model_corr1 + model_corr2 + model_corr3 + model_corr4 + model_corr5)
weight4 = model_corr4 / (model_corr1 + model_corr2 + model_corr3 + model_corr4 + model_corr5)
weight5 = model_corr5 / (model_corr1 + model_corr2 + model_corr3 + model_corr4 + model_corr5)

model_corr_list = [weight1, weight2, weight3, weight4, weight5]

compos_array_list = []

# 使用内存映射文件创建一个空的数组，用于存储最终组合的数据
# output_shape = (29219, 360, 720)
output_shape = (5113, 360, 720)
output_dtype = np.float16
output_filename = 'E:\\CDHW_conflict\\future_climate\\t_mean\\compos_history.dat'
output_memmap = np.memmap(output_filename, dtype=output_dtype, mode='w+', shape=output_shape)

# 初始化当前索引
current_index = 0

for i in range(0, len(model1_path_list), 1):
    compos_array = np.array(nc.Dataset(model1_path_list[i]).variables['tas'][:] * model_corr_list[0],
                            dtype=np.float16)
    for j in range(1, len(model_path_list), 1):
        model_array = np.array(nc.Dataset(model_path_list[j][i]).variables['tas'][:] * model_corr_list[j],
                               dtype=np.float16)
        compos_array += model_array
        del model_array  # 删除不再需要的数组，释放内存

    print(compos_array.shape)
    output_memmap[current_index:current_index + compos_array.shape[0], :, :] = compos_array
    current_index += compos_array.shape[0]
    del compos_array  # 删除不再需要的数组，释放内存

# 关闭内存映射文件
del output_memmap

# 重新加载内存映射文件以进行后续处理
output_memmap = np.memmap(output_filename, dtype=output_dtype, mode='r', shape=output_shape)


def is_leap_year(year):
    """判断年份是否为闰年"""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_year(year):
    """根据年份返回该年的天数"""
    return 366 if is_leap_year(year) else 365


def calculate_monthly_averages_from_3d_array(three_d_array):
    """
    Calculate the monthly averages from a 3D array representing daily data for a single year.

    Parameters:
    - three_d_array: 3D numpy array where the first dimension represents days,
                     the second dimension represents height, and the third dimension
                     represents width.

    Returns:
    - monthly_averages: 3D numpy array where the first dimension represents months,
                        the second dimension represents height, and the third dimension
                        represents width.
    """
    num_days, height, width = three_d_array.shape

    # Days in each month for a leap and a non-leap year
    days_in_month_leap = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    days_in_month_non_leap = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # Check if the year is a leap year based on the number of days
    Is_leap_year = num_days == 366

    # Choose the correct days in month array
    days_in_month = days_in_month_leap if Is_leap_year else days_in_month_non_leap

    # Initialize an array to store monthly averages
    monthly_averages = np.zeros((12, height, width))

    start_day = 0
    for month in range(12):
        end_day = start_day + days_in_month[month]
        monthly_data = three_d_array[start_day:end_day, :, :]
        monthly_averages[month, :, :] = np.mean(monthly_data, axis=0)
        start_day = end_day

    return monthly_averages


# 计算起始年份和结束年份
start_year = 2001
end_year = 2014

# 用于保存当前年份的起始索引
current_index = 0

# 遍历年份，并保存每年的数组
for years in range(start_year, end_year + 1):
    print(years)
    days = days_in_year(years)
    year_data = output_memmap[current_index:current_index + days, :, :]
    month_mean_data = calculate_monthly_averages_from_3d_array(year_data)

    # 保存每年的数据到 GeoTIFF 文件
    save_path = year_save_file + str(years) + '.tif'
    save_global_image2(month_mean_data, save_path)

    # 更新当前索引
    current_index += days

# 最后，删除内存映射文件
del output_memmap
# os.remove(output_filename)
