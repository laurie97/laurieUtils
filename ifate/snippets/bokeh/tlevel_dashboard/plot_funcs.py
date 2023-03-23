import logging
from bokeh.plotting import figure
from bokeh.models import NumeralTickFormatter
from bokeh.palettes import Category20
from bokeh.transform import dodge
from bokeh.models.ranges import DataRange1d
from . import data_funcs


def plot_starts_timeseries(
    source,
    data,
    source_tooltip,
    x,
    x_range,
    category,
    initial_categories,
    title,
    tools,
    disclosure_control_suffix,
    metric_name='Metric',
    category_order=None,
):

    """ Plot a timeseries of starts/providers"""

    circle_size = 10

    tooltips = [
        (f'{x}', f'@{{{x}}}'),
        (category, f'@{{{category}}}'),
        (f'{metric_name}', f'@{{{metric_name}}}'),
        ('Value', f'@value_{disclosure_control_suffix}'),
    ]

    plot = figure(
        tools=tools,
        tooltips=tooltips,
        x_range=x_range,
        plot_width=1000,
        plot_height=525,
        title=title,
    )
    plot.toolbar.logo = None

    categories = [col for col in data.columns if col not in [x, metric_name]]
    if category_order:
        for c in category_order:
            if c not in categories:
                raise KeyError(
                    f'category_order contains {c} which is not in data.columns'
                )
        categories = category_order

    colors = Category20[len(categories)]

    lines = []  # List lines, as these will be used to auto-zoom later
    for i, y in enumerate(categories):
        line = plot.line(x=x, y=y, source=source, legend_label=y, color=colors[i])
        circle = plot.circle(
            x=x, y=y, source=source, legend_label=y, color=colors[i], size=circle_size
        )
        if y not in initial_categories:
            line.visible = False
            circle.visible = False
        lines.append(line)

    ## Create Invisible Circles for tooltip
    ## Adapted from https://stackoverflow.com/a/50224376/15981460
    plot.circle(x, 'value', source=source_tooltip, alpha=0, size=circle_size + 1)

    plot.yaxis.axis_label = 'Number of Starts'
    plot.xaxis.axis_label = 'Academic Year'

    plot.yaxis[0].formatter = NumeralTickFormatter(format='0,0')

    # Enable auto-zoom on y-axis
    plot.y_range = DataRange1d(
        only_visible=True, start=0, range_padding=0.2, renderers=lines, min_interval=10
    )

    plot.legend.click_policy = 'hide'

    return plot


def calculate_academic_year_plot_range(data, academic_year):
    """
    Helper function for pages starts_and_providers_growth.py
    Calculate plot range using academic years.
    Lower end of range is min seen in data
    Upper end of range is max year in data + 2, the +2 gives room for legend
    If too few years are present, upper end is min_academic_year + 3 is used instead

    Args:
        data (pd.df): data which will be used to plot
        academic_year (str): Name of academic_year column in data

    Returns:
        plot_range (list): List of academic years (strings) to be used.
    """
    plot_range = []

    min_academic_year = data[academic_year].min()
    max_academic_year = max(
        data_funcs.helper_add_to_academic_year(data[academic_year].max(), 2),
        data_funcs.helper_add_to_academic_year(min_academic_year, 3),
    )

    academic_year = min_academic_year
    while academic_year <= max_academic_year:
        plot_range.append(academic_year)
        academic_year = data_funcs.helper_add_to_academic_year(academic_year, 1)

    return plot_range


