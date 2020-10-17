### I am found in /home/lmcclymont/public/lmcclymont/git_laurie/laurie_utils/imports/laurie_utils.py

### Usual imports
import pandas as pd
import numpy as np
import time, datetime
import sys

### Plot imports
import matplotlib.pyplot as plt
from pylab import text
import seaborn as sns
%matplotlib inline

## Spark imports
import pyspark.sql.functions as f
from pyspark.sql.functions import col  as c
from pyspark.sql import Window
from pyspark.sql.types import *

## Alway reload packages when asked to!
%load_ext autoreload
%autoreload 2

## WARNINGS :)
import warnings
warnings.filterwarnings('once')

## Set width notebook
from IPython.display import Markdown, HTML, display
display(HTML("<style>.container { width:80% !important; }</style>"))

## Plot Stuff

### Colours
blue =  '#79a5f7'
red  =  '#ff9696'
green=  '#9ebd9e'
sns_colours = sns.color_palette()

### Plot Size (supersize_me)
import matplotlib.pylab as pylab
params = {'legend.fontsize': 'x-large',
          'axes.labelsize': 'x-large',
          'axes.titlesize':'x-large',
          'xtick.labelsize':'x-large',
          'ytick.labelsize':'x-large',
          'figure.titlesize':'xx-large'}
pylab.rcParams.update(params)

####################################
######## Laurie Utils ##############
####################################

userhome = os.path.expanduser("~")
sys.path.append('{}/public/lmcclymont/git_laurie/laurie_utils/imports/'.format(userhome))


import laurie_plot_utils_functions
from laurie_plot_utils_functions import *

## Some more utils that will exported at some point
## Laurie's custom spark query function
#  It can - Store query in hive
#         - Retrieve query
#         - Gives info on sdf you created
import laurie_spark_utils_functions
from laurie_spark_utils_functions import *


def query_to_spark(query, do_store=False, do_load=False, do_refresh=False, do_cache=True, do_count=False, cache_and_count=False, queryName='query', schemaName='laurie'):
    return query_to_spark_wrapper(spark,query=query
                                  ,do_store=do_store, do_load=do_load, do_refresh=do_refresh, do_cache=do_cache, do_count=do_count,cache_and_count=cache_and_count
                                  ,queryName=queryName,schemaName=schemaName)

def save_table(sdf_in, table_name, table_comment=False,repartition=False):
    save_table_wrapper(spark,sdf_in, table_name, table_comment=table_comment,repartition=repartition)


now=str(datetime.datetime.today()).split('.')[0]
app_name='lauries_amazing_jupyter_notebook_{}'.format(now.replace(' ','_'))
spark = (SparkSession.builder
             .config("spark.sql.shuffle.partitions", "1024")
             .config("spark.speculation",True)
             .appName(app_name)
             .enableHiveSupport()
             .getOrCreate()
         )
spark.sparkContext.setLogLevel("FATAL")



