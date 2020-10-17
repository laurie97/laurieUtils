from __future__ import print_function

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pylab import text
import seaborn as sns
sns_colours = sns.color_palette()
from matplotlib.ticker import MultipleLocator
from IPython.display import display, HTML
import datetime


## Display everything, be a little careful
def display_full(x,force=False):
    
    if (len(x) > 200) and not force:
        print("This is {:,.0f} rows, which is more than 200, are you sure you want to display full?".format(len(x)))
        print("If so, use the force option")
        return
    
    pd.set_option('display.max_rows', len(x))
    display(x)
    pd.reset_option('display.max_rows')

## 
def get_ax(ny=1,nx=1,sx=8,sy=5,sharex=False,sharey=False,return_fig=False):
    fig,ax_obj=plt.subplots(ny,nx,figsize=(sx,sy),sharex=sharex,sharey=sharey)
    if return_fig: return fig,ax_obj
    return ax_obj

def force_ax_grid(axs,x_seperators=False,y_seperators=False):

    ## To do add major locator thing to seperators

    ## If list run on each element
    if type(axs)==list:
        for this_ax in axs:
            force_ax_grid(this_ax,x_seperators,y_seperators)

    ## 
    else:
        if x_seperators:
            loc = MultipleLocator(base=x_seperators) # this locator puts ticks at regular intervals
            axs.xaxis.set_major_locator(loc)
            
        if y_seperators:
            loc = MultipleLocator(base=y_seperators) # this locator puts ticks at regular intervals
            axs.yaxis.set_major_locator(loc)
            
        axs.grid()
        axs.set_axisbelow(True)

    
## Show xaxis string labels
def force_xaxis_labels(ax,data,x,tick_freq=False):

    if tick_freq!=False:
        majorLocator = MultipleLocator(tick_freq)
        ax.xaxis.set_major_locator(majorLocator)

    
    locs=ax.get_xaxis().get_ticklocs()
    x_series=data.reset_index()[x]
    labels=[]

    
    for loc in locs:
        if loc < 0:                   labels.append("")
        elif loc >= len(x_series):    labels.append("")
        elif not float(loc).is_integer():
            print("force_xaxis_labels: WARNING! : There is a tick I can't label. Set tick_freq to fix this")
            labels.append("")
        else:
            try:      labels.append(x_series[loc])
            except:
                print("Laurie Debug:  I HATE HATE HATE THIS FUNCTION, my apologies")
                print("Laurie Debug:  I broke at loc = {} \n Laurie Debug: where locs = {} \n Laurie Debug: and x_series = {}".format(loc,locs,x_series))
    ax.set_xticklabels(labels)

## A function useful for using _new
def remove_sum_from_df_col_names(df_in, verbose=False):
    rename_dict={}
    if(verbose): print("remove_sum_from_df_col_names: What am I renaming")
    for col in df_in:
        col_no_sum=col.replace("sum(","").replace(")","")
        if(verbose): print("- {:25} =>     {:20}".format(col,col_no_sum))
        rename_dict[col]=col_no_sum
    df_out=df_in.rename(index=str,columns=rename_dict)
    return df_out

## Get Ratio
def get_ratio(num,den):
    if den==0:  return 0
    else: return float(num)/float(den)


## Make Ratio
def make_ratio(df,ratio_name,num,den,percent=False,error=False):

    #print("make_ratio!!!!")
    if percent:
        df[ratio_name]=df.apply(lambda row: get_ratio(row[num]*100.0,row[den]), axis=1)
    else:
        df[ratio_name]          = df.apply(lambda row: get_ratio(row[num],row[den]), axis=1)

    if error:
        ## Add in quadrature
        print("I am doing this")
        df[ratio_name+"_err"]      = df.apply(lambda row:  row[ratio_name] * np.sqrt( get_ratio(row[num+"_err"],row[num])**2 + get_ratio(row[den+"_err"],row[den])**2 ), axis=1)
        df[ratio_name+"_var_up"]   = df[ratio_name]+2*df[ratio_name+"_err"]
        df[ratio_name+"_var_down"] = df[ratio_name]-2*df[ratio_name+"_err"]


    return df

## Make Ratio
def make_diff(df,diff_name,num,den,percent=False):

    if percent:
        df[diff_name]=df.apply(lambda row: get_ratio((row[num]-row[den])*100,row[den]), axis=1)
    else:
        df[diff_name]=df[num]-df[den]
        
    return df

## Plot from command
## Command_dict contains:
##  - cols
##  - ylabel
##  - title
##
##

