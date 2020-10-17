### I am found in /home/lmcclymont/public/lmcclymont/git_laurie/laurie_utils/imports/laurie_spark_utils.py
from __future__ import print_function

### Usual imports
import pandas as pd
import numpy as np
import time, datetime
import pyspark
import pyspark.sql.functions as f
import os

## Some utils that I will put in an external folder at some point

def printAndLog(thing,list_of_things):
    print(thing)
    list_of_things.append(thing)
    return

def writeLog(list_log, doTime=True, logName="log"):
    
    current_date=time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime()) 
    if doTime: logName=logName+"_"+str(current_date)
    
    if not os.path.exists("queries"):
        os.mkdir('queries')
    
    ## Write list_log to file
    outfile= open('queries/'+logName,'w')
    for line in list_log:
        outfile.write(line+'\n')
    outfile.close()
    print("*** writeLog: saved query log to {}".format(logName))
    return

def save_spark(sdf, doTime=False, queryName='query', schemaName='laurie'):
    if doTime: queryName=queryName+"_"+str(current_date) 
    fullName=schemaName+"."+queryName   
    sdf.write.saveAsTable(fullName, mode='overwrite', format='orc')
    print("*** saveSpark: saved query to {}".format(fullName))



def check_sdf_nulls(sdf):
    df_nulls=sdf.select([f.sum(f.col(col).isNull().cast("integer")).alias(col) for col in sdf.schema.names]).toPandas()
    df_nulls['n_rows']=sdf.count()
    display(df_nulls.T)

def make_a_greater_than_col(df,col,gt_cut=10):
    gt=df.loc[df[col]>gt_cut].sum()
    gt[col]="> {}".format(gt_cut)
    df=df.loc[df[col]<=gt_cut].append(gt,ignore_index=True)
    return df

