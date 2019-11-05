# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:00:40 2019

@author: lpz
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt



# running super slowly, presumably b.c. of the dictionary of large pandas dfs
def parse_data(fname, data_name="Broods"):
    # data_name only used if the textfile passed in has only
    # one type of measurement

    df = pd.read_csv(fname, delim_whitespace=True)
    df['time'] = pd.to_datetime(df['time'],unit='ms')

    # init dict indexed by measurement type, of empty DataFrames
    types = False
    if 'type' in set(df['type']):
        parsed_dfs = dict.fromkeys(set(df['type']), pd.DataFrame())
        types = True
    else:
        parsed_dfs = {data_name: pd.DataFrame()}

    hives = df.groupby('hive')
    if types:
        for hive_name, hive_group in hives:
            # parse the different measurement types
            parameters = hive_group.groupby('type')
            for measurement_name, groupby_hiveANDmeasurement in parameters:
                groupby_hive_measure = groupby_hiveANDmeasurement.set_index('time')
                groupby_hive_measure.index = groupby_hive_measure.index.floor('1H')
                groupby_hive_measure = groupby_hive_measure.drop(['type','hive'], axis=1)
                this_by_hiveNmeasure = groupby_hive_measure.rename(
                        columns={"value": hive_name}
                )

                parsed_dfs[measurement_name] = pd.merge(
                        parsed_dfs[measurement_name], this_by_hiveNmeasure,
                        left_index=True, right_index=True, how='outer'
                )
    else:
        for hive_name, hive_group in hives:
            groupby_hive = hive_group.set_index('time')
            groupby_hive.index = groupby_hive.index.floor('1H')
            groupby_hive = groupby_hive.drop(['hive'], axis=1)
            this_hive = groupby_hive.rename(columns={"value": hive_name})
            parsed_dfs[data_name] = pd.merge(
                    parsed_dfs[data_name], this_hive,
                    left_index=True, right_index=True, how='outer'
            )
    return parsed_dfs