def plot_line_from_command(df,x,command_dict,ax):
    
    keys=command_dict.keys()
    cols=command_dict["cols"]
    
    for col in cols:
        df.plot(x=x,y=col,ax=ax,label=col)
        
    if "ylabel" in keys:
        ax.set_ylabel(command_dict["ylabel"])   
    if "title" in keys:
        ax.set_title(command_dict["title"])
        
## Plot from command
def plot_dfs_side_by_side(df_left, df_right, x='created_date',tag_left="left", tag_right="right",percent=False,diff=False,ratio_range=False,max_n=20):

    for i_col,col in enumerate(df_left):

        if i_col > max_n:
            print("You have {} plots, so I quit".format(max_n))
            break

        
        #print(col)
        
        if col == x: continue
        #fig,(ax1,ax2)=plt.subplots(1,2,sharey=True,sharex=True,figsize=(20,8))
        
        fig = plt.figure(figsize=(24,6))
        ax1 = fig.add_subplot(1, 3, 1)
        ax2 = fig.add_subplot(1, 3, 2, sharex = ax1, sharey = ax1)
        ax3 = fig.add_subplot(1, 3, 3, sharex = ax1)
        
        df_left.plot(x=x,y=col,ax=ax1,label="{} - {}".format(tag_left,col))        
        try: 
            df_right.plot(x=x,y=col,ax=ax2,color = ['r'],label="{} - {}".format(tag_right,col))
            plot_ratio_from_dfs(ax=ax3,x=x, 
                                df_num=df_left, col_num=col, 
                                df_den=df_right, ratio_name="Ratio left/right",percent=percent,diff=diff)
        except: print("")
            
        if ratio_range:
            ax3.set(ylim=ratio_range)

        fig.suptitle(col.replace('_',' '))
        ax1.set_title(tag_left)
        ax2.set_title(tag_right)
                     
        if percent and diff:
           ax3.set_title("Percent Difference Between {} And {}".format(tag_left,tag_right))
        elif diff:
           ax3.set_title("Absolute Difference Between {} And {}".format(tag_left,tag_right))
        else:
           ax3.set_title("Ratio of {} to {}".format(tag_left,tag_right))

        force_ax_grid([ax1,ax2,ax3])
           
def plot_dfs_with_ratio(df_left, df_right, x='created_date',tag_left="left", tag_right="right",percent=False,diff=False,ratio_range=False,max_n=20):

    list_cols=list(set(list(df_left.columns)+list(df_right.columns)))
    
    for i_col,col in enumerate(list_cols):

        if i_col > max_n:
            print("You have {} plots, so I quit".format(max_n))
            break

        
        print(col)
        if col == x: continue
        #fig,(ax1,ax2)=plt.subplots(1,2,
        #                           sharex=True,figsize=(20,8))

        #ax1,ax2=get_ax(nx=2)

        
        fig,(ax1,ax2)=get_ax(nx=2,sx=15,sharex=True,return_fig=True)

        if col in df_left.columns:  df_left.plot(x=x,y=col,ax=ax1,label="{}".format(tag_left))
        if col in df_right.columns: df_right.plot(x=x,y=col,ax=ax1,linestyle='--',color = ['r'],label="{}".format(tag_right))
        if (col in df_left.columns) and (col in df_right.columns):
            plot_ratio_from_dfs(ax=ax2,x=x, 
                                df_num=df_left, col_num=col, 
                                df_den=df_right, ratio_name="Ratio left/right",percent=percent,diff=diff
            )
            
        if ratio_range:
            ax2.set(ylim=ratio_range)

        fig.suptitle(col.replace('_',' '))
        ax1.set_title('Column Comparison')
                     
        if percent and diff:
           ax2.set_title("Percent Difference")
        elif diff:
           ax2.set_title("Absolute Difference")
        else:
           ax2.set_title("Ratio")

        force_ax_grid([ax1,ax2])
           


def plot_dfs_without_ratio(df_left, df_right, x='created_date',tag_left="left", tag_right="right",percent=False,diff=False,ratio_range=False,max_n=20):

    for i_col,col in enumerate(df_left):

        if i_col > max_n:
            print("You have {} plots, so I quit".format(max_n))
            break

        
        print(col)
        if col == x: continue
        
        fig,ax1=get_ax(return_fig=True)
        title=col.replace('_',' ')
        fig.suptitle(title)
        
        df_left.plot(x=x,y=col,ax=ax1,label="{}".format(tag_left))
        try: 
            df_right.plot(x=x,y=col,ax=ax1,linestyle='--',color = ['r'],label="{}".format(tag_right))
            plot_ratio_from_dfs(ax=ax2,x=x, 
                                df_num=df_left, col_num=col, 
                                df_den=df_right, ratio_name="Ratio left/right",percent=percent,diff=diff)
        except: print("")
        
        force_ax_grid([ax1])


