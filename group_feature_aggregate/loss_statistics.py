import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.stats.weightstats as sw


def remove_trend(arr):
    degree = 1  # 多项式的次数
    x = np.array([-2, -1, 0, 1, 2])
    coefficients = np.polyfit(x, arr, degree)
    polynomial = np.poly1d(coefficients)

    y_fit = polynomial(x)
    mean = np.mean(arr)

    remove_trend_y = arr - y_fit + mean
    return np.array([remove_trend_y])


class Event:
    def __init__(self, cdhw, flood, cold_wave, feature):
        self.cdhw = cdhw
        self.flood = flood
        self.cold_wave = cold_wave
        self.feature = feature


def compress_array(event_list):
    # 压缩后的新列表
    compressed_list = []

    # 遍历原始列表
    i = 0
    while i < len(event_list):
        current_event = event_list[i]

        # 检查连续的对象的cdhw属性是否为1
        if current_event.cdhw == 1:
            # 初始化用于计算平均值的变量
            total_feature = current_event.feature
            total_flood = current_event.flood
            total_cold_wave = current_event.cold_wave
            count = 1

            # 继续遍历连续的对象并计算平均值
            while i + 1 < len(event_list) and event_list[i + 1].cdhw == 1:
                i += 1
                total_feature += event_list[i].feature
                total_flood += event_list[i].flood
                total_cold_wave += event_list[i].cold_wave
                count += 1

            # 创建新对象替代连续的对象，feature属性取平均值
            average_feature = total_feature / count
            if total_flood != 0:
                flood = 1
            else:
                flood = 0

            if total_cold_wave != 0:
                cold_wave = 1
            else:
                cold_wave = 0
            compressed_list.append(Event(cdhw=1, feature=average_feature, flood=flood, cold_wave=cold_wave))
        else:
            # 如果cdhw属性不为1，则直接添加原对象到新列表
            compressed_list.append(current_event)

        i += 1

    # for i in range(len(compressed_list)):
    #     print(compressed_list[i].feature)
    return compressed_list


def extract_array(event_list):
    window_list = []
    for i in range(2, len(event_list) - 2, 1):
        current_event = event_list[i]

        surround = \
            event_list[i - 1].feature + event_list[i - 2].feature + event_list[i + 1].feature + event_list[i + 2].feature

        # 检查是否满足事件A的条件
        if (current_event.cdhw == 1 and
                event_list[i - 1].cdhw == 0 and
                event_list[i - 2].cdhw == 0 and
                event_list[i + 1].cdhw == 0 and
                event_list[i + 2].cdhw == 0 and
                surround != 0):
            # 将符合条件的事件A添加到列表中
            window = np.array([[event_list[i - 2].feature,
                                event_list[i - 1].feature,
                                event_list[i].feature,
                                event_list[i + 1].feature,
                                event_list[i + 2].feature]])

            flood_window = np.array([[event_list[i - 2].flood,
                                      event_list[i - 1].flood,
                                      event_list[i].flood,
                                      event_list[i + 1].flood,
                                      event_list[i + 2].flood]])

            cold_wave_window = np.array([[event_list[i - 2].cold_wave,
                                          event_list[i - 1].cold_wave,
                                          event_list[i].cold_wave,
                                          event_list[i + 1].cold_wave,
                                          event_list[i + 2].cold_wave]])
            if (np.sum(window) == 0) or (np.sum(flood_window) != 0) or (np.sum(cold_wave_window) != 0):
                continue
            # if np.sum(window) == 0:
            #     continue
            window_list.append(window)

    # print(window_list)
    return window_list


def compress_and_extract(event_list):
    compress_event_list = compress_array(event_list)
    result_sequences = extract_array(compress_event_list)

    if len(result_sequences) != 0:
        sequences_array = remove_trend(result_sequences[0][0])
        for i in range(1, len(result_sequences), 1):
            sequences_array = np.append(sequences_array, remove_trend(result_sequences[i][0]), axis=0)
        return len(result_sequences), sequences_array
    else:
        return 0, np.zeros((1, 1))


