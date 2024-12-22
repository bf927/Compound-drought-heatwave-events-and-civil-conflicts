import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt

path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\water\\gw_compare.xlsx'
data = pd.read_excel(path)
total_gw = np.array(data['total_gw'])
real_gw = np.array(data['GCWM'])
print(real_gw.shape)

fig = plt.figure(figsize=(8, 8))

r2 = r2_score(real_gw, total_gw)
print(r2)

# 绘制散点图
plt.scatter(real_gw, total_gw, c='#9370DB')

font = {'family': 'Arial',
        'color': 'black',
        'weight': 'normal',
        'size': 18,
        }

# 添加直线 y=x
plt.plot([min(real_gw), max(real_gw)], [min(real_gw), max(real_gw)], color='red', linestyle='dashed')

plt.xlabel('Validate Green Water', fontdict=font)
plt.ylabel('Predict Green Water', fontdict=font)
plt.title('Precision Comparison', fontdict=font)

plt.yticks(fontproperties='Arial', size=18)
plt.xticks(fontproperties='Arial', size=18)

ax = plt.gca()
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')

# plt.savefig('C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\'
#             'data\\plt\\exposure\\water.png',
#             dpi=600,
#             bbox_inches='tight')
plt.show()