def breakdown_by_col_spark(sdf_in,col,set_col=False,
                           sortByCol=False,sortBySetCol=True,
                           sum_over=False,output_name=False,set_name='set',
                           plot=False, gt_cut=False, do_cumu=False, min_pct=False,
                           display=True, return_df=False ):

    if display==False: return_df=True ## This retains old functionality

    if type(col)!=list: col=[col]
    if set_col and type(set_col)!=list: set_col=[set_col]
    if set_col==False: sortBySetCol=False ## If there is no set_col, then you can't sort by it.
    
    if set_col: gb_key=set_col+col
    else:       gb_key=col 
    
    if(sum_over):
        if not (output_name): output_name="frequency"
        df_breakdown=sdf_in.groupBy(gb_key).agg(f.sum(sum_over).alias(output_name)).toPandas()    
    else:
        if not (output_name): output_name="count"
        df_breakdown=sdf_in.groupBy(gb_key).agg(f.count(f.lit(1)).alias(output_name)).toPandas()
    if sortByCol:
        df_breakdown=df_breakdown.sort_values(gb_key,ascending=True).reset_index(drop=True)
    elif sortBySetCol:
        df_breakdown=df_breakdown.sort_values(set_col+[output_name],ascending=[True]*len(set_col)+[False]).reset_index(drop=True)
    else:
        df_breakdown=df_breakdown.sort_values(output_name,ascending=False).reset_index(drop=True)

    if gt_cut:
        df_breakdown=make_a_greater_than_col(df=df_breakdown,col=col[0],gt_cut=gt_cut)
    
    total=df_breakdown[output_name].sum()
    df_breakdown["percentage"]=df_breakdown.apply(lambda row: float(row[output_name])*100/total,axis=1)

    if do_cumu:
        df_breakdown["cumulative_percentage"]=df_breakdown["percentage"].cumsum()
        
    output_name_set=output_name+' in '+set_name
    percentage_of_set='percentage of '+set_name
    cumu_percentage_of_set='cumulative_percentage of '+set_name
        
    if set_col:
        df_total=df_breakdown.groupby(set_col)[[output_name]].sum().rename(columns={output_name:output_name_set}).reset_index()
        df_breakdown=df_breakdown.merge(df_total,on=set_col,how='left')
        df_breakdown[percentage_of_set]=df_breakdown[output_name]*100.0/df_breakdown[output_name_set]

        if do_cumu:
            ## Do cumu for set as well
            #df_breakdown[cumu_percentage_of_set]=df_breakdown["percentage of set"].cumsum()
            #while max(df_breakdown[cumu_percentage_of_set]>100):
            #    df_breakdown.loc[lambda df: df[cumu_percentage_of_set]>100.0000001,cumu_percentage_of_set]=df_breakdown.loc[lambda df: df[cumu_percentage_of_set]>100.0000001,cumu_percentage_of_set]-100

            ## Step 1. Create Synth. Single Set Col
            for set_col_part in set_col:
                if set_col_part==set_col[0]: df_breakdown['syntetic_set_col'] = df_breakdown[set_col_part].astype(str)
                else:                        df_breakdown['syntetic_set_col'] = df_breakdown['syntetic_set_col']+', '+df_breakdown[set_col_part].astype(str)
                
            ## Then do the work
            for this_synth_set_col_value in list(set(list(df_breakdown['syntetic_set_col']))):
                loc_this_synth_set=lambda df: df['syntetic_set_col']==this_synth_set_col_value
                df_breakdown.loc[loc_this_synth_set,cumu_percentage_of_set]=df_breakdown.loc[loc_this_synth_set,percentage_of_set].cumsum()
            
        #Select output columns in the right order
        out_col_list=gb_key+[output_name,'percentage']
        if do_cumu:   out_col_list=out_col_list+['cumulative_percentage']                       
        out_col_list=out_col_list+[percentage_of_set]
        if do_cumu:   out_col_list=out_col_list+[cumu_percentage_of_set]                       
        out_col_list=out_col_list+[output_name_set]
        df_breakdown=df_breakdown[out_col_list]
    
    if plot:
        fig,ax1=plt.subplots(1,1,figsize=(10,15))
        df_breakdown.plot(x=col,y="percentage",kind='barh',ax=ax1)
        ax1.set(xlabel="Percentage of {}".format(output_name),ylabel=col)
        
        if do_cumu:
            fig,ax2=plt.subplots(1,1,figsize=(10,15))
            df_breakdown.plot(x=col,y="cumulative_percentage",kind='barh',ax=ax2)
            ax2.set(xlabel="Cumulative Percentage of {}".format(output_name),ylabel=col)
            
        plt.gca().invert_yaxis()

    if display:
        from IPython.display import display
        
        if min_pct: df_breakdown=df_breakdown.loc[lambda df: df.percentage > min_pct]
        
        display(df_breakdown
                .set_index(gb_key)
                .style
                .format({output_name:"{:,.0f}",'percentage':'{:.1f}%','cumulative_percentage':'{:.1f}%',
                         output_name_set:"{:,.0f}",percentage_of_set:'{:.1f}%',cumu_percentage_of_set:'{:.1f}%'})
                .set_properties(**{'text-align': 'right'})
                )

    if return_df:
        return df_breakdown
    else:
        return None



def query_to_spark_wrapper(spark, query, do_store=False, do_load=False, do_refresh=False, do_cache=True, do_count=False, cache_and_count=False, queryName='query', schemaName='laurie'):

    if cache_and_count:
        do_cache=True
        do_count=True

    output_list=[]
    if do_store and do_load:
        print("queryToSpark: WARNING! I won't allow you to load and store...")
        print("queryToSpark: Setting do_store to 'False'")
        do_store=False
    printAndLog("*************************",output_list)
    printAndLog("****** queryToSpark *****",output_list)
    printAndLog("*************************",output_list)
    if do_refresh:
        fullName=schemaName+"."+queryName
        print("******* REFRESHING... ******")
        print("** Refresh {}".format(fullName))
        query="REFRESH TABLE "+fullName
        spark.sql(query)
        return "Hello, I'm not a sdf. Try turning off refresh mode"
        
    if do_load:
        fullName=schemaName+"."+queryName
        print("**")
        print("******* LOAD MODE! ******")
        print("** Loading data from {}".format(fullName))
        query="SELECT * FROM "+fullName
        print("**")
    start_time=time.time()
    printAndLog("**** Launch Time "+str(time.ctime()),output_list)
    printAndLog("** ",output_list)
    printAndLog("**** What am I doing? ",output_list)
    printAndLog(query,output_list)
    printAndLog("",output_list)
    printAndLog("********* Ok Let's Go ***********",output_list)
    sdf=spark.sql(query)
    if do_cache:
        sdf=sdf.cache()
    if do_count:
        count = sdf.count()
        printAndLog("***** What is the spark dataframe like ****",output_list)
        printAndLog("****  Count:"+str(count),output_list)
        printAndLog("**",output_list)
        #printAndLog("****  Schema:",output_list)
        #printAndLog(str(sdf.printSchema()),output_list)
        #printAndLog("**",output_list)
    #printAndLog("**** Describe",output_list)
    #printAndLog(str(sdf.describe().toPandas()),output_list)
    #printAndLog("**",output_list)
    if do_store:
        printAndLog("****  STORE MODE is ON!!! ",output_list)
        save_spark(sdf, doTime=False, queryName=queryName, schemaName=schemaName)
        printAndLog("****  saved to {}.{}".format(schemaName,queryName),output_list)
    end_time=time.time()
    elapsed_time=end_time-start_time
    printAndLog("**** Time take:"+str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))),output_list)
    printAndLog("*************************",output_list)

    return sdf


