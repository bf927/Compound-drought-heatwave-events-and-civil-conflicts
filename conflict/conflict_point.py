import numpy as np
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd


conflict_event = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\' \
                 'conflict_data\\civil_conflict_data.xlsx'
output_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\conflict_data\\conflict_shp.shp'
event_data = pd.read_excel(conflict_event)

# 提取属性
year = np.array(event_data['year'])
side_a = np.array(event_data['side_a'])
side_b = np.array(event_data['side_b'])
latitude = np.array(event_data['latitude'])
longitude = np.array(event_data['longitude'])
country = np.array(event_data['country'])
region = np.array(event_data['region'])
best = np.array(event_data['best'])

point_list = []
for i in range(0, year.shape[0], 1):
    point = Point(longitude[i], latitude[i])
    point_list.append(point)

gpd_output = gpd.GeoDataFrame({'index': list(range(year.shape[0])),
                               'geometry': point_list,
                               'year': list(year),
                               'side_a': list(side_a),
                               'side_b': list(side_b),
                               'country': list(country),
                               'region': list(region),
                               'best': list(best)
                               })
# 添加坐标系
gpd_output.crs = {'init': 'epsg:4326'}
gpd_output.to_file(output_path)