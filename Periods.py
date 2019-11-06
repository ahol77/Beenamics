# -*- coding: utf-8 -*-
"""
Created on Mon Oct 21 23:29:41 2019

@author: aholm
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
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

df = pd.read_csv('cleaned.txt', delim_whitespace=True)
df['time'] = pd.to_datetime(df['time'],unit='ms')

hives = df.groupby('hive')
for hive_name, hive_group in hives:
    parameters = hive_group.groupby('type')

    for para_name, para_group in parameters:
        specific_parameter = parameters.get_group(para_name)
        specific_parameter_indexed = specific_parameter.set_index('time')
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

def plot_df(df, data_name, interval='W', fontsize=24):
    #Can use either D (day), W (week), or M (month) to group data
    plt.figure()
    plt.plot(df.resample(interval).mean())
    plt.legend(df)
    plt.xlabel("Time", fontsize = fontsize)
    plt.ylabel(data_name, fontsize = fontsize)

plot_df(Weight, "Weight")
plot_df(Broods, "Brood Percent")

#########################
### Linear Regression ###
#########################

# corresponds to success/failure of
#              R1, R2, R3, R5, R6
y = np.array([0,  1,  0,  1,  1])

interval = pd.DataFrame({'year':  [2019, 2019],
                         'month': [2,    4],
                         'day':   [25,   22]})
t_bounds = pd.to_datetime(interval)
start = t_bounds[0]
end = t_bounds[1]

relevant_hives = ['R1','R2','R3','R5','R6']

interval = 'W'
rel_H = Humidity.loc[start:end, relevant_hives].resample(interval).mean()
rel_iT = TempInt.loc[start:end, relevant_hives].resample(interval).mean()
# only 1 column bc we assume only 1 true external temperature
rel_eT = TempExt.loc[start:end, relevant_hives].resample(interval).mean().mean(axis=1)
# cast the external temperatures into the shape of the other data
rel_eT = np.tile(rel_eT.to_numpy(), (len(relevant_hives),1))
rel_W = Weight.loc[start:end, relevant_hives].resample(interval).mean()
# weights for R6 are only available after 3.10.19
# and also missing data for R1 @ 4.22
rel_W = rel_W.dropna()

# get numpy array where each row is a hive, with
# [ ..humidity data.., ..temperature data.., ..weight data.. ].T
# so that dim(X) = (# hives, # all data pts)
#     and dim(y) = (# hives, 1)

some_data = np.hstack([rel_H.to_numpy().T, rel_iT.to_numpy().T])
more_data = np.hstack([some_data, rel_eT])
all_data  = np.hstack([more_data, rel_W.to_numpy().T])

X = all_data
X = sm.add_constant(X)
# logistic regression
model = sm.Logit(y,X)
# errors out with "PerfectSeparationError" bc too many Xs and not enough ys
#results = model.fit()
#print(results.summary())

# try logistic regression w/regularization to take care of extra DoFs
results = model.fit_regularized(method='l1', alpha=0.5)
print(results.summary())

# TODO:
# maybe also try with GLS to avoid problems w/collinearity?

# TODO:
# abstract this procedure into re-usable functions

# find the best alpha and evaluate model
# with
# leave one out cross-validation:
#   train the model on data from n-1 (= 4) hives, and evaluate the prediction
#   on the fifth hive
X_permutations = np.zeros((5, X.shape[0] -1, X.shape[1]))
for i in range(X.shape[0]):
    X_permutations[i] = util.drop_row(i, X)

models = [sm.Logit(util.drop_row(i,y), X) for i, X in enumerate(X_permutations)]
test_err = []
# range of values used for fitting models with different
# penalizations/regularizations for extra parameters
reg_range = np.linspace(0.1,1,40)
for a in reg_range:
    fit_params = [model.fit_regularized(alpha=a).params for model in models]
    errors = np.abs(y - np.array([
            model.predict(params, X[i,:])
            for i, (model, params) in enumerate(zip(models, fit_params))
    ]))
    test_err.append(np.sum(errors)/len(errors))

plt.plot(reg_range, test_err)

# index of minimal test error
idx = test_err.index(min(test_err))
# corresponds to the alpha that minimizes error
alpha = np.round(reg_range[idx], 3)
print(alpha)

