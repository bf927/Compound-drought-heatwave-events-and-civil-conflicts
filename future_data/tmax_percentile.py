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


model1_file = 'E:\\CDHW_conflict\\future_climate\\t_max\\GFDL_ESM4\\history\\'

output1 = 'E:\\CDHW_conflict\\future_climate\\t_max\\percentile_2041_2014\\25.tif'
output2 = 'E:\\CDHW_conflict\\future_climate\\t_max\\percentile_2041_2014\\75.tif'
output3 = 'E:\\CDHW_conflict\\future_climate\\t_max\\percentile_2041_2014\\90.tiff'

model1_path_list = glob.glob(model1_file + '*.nc')

compos_array_list = []

# 使用内存映射文件创建一个空的数组，用于存储最终组合的数据
output_shape = (27028, 360, 720)
output_dtype = np.float16
output_filename = 'E:\\CDHW_conflict\\future_climate\\t_max\\1941_2014.dat'
output_memmap = np.memmap(output_filename, dtype=output_dtype, mode='w+', shape=output_shape)

# 初始化当前索引
current_index = 0

for i in range(0, len(model1_path_list), 1):
    compos_array = np.array(nc.Dataset(model1_path_list[i]).variables['tasmax'][:], dtype=np.float16)
    print(compos_array.shape)
    output_memmap[current_index:current_index + compos_array.shape[0], :, :] = compos_array
    current_index += compos_array.shape[0]
    del compos_array  # 删除不再需要的数组，释放内存

# 关闭内存映射文件
del output_memmap

# 重新加载内存映射文件以进行后续处理
output_memmap = np.memmap(output_filename, dtype=output_dtype, mode='r', shape=output_shape)

image_25 = np.percentile(output_memmap, 25, axis=0)
save_global_image(image_25, output1)

image_75 = np.percentile(output_memmap, 75, axis=0)
save_global_image(image_75, output2)

image_90 = np.percentile(output_memmap, 90, axis=0)
save_global_image(image_90, output3)

# 最后，删除内存映射文件
del output_memmap