def SEA(data, feature_name):
    group_array = np.array(data['group'])
    CDHW_array = np.array(data['CDHW'])
    flood_array = np.array(data['flood'])
    cold_wave_array = np.array(data['cold wave'])
    feature_array = np.array(data[feature_name])

    sea_array_list = []
    for i in range(0, group_array.shape[0], 20):
        group_index = group_array[i]
        group_CDHW = CDHW_array[i:i + 20]
        group_flood = flood_array[i:i + 20]
        group_cold_wave = cold_wave_array[i:i + 20]
        group_feature = feature_array[i:i + 20]
        input_list = []
        for num in range(0, group_feature.shape[0], 1):
            event = Event(group_CDHW[num], group_flood[num], group_cold_wave[num], group_feature[num])
            input_list.append(event)
        length, sequences = compress_and_extract(input_list)

        if length == 0:
            continue
        else:
            remove_array = np.delete(sequences, 2, axis=1)
            mean = np.mean(remove_array, axis=1).reshape((-1, 1))
            sequences = sequences / mean
            index = np.full((sequences.shape[0], 1), group_index)
            sequences = np.append(index, sequences, axis=1)
            sea_array_list.append(sequences)

    sea_array = sea_array_list[0]
    for i in range(1, len(sea_array_list), 1):
        sea_array = np.append(sea_array, sea_array_list[i], axis=0)

    return sea_array


def bootstrap_sample(data):
    n = len(data)
    indices = np.random.choice(n, size=n, replace=True)
    return data[indices]


def Significance_verification(data, alter):
    # 计算数据的均值和标准差
    mean_value = np.mean(data)
    std_dev = np.std(data)

    # 设置置信水平和自由度
    confidence_level = 0.95  # 置信水平为95%

    # 对于较大样本量，可以使用正态分布（stats.norm.interval）计算置信区间
    # confidence_interval = stats.norm.interval(confidence_level, loc=mean_value, scale=std_dev / np.sqrt(len(data)))
    # print(f"置信区间为: {confidence_interval}")

    # 假设检验
    null_hypothesis_mean = 1  # 原假设的均值
    z_statistic, p_value = sw.ztest(data, value=null_hypothesis_mean, alternative=alter)

    # print(z_statistic)
    print(p_value)


def bootstrap(sea_array, alter):
    num_bootstrap_samples = 1000
    sample_list = []
    for i in range(0, num_bootstrap_samples, 1):
        sample_list.append(np.mean(bootstrap_sample(sea_array)))
    # print(np.mean(sample_list))

    # fig = plt.figure(figsize=(14, 8))
    plt.hist(sample_list, bins=20, color='skyblue', edgecolor='black')
    Significance_verification(sample_list, alter)

    font = {'family': 'Times New Roman',
            'color': 'black',
            'weight': 'normal',
            'size': 16,
            }

    plt.xlabel("event year difference from control", fontdict=font)
    plt.ylabel("event number", fontdict=font)
    ax = plt.gca()
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.yticks(fontproperties='Times New Roman', size=12)
    plt.xticks(fontproperties='Times New Roman', size=12)
    # plt.savefig(sp, dpi=600)
    plt.show()


if __name__ == '__main__':
    # data_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\CDHW2\\' \
    #                   'vulnerability_index_plus.xlsx'
    # data_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\CDHW2\\mechanism\\' \
    #             'no_conflict.xlsx'
    # data_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\CDHW2\\mechanism\\' \
    #             'agriculture\\p4_rainfall_ad_vi.xlsx'
    # data_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\CDHW2\\mechanism\\' \
    #             'agriculture\\p4_irritated_ad_vi.xlsx'
    # data_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\CDHW2\\mechanism\\' \
    #             'agriculture\\p4_rainfall_crop_vi.xlsx'
    data_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\CDHW2\\mechanism\\' \
                'agriculture\\p4_hsvi_vi_plus.xlsx'
    data_pd = pd.read_excel(data_path)

    name = 'rainfall_area'
    # name = 'rainfall_crop'
    # name = 'irritated_crop'
    # name = 'irritated_crop_by_area'
    # name = 'rainfall_crop_by_area'
    # name = 'sum_crop_by_area'
    # name = 'pf'
    # name = 'imr'
    # name = 'neonatal'
    # name = 'log_gdp'
    # name = 'under5'
    # name = 'exclusion'
    # name = 'log_ec'
    # name = 'log_population'
    # name = 'rainfall_ad'
    # name = 'irritated_ad'
    # name = 'urban'
    # name = 'his_conf'
    # name = 'political_group'
    # name = 'hsvi'
    # name = 'ssvi'

    alternative = 'smaller'
    # alternative = 'larger'
    result = SEA(data_pd, name)
    print(result.shape)
    sign = result[:, 3]
    print(np.mean(result, axis=0))
    bootstrap(sign, alternative)