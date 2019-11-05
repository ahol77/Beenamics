# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 23:29:41 2019

@author: aholm
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import statsmodels.api as sm

import util

df = pd.read_csv('cleaned.txt', delim_whitespace=True)
df['time'] = pd.to_datetime(df['time'],unit='ms')

Humidity = pd.DataFrame()
Weight = pd.DataFrame()
TempExt = pd.DataFrame()
TempInt = pd.DataFrame()
Broods = pd.DataFrame()

hives = df.groupby('hive')
for hive_name, hive_group in hives:
    parameters = hive_group.groupby('type')
    for para_name, para_group in parameters:
        specific_parameter_indexed = para_group.set_index('time')
        specific_parameter_indexed.index = specific_parameter_indexed.index.floor('1H')
        spec_p_i = specific_parameter_indexed.drop(['type','hive'], axis=1)
        spec = spec_p_i.rename(columns={"value": hive_name})

        if para_name == "Humidity":
            Humidity = pd.merge(Humidity, spec, left_index=True,
                                right_index=True, how='outer')
        elif para_name == "Weight":
            Weight = pd.merge(Weight, spec, left_index=True,
                              right_index=True, how='outer')
        elif para_name == "TempExt":
            TempExt = pd.merge(TempExt, spec, left_index=True,
                               right_index=True, how='outer')
        elif para_name == "TempInt":
            TempInt = pd.merge(TempInt, spec, left_index=True,
                               right_index=True, how='outer')

broods = pd.read_csv('cleaned_broods.txt', delim_whitespace=True)
broods['time'] = pd.to_datetime(broods['time'],unit='ms')
brood_hives = broods.groupby('hive')

for brood_hive_name, brood_hive_group in brood_hives:
    specific_parameter_indexed = brood_hive_group.set_index('time')
    specific_parameter_indexed.index = specific_parameter_indexed.index.floor('1H')
    spec_p_i = specific_parameter_indexed.drop(['hive'], axis=1)
    spec = spec_p_i.rename(columns={"value": brood_hive_name})
    Broods = pd.merge(Broods, spec, left_index=True,
                                right_index=True, how='outer')

#Can use either D (day), W (week), or M (month) to group data
if False:
    plt.figure()
    plt.plot(Weight.resample('M').mean())
    plt.legend(Weight)
    plt.title("Weight", fontsize = 24)
    plt.xlabel("Time", fontsize = 24)
    plt.ylabel("Weight", fontsize = 24)

if False:
    plt.figure()
    plt.plot(Broods.resample('D').mean())
    plt.legend(Broods)
    plt.title("Brood Number", fontsize = 24)
    plt.xlabel("Time", fontsize = 24)
    plt.ylabel("Relative Brood Quantity (not sure units)", fontsize = 24)

interval = pd.DataFrame({'year':  [2019, 2019],
                         'month': [2,    4],
                         'day':   [25,   22]})
t_bounds = pd.to_datetime(interval)
start = t_bounds[0]
end = t_bounds[1]

relevant_hives = ['R1','R2','R3','R5','R6']
# humidity needs mean by day
relevant_H = Humidity.loc[start:end, relevant_hives]







