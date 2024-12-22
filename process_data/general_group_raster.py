from osgeo import gdal, ogr
import os
from pyrs.algorithm import rs_image
import numpy as np

os.environ['PROJ_LIB'] = 'C:\\Python\\Lib\\site-packages\\osgeo\\data\\proj'
gdal.PushErrorHandler("CPLQuietErrorHandler")


def rasterize_vector(input_vector, input_raster, output_raster, field_name, field_value):
    # 打开输入矢量文件
    vector_ds = ogr.Open(input_vector)
    vector_layer = vector_ds.GetLayer()

    # 打开输入栅格文件以获取空间参考信息
    raster_ds = gdal.Open(input_raster)
    geo_transform = raster_ds.GetGeoTransform()
    projection = raster_ds.GetProjection()
    x_size = raster_ds.RasterXSize
    y_size = raster_ds.RasterYSize
    raster_ds = None  # 关闭栅格文件

    # 创建输出栅格文件
    driver = gdal.GetDriverByName('GTiff')
    target_ds = driver.Create(output_raster, x_size, y_size, 1, gdal.GDT_Byte)
    target_ds.SetGeoTransform(geo_transform)
    target_ds.SetProjection(projection)
    band = target_ds.GetRasterBand(1)
    band.SetNoDataValue(0)

    # 过滤字段
    vector_layer.SetAttributeFilter(f"{field_name} = {field_value}")

    # 栅格化
    gdal.RasterizeLayer(target_ds, [1], vector_layer, options=["ALL_TOUCHED=TRUE", "ATTRIBUTE=" + field_name])

    # 清理
    target_ds = None
    vector_ds = None


if __name__ == '__main__':
    # 调用函数
    input_vector = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\group_region_file\\shp\\' \
                   'group_region.shp'
    input_raster = 'D:\\Drought_and_heat_wave_coupling\\data\\deaths_pf_per_100,000\\' \
                   '202206_Global_Pf_Mortality_Rate_2001.tif'
    output_raster_file = 'D:\\Drought_and_heat_wave_coupling\\data\\mask\\gw\\raster\\'
    output_raster_file2 = 'D:\\Drought_and_heat_wave_coupling\\data\\mask\\gw\\raster_filter\\'
    field_name = 'conflict'
    for i in range(1, 171, 1):
        field_value = i
        formatted = "{:03}".format(int(i))
        save_path = output_raster_file + formatted + '.tif'
        # First
        # rasterize_vector(input_vector, input_raster, save_path, field_name, field_value)

        # Second
        data = rs_image.Image(save_path)
        array = data.get_array(True, 1)
        num = np.sum(array == i)
        print(str(i) + ': ' + str(num))
        if num == 0:
            continue
        else:
            array = np.where(array == i, 1, array)
            nan_pos = np.isnan(array)
            array[nan_pos] = 0

            save_path2 = output_raster_file2 + formatted + '.tif'
            data.save(save_path2, array)