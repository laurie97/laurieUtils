import logging
from marko.ext.gfm import gfm

from bokeh.models.widgets import Div
from data.disclosure_control import disclosure_control, add_disclosure_control_columns

from .. import data_funcs

from ...base_pages import BaseBokehPage

METRICS_AND_DESCRIPTIONS = {
    'Starts': (
        'Number of learners that begin a T Level in an academic year, showing the take-up of T Levels. '
        'If a learner changes T Level then this a new start. Data from ILR/School Census.'
    ),
    'Providers': (
        'Number of providers that have at least one start in ILR/School census data.'
    ),
    'Continuing Starts': (
        'Number of starts, where the learner is still contining learning activities towards the T Level. Data from ILR/School Census.'
    ),
    'Cumulative Starts': 'Total number of starts since T Levels were launched.',
    'Learning Aim Status Name': (
        'What is the status of the learner studying on a T Level. '
        'Read more [here](https://find-npd-data.education.gov.uk/en/data_elements/87fb3186-594b-412d-8b94-9097005b5a34)'
    ),
    'Completed': 'Learner has completed the T Level learning activities.',
    'Continuing': (
        'Learner is continuing or intending to continue activities leading towards the T Level.'
    ),
    'Transfer To New Aim': (
        'Learner has withdrawn from T Level and as a direct result has at the same time started '
        'studying for another learning aim within the same provider (including starting a different T Level).'
    ),
    'Withdrawn': 'Learner has withdrawn from the T Level learning activities.',
    'Completion Rate (%)': 'Proportion of learners that have completed.',
    'Student With Exam Attempt': 'Learners with at least one attempt at the component or subcomponent.',
    'Pass': 'Learners that have passed the component or subcomponent.',
    'Good Pass': 'Learners that have recieved a high grade on the component or subcomponent (defined as A* to C on the Core component and Distiction or Merit on the Occupational Specialism).',
    'Pass Rate (%)': 'Proportion of learners where the grade is known that passed the component or subcomponent',
    'Grade Known': 'Learners that have attempted the component or subcomponent and the grade is known in the data provided by Ofqual. In download data only.',
    'Unknown': (
        'This data can contain provisional grades data provided by Ofqual. In provisional data-sets grades can be "Unknown" for a few reasons, e.g. the exam board is missing information, seeking clarification or has not recieved a paper where one was expected.'
    ),
    'Percentage Of Known Grades': (
        'Distribution of grades on a component when unknown grades are ignored. Be aware that this might be a biased calculation as there are specific reason for grades being unknown.'
    ),
    'U': '"Ungraded". This means the component/subcomponent was not passed.',
    'TQ': (
        'Technical Qualification. '
        'This is the the main, classroom-based element of the T Level, and IfATE is responsible for them. '
        'The TQ equips students with the skills and knowledge necessary to give them a broad understanding of their chosen occupational route.'
    ),
}

METRICS_AND_DESCRIPTIONS['Student Learning Status'] = METRICS_AND_DESCRIPTIONS[
    'Learning Aim Status Name'
]

status_and_count = [
    ('Completed', 'Completions'),
    ('Continuing', 'Continuing Learners'),
    ('Transfer To New Aim', 'Transfers'),
    ('Withdrawn', 'Withdrawls'),
]
for status, status_count in status_and_count:
    METRICS_AND_DESCRIPTIONS[status_count] = METRICS_AND_DESCRIPTIONS[status].replace(
        'Learner has', 'Number of learners that have'
    )