def plot_hbar_with_categories(
    source,
    stacked_data,
    y,
    y_name,
    category_list,
    initial_metric,
    title,
    tools,
    disclosure_control_suffix,
    view,
    metric_name='Metric',
    x_label=None,
    total_bar_height=0.75,
    legend_outside=False,
    y_range=None,
):
    """
    Plot some variables as categories some y value
    """

    y_range = y_range or list(stacked_data[y].unique())
    y_range.reverse()

    colors = ['#718dbf', '#e84d60', '#c9d9d3']
    tooltips = [(f'{y_name}', f'@{{{y}}}'), (f'{metric_name}', f'@{{{metric_name}}}')]
    for category in category_list:
        ## The extra double curly bracket allows bokeh to read / in column names
        ## https://discourse.bokeh.org/t/2186
        tooltips.append((f'{category}', f'@{{{category}_{disclosure_control_suffix}}}'))

    plot = figure(
        tools=tools,
        tooltips=tooltips,
        y_range=y_range,
        x_range=DataRange1d(only_visible=True, start=0, range_padding=0.2),
        plot_width=1000,
        plot_height=475,
        title=title,
    )
    plot.toolbar.logo = None

    ## Loop over values to create multiple bars.

    n_categories = len(category_list)
    category_bar_height = total_bar_height / n_categories

    mid_index = (n_categories - 1) / 2

    for i, category in enumerate(category_list):
        dodge_value = (mid_index - i) * category_bar_height
        plot.hbar(
            y=dodge(y, dodge_value, plot.y_range),
            right=category,
            source=source,
            height=category_bar_height,
            legend_label=category_list[i],
            color=colors[i],
            view=view,
        )

    plot.xaxis.axis_label = x_label or initial_metric
    plot.xaxis[0].formatter = NumeralTickFormatter(format='0,0')

    plot.legend.location = 'center_right'
    plot.legend.click_policy = 'hide'

    if legend_outside:
        plot.legend.orientation = 'horizontal'
        plot.legend.spacing = 12
        plot.legend.location = 'left'
        plot.add_layout(plot.legend[0], 'above')

    return plot


def get_learner_status_colors(statuses):
    """
    Get list of colors for a set of learning aim statuses.

    Args:
        statuses (list): List of statuses being shown.

    Returns:
        list: Colours to be used in plot
    """
    colors_map = {
        'Completed': '#99c140',
        'Continuing': '#e7b416',
        'Transfer to new aim': '#db7b2b',
        'Withdrawn': '#cc3232',
    }
    colors = [colors_map[s] for s in statuses]
    return colors


def get_grade_colors(grades):
    """
    Get list of colors for a set for

    Args:
        statuses (list): List of statuses being shown.

    Returns:
        list: Colours to be used in plot
    """

    colors_map = {
        'A*': '#006203',
        'A': '#0f9200',
        'B': '#30cb00',
        'C': '#4ae54a',
        'D': '#a4fba6',
        'E': '#d3ffd4',
        'Distinction*': '#0b295f',
        'Distinction': '#1246a4',
        'Merit': '#1e65e4',
        'Pass': '#6394ec',
        'U': '#db7b2b',
        'Unknown': '#e7b416',
    }
    colors = [colors_map[g] for g in grades]
    return colors


def plot_stacked_hbar(
    source,
    stacked_data,
    view,
    y,
    y_name,
    x_label,
    stackers,
    initial_metric,
    title,
    tools,
    disclosure_control_suffix,
    colors=None,
    extra_tooltip_columns=None,
    legend_outside=False,
    y_range=None,
    y_label=None,
):
    """
    Plot Stacked Bar Chart
    """

    if not y_name:
        y_name = y

    if not colors:
        colors = [
            '#99c140',
            '#e7b416',
            '#db7b2b',
            '#cc3232',
        ]
        colors = colors[: len(stackers)]

    y_range = y_range or list(stacked_data[y].unique())
    y_range.reverse()

    tooltips = [(f'{y_name}', f'@{{{y}}}')]
    if extra_tooltip_columns:
        for col in extra_tooltip_columns:
            tooltips.append((f'{col}', f'@{{{col}}}'))
    for stack in stackers:
        ## The extra double curly bracket allows bokeh to read / in column names
        ## https://discourse.bokeh.org/t/2186
        tooltips.append((f'{stack}', f'@{{{stack}_{disclosure_control_suffix}}}'))

    plot = figure(
        tools=tools,
        tooltips=tooltips,
        y_range=y_range,
        plot_width=1000,
        plot_height=500,
        title=title,
    )
    plot.toolbar.logo = None
    plot.xaxis.axis_label = x_label
    plot.yaxis.axis_label = y_label

    plot.hbar_stack(
        stackers=stackers,
        y=y,
        source=source,
        view=view,
        height=0.8,
        legend_label=stackers,
        color=colors,
    )

    plot.xaxis[0].formatter = NumeralTickFormatter(format='0,0')

    if legend_outside:
        plot.legend.orientation = 'horizontal'
        plot.legend.spacing = 12
        plot.legend.location = 'left'
        plot.add_layout(plot.legend[0], 'above')

    return plot
