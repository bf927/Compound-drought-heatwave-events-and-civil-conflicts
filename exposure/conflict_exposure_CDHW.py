import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymannkendall as mk
import seaborn as sns


data_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\CDHW2\\' \
            'exposure\\exposure.xlsx'

save_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\plt\\exposure\\all_samples.png'
data = pd.read_excel(data_path)
conflict_frequency = data['conflict_frequency']
conflict_frequency = np.array(conflict_frequency)
CDHW_frequency = data['frequency']
CDHW_frequency = np.array(CDHW_frequency)
CDHW_frequency = np.where(CDHW_frequency != 0, 1, 0)

fraction_list = []
for i in range(0, 20, 1):
    # print('year' + str(i))
    CDHW_list = []
    conflict_list = []
    for j in range(0, conflict_frequency.shape[0] // 20, 1):
        index = j * 20 + i
        CDHW_list.append(CDHW_frequency[index])
        conflict_list.append(conflict_frequency[index])
    year_CDHW = np.array(CDHW_list)
    year_conflict = np.array(conflict_list)
    CDHW_pos = np.where(year_CDHW == 1)[0]
    conflict_exposure_sum = np.sum(year_conflict[CDHW_pos])
    conflict_sum = np.sum(year_conflict)
    if conflict_sum == 0:
        fraction_list.append(0)
    else:
        fraction_list.append(conflict_exposure_sum / conflict_sum)
        # fraction_list.append(conflict_sum)

print(fraction_list)
# print(np.mean(fraction_list))
year = np.arange(2001, 2021, 1)
x = year
y = fraction_list
sns.regplot(x=x, y=y, order=4, scatter=False, ci=95, line_kws={"color": "red", "lw": 2})
res = mk.original_test(y, alpha=0.05)
plt.show()
# year = np.arange(2001, 2021, 1)
# degree = 4  # 多项式的次数
# coefficients = np.polyfit(year, fraction_list, degree)
# polynomial = np.poly1d(coefficients)
#
# x_fit = np.linspace(min(year), max(year), 100)
# y_fit = polynomial(x_fit)
#
# res = mk.original_test(fraction_list, alpha=0.05)
# print(f'trend:{res.trend}', 'p_value:{:.2f}'.format(res.p), 'slope:{:.2f}'.format(res.slope), sep=',')
#
# fig = plt.figure(figsize=(14, 8))
# plt.plot(x_fit, y_fit, color='#B22222', linewidth=4.0)
# # plt.scatter(year, fraction_list, color='#A9A9A9')
# plt.plot(year, fraction_list, color='#A9A9A9')
#
# font = {'family': 'Arial',
#         'color': 'black',
#         'weight': 'normal',
#         'size': 16,
#         }
#
# # Times New Roman
# plt.xticks(year)
# plt.xlabel("Year", fontdict=font)
# plt.ylabel("Fractional Ratio", fontdict=font)
# plt.yticks(fontproperties='Arial', size=12)
# plt.xticks(fontproperties='Arial', size=12)
#
# ax = plt.gca()
# ax.spines['right'].set_color('none')
# ax.spines['top'].set_color('none')
#
# plt.tight_layout()
# # plt.savefig(save_path, format='png', bbox_inches='tight')
# plt.show()