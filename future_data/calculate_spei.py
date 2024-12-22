from pyrs.algorithm import rs_image
import numpy as np
from climate_indices import indices
from climate_indices import compute


def lat_matrix_get(data):

    tif_geotrans = data.geotrans
    lat_left_left = tif_geotrans[3]  # 左上角像元的左上角纬度
    raster_res = tif_geotrans[1]  # 空间分辨率

    # 左上角像元的中心纬度
    lat_left_center = lat_left_left - raster_res / 2

    # 创建存储纬度矩阵的空数组
    row = data.height
    col = data.width
    lat_matrix = np.full((row, col), fill_value=np.NaN, dtype='float32')

    # lat_matrix填充
    for ii in np.arange(row):
        lat_matrix[ii, :] = lat_left_center - raster_res * ii
        # print(lat_left_center - raster_res * ii)

    return lat_matrix


def raster_spei_cal(mask, tas_data, pre_data, lat_matrix, styr, edyr, cal_styr, cal_edyr, scale_aim):
    # 创建存储计算结果的三维数组
    # 创建列名
    spei_aim_data = np.full(pre_data.shape, fill_value=-9999, dtype='float32')

    # 逐栅格计算SPEI
    row = pre_data.shape[1]
    col = pre_data.shape[2]
    for row_temp in range(0, row):
        for col_temp in range(0, col):
            if mask[row_temp, col_temp] == 0:
                continue
            else:
                tas_temp = tas_data[:, row_temp, col_temp] - 273.15
                pre_temp = pre_data[:, row_temp, col_temp]

                lat_temp = lat_matrix[row_temp, col_temp]

                # pet计算-桑斯维特方法
                pet_data = indices.pet(
                    temperature_celsius=tas_temp,
                    latitude_degrees=lat_temp,
                    data_start_year=styr
                )

                # spei计算
                spei_temp = indices.spei(
                    precips_mm=pre_temp,
                    pet_mm=pet_data,
                    scale=scale_aim,
                    distribution=indices.Distribution.gamma,  # 选择gamma分布拟合
                    periodicity=compute.Periodicity.monthly,
                    data_start_year=styr,
                    calibration_year_initial=cal_styr,
                    calibration_year_final=cal_edyr
                )

                spei_aim_data[:, row_temp, col_temp] = spei_temp

    return spei_aim_data


if __name__ == '__main__':
    mask_path = 'D:\\Drought_and_heat_wave_coupling\\data\\Tmax_data\\2001\\200101\\01.tiff'
    mask_data = rs_image.Image(mask_path)
    mask_array = mask_data.get_array(True, 1)
    mask_array = np.where(mask_array == -9999, 0, 1)

    tas_path = 'E:\\CDHW_conflict\\future_climate\\t_mean\\total_data\\ssp370_1941_2100_model1.tif'
    pre_path = 'E:\\CDHW_conflict\\future_climate\\precipitation\\total_data\\ssp370_1941_2100_model1.tif'
    # pre_path = 'E:\\CDHW_conflict\\future_climate\\precipitation\\MIROC6\\ssp585.tif'

    tas = rs_image.Image(tas_path).get_array(True, 0)
    print(tas.shape)
    pre = rs_image.Image(pre_path).get_array(True, 0)
    print(pre.shape)

    lat = lat_matrix_get(mask_data)

    spei = raster_spei_cal(mask_array, tas, pre, lat, 1941, 2100, 1989, 2020, 1)
    mask_data.save('E:\\CDHW_conflict\\future_climate\\spei\\ssp370_model1_1989_2020_01.tif', spei)