import netCDF4 as nc
import cv2
from osgeo import gdal, osr
import os

os.environ['PROJ_LIB'] = 'C:\\Python\\Lib\\site-packages\\osgeo\\data\\proj'
gdal.PushErrorHandler("CPLQuietErrorHandler")

file = 'D:\\landcover\\2020\\C3S-LC-L4-LCCS-Map-300m-P1Y-2020-v2.1.1.nc'
output_tiff = 'D:\\Drought_and_heat_wave_coupling\\data\\landcover\\2020.tif'

dataset = nc.Dataset(file)
all_vars = dataset.variables.keys()
# print(all_vars)
# print(len(all_vars))

# 获取所有变量信息
all_vars_info = dataset.variables.items()
# print(all_vars_info)
all_vars_info = list(all_vars_info)

# # 获取单独的一个变量的数据
array = dataset.variables['lccs_class'][:][0]
print(array.shape)

array_data = cv2.resize(array, (8016, 4008), interpolation=cv2.INTER_NEAREST)
# 获取数组的行数和列数
rows, cols = array_data.shape

# 创建一个新的GeoTIFF文件
driver = gdal.GetDriverByName('GTiff')
dataset = driver.Create(output_tiff, cols, rows, 1, gdal.GDT_Byte)

# 设置数组数据
band = dataset.GetRasterBand(1)
band.WriteArray(array_data)

# 添加地理坐标系和全球范围
projection = osr.SpatialReference()
projection.ImportFromEPSG(4326)  # WGS 1984坐标系
dataset.SetProjection(projection.ExportToWkt())

# 定义全球范围的坐标范围
x_min = -180
x_max = 180
y_min = -90
y_max = 90

# 设置全球范围的空间分辨率
x_resolution = (x_max - x_min) / float(array_data.shape[1])
y_resolution = (y_max - y_min) / float(array_data.shape[0])

dataset.SetGeoTransform([x_min, x_resolution, 0, y_max, 0, -y_resolution])

# 保存数据并关闭文件
band.FlushCache()
dataset = None