class BaseTLevelPage(BaseBokehPage):
    def __init__(self):
        """In the init I will set-up constants used for T Level Dashboard"""
        super().__init__()
        self.default_blank_col_width = 190
        self.default_blank_row_height = 10
        self.metric_name = 'Metric'  # Name for column containing metrics
        self.disclosure_control_flag = 'disclosure_control_flag'

        self.description_head = 'T Level Dashboard'
        self.starts_data_warning = '</br>'.join(
            [
                "⚠️ **Starts numbers here don't exactly match ESFA numbers. Alignment work is in progress.**",
                # Alignment work is Feature 144323 https://dfe-ssp.visualstudio.com/S129-Institute-Data-System/_boards/board/t/S129-Institute-Data-System%20Team/Features/?workitem=144323
            ]
        )
        self.data_guidance_text = 'All Data is Official Sensitive - Restricted Use'
        self.data_guidance_text_short = 'Official Sensitive'

        self.tools = 'pan,box_zoom,reset,hover,save'

        self.tlevel = 'tlevel_name'
        self.tlevel_total_name = 'All T Levels'

        self.route = 'route'
        self.route_total_name = self.tlevel_total_name

        self.cohort = 'academic_year'
        self.cohort_total_name = 'All Cohorts'

        self.gender = 'gender_name'
        self.gender_total_name = 'All Genders'

        self.blank_select_row = (
            '-----------'  # Default null entry in select columns for formatting
        )

        self.test_disclosure_control = False

    def build_bokeh_help_description(
        self,
        n_filters=1,
        click_legend=False,
        table=True,
        download_button=True,
        metric_descriptions=False,
        disclosure_warning=False,
    ):
        """
        Build help bullet points in markdown based on arguments that
        indicate which features are used in the dashboard.
        """

        help_desc = []

        line_1 = '  - Create plots'
        if n_filters > 0 or click_legend:
            line_1 += ' using'
        if n_filters > 0:
            line_1 += ' the filter'
            if n_filters > 1:
                line_1 += 's'
            if click_legend:
                line_1 += ' and'
        if click_legend:
            line_1 += ' the click-able legend'
        line_1 += ' and save using the floppy disc icon.'
        help_desc.append(line_1)

        if table or download_button:
            line_2 = '  - Get exact numbers using'
            if table:
                line_2 = line_2 + ' the download data button'
                if download_button:
                    line_2 = line_2 + ' or'
            if download_button:
                line_2 = line_2 + ' the data table below the plot'
            line_2 = line_2 + '.'
            help_desc.append(line_2)

        if metric_descriptions:
            line_3 = '  - Descriptions of terms can be found at the bottom of the page.'
            help_desc.append(line_3)

        if disclosure_warning:
            help_desc.append(
                '- The data contains sensitive information, be careful to avoid identifying individual students.'
            )

        if self.test_disclosure_control:
            help_desc.append('- ***DISCLOSURE CONTROL MODE IS ON!!!***')

        self.description_bokeh_help = '\n'.join(help_desc)

    def disclosure_control_and_format_numbers(
        self,
        data,
        cols_to_exclude=['Providers'],
        cols_to_include=None,
        supress_as_number=False,
        pct_col=None,
        str_formatter='{:,.0f}',
        do_format=True,
        **kwargs,
    ):
        """
        Customise disclosure_control with default args for this dashboard
        If supressing as a string then format numbers.
        """
        data = disclosure_control(
            data,
            cols_to_exclude=cols_to_exclude,
            cols_to_include=cols_to_include,
            supress_as_number=supress_as_number,
            **kwargs,
        )

        if (not supress_as_number) or (not do_format):
            data = data_funcs.string_format_numbers(
                data,
                pct_col=pct_col,
                str_formatter=str_formatter,
                columns=cols_to_include,
            )

        return data

    def add_disclosure_control_string_columns(
        self, data, metric_name='Metric', pct_col=None, **kwargs
    ):
        """
        Customise add_disclosure_control so that it
        - Uses default args for this dashboard.
        - Adds columns that is formatted string for tool-tip.
        """

        data = (
            data.pipe(
                add_disclosure_control_columns,
                supress_as_number=False,
                keep_edge_value=True,
                col_suffix=data_funcs.DISCLOSURE_CONTROL_SUFFIX,
                **kwargs,
            )
            .pipe(
                data_funcs.remove_disclose_control_for_metrics,
                metrics_to_disclose=['Providers'],
                disclosure_control_suffix=data_funcs.DISCLOSURE_CONTROL_SUFFIX,
                metric_name=metric_name,
            )
            .pipe(
                data_funcs.string_format_columns_with_suffix,
                col_suffix=data_funcs.DISCLOSURE_CONTROL_SUFFIX,
                str_formatter='{:,.0f}',
                pct_col=pct_col,
            )
        )

        return data

    def get_download_filename(self, stem):
        filename = f'official_sensitive__tlevel_dashboard_data__{stem}.csv'
        return filename

    def get_plot_data(self, data):
        plot_data = data.copy()
        plot_data = self.shorten_tlevel_name(plot_data)
        return plot_data

    def get_sources(self, data, metrics, initial_metric, metric_name='Metric'):
        """
        Get a source for each metric in a dict, as well as a initial_source for the initial_metric.
        Then one should build a plot from the initial_source.
        In a JS callback the data from any of the sources can be used to overwrite data allowing interactive plots.

        Args:
            data (pd.df): Dataframe including a metric column.
            metrics (list of str): List of metrics to be used in a plot
            initial_metric (str): Metric to be shown initially
            metric_name (str): Name of metric column (default='Metric')

        Returns:
            sources (dict containing bokeh ColumnDataSource)
            initial_source (ColumnDataSource)
        """

        sources = {}
        for metric in metrics:
            data_slice = data_funcs.filter_stacked_df(data, metric, column=metric_name)
            sources[metric] = self.get_source(data_slice)

        initial_data_slice = data_funcs.filter_stacked_df(
            data, initial_metric, column=metric_name
        ).copy()
        initial_source = self.get_source(initial_data_slice)

        return sources, initial_source

    def get_metric_description(self, metric):
        metric_title = data_funcs.make_col_name_title(metric)
        if metric_title in METRICS_AND_DESCRIPTIONS:
            metric_description = METRICS_AND_DESCRIPTIONS[metric_title]
        elif metric in METRICS_AND_DESCRIPTIONS:
            metric_description = METRICS_AND_DESCRIPTIONS[metric]
        else:
            metric_description = None
            logging.warn('No description avaliable for metric "%s"', metric)
        return metric_description

    def create_metric_description_table(self, metrics):
        markdown_list = [
            '###### Glossary of Metrics:',
            '\n',
        ]
        for metric in metrics:
            logging.info('create_metric_description_table: %s', metric)
            description = self.get_metric_description(metric)
            if description:
                markdown_list.append(f'- **{metric}**: {description}')

        markdown = '\n'.join(markdown_list)
        html_text = gfm.convert(markdown)
        div = Div(text=html_text)
        return div

    def calculate_unique_list(self, data, col, sort=True):
        unique_list = list(data[col].drop_duplicates())
        if sort:
            unique_list = sorted(unique_list)
        return unique_list

    def shorten_tlevel_name(self, data, tlevel_name_col=None):

        tlevel_name_col = tlevel_name_col or self.tlevel

        if tlevel_name_col in data.columns:
            data[tlevel_name_col] = data[tlevel_name_col].str.replace(
                'Engineering and Manufacturing', 'E&M'
            )
        return data
