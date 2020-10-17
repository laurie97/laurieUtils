## Functions to run a causal inference analysis

## Imports ##
import laurie_plot_utils_functions
from laurie_plot_utils_functions import *


# stats functions
import scipy.stats as stats

# regression
import statsmodels.api as sm
import statsmodels.formula.api as smf

## Causal Inference
#### https://pypi.org/project/CausalInference/
#### https://causalinferenceinpython.org/
#### $ pip install causalinference

from causalinference import CausalModel

## Causal Impact
#### https://github.com/dafiti/causalimpact
#### pip install pycausalimpact

from causalimpact import CausalImpact

import pandas as pd
import numpy as np
import time, datetime
import sys

### Plot imports
import matplotlib.pyplot as plt
from pylab import text
import seaborn as sns
%matplotlib inline

### Plot Size (supersize_me)
import matplotlib.pylab as pylab
params = {'legend.fontsize': 'x-large',
          'axes.labelsize': 'x-large',
          'axes.titlesize':'x-large',
          'xtick.labelsize':'x-large',
          'ytick.labelsize':'x-large',
          'figure.titlesize':'xx-large'}
pylab.rcParams.update(params)

## Causal Impact Functions

def get_days_before(day_string,n_days):
    day_ts=datetime.datetime.strptime(day_string,'%Y-%m-%d')
    day_before_ts=day_ts-datetime.timedelta(days=n_days)
    day_before_string=str(day_before_ts.date())
    return day_before_string

def get_day_before(day_string):
    return get_days_before(day_string,n_days=1)

def get_week_before(day_string):
    return get_days_before(day_string,n_days=7)


## Run Synthetic Control
def run_synthetic_control(
    df_daily,          
    x,                              
    y,
    experiment_group,
    intervention_market,
    data_start,
    intervention_start,
    intervention_length,
    nseasons=[{'period': 7},{'period': 365,'harmonics':2}],
    prior_level_sd=None,
    plot_params=True,
    plot_ci=True,
    print_summary=True
):

    '''
    
    Input:
    - df_daily, pd data frame containing timeseries with a x column, y column and experiment_group column  
    - x, the x axis (usually date)
    - y, the metric we want to see if it shifted (e.g. bookings)
    - experiment_group, The groups that define control group or variant (e.g. all 10 coutries in experiment)
    - intervention_market, Which experiment group has the intervention
    - data_start, when does the data start
    - intervention_start, the day when the intervention started
    - intervention_length, how long is the intervention
    - nseasons, model setting
    - prior_level_sd, model setting
    - plot_params, plot the fitted params of the model
    - plot_ci, plot the timeseries and conf interval plots
    - print_summary, print the results

    Output
    - causal impact model

    '''
    
    ## Set up Periods
    pre_period=[data_start,get_day_before(intervention_start)]
    post_period=[intervention_start, add_days_to_day_string(intervention_start,(intervention_length-1)) ]
    

    ## Pivot Data Into Form we want
    data_experiment_prep=(
        df_daily
         [[x,'experiment_group',y]]
    )
        
    data_experiment=do_pivot(
        data_experiment_prep,
        values=[y],
        columns=['experiment_group'],
        index=x
    ).set_index(x)

    
    ## Set up order of columns as I like them
    col_intervention=y+'_'+intervention_market
    cols_ordered=[col_intervention]+[col for col in data_experiment.columns if col!=col_intervention]
    data_experiment=data_experiment[cols_ordered]

    ## Build causal model
    causal_impact = CausalImpact(data_experiment, pre_period , post_period, 
                                 nseasons=nseasons, 
                                 prior_level_sd=prior_level_sd
                                )
    
    if plot_params:
        ax=get_ax()
        np.abs(causal_impact.trained_model.params).sort_values(ascending=True).head(25).plot.barh(ax=ax)
        force_ax_grid(ax)
      
    if plot_ci:
        causal_impact.plot()

    if print_summary:
        print('\n',causal_impact.summary(),'\n')
        
    return causal_impact



