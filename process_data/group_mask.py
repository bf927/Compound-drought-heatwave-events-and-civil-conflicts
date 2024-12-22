from pyrs.algorithm import supervision_classification as sc
from pyrs.algorithm import rs_image
import numpy as np
from osgeo import gdal

path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\GeoEPR-2021\\Export_Output.shp'
ex_path = 'D:\\Drought_and_heat_wave_coupling\\data\\SPEI_data\\spei\\1989\\01.tiff'

ex_image = rs_image.Image(ex_path)
array = sc.shapefile_to_raster(path, 360, 720, ex_image.proj, ex_image.geotrans, 'conflict', gdal.GDT_Float32)
print(np.unique(array))
print(np.unique(array).shape)
array = np.where(array == 0, -1, array)
array = np.where(array == 170, 0, array)
ex_image.save('D:\\Drought_and_heat_wave_coupling\\data\\mask\\group.tif',
              array)