def doListMagic(fileListRaw, histNameListRaw,verbose=False,preserve_string=False):

    if(verbose): print('fileListRaw', fileListRaw)
    if(verbose): print('histNameListRaw', histNameListRaw)
    
    if not ( isinstance(fileListRaw, list) or isinstance(histNameListRaw, list) ):
        if preserve_string:
            histNameList = histNameListRaw
            fileList     = fileListRaw

        else:
            histNameList = [ histNameListRaw ]
            fileList     = [ fileListRaw ]
     
    elif not (isinstance(fileListRaw, list)):
        fileList=[]
        for histName in histNameListRaw:
            fileList.append(fileListRaw)
        histNameList=histNameListRaw

    elif not (isinstance(histNameListRaw, list)):
        histNameList=[]
        for file in fileListRaw:
            histNameList.append(histNameListRaw)
        fileList=fileListRaw
    
    elif( len(fileListRaw) == len(histNameListRaw) ):
        return fileListRaw, histNameListRaw
    
    else:
        raise SystemExit('\n***ERROR*** doListMagic: No magic here len(fileListRaw) != len(histNameListRaw), and both are lists\n  - fileListRaw = {f} \n - histListRaw = {h}'.format(f=type(fileListRaw),h=type(histNameListRaw)))
        

    return fileList, histNameList
        

## df_num, col_num, df_den and df_den can be a single item, or a list of items
## It will produce a ratios equal in lenght to the size of the list you put in.
def plot_ratio_from_dfs(ax,x,
                        df_num,      col_num,
                        df_den=None, col_den=False,
                        ratio_name="ratio",colour=False,doListMagicTest=False,percent_diff=False, percent=False,
                        diff=False,kind='line',colour_palette=sns.color_palette()
                        ,error=False,linestyle='-',marker=None):

    if percent_diff:
        diff=True
        percent=True
    
    ## This bit of code is horrible, I apologise

    if not (col_den): 
        col_den=col_num

    try:    df_den.head(2)
    except: 
        try: df_den[0].head(2)
        except: df_den=df_num 
    
    
    ## do list magic is some crazy function I wrote a while ago....
    ## The aim is that I can plot multiple ratios with ease by inputting lists
    ## The magic is that I can enter either a single item or a list of items and either will work
    ## For example I always want the df used for the numerator to 'example_df'
    ## If I set df_num='example_df', the magic will know that I want that to be a list.
    if(doListMagicTest): print("\ndoList nums:")
    (df_num,col_num) = doListMagic(df_num,col_num,preserve_string=True)
    if(doListMagicTest): print("df_num ",type(df_num),len(df_num))
    if(doListMagicTest): print("col_num ",type(col_num),len(col_num))
                       
    if(doListMagicTest): print("\ndoList dens:")
    (df_den,col_den) = doListMagic(df_den,col_den,preserve_string=True)
    if(doListMagicTest): print("df_den ",type(df_den),len(df_den))
    if(doListMagicTest): print("col_den ",type(col_den),len(col_den))

    if(doListMagicTest): print("\ndoList dfs")
    (df_den, df_num)  = doListMagic(df_den, df_num)
    if(doListMagicTest): print("df_den ",type(df_den),len(df_den))
    if(doListMagicTest): print("df_num ",type(df_num),len(df_num))

    if(doListMagicTest): print("doList cols")
    (col_num,col_den) = doListMagic(col_num,col_den)
    if(doListMagicTest): print("col_den ",type(col_den),len(col_den))
    if(doListMagicTest): print("col_num ",type(col_num),len(col_num))
    
    # These two protect backwards compatibility, but will lead to stupid plots....
    (df_num,ratio_name) = doListMagic(df_num,ratio_name)
    if colour!=False:
        (df_num,colour) =     doListMagic(df_num,colour)
    
    if (doListMagicTest):
        print("df_den",df_den)
        print("col_den",col_den)
        print("df_num",df_num)
        print("col_num",col_num)
        print("ratio_name",ratio_name)
        return

    

    df_ratio=pd.DataFrame()
    df_ratio[x]=df_num[0][x]
    df_ratio=df_ratio.sort_values(x).set_index(x)
    for i_ratio in range(0,len(df_den)):
        this_ratio_name=ratio_name[i_ratio]
        this_df_num=df_num[i_ratio].sort_values(x).set_index(x,drop=True)
        this_df_den=df_den[i_ratio].sort_values(x).set_index(x,drop=True)

        this_col_num=col_num[i_ratio]
        this_col_den=col_den[i_ratio]
        
        df_ratio["num"]=this_df_num[this_col_num]
        df_ratio["den"]=this_df_den[this_col_den]

        if error:
            df_ratio["num_err"]=this_df_num[this_col_num+"_err"]
            df_ratio["den_err"]=this_df_den[this_col_den+"_err"]

        ## Yeah ok, now I added a diff functionality this shouldn't be df_ratio... Legacy.
        if diff:  df_ratio=make_diff(df=df_ratio,num="num",den="den",diff_name=this_ratio_name, percent=percent) 
        else:     df_ratio=make_ratio(df=df_ratio,num="num",den="den",ratio_name=this_ratio_name,percent=percent,error=error)  

        df_ratio=df_ratio.drop(["num","den"],axis=1)
        
    df_ratio=df_ratio.reset_index()


    ## If colour not set use pallete
    if not colour:        colour=colour_palette[0:len(df_den)]
        

    
    df_ratio.plot(x=x,y=ratio_name,ax=ax,color=colour,label=ratio_name,kind=kind,linestyle=linestyle,marker=marker)
    if error:
        ratio_name_var_up   = [name+"_var_up"   for name in ratio_name]
        ratio_name_var_down = [name+"_var_down" for name in ratio_name]
        ratio_name_error =    ["Uncert. (95% C.I.)" for name in ratio_name]
        ratio_no_legend  =    [None for name in ratio_name]

        df_ratio.plot(x=x,y=ratio_name_var_up  , ax=ax,color=colour,kind=kind,linestyle='--',label=ratio_name_error,marker=marker)
        df_ratio.plot(x=x,y=ratio_name_var_down, ax=ax,color=colour,kind=kind,linestyle='--',label=ratio_no_legend,marker=marker)
        clean_legend(ax)


    if (diff):      plt.axhline(0,   color='k')
    elif(percent):  plt.axhline(100, color='k')
    else:
        plt.axhline(1,   color='k')


        
    return df_ratio

