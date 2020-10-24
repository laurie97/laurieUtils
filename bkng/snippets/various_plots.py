#################################
#### Experiment Result Box Plot
#################################


def add_box_plot(ax,results_and_stats):
    
    pvalue=results_and_stats['p-value']
    
    if pvalue > 0.1: color='blue'
    elif results_and_stats['observed'] < 0 : color='red'
    else: color='green'
        
    ci_box=[
        results_and_stats['90_pct_ci_down'],
        results_and_stats['90_pct_ci_down'],
        results_and_stats['observed'],
        results_and_stats['90_pct_ci_up'],
        results_and_stats['90_pct_ci_up']
    ]
    sns.boxplot(x=ci_box,ax=ax,color=color)
    
    max_range=1.5*max([abs(x) for x in [results_and_stats['90_pct_ci_down'], results_and_stats['90_pct_ci_up']]])
    
    ax.set(xlim=[-max_range, +max_range], 
           xlabel='Result = {:,.0f} Between ({:,.0f} and {:,.0f}), p-value = {:.2f}'.format(
                         results_and_stats['observed'],results_and_stats['90_pct_ci_down'],results_and_stats['90_pct_ci_up'],
                         results_and_stats['p-value']
                     ),
           title=results_and_stats['metric_title']
    )    
    ax.grid()
    ax.set_axisbelow(True)

#################################
#### Plot Proj Against Obj (Used to validation of projection)
#################################

