import numpy as np
import pandas as pd


table_path = 'C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\CDHW_conflict.xlsx'
table = pd.read_excel(table_path)
conflict = np.array(table['conflict'])

for i in range(0, conflict.shape[0], 34):
    group_conflict = conflict[i:i+34]
    conflict_2000_2019 = group_conflict[11:31]