def clean_legend(ax,ncol=1):
    
    handles, labels = ax.get_legend_handles_labels()
    print(labels)
    for (handle,label) in zip(handles,labels):
        if label==None or label==False or label=='None' or label=='False':
            i=labels.index(label)
            del handles[i]
            del labels[i]     
    ax.legend(handles, labels,ncol=ncol)


## Plot series with splits
def plot_by_split(df_to_plot,split,x,y,
                       ax,ax_ratio=False,
                       max_n=5,min_n=0,plot_total=False,
                       prefix=False,ratio_type="total",
                       sort_order=False,
                       error=False,
                       linestyle="-",colours=None,marker=None,
                       percent=False,diff=False):

    if colours is None:
        colours=sns_colours*5
    else:
        colours=colours*5

    if type(linestyle)!=type([]):
        linestyle=[linestyle]*100
        
    ## Get total and plot if required
    df_total=df_to_plot.groupby(x)[[y]].sum().reset_index()
    if plot_total:
        if prefix==False:
            label ="{}".format('total')
        elif prefix==True or prefix == 'split':
            label ="{} : {}".format(split,'total')
        else:
            label ="{} : {}".format(prefix,'total')

        df_total.plot(x=x,y=y,ax=ax,label=label,color='black',linestyle=linestyle[0],marker=marker)

    ## How am I plotting this
    ### Default == Total
    if isinstance(ratio_type, pd.DataFrame):
        df_den=ratio_type.sort_values(x)
        ratio_type="df input"
    elif ratio_type=="total":
        df_den=df_total
        percent=True

    ## Cumulative will mean a bit of work :)
    elif ratio_type=="cumu":
        print("Ok I'll do a cumulative if you insist")

    ### Set to specific split to get relative to that.
    else:
        df_den=(df_to_plot
             .loc[lambda df: df[split] == ratio_type]
             .sort_values(x)
        )
    
    if sort_order==False:
        sort_order_col=y
        sort_order_ascending=False
        sort_order_base=False
    else:
        if type(sort_order)==type([]):
            sort_order_col=sort_order[0]
            if len(sort_order) > 1: sort_order_ascending=sort_order[1]
            else:                   sort_order_ascending=True
            if len(sort_order) > 2: sort_order_base=sort_order[2]
            else: sort_order_base=False
        else:
            sort_order_col=sort_order
            sort_order_ascending=True
            sort_order_base=False
            
                 
    if split==sort_order_col:
        list_of_splits=list(set(list(df_to_plot[split].sort_values(ascending=sort_order_ascending))))
    else:
        if type(sort_order_col)==type([]): list_sort_order_col=sort_order_col
        else:                              list_sort_order_col=[sort_order_col]
            
        list_of_splits=list(df_to_plot.groupby(split)[list_sort_order_col].sum().sort_values(list_sort_order_col,ascending=sort_order_ascending).index)

    if sort_order_base!=False:
        
        if type(sort_order_base) != type([]):
            sort_order_base=[sort_order_base]

        for this_sort_order_base in reversed(sort_order_base):
            if this_sort_order_base in list_of_splits:
                index=list_of_splits.index(this_sort_order_base)
                del list_of_splits[index]
                list_of_splits=[this_sort_order_base]+list_of_splits
    
    print("list_of_splits: ",list_of_splits)
    
    for i_split,this_split in enumerate(list_of_splits[min_n:min(max_n,len(list_of_splits))]):
    
            data=(df_to_plot
             .loc[lambda df: df[split] == this_split]
             .sort_values(x)
            )
        
            if ratio_type=="df input":
                data_den=(df_den
                      .loc[lambda df: df[split] == this_split]
                      .sort_values(x)
                )
            elif ratio_type!="cumu":
                data_den=df_den
            

            
            if prefix==False:
                label ="{}".format(this_split)
            elif prefix==True or prefix == 'split':
                label ="{} : {}".format(split,this_split)
            else:
                label ="{} : {}".format(prefix,this_split)
                
                
            if len(data) == 0 : continue

                
            colour=colours[i_split]
            this_linestyle=linestyle[i_split+int(plot_total)]

            data.plot(x=x,y=y,ax=ax,label=label,color=colour,linestyle=this_linestyle,marker=marker)
            
            if ax_ratio:

                if ratio_type=="cumu":
                    n_entries=data[y].sum()
                    data_cumu=data
                    data_cumu[y]=data[y].cumsum()*100.0/n_entries
                    data_cumu.plot(x=x,y=y,ax=ax_ratio,label=label,color=colour,marker=marker)
                    print(this_split, data_cumu.loc[lambda d: d[x]==10][y])
                    continue
                
                if ratio_type==this_split: continue
                
                plot_ratio_from_dfs( ax=ax_ratio,x=x,col_num=y
                                     , df_num=data,df_den=data_den
                                     , colour=colour,ratio_name=label,error=error,linestyle=this_linestyle
                                     , marker=marker,percent=percent,diff=diff
                )

    #if 'date' not in x:
    #    force_xaxis_labels(ax,data,x)
    #    if ax_ratio: force_xaxis_labels(ax_ratio,data,x)
    
    ax.set(ylabel=y)
    
    if ax_ratio and (ratio_type!="df input"):
        if   (ratio_type=="cumu"):  ax_ratio.set(ylabel="Cumulative Distibution (%)")
        elif (ratio_type=="total"): ax_ratio.set(ylabel="Percentage of Total")
        else: ax_ratio.set(ylabel="Ratio Relative to "+ratio_type)

        