def save_table_wrapper(spark,sdf_in,table_name,table_comment=False,repartition=True):

    
    ''' Write the table to hadoop!! '''
    
    print("laurie_spark_utils : Trying to save table {}".format(table_name))

    if type(repartition)==int:
        print("laurie_spark_utils : Repartitioning to {} partitions: {}".format(repartition,table_name))
        sdf_out=sdf_in.repartition(repartition)
                
    print("laurie_spark_utils : Trying to save table to {}".format(table_name))
    sdf_out.write.saveAsTable(table_name,mode='overwrite',format='orc')
    print("laurie_spark_utils : Succesfully saved table to {}".format(table_name))
    #print_me(" Succesfully saved table to {}".format(table_name))

    if table_comment:
      if table_comment.lower()=='no':   table_comment="Not for general use"
      print("laurie_spark_utils : Setting table comment: {}".format(table_comment))
      spark.sql("ALTER TABLE {} SET TBLPROPERTIES ('comment' = '{}')".format(table_name, table_comment))


## Save and return a frame pointing to the table
def hard_cache(spark,sdf,table_name,repartition=True,just_load=False):
    
    if just_load==False:
        save_table_wrapper(spark,sdf,table_name,table_comment='no',repartition=repartition)
        
    sdf=spark.table(table_name)
    return sdf


def check_sdf_for_nulls(sdf):
    
    display(sdf.select([f.sum(f.col(col).isNull().cast("integer")).alias(col) for col in sdf.schema.names]).toPandas().T)


# Monitoring
from IPython.display import Markdown, HTML, display
import shlex
from subprocess import Popen, PIPE


def print_spark_site(spark):
    ### Look at me                                                                                                                            
    print("Here is a monitoring URL:")
    print(spark.sparkContext._conf.get('spark.org.apache.hadoop.yarn.server.webproxy.amfilter.AmIpFilter.param.PROXY_URI_BASES').split(',')[0])


def get_exitcode_stdout_stderr(cmd):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    args = shlex.split(cmd)

    proc = Popen(args, stdout=PIPE, stderr=PIPE, shell=False)
    out, err = proc.communicate()
    exitcode = proc.returncode
    #
    return exitcode, str(out), str(err)
    
def get_cluster():
    
    cmd = 'cat /etc/motd'  
    exitcode, out, err = get_exitcode_stdout_stderr(cmd)
    #print (out)
    
    if     out.find("hadoop_lhr4") != -1:      cluster = "hadoop-lhr4"
    elif   out.find("hadoop_ams4") != -1:      cluster = "hadoop-ams4"
    elif   out.find("Debian GNU/Linux") != -1: cluster = "bgcloud"
    else:  return -1
    return cluster

    

# Union from many sdfs

### Stolen from https://datascience.stackexchange.com/a/14485
def union_all_recursion(list_sdfs):

    print('Recursion depth = {}'.format(len(list_sdfs)))
    if len(list_sdfs) > 1:
        return list_sdfs[0].union(union_all_recursion(list_sdfs[1:]))
    else:
        return list_sdfs[0]