def get_uncertainty(ci):
    summary_data=ci.summary_data
    low=summary_data.loc['predicted_lower','average']
    up=summary_data.loc['predicted_upper','average']
    uncertainty=((up-low)/2.0)
    return uncertainty


def blind_data_frame(df_daily,intervention_date=setting_intervention_date,target="Target Countries"):
    
    df_daily_blinded=df_daily.loc[lambda df: (df.yyyy_mm_dd < setting_intervention_date)].copy()
    
    df_fake_news=(
        df_daily
        .loc[lambda df: df.yyyy_mm_dd == get_day_before(setting_intervention_date)]    
        .drop('yyyy_mm_dd',axis=1)
    )
    
    df_fake_news['key']=int(0)
    df_fake_news=df_fake_news.merge(df_blind_days,how='left',on='key').drop('key',axis=1)
    
    display(df_fake_news)
    
    df_daily_blinded=pd.concat([df_daily_blinded,df_fake_news])
            
    return df_daily_blinded


## Loop over fake intervention dates

dict_region_fake={}
dict_region_fake['n_days_before']=[]
dict_region_fake['uncertainty']=[]
dict_region_fake['p_value']=[]

for n_days_before in [7*(n_weeks+1) for n_weeks in range(10)]:
    
    print('***  N Days = {}  ***\n'.format(n_days_before))

    ci_fake=run_synthetic_control(
        df_daily=df_daily_by_region,
        y='total_installs',
        data_start=setting_start_date,
        intervention_start=add_days_to_day_string(setting_intervention_date,-n_days_before),
        intervention_length=7
    )

    uncert=get_uncertainty(ci_fake)
    p_value=ci_fake.p_value
    dict_region_fake['n_days_before'].append(n_days_before)
    dict_region_fake['uncertainty'].append(uncert)
    dict_region_fake['p_value'].append(p_value)
    print('\n')

## Plot fake intervention dates

df_region_fake=pd.DataFrame(dict_region_fake)
ax=get_ax()
df_region_fake.plot(x='n_days_before',y='p_value',ax=ax)

df_region_fake=pd.DataFrame(dict_region_fake)
ax=get_ax()
df_region_fake.hist('p_value',ax=ax)


##############################
#####  Causal Inference  #####
##############################

## Propensity and matching using causal inference

cm = CausalModel(Y=observed_data_3.Y.values, 
                 D=observed_data_3.X.values, 
                 X=observed_data_3.loc[:, ['Z', 'Z1', 'Z2']].values)
cm.est_propensity()

propensity_scores = cm.propensity["fitted"]

cm2 = CausalModel(Y=observed_data_3.Y.values, 
                 D=observed_data_3.X.values, 
                 X=propensity_scores)
cm2.est_via_matching()

print(cm2.estimates)


## logistic regression for propensity, causalinference for matching

log_reg = smf.logit(formula='X ~ Z + Z1 + Z2', data=observed_data_3).fit()
propensity_scores = log_reg.predict()

cm2 = CausalModel(
                 Y=observed_data_3.Y.values, 
                 D=observed_data_3.X.values, 
                 X=propensity_scores
                 )

cm2.est_via_matching()

## Using inverse propensity weighting

propensity = smf.logit(formula='X ~ Z', data=observed_data_4).fit()
# or :
# cm = CausalModel(
#     Y=observed_data_1.y.values, 
#     D=observed_data_1.x.values, 
#     X=observed_data_1.z.values)

# cm.est_propensity_s()
# propensity = cm.propensity["fitted"]

observed_data_4['pscore'] = propensity.predict()
observed_data_4['iptw'] = observed_data_4.X*(1/observed_data_4.pscore) + (1 - observed_data_4.X)/(1 -observed_data_4.pscore)
observed_data_4['Y_x_iptw'] = observed_data_4.Y*observed_data_4.iptw  

smf.ols(formula='Y_x_iptw ~ X', data=observed_data_4).fit().summary()