def plot_obs_vs_proj(df_bookings_per_variant_retro_flat, exp_details,
                    metric='expected_stays_adjusted_thousands',
                    ratio_range=[-10,40],
                    ratio_y_seperators=5,
                    split_col='variant',
                    splits=[[0,'Base'],[1,'Variant']],
                     do_delta=True, is_delta=False,percent=True,plot_old=True
                    ):

    if is_delta and do_delta:
        print("I can't do is_delta and do_delta at same time")
        do_delta=False
    
    fig,(ax,ax_ratio)=get_ax(nx=2,sx=18,sharex=True,return_fig=True)
    
    colours=[sns_colours[0],sns_colours[3],sns_colours[1],sns_colours[2],sns_colours[4],sns_colours[5]]
    max_y=0.001
    
    linestyles=['-','--',':']
    
    for i_split,split_instruction in enumerate(splits):
        this_split=split_instruction[0]
        split_label=split_instruction[1]
        colour=colours[i_split]
    
        this_df=df_bookings_per_variant_retro_flat.loc[lambda df: df[split_col] == this_split]
        if plot_old==False:
            this_df=this_df.loc[lambda df: df.col_type_formal!="Old Projection"]
        
        
        max_y=max(max(this_df[metric]),max_y)
        
        
        plot_by_split_time(this_df,
                           time='days_after_install',y=metric,
                           split='col_type_formal',prefix=split_label,
                           ax=ax,ax_ratio=ax_ratio,
                           ratio_type='Actual',
                           sort_order=['col_type',False,['Actual','Projected']],
                           linestyle=linestyles,colours=[colour]*3,marker='o',
                           percent=percent,diff=True
                          )
     
    if do_delta:
        
        delta_join_cols=['days_after_install','col_type','col_type_formal']
    
        df_bookings_per_variant_retro_flat_delta=get_delta_df(df_bookings_per_variant_retro_flat,
                                                              delta_join_cols,
                                                              variant=splits[1][0])
        
        fig_delta,(ax_delta,ax_delta_ratio)=get_ax(nx=2,sx=18,sharex=True,return_fig=True)
        
        plot_by_split_time(df_bookings_per_variant_retro_flat_delta,
                       time='days_after_install',y=metric,
                       split='col_type_formal',prefix='({} - {})'.format(splits[1][1],splits[0][1]),
                       ax=ax_delta,ax_ratio=ax_delta_ratio,
                       ratio_type='Actual',
                       sort_order=['col_type',False,['Actual','Projected']],
                       linestyle=linestyles,colours=['grey']*3,marker='o',
                       percent=percent,diff=True
                      )
    
    ax_title = 'Expected Stays'
    ax_ylabel= 'Expected Stays'
    suptitle = 'Long-Term Impact of App First Opens - Projected vs. Actuals'
    
    if 'adjusted' in metric:
        suptitle=suptitle.replace('Actuals','Adjusted Actuals')
        
    if 'per_day' in metric:
        ax_title=ax_title.replace('Expected Stays','Expected Stays per Day of Adverts')
        suptitle=suptitle.replace('Expected Stays','Expected Stays per Day of Adverts')

    
    if 'post_experiment' in metric:
        ax_title=ax_title.replace('Expected Stays','Expected Stays (Created > 7 Days After Install)')
        suptitle=suptitle.replace('Expected Stays','Expected Stays (Created > 7 Days After Install)')
    
    if 'per_visitor' in metric:
        ax_title=ax_title.replace('Expected Stays','Expected Stays per Visitor with Install')
        suptitle=suptitle.replace('Expected Stays','Expected Stays per Visitor with Install')
        
        
    if 'thousands' in metric:
        ax_ylabel=ax_ylabel+' (Thousands)'
    
    if is_delta:
        ax_title=ax_title.replace('Expected Stays','Additional Expected Stays')
        suptitle=suptitle.replace('Expected Stays','Additional Expected Stays')

    
    ax.set(ylabel=ax_ylabel,
           xlabel='Days After Install',
           title=ax_title,
           ylim=[0,max_y*1.2],
           xlim=[-3,370]
           
          )
    
    if percent:
        ax_ratio.set(title='Projected With Respect to Actual (% Diff)',
                     xlabel='Days After Install',
                     ylabel='Percent Difference',
                     ylim=ratio_range
                    )
    else:
        ax_ratio.set(title='Projected With Respect to Actual (Abs. Diff)',
                     xlabel='Days After Install',
                     ylabel='Absoltue Difference',
                     ylim=ratio_range
                    )
        

    
    
    
    ax.legend()
    ax_ratio.legend()
    
    force_ax_grid([ax],x_seperators=30)
    force_ax_grid([ax_ratio],x_seperators=30,y_seperators=ratio_y_seperators)

    if type(exp_details)==dict: 
        tag_name=exp_details['tagname']
    else:
        tag_name=exp_details
              
    fig.suptitle('{} \n {}'.format(suptitle,tag_name),y=1.05)
    
    if do_delta:
        
        ax_title=ax_title.replace('Expected Stays','Additional Expected Stays')
        suptitle=suptitle.replace('Expected Stays','Additional Expected Stays')

    
        ax_delta.set(ylabel=ax_ylabel,
               xlabel='Days After Install',
               title=ax_title,
               ylim=[ 0, max(df_bookings_per_variant_retro_flat_delta[metric]*1.2) ]
        )
        
        if percent:
            ax_delta_ratio.set(title='Actual With Respect to Projected (% Diff)',
                         xlabel='Days After Install',
                         ylabel='Percent Difference'
            )
        else:
            ax_delta_ratio.set(title='Actual With Respect to Projected (Abs. Diff)',
                         xlabel='Days After Install',
                         ylabel='Abs. Difference'
            )
            
    
        
        ax_delta.legend()
        ax_delta_ratio.legend()
        
        force_ax_grid([ax_delta],x_seperators=30)
        force_ax_grid([ax_delta_ratio],x_seperators=30,y_seperators=ratio_y_seperators)
        fig_delta.suptitle('{} \n {}'.format(suptitle,tag_name),y=1.05)
        
        return (fig,ax,ax_ratio,ax_delta,ax_delta_ratio)
    
    return (fig,ax,ax_ratio)

#################################
#### How to style a data frame in a nice way.
#################################

