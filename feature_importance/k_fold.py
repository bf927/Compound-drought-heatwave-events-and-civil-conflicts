import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, KFold
import shap
import matplotlib.pyplot as plt
import openpyxl
from matplotlib.gridspec import GridSpec


data_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\reg_feature\\' \
            'main_norm_lag.xlsx'
data = pd.read_excel(data_path)

# 分割数据集为特征和目标变量
X = data[[
          'pop_dens', 'imr',
          'his_conf', 'exclusion', 'political_group',
          ]]
# X = data[['pop_dens', 'gdp_cap', 'urban', 'imr', 'exclusion', 'his_conf', 'political_group',
#           'Effectiveness']]

y = data['conflict_frequency']

# 构建随机森林回归模型
rf_model = RandomForestRegressor(n_estimators=500, oob_score=True, verbose=1, n_jobs=-1)
rf_model.fit(X, y)


k = 5  # 可以修改为想要的折数
kf = KFold(n_splits=k, shuffle=True)

# 4. 进行交叉验证
scores = cross_val_score(rf_model, X, y, cv=kf, scoring='r2')

# 5. 输出结果
print(f'每一折的得分: {scores}')
print(f'平均得分: {np.mean(scores)}')