### Function to use
def union_all(list_sdfs_to_union,debug=False):


    list_sdfs_to_union_trimmed=[]
    
    ## Check that they all have the same columns
    for i_sdf,sdf in enumerate(list_sdfs_to_union):
        if i_sdf==0:
            column_names_first_sdf=sdf.columns
            
        else:
            for column in column_names_first_sdf:
                if column not in sdf.columns:
                    print('Table of index {} in list does not contain column {}. Everything will break!'.format(i_sdf,column))

        list_sdfs_to_union_trimmed.append(sdf.select(*column_names_first_sdf))
    
    ## Do union using recursion
    sdf_merge=union_all_recursion(list_sdfs_to_union_trimmed)

    if debug:
        n_rows_combined=0
        print( 'Checking that the number of rows in union adds up')
        for i_sdf,sdf in enumerate(list_sdfs_to_union):
            n_rows=sdf.count()
            n_rows_combined=n_rows_combined+n_rows
            print( '- {:12,.0f} : Table in list, index {}'.format(n_rows,i_sdf))
        print( '- {:12,.0f} : Addition of n_rows in input tables'.format(n_rows_combined))
        n_rows=sdf_merge.count()
        print( '- {:12,.0f} : Output table'.format(n_rows))

    return sdf_merge


def join_without_nulls(sdf_base,sdf_join,on,how='inner'):
            
        ''' Left join sdf_base and sdf_join, with an exception if any of the join keys is Null in sdf_base.
            If join keys are non-null, do join as normal.
            If any of koin keys is null, then treat the row in sdf_base as if no match can be found in sdf_join.
            This function is used to avoid imbalanced joins on Null keys.
        '''
        
        # If only one key, force to be list
        if type(on)==str: on=[on]
        
        clause=''
        for i,key in enumerate(list(on)):
            if i > 0: clause+=' AND '
            clause+=key
            clause+=' IS NOT NULL'
        sdf_result=join_with_exception(sdf_base,sdf_join,clause=clause,on=on,how=how)
        return sdf_result


def join_with_exception(sdf_base,sdf_join,clause,on,how='inner'):
    
        ''' Left join sdf_base and sdf_join, with a special exception on the join logic given by the variable 'clause'.
            Clause is a sql where expression
            When the clause is true, do the join as normal
            When the clasue is false, treat as if it was a left join where there was not a match found in sdf_join.
        '''
        ## Split By Clause
        sdf_base=sdf_base.withColumn('has_clause',f.when(f.expr(clause),1).otherwise(0))
        sdf_join=sdf_join.withColumn('has_clause',f.when(f.expr(clause),1).otherwise(0))
        
        sdf_base_with   =sdf_base.where('has_clause = 1').drop('has_clause')     
        sdf_base_without=sdf_base.where('has_clause = 0').drop('has_clause')
        sdf_join_with   =sdf_join.where('has_clause = 1').drop('has_clause')  
        
        ## Do Join with clause
        sdf_result_with=sdf_base_with.join(sdf_join_with,how=how,on=on)
        
        ## Fill out columns in without part
        for col in sdf_join.schema.fields:
            if col.name in sdf_base.columns: continue
            sdf_base_without = sdf_base_without.withColumn(col.name, f.lit(None).cast(col.dataType))
            
        ## Union without and return
        sdf_result_full=sdf_result_with.select(*[col for col in sdf_base_without.columns]).union(sdf_base_without)
        return sdf_result_full


## Function to help identify where everything goes wrong
def debug_complete_stage(stage_name,sdf=None):
    
    if not args.debug: return
    
    if sdf:
        print('{} - Running'.format(stage_name) )
        n_rows=sdf.count()
        sdf=sdf.cache()
        print('{} - Run, n_rows = {:,.0f}'.format(stage_name,n_rows) )
        
    else:
        print('{} occured, sdf not provided or not valid'.format(stage_name))


## Check uniqueness of an id.
def count_n_rows_per_id(sdf,column_id,return_sdf=False):

    sdf_gb=sdf.groupBy(column_id).agg(f.count(f.lit(1)).alias('n_rows_per_id'))
    print ('Counting n_rows per ', column_id)
    breakdown_by_col_spark(sdf_gb,'n_rows_per_id',display=True,do_cumu=True,sortByCol=True)
    
    if return_sdf: 
        return sdf_gb

def count_n_rows(sdf,text='n_rows'):
    n_rows=sdf.count()
    print("{} = {:,.0f}" .format(text,n_rows))
    return n_rows