(
    df_bw_jan_just_site_class
    .loc[lambda df: df.site_class!="other"]
    .sort_values('site_class')
    .set_index('site_class')
    [["cancellation_rate","gross_roomnights_share","cancelled_roomnights_share","mean_book_window_gross","mean_book_window_cancelled"]]
    .style
    .format({"cancellation_rate":"{:.1f}%",
             "gross_roomnights_share":"{:,.1f}%",
             "cancelled_roomnights_share":"{:,.1f}%",
             "mean_book_window_gross":"{:,.1f} Days",
             "mean_book_window_cancelled":"{:,.1f} Days"
            
            }
           )
    .set_properties(**{'text-align':'right'})
    .bar(subset="cancellation_rate",   color=blue,width=58,  align='mid')
    .bar(subset="gross_roomnights_share",    color=green,width=43, align='mid')
    .bar(subset="cancelled_roomnights_share",color=red,width=45,   align='mid')
    .bar(subset="mean_book_window_gross",    color=blue,width=41, align='mid')
    .bar(subset="mean_book_window_cancelled",color=blue,width=62,   align='mid')
)

#################################
#### Scatter with Fit and Custom Legend
#################################

## Do Fit
from sklearn.linear_model import LinearRegression

## x and y
x = df_for_fit[['abrn_mobile_thousands_per_day']]
y = df_for_fit['nr_first_opens_per_day_thousands']

## Fit
model_scatter = LinearRegression()
model_scatter.fit(X=x, y=y)


## Add back to df
df_first_open_projection_abrn_monthly['nr_first_opens_per_day_thousands_projection']=(
    model_scatter.predict(df_first_open_rate_abrn_monthly[['abrn_mobile_thousands_per_day']])
)


## Plot
ax=get_ax(sx=8,sy=8)

colours=['black']+sns_colours

for i,mapping_simple in enumerate(['total']+list_mapping_simple):
    
    
    if mapping_simple=='total':
        this_df=(
            df_first_open_projection_abrn_monthly
            .sort_values('abrn_mobile_thousands_per_day')
        )
    else:     
        this_df=(
            df_first_open_projection_abrn_mapping_monthly
            .sort_values('abrn_mobile_thousands_per_day')
            .loc[lambda df: df.mapping_simple==mapping_simple]
        )
    
    fit_df=this_df.loc[loc_for_fit]    
    removed_df=this_df.loc[loc_for_removed]
         
    (
        fit_df
        .plot(kind='scatter',ax=ax,
          y='nr_first_opens_per_day_thousands',
          x='abrn_mobile_thousands_per_day',
          color=colours[i]
          )
    )
    
    
    (
        removed_df
        .plot(kind='scatter',ax=ax,
          y='nr_first_opens_per_day_thousands',
          x='abrn_mobile_thousands_per_day',
          color=colours[i],marker='x'
          )
    )

    
    (
        this_df
        .sort_values('abrn_mobile_thousands_per_day')
        .plot(kind='line',ax=ax,
              y='nr_first_opens_per_day_thousands_projection',
              x='abrn_mobile_thousands_per_day',
              color=colours[i],linestyle='--',
              label=mapping_simple
             )
        
    )
force_ax_grid(ax)
ax.set(xlim=[-200,1200],ylim=[-100,600],
       xlabel='Mobile ABRN (000s per day)',ylabel='# First Opens (000s per day)',
       title=''
      )


## Force Axis

from matplotlib.lines import Line2D

handles,labels=ax.get_legend_handles_labels()
handles.append(Line2D([0], [0], marker='.', color='black',linewidth=0))
labels.append('Data Used In Fit')


handles.append(Line2D([0], [0], marker='x', color='black',linewidth=0))
labels.append('Data Excluded From Fit')
ax.legend(handles,labels)


#################################
#### Stacked Histogram
#################################

## df_pivot_aug_site_type columns:
## - site_type_simplified
## - type
## - App
## - Desktop
## - Mdot
## - Other

ax=get_ax()
(
df_pivot_aug_site_type.sort_values('App',ascending=False)
                      .plot(x='type',y=['App','Desktop','Mdot','Other'],
                            kind='barh',stacked=True,ax=ax,
                            color=[sns_colours[3],sns_colours[0],sns_colours[1],sns_colours[2]]
                           )
)
ax.legend(bbox_to_anchor=(1,1))
ax.set(ylabel='')
force_ax_grid(ax,x_seperators=10)

for bar in ax.patches:
    w, h = bar.get_width(), bar.get_height()
    if w > 8:
        plt.text(bar.get_x() + w/2, 
                 bar.get_y() + h/2,
                 s="{:,.1f}%".format(w), 
                 ha="center", 
                 va="center",
                 size=14,
                 color='white'
                )

