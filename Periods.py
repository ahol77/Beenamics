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

def parse_data(fname):
    df = pd.read_csv(fname, delim_whitespace=True)
    df['time'] = pd.to_datetime(df['time'],unit='ms')

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

    return (Weight, Humidity, TempExt, TempInt)

Weight, Humidity, TempExt, TempInt = parse_data('cleaned.txt')

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

# utility function for quick plotting
def plot_df(df, label, interval='D', fontsize=24):
    #Can use either D (day), W (week), or M (month) to group data
    plt.figure()
    plt.plot(df.resample(interval).mean())
    plt.legend(df)
    plt.xlabel("Time", fontsize = 24)
    plt.ylabel(label, fontsize = 24)

#Can use either D (day), W (week), or M (month) to group data
plot_df(Weight, "Weight", interval='W')
plot_df(Broods, "Brood Percent", interval='W')
plot_df(TempInt, "External Temperature (F)", interval='W')

plt.figure()
plt.plot(TempInt["R1"].resample('H').mean(), label = "External Temp")
plt.plot(Broods["R1"].resample('D').mean(), label = "Broods")
plt.legend()

