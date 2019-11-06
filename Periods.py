# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 23:29:41 2019

@author: aholm
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

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
plt.figure()
plt.plot(TempExt.resample('H').mean())
plt.legend(TempExt)
plt.title("Temp", fontsize = 24)
plt.xlabel("Time", fontsize = 24)
plt.ylabel("Temp", fontsize = 24)

Broods_interest = ['R1','R2','R3','R5','RHH']

plt.figure()
plt.rc('font', size=24)
plt.plot(Broods[Broods_interest].resample('D').mean())
plt.legend(Broods[Broods_interest], prop={'size': 16})
plt.xlabel("Time", fontsize = 24)
plt.ylabel("Brood Percentage", fontsize = 24)

plt.figure()
plt.plot(TempInt["R1"].resample('H').mean(), label = "External Temp")
plt.plot(Broods["R1"].resample('D').mean(), label = "Broods")
plt.legend()

