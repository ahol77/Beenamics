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

hives = df.groupby('hive')
for hive_name, hive_group in hives:
    specific_hive = hives.get_group(hive_name)
    parameters = specific_hive.groupby('type')
    
    for para_name, para_group in parameters:
        specific_parameter = parameters.get_group(para_name)
        specific_parameter_indexed = specific_parameter.set_index('time')
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
        
#Can use either D (day), W (week), or M (month) to group data
plt.plot(Weight.resample('D').mean())