ax.set(title="Site-Type Share of Gross Reservations Made in 2020-08")

#################################
#### Waterfall
#################################


## Build up df
df_waterfall['pct_effect_size']=df_waterfall['effect_size']*100/df_waterfall.loc['total','effect_size']
df_waterfall['pct_of_explainable_effect_size']=df_waterfall['effect_size']*100/df_waterfall.loc['explainable','effect_size']

## Neg only allows us to veary colour
df_waterfall['effect_size_neg_only']=df_waterfall.apply(lambda row: 0 if row['effect_size'] >= 0  else row['effect_size'] ,axis=1)
df_waterfall['effect_size_major']=df_waterfall.apply(lambda row: row['effect_size'] if row.name in ['total','explainable'] else 0 ,axis=1)

##
df_waterfall['pct_effect_size_neg_only']=df_waterfall.apply(lambda row: 0 if row['pct_effect_size'] >= 0  else row['pct_effect_size'] ,axis=1)
df_waterfall['pct_effect_size_major']=df_waterfall.apply(lambda row: row['pct_effect_size'] if row.name in ['total','explainable'] else 0 ,a

### Do Waterfall plot                                                         
fig,ax=get_ax(sy=10,return_fig=True)
df_waterfall=df_waterfall.sort_values('effect_size')
## Plot All in Red                                                         
df_waterfall.plot(y='effect_size',kind='barh',ax=ax,label='Factors That Increased AHT',color=sns_colours[3])
## Plot All Reducers of AHT in Green
df_waterfall.plot(y='effect_size_neg_only',kind='barh',ax=ax,label='Factors That Decreased AHT',color='green')
## Plot neutral blocks in black                                                         
df_waterfall.plot(y='effect_size_major',kind='barh',ax=ax,label='Overall Summary',color=sns_colours[0])

## Annotate: # For each bar: Place a label                                                         
rects=ax.patches
y_values_seen=[]
for rect in rects:
    
    # Get X and Y placement of label from rect.
    x_value = rect.get_width()
    pct_value=x_value*100.0/61.1
    y_value = rect.get_y() + rect.get_height() / 2
    if x_value == 0: continue
    if y_value in y_values_seen: continue
    y_values_seen.append(y_value)

    # Number of points between bar and label. Change to your liking.
    space = 65
    # Vertical alignment for positive values
    ha = 'right'

    # Use X value as label and format number with one decimal place
    label = "{:.1f} s".format(x_value,pct_value)

    # Create annotation
    plt.annotate(
        label,                      # Use `label` as label
        (70, y_value),         # Place label at end of the bar
        xytext=(space, 0),          # Horizontally shift label by `space`
        textcoords="offset points", # Interpret `xytext` as offset in points
        va='center',                # Vertically center label
        ha=ha ,                     # Horizontally align label differently for
        fontsize=16,
        fontfamily='sans-serif' 
      )                             # positive and negative values.


force_ax_grid(ax,x_seperators=10)

ax.set(title='What has caused an Increased AHT since {}?'.format(waterfall_start),xlabel='Contribution to AHT (Seconds)',xlim=[-15,70])

fig.savefig(plot_dir+'waterfall')


###########################################
#### Get Correlation Plot
###########################################


import seaborn as sns
                                                         
## Set up clour scheme                                                         
colour_scheme=(sns.color_palette("RdBu", n_colors=11))[::-1]
del colour_scheme[-2]
sns.palplot(colour_scheme)
                                                         
## Features                                                         
features=get_non_zero_features(model)
features=[feature for feature in features if 'day_of_week' not in feature]
features.sort()
df_correlation=df_source[features].corr()
df_abs_correlation=abs(df_source[features].corr())

## Seaborn plot
                                                         

ax = get_ax(sx=30,sy=30)
sns.heatmap(df_abs_correlation, 
            mask=np.zeros_like(df_correlation, dtype=np.bool), 
            cmap=colour_scheme,
            square=True, ax=ax, linewidths=.5
)                                                        
