"""
Functions to plot using matplotlib and pandas
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import seaborn as sns
from scipy import stats

def get_ax(
    nrows=1, ncols=1,
    width=8, height=5,
    sharex=False, sharey=False,
    return_fig=False
):
    """
    Get a matplotlib axis object with some sensible starting parameters.
    Wrapper for plt.subplots function.

    args:
    - nrows, int: # Of Rows for axis object
    - ncols, int: # of Columns in axis object
    - width, float: Horizontal size of matplotlib axis object
    - height, float: Vertical size of matplotlib axis object
    - sharex, bool: All axes in axis object share x-axis
    - sharey, bool: All axes in axis object share y-axis
    - return_fig, bool: If True return fig and ax

    Returns:
    - If return_fig == True:
        - fig: matplotlib figure
        - ax: matplotblib ax object as returned by plt.subplots
    - If return_fig == False:
        - ax: matplotlib ax object as above.
    """

    fig, ax = plt.subplots(
        nrows, ncols, figsize=(width, height), sharex=sharex, sharey=sharey
    )
    if return_fig:
        return fig, ax
    return ax


def force_ax_grid(axs, x_seperators=None, y_seperators=None):
    """
    Force matplotlib axes to have a grid and optinally set the grid axis seperation distance

    Args:
    - axs: Either a matlotlib axes or a list of matplotlib axes
    - x_seperators: (Int, optional) : The distance between x-axis grid lines
    - y_seperators: (Int, optional) : The distance between y-axis grid lines
    """


    ## If list run on each element
    if type(axs)==list:
        for this_ax in axs:
            force_ax_grid(this_ax,x_seperators,y_seperators)

    ## If axis just run on it
    else:
        if x_seperators:
            loc = MultipleLocator(base=x_seperators) # this locator puts ticks at regular intervals
            axs.xaxis.set_major_locator(loc)
            
        if y_seperators:
            loc = MultipleLocator(base=y_seperators) # this locator puts ticks at regular intervals
            axs.yaxis.set_major_locator(loc)
            
        axs.grid()
        axs.set_axisbelow(True)


def annotate_hbar_ax(ax, annotate_format='{:,.0f}', annotate_size=12, annotate_offset=45):
    """
    Add annotation to an axis containing horizontal bar plot.

    Args:
    - ax, matplotlib ax object to be changed
    - annotate_format, str, how to format the number in the annotation
    - annotate_size, int, what size is the annotation text
    - annotate_offset, int, distance to the right end of the axis to annotation text.
    """

    
    x_max = ax.get_xlim()[1]
    
    for patch in ax.patches:

        if patch.get_width() != patch.get_width(): 
            continue

        ax.annotate(
            annotate_format.format(patch.get_width()),
            xy=(x_max, patch.get_y() + patch.get_height() / 2),
            xytext=(annotate_offset, 0),
            textcoords='offset points', ha="right", va="center",
            size=annotate_size
        )
    

def plot_hbar(
    data, ax, x, y, hue=None, 
    xlabel=None, x_max=None, x_seperators=None,
    annotate=True, annotate_size=12, annotate_format='{:,.0f}',
    annotate_offset=45, hue_order=None
):
    """
    Plot a horizontal bar plot using seaborn

    Args:
    - data, pandas df for plot
    - ax, matplotlib axes
    - x, str, column to go on x-axis (number column)
    - y, str, column to go on y-axis (category column)
    - hue, str, column that dictates color of plot
    - xlabel, str, x-axis title
    - x_max, str, optionally limit the plot to below x_max
    - x_seperators, float, distance between x-axis grid lines
    - annotate, bool, if True add annotation
    - annotate_size, int, size of text
    - annotate_format, str, How to format annotation text
    - annotate_offset, int, Distance betweeen end of x-axis and text
    - hue_order, list of str, order of hue
    """

    data_to_plot = data.copy()
    if x_max:
        data_to_plot = data_to_plot.loc[lambda df: df[x] < x_max]
    else:
        x_max = data_to_plot[x].max() * 1.2
    
    sns.barplot(data=data_to_plot, y=y, x=x, ax=ax, hue=hue, hue_order=hue_order)
    
    ax.set(ylabel='', xlim=[0, x_max], xlabel=xlabel)
    ax.legend(title='')
    
    force_ax_grid(ax, x_seperators=x_seperators)

    if annotate:
        annotate_hbar_ax(ax, annotate_format, annotate_size, annotate_offset=45)

    return ax

def annotate_stacked_bar_plot(
        ax,
        orientation,
        horizontalalignment='center',
        verticalalignment='center',
        color='white',
        size=12,
        min_value=0
        ):

    h_orientation_values = ['h', 'H', 'horizontal']
    v_orientation_values = ['v', 'V', 'vertical']
    if orientation in h_orientation_values:
        orientation = 'h'
    elif orientation in v_orientation_values:
        orientation = 'h'
    else:
        print(f'Orientation must be in {h_orientation_values}, or {v_orientation_values}')

    for p in ax.patches:
        width, height = p.get_width(), p.get_height()
        if orientation == 'h':
            value = width
        else:
            value = height

        x, y = p.get_xy()
        if value < min_value:
            continue

        ax.text(
            x+width/2,
            y+height/2,
            '{:.0f}%'.format(value),
            horizontalalignment=horizontalalignment,
            verticalalignment=verticalalignment,
            color=color,
            size=size,
        )

def plot_scatter_with_correlation(
    data,
    x,
    y,
    x_title=None,
    y_title=None,
    ax=None,
):

    if not ax:
        ax = get_ax()

    if not x_title:
        x_title=x.replace('_', ' ').title()
    if not y_title:
        y_title=y.replace('_', ' ').title()
    
    rho, pvalue = stats.pearsonr(data[x], data[y])


    data.plot(x=x, y=y, ax=ax, kind='scatter')
    force_ax_grid(ax)

    ax.set(
        xlabel = x_title,
        ylabel = y_title,
        title = (f'Checking Correlation between\n'
                f'{x_title} and {y_title}\n'
                f'(Co-effecient = {rho:,.2f}, p-value = {pvalue:,.2f})'
        )
    )

    return ax