def format_date_df(df,col='yyyy_mm_dd',date_format='%Y-%m-%d'):
    df[col] = df[col].apply(lambda x: pd.to_datetime(str(x), format=date_format))
    df.sort_values(col,inplace=True)
    return df

def supersize_me():

    command='''
import matplotlib.pylab as pylab
params = {'legend.fontsize': 'x-large',
          'axes.labelsize': 'x-large',
          'axes.titlesize':'x-large',
          'xtick.labelsize':'x-large',
          'ytick.labelsize':'x-large',
          'figure.titlesize':'xx-large'}
pylab.rcParams.update(params)

'''
    print(command)

#### Make a lovely heatmap...
def do_heatmap(df,x,y,values,ax):
    pivot_table = df.pivot_table(index=y, columns=x,values=values)
    sns_hm = sns.heatmap(pivot_table, robust=True, ax=ax)


def do_pivot(df,values,index,columns,fill_value=0):

    ''' Perform pivot, without the subcolumn nonsense.
        Output: Index is row, columns of form 'value_column' for each entry in values and columns.
    ''' 
    
    df_pivot =   pd.pivot_table(df, 
                            values=values,
                            index=index,
                            columns=columns,
                            aggfunc=np.sum,
                            fill_value=fill_value
                           )
    
    df_pivot.columns = ['_'.join(col).strip() for col in df_pivot.columns.values]
    
    df_pivot=df_pivot.reset_index()
    
    return df_pivot

def add_days_to_day_string(input_day_string,delta_days):
    
    day_ts=datetime.datetime.strptime(input_day_string,'%Y-%m-%d')
    output_day_ts=day_ts+datetime.timedelta(days=delta_days)
    output_day_string=str(output_day_ts.date())
    return output_day_string



