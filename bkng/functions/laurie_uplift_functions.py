## Spark imports
import pyspark.sql.functions as f
from pyspark.sql.functions import col  as c
from pyspark.sql import Window
from pyspark.sql.types import *
from pyspark.sql.window import Window

import laurie_spark_utils_functions
from laurie_spark_utils_functions import *


def produce_percentile_performance_exp(sdf_in,prediction_col,n_bins=10,bootstrap=False):
    
    ''' 
    Create performance in projected bookings from mdot/deeplink and install depending on fraction of data shown
    Take in sdf with a column representing predicted uplift. We then order by this as group into fractions.
    '''
    
    if not bootstrap: 
        sdf_in=sdf_in.withColumn('boot',f.lit("Actual"))
        
    sdf_n_rows=(
        sdf_in
        .groupBy('boot')
        .agg(f.count(f.lit(1)).alias('n_rows'))
    )
    
    order_cols=[f.col(prediction_col).desc(),'uvi']
    window=Window.partitionBy('boot').orderBy( order_cols )
        
    sdf_prep=(
        sdf_in
        .join(sdf_n_rows,how='left',on='boot')
        .withColumn("percent_row",      f.row_number().over( window ) / f.col('n_rows')   )
        .withColumn('fraction_of_data', f.ceil(f.col('percent_row')*f.lit(n_bins))*f.lit(1.0/n_bins) )
    )

    
    sdf_grouped=(
        sdf_prep
        .groupBy(["fraction_of_data","boot"])
        .agg(
            f.count(f.expr('1')).alias('n_visitors'),
            f.max(prediction_col).alias('predict_cut_off'),
            f.count(f.expr('IF(variant=0,1,NULL)')).alias('n_visitors_base'),
            f.sum(  f.expr('IF(variant=0,app_projected,NULL)')).alias('n_app_projected_base'),
            f.sum(  f.expr('IF(variant=0,mdot_or_deep_projected,NULL)')).alias('n_mdot_or_deep_projected_base'),
            f.sum(  f.expr('IF(variant=0,total_projected,NULL)')).alias('n_total_projected_base'),
            f.count(f.expr('IF(variant=1,1,NULL)')).alias('n_visitors_variant'),
            f.sum(  f.expr('IF(variant=1,app_projected,NULL)')).alias('n_app_projected_variant'),
            f.sum(  f.expr('IF(variant=1,mdot_or_deep_projected,NULL)')).alias('n_mdot_or_deep_projected_variant'),
            f.sum(  f.expr('IF(variant=1,total_projected,NULL)')).alias('n_total_projected_variant')
        )
    )
    
    sdf_zero=(
        sdf_grouped
        .groupBy('boot')
        .agg(*[f.max(f.lit(0)).alias(col) for col in sdf_grouped.columns if col!='boot'])
    )
    

    sdf_out=union_all([sdf_grouped,sdf_zero])
    
    if bootstrap==False:
        sdf_out=sdf_out.drop('boot')
    
    return sdf_out


def make_qini(df_grouped,
              x='fraction_of_data',
              y=['conversions','installs'],
              bootstrap=False
             ):
    '''
    Make Qini Curves From a Pandas DF of Fraction and Data and Performance Stats
    '''
    
    
    df_cumu=df_grouped.copy().sort_values(x)
    
    if bootstrap==False:
        df_cumu['boot']="Actual"
    
    for col in df_cumu.columns:
        if col in [x,'boot']: continue 
        df_cumu[col]=df_cumu.groupby('boot')[col].transform(np.cumsum)
    
    if type(y)!=list:
        y=[y]
        
    for this_y in y:
    
        y_base='n_{}_base'.format(this_y)
        y_variant='n_{}_variant'.format(this_y)
        n_base='n_visitors_base'
        n_variant='n_visitors_variant'
    
        
        qini_curve_name='qini_curve_{}'.format(this_y)
        df_cumu[qini_curve_name]=df_cumu[y_variant]-(df_cumu[y_base]/df_cumu[n_base])*df_cumu[n_variant]
        df_cumu.loc[lambda df: df[n_base]==0,qini_curve_name]=0
        df_cumu.loc[lambda df: df[n_variant]==0,qini_curve_name]=0
    
        df_cumu[qini_curve_name+'_full_traffic']= df_cumu[qini_curve_name] * ( (df_cumu[n_base]+df_cumu[n_variant])/df_cumu[n_variant])
        df_cumu.loc[lambda df: df[n_variant]==0,qini_curve_name+'_full_traffic']=0
        df_cumu.loc[lambda df: df[n_base]==0,qini_curve_name+'_full_traffic']=0
    
    return df_cumu
    
