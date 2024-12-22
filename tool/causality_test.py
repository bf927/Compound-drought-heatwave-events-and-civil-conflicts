import pandas as pd
import statsmodels.api as sm

# data = pd.read_excel('C:\\Users\\Administrator\\Desktop\\Drought_and_heat_wave_coupling\\data\\CDHW_conflict.xlsx')
#
# group = pd.get_dummies(data['group'], prefix='group', drop_first=True)
#
# X = data[['frequency', 'duration', 'severity', 'ad', 'GDP', 'population', 'IMR']]
# y = data['conflict']
#
# X = sm.add_constant(X)
# X = pd.concat([X, group], axis=1)
#
# model = sm.Logit(y, X)
#
# results = model.fit()
#
# print(results.summary())

# xls2dta:import excel "C:\Users\Administrator\Desktop\Drought_and_heat_wave_coupling\data\CDHW_conflict _2001_2020.xlsx",first case(lower)

# xtset group year

# xtlogit conflict frequency duration severity sum_ad population sum_crop fire_area gdp ec urban pr imr i.year, fe
# xtreg conflict_frequency frequency duration severity rainfall_ad irritated_ad rainfall_crop irritated_crop log_population fire_area log_gdp log_ec urban pr imr exclusion his_conf i.year, fe

# margins, dydx(frequency duration severity rainfall_crop irritated_crop population fire_area gdp ec urban pr imr exclusion his_conf)

# estimates store myregression
# outreg2 using C:\Users\Administrator\Desktop\Drought_and_heat_wave_coupling\data\CDHW2\p4_irritated_ad.doc, replace ci se

# margins, at(duration=(0(20)133))

# reghdfe conflict_frequency frequency duration severity rainfall_ad irritated_ad rainfall_crop irritated_crop log_population fire_area log_gdp urban imr exclusion his_conf political_group, absorb(group year)
# reghdfe conflict_frequency l.duration l.rainfall_ad l.irritated_ad l.rainfall_crop l.irritated_crop l.log_population l.fire_area l.log_gdp l.urban l.imr l.exclusion l.his_conf l.political_group, absorb(group year)
# reghdfe conflict_frequency l.duration c.l.duration##i.l.hs_encode l.hsvi l.ssvi, absorb(group year)
# margins, dydx(l.duration) at(l.hs_encode=(1 2 3 4))
# margins, dydx(duration) at(hs_encode=(1 2 3 4))

# reghdfe ks duration c.duration##i.hs_encode hsvi ssvi, absorb(group year)
# reghdfe rainfall_area ks c.ks##i.hs_encode hsvi ssvi, absorb(group year)


# l2滞后
# 取出duration p4以上的
# 使用glm family(gaussian) link(identity)
# 使用neo
# 不进行对数化
# 使用sum crop
# spei-n

# onset
# urban robust
# 暴露在CDHW的农业面积
# 选取gdp最不平衡的国家
# 分区域测试
# p4 ssvi
# 机会成本
# p1 gdp
# 移民
# 发生cdhw未发生冲突

# cluster(group)
