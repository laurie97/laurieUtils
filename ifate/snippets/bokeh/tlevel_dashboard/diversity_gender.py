import logging
import numpy as np
import pandas as pd

from bokeh.embed import components
from bokeh.layouts import row, column
import bokeh.models as bm

from .base import BaseTLevelPage
import data.disclosure_control as dc
from data.structures.tlevel import tlevelData
import data.pandas_utils as pd_utils

from .. import plot_funcs, data_funcs


class DiversityGender(BaseTLevelPage):
    def __init__(self):
        """In the init I will set-up constants used for this dashboard"""
        super().__init__()
        ## Set-up page Constants
        self.initial_metric = 'share_of_starts_%'  # Metric shown when user opens pages

        self.metrics_structured = [
            ['starts', 'share_of_starts_%'],
            ['completions', 'withdrawls', 'transfers', 'continuing_learners'],
            [
                'completion_rate_%',
                'withdrawl_rate_%',
                'transfer_rate_%',
                'continuing_rate_%',
            ],
        ]

        self.result_aggregations = [
            'core',
            'occupational specialism',
            'core: exam',
            'core: employer set project',
        ]
        self.result_metric_types = [
            'student_with_exam_attempt',
            'grade_known',
            'pass',
            'pass_rate_%',
            'good_pass',
            'good_pass_rate_%',
        ]

        for agg in self.result_aggregations:
            self.metrics_structured.append(
                [f'{metric}_{agg}' for metric in self.result_metric_types]
            )

        # self.metric_select_list is a flattened version of self.metrics_structured
        # with blank rows involved and no grade_known
        self.metric_select_list = []
        for i, metric_list in enumerate(self.metrics_structured):
            if i > 0:
                self.metric_select_list.append(self.blank_select_row)
            for m in metric_list:
                if not m.startswith('grade_known'):  # Hide this from metric list
                    self.metric_select_list.append(m)

        # self.metrics is a flattened version of self.metrics_structured
        self.metrics = []
        for these_metrics in self.metrics_structured:
            self.metrics += these_metrics

        self.metric_name = 'Metric'

        self.ratio_definitions = {
            'share_of_starts_%': ('starts', 'bar_total_starts'),
            'completion_rate_%': ('completions', 'starts'),
            'withdrawl_rate_%': ('withdrawls', 'starts'),
            'transfer_rate_%': ('transfers', 'starts'),
            'continuing_rate_%': ('continuing_learners', 'starts'),
        }

        for agg in self.result_aggregations:
            for pass_type in ['pass', 'good_pass']:
                self.ratio_definitions[f'{pass_type}_rate_%_{agg}'] = (
                    f'{pass_type}_{agg}',
                    f'grade_known_{agg}',
                )

        self.ratio_cols = list(self.ratio_definitions.keys())

        self.initial_cohort = self.cohort_total_name

        self.y = 'split_name'  # Value on y-axis of h-bar plot
        self.y_name = 'Split'  # What to call y in tool tip
        self.y_type_name = 'split_type'  # What to call y in tool tip
        self.y_types_active = [
            'Programme',
            'Route',
        ]  # Which settings are initial turned on

        self.bar_cols = [self.route, self.tlevel, self.cohort]

        self.category = self.gender  # Categories to be compare
        self.category_name = 'Gender'  # What to call variable in plot text
        self.category_values = ['Female', 'Male']

        self.category_total_name = 'All Learners'  # Total of category name

        self.display_cols = self.bar_cols + [self.category] + self.metrics

    def get_page_title(self):
        title = 'Diversity and Inclusion</br>Gender Diversity of T Levels'
        return title

    def get_description(self):
        self.build_bokeh_help_description(
            n_filters=4,
            metric_descriptions=True,
            click_legend=True,
            disclosure_warning=True,
        )
        description = '\n'.join(
            [
                f'- Compare a range of metrics by {self.category_name} for T Level students',
                f'{self.description_bokeh_help}',
                '',
                f'{self.starts_data_warning}',
            ]
        )
        return description

    def get_data(self):
        """Call all data-sets needed for dashboard page"""

        core_data = self.get_core_data()
        self.cohort_list = self.calculate_unique_list(core_data, self.cohort)
        self.y_type_list = self.calculate_unique_list(core_data, self.y_type_name)

        stacked_data = self.get_stacked_data(core_data)
        plot_data = self.get_plot_data(stacked_data)
        table_data = self.get_table_data(stacked_data)
        download_data = self.get_download_data(core_data)

        return (plot_data, download_data, table_data)

    def get_core_starts(self, tlevel_data, bar_and_cat_cols):
        """
        Get df of all starts metrics (e.g. starts/withdrawls) grouped by
        bar cols (cols that define what is in an individual bar e.g. tlevel/route/cohort)
        and the category col (which defines what is being compared e.g. gender).

        Args:
            tlevel_data (tlevelData): Data structure object to get tlevel data.
            bar_and_cat_cols (list of strings): Cols the define a bar and the category being compared

        Returns:
            df_core_starts (pd.df): df of starts metrics for use in dashboard.
        """

        df_starts = tlevel_data.get_starts()

        if self.test_disclosure_control:
            df_starts = df_starts.sample(500)

        df_status_pivot = (
            pd.pivot_table(
                df_starts,
                index='unique_start_id',
                columns='learning_aim_status_name',
                values='starts',
                fill_value=0,
            )
            .reset_index()
            .pipe(pd_utils.apply_snake_case_to_df)
            .rename(
                columns={
                    'completed': 'completions',
                    'continuing': 'continuing_learners',
                    'transfer_to_new_aim': 'transfers',
                    'withdrawn': 'withdrawls',
                }
            )
        )

        start_cols = ['starts']
        status_cols = [col for col in df_status_pivot.columns if col in self.metrics]

        dict_group_sets = {
            self.tlevel: self.tlevel_total_name,
            self.route: self.route_total_name,
            self.cohort: self.cohort_total_name,
        }

        df_core_starts = (
            df_starts.pipe(
                pd_utils.apply_grouping_sets, dict_group_sets=dict_group_sets
            )
            .merge(df_status_pivot, how='left', on='unique_start_id',)
            .assign(**{self.category: lambda df: df[self.category].astype('category')})
            .groupby(bar_and_cat_cols)[start_cols + status_cols]
            .sum()
            .reset_index()
            .assign(  # For creating rations within bars
                bar_total_starts=lambda df: df.groupby(self.bar_cols)[
                    'starts'
                ].transform(sum),
            )
            .assign(  # For ordering in to routes
                route_total_starts=lambda df: np.where(
                    df[self.tlevel] == self.tlevel_total_name, df['bar_total_starts'], 0
                )
            )
        )

        # Finally, I need to filter to remove the rows produced by groupby when T Level does not match the route
        # These occur because pandas is treating route as a category in the groupby (with arg observed=False)
        # This will produce a row with 0 starts for non-matches for T Level and route, which is
        # a desirable feature for Gender but not for route.
        df_core_starts = df_core_starts.loc[lambda df: df['bar_total_starts'] > 0]

        return df_core_starts

    def get_core_results(self, tlevel_data, bar_and_cat_cols, result_type='component'):
        """
        Get df of all results metrics (e.g. # results/% passs) grouped by
        bar cols (cols that define what is in an individual bar e.g. tlevel/route/cohort)
        and the category col (which defines what is being compared e.g. gender).

        Args:
            tlevel_data (tlevelData): Data structure object to get tlevel data.
            bar_and_cat_cols (list of strings): Cols the define a bar and the category being compared
            result_type (str, optional): Should we get results at 'component' or 'sub_component' level. Defaults to 'component'.

        Raises:
            ValueError: result_type must be 'component' or 'sub_component'

        Returns:
            df_core_results (pd.df): df of all results metrics grouped by bar cols and the cat col.
        """

        dict_group_sets = {
            self.tlevel: self.tlevel_total_name,
            self.route: self.route_total_name,
            self.cohort: self.cohort_total_name,
        }

        if result_type == 'component':
            df_results_raw = tlevel_data.get_component_grades()
            first_part = 'core'
        elif result_type == 'sub_component':
            df_results_raw = tlevel_data.get_sub_component_grades()
            first_part = 'core: exam'
        else:
            raise ValueError('result_type must be "component" or "sub_component"')

        df_results = df_results_raw.pipe(
            data_funcs.add_grade_categories, f'{result_type}_grade'
        ).assign(
            **{f'{result_type}_type': lambda df: df[f'{result_type}_type'].str.lower()}
        )

        df_results = (
            df_results.pipe(
                pd.pivot_table,
                index=[
                    'unique_learner_number',
                    self.tlevel,
                    self.route,
                    self.category,
                    self.cohort,
                ],
                columns=[f'{result_type}_type'],
                values=[
                    f'{result_type}_grade',
                    'pass',
                    'good_pass',
                    'grade_known',
                    'student_with_exam_attempt',
                ],
            )
            .pipe(pd_utils.remove_multilevel_columns)
            .reset_index()
        )

        if self.test_disclosure_control:
            df_results = df_results.sample(500)

        result_cols = [
            col
            for col in df_results.columns
            if (col in self.metrics)
            or ('grade_known' in col)  # grade_known used in pass rate calcs
        ]
        # For some reason this the groupby and sum breaks without this
        for c in result_cols:
            df_results[c] = df_results[c].fillna(0)

        df_core_results = (
            df_results.pipe(
                pd_utils.apply_grouping_sets, dict_group_sets=dict_group_sets
            )
            .groupby(bar_and_cat_cols)[result_cols]
            .sum()
            .reset_index()
        )

        df_core_results = df_core_results.assign(  # For creating rations within bars
            bar_total_attempts=lambda df: df.groupby(self.bar_cols)[
                f'student_with_exam_attempt_{first_part}'
            ].transform(sum),
        ).loc[lambda df: df['bar_total_attempts'] > 0]

        return df_core_results

    def disclosure_control_and_format_numbers(
        self, data, cols_to_exclude=None, **kwargs
    ):
        """Run disclosure_control_and_format_numbers from super class with different default args"""
        return super().disclosure_control_and_format_numbers(
            data, cols_to_exclude=cols_to_exclude, **kwargs
        )

    def get_core_data(self):
        """
        Get the core data-set used throughout dashboard.
        Combine starts and results metrics grouped by
        bar cols (cols that define what is in an individual bar e.g. tlevel/route/cohort)
        and the category col (which defines what is being compared e.g. gender).

        Returns:
            core_data (pd.df): core data-set used throughout dashboard
        """
        tlevel_data = tlevelData(remove_ofqual_prefix=True)
        bar_and_cat_cols = self.bar_cols + [self.category]

        df_starts = self.get_core_starts(tlevel_data, bar_and_cat_cols)

        df_component_grades = self.get_core_results(
            tlevel_data, bar_and_cat_cols, result_type='component'
        )

        df_sub_component_grades = self.get_core_results(
            tlevel_data, bar_and_cat_cols, result_type='sub_component'
        )

        df_core_starts = (
            df_starts.merge(df_component_grades, how='left', on=bar_and_cat_cols)
            .merge(df_sub_component_grades, how='left', on=bar_and_cat_cols)
            .pipe(
                data_funcs.create_programme_route_tlevel_bars,
                bar_name=self.y,
                bar_type=self.y_type_name,
            )
            .pipe(pd_utils.convert_academic_year_col_format)
            .pipe(
                data_funcs.sort_data_by_group_total,
                group_cols='route',
                sort_col='route_total_starts',
                other_sort_cols=[self.y_type_name, self.y, self.cohort, self.category],
                ascending=[False, True, True, False, True],
            )
            .pipe(pd_utils.calculate_ratios, self.ratio_definitions, as_pct=True,)
            .fillna(0)
        )

        ### Apply Disclosure control
        share_cols = ['share_of_starts_%']

        df_core_with_disclosure_control = df_core_starts.pipe(
            self.disclosure_control_and_format_numbers,
            cols_to_exclude=self.ratio_cols,
            supress_as_number=True,
            add_disclosure_control_flag=True,
            keep_edge_value=True,
        )

        ## For ratio cols use if num was disc controlled
        assign_disclosure_control_flags = {
            f'{col}_disclosure_control_flag': df_core_with_disclosure_control[
                f'{num}_disclosure_control_flag'
            ]
            for col, (num, den) in self.ratio_definitions.items()
        }

        df_core_with_disclosure_control = (
            df_core_with_disclosure_control.assign(**assign_disclosure_control_flags)
            # For share of starts, if less than 5 male starts then need hide female % and vice versa
            .assign(
                **{
                    'share_of_starts_%_disclosure_control_flag': lambda df: df.groupby(
                        self.bar_cols
                    )['share_of_starts_%_disclosure_control_flag'].transform(max)
                }
            )
            # Show hidden value if less 10
            .pipe(
                self.disclosure_control_and_format_numbers,
                cols_to_include=self.ratio_cols,
                supress_as_number=True,
                use_threshold_and_disclosure_control_flag=True,
                threshold=5,
                keep_edge_value=True,
            )
            # For share; hide value if greater than 95 to match
            .pipe(
                self.disclosure_control_and_format_numbers,
                cols_to_include=share_cols,
                supress_as_number=True,
                use_threshold_and_disclosure_control_flag=True,
                threshold=95,
                edge_value=100,
                keep_edge_value=True,
                operator='>',
            )
        )

        # Update names to be titles
        core_data = data_funcs.make_df_columns_titles(df_core_with_disclosure_control)

        init_variables = [
            self.y,
            self.category,
            self.route,
            self.initial_metric,
            self.cohort,
            self.y_name,
            self.y_type_name,
            self.metrics,
            self.metric_select_list,
            self.display_cols,
            self.ratio_cols,
            self.result_metric_types,
        ]

        renamed_init_variables = []
        for x in init_variables:
            if isinstance(x, list):
                y = data_funcs.make_col_names_title(x)
            else:
                y = data_funcs.make_col_name_title(x)
            renamed_init_variables.append(y)

        [
            self.y,
            self.category,
            self.route,
            self.initial_metric,
            self.cohort,
            self.y_name,
            self.y_type_name,
            self.metrics,
            self.metric_select_list,
            self.display_cols,
            self.ratio_cols,
            self.result_metric_types,
        ] = renamed_init_variables

        self.bar_cols = [self.route, self.y, self.cohort]

        return core_data

    def get_stacked_data(self, core_data):
        """
        Get Dataframe that is reformatted with
        - Each unique index, metric combination has a separate row
        - Columns as separate columns.
        - A new column containing the metric is created.
        - Disclosure control applied
        - And additional columns with a suffix (dc_suffix) which has human readable
          based disclosure control (e.g. will say "Less than 5").
          This will be used in the hover tool/tables.

        This is done as this format allows us to display the core_data within bokeh.

        Args:
            core_data (pd.df): Core grouped data

        Returns:
            stacked_data (pd.df): reformatted data ready for bokeh
        """

        index = self.bar_cols + [self.y_type_name]
        columns = [self.category]
        values = self.metrics
        dc_suffix = data_funcs.DISCLOSURE_CONTROL_SUFFIX

        data_to_sort_on = core_data[index].drop_duplicates().reset_index()

        # Stack numeric data
        stacked_data = data_funcs.convert_df_to_stacked_df(
            core_data, index, columns, values, var_name=self.metric_name
        )

        # Repeat, but do it with string based disclosure control.
        # This is used in hover tool/table
        stacked_tooltip_data = (
            core_data.pipe(
                dc.disclosure_control,
                supress_as_number=False,
                use_disclosure_control_flag=True,
                keep_edge_value=True,
            )
            .pipe(
                data_funcs.convert_df_to_stacked_df,
                index,
                columns,
                values,
                var_name=self.metric_name,
            )
            .rename(
                columns={
                    c: f'{c}_{dc_suffix}'
                    for c in stacked_data.columns
                    if ((c not in index) and (c != self.metric_name))
                }
            )
            .assign(
                metric_type=lambda df: np.where(
                    df[self.metric_name].isin(self.ratio_cols), 'percentage', 'number',
                )
            )
            .pipe(
                data_funcs.string_format_numbers,
                pct_col='metric_type',
                str_formatter='{:,.0f}',
            )
        )

        for cat in self.category_values:
            cat_disc = f'{cat}_disclosure_control'
            stacked_tooltip_data[cat_disc] = np.where(
                (stacked_tooltip_data['metric_type'] == 'percentage')
                & (stacked_tooltip_data[cat_disc] == 'Less than 5'),
                '-',
                stacked_tooltip_data[cat_disc],
            )

        # Merge numeric and 'string' based data together.
        stacked_data = (
            stacked_data.merge(
                stacked_tooltip_data, on=index + [self.metric_name], how='left'
            )
            .merge(data_to_sort_on, on=index, how='left')
            .sort_values('index')
            .drop(['index', 'metric_type'], axis=1)
        )

        return stacked_data

    def get_download_data(self, core_data):
        """DL data is same as core data with human-readable disclosure applied.
        Args:
            core_data (pd.df): Stacked data
        Returns:
            download_data (pd.df): Data that can be used by download feature

        """

        download_data = (
            core_data.pipe(dc.disclosure_control, use_disclosure_control_flag=True)
            .pipe(
                data_funcs.string_format_numbers,
                columns=self.ratio_cols,
                str_formatter='{:.1f}%',
            )
            .pipe(data_funcs.string_format_numbers, str_formatter='{:,.0f}')[
                self.display_cols
            ]
        )

        for col in self.ratio_definitions.keys():
            col = data_funcs.make_col_name_title(col)
            download_data[col] = download_data[col].replace('Less than 5', '-')

        return download_data

    def get_table_data(self, stacked_data):
        """Table data is same as stacked data with human-readable disclosure applied.
        Args:
            stacked_data (pd.df): Stacked data
        Returns:
            table_data (pd.df): Data for use in table
        """
        dc_suffix = data_funcs.DISCLOSURE_CONTROL_SUFFIX
        table_data = data_funcs.use_string_dc_columns_from_stacked_data(
            stacked_data, dc_suffix
        )
        table_data = table_data[
            [self.metric_name] + self.bar_cols + self.category_values
        ]

        return table_data

    def create_custom_title(self, title):
        """Create a text that can be updated by bokeh javascript
        Args:
            title (str): Initial plot name
        Returns:
            custom_title (str):
                A plot name that can be input in a widget javascript and will be updated.
        """
        custom_title = title.replace(
            self.initial_metric, '" + metric_select.value + "'
        ).replace(self.initial_cohort, '" + cohort_select.value + "')
        return custom_title

    def get_widgets(self, data, source, table_source, filters, plot):
        """
        Create user interaction widgets and Javascript call-backs that will
        update plot/table when a user interacts.

        Args:
            data (pd.df): Stacked data frame used for plots
            source (bokeh.ColumnDataSource): Bokeh source used for plot
            table_source (bokeh.ColumnDataSource): Bokeh source used for table
            filters (list of bokeh.filters): List of filters which are applied to data.
            plot (bokeh.plotting.figure): The bokeh plot

        Returns:
            list of bokeh.models: Bokeh widgets for use on page
        """

        metric_filter, cohort_filter, route_and_y_type_filter = filters

        metric_select = bm.Select(
            title=self.metric_name,
            value=self.initial_metric,
            options=self.metric_select_list,
        )

        cohort_select = bm.Select(
            title='Cohort:', value=self.initial_cohort, options=self.cohort_list,
        )

        custom_plot_title = self.create_custom_title(title=self.plot_title)
        custom_x_label = self.create_custom_title(title=self.x_label)

        route_list = self.calculate_unique_list(data, self.route)
        route_list.remove(self.route_total_name)
        route_select = bm.MultiChoice(
            value=route_list, options=route_list, title='Select Route:'
        )

        y_types_active_i = [
            i
            for i, value in enumerate(self.y_type_list)
            if value in self.y_types_active
        ]
        y_type_select = bm.CheckboxButtonGroup(
            labels=self.y_type_list, active=y_types_active_i,
        )

        callback = bm.CustomJS(
            args=dict(
                metric_select=metric_select,
                metric_filter=metric_filter,
                cohort=self.cohort,
                cohort_select=cohort_select,
                cohort_filter=cohort_filter,
                categories=self.category_values,
                y_type=self.y_type_name,
                y_type_select=y_type_select,
                y_type_list=self.y_type_list,
                y=self.y,
                route=self.route,
                route_select=route_select,
                route_total_name=self.route_total_name,
                route_and_y_type_filter=route_and_y_type_filter,
                plot_xaxis=plot.xaxis[0],
                plot_title=plot.title,
                plot_y_range=plot.y_range,
                source=source,
                table_source=table_source,
            ),
            code=f'''
                // Log what we are filtering to.
                console.log(
                    'Bokeh Log: Filter to metric = ', metric_select.value,
                    ', cohort = ', cohort_select.value,
                    ', routes = ', route_select.value
                )
                plot_xaxis.axis_label = "{custom_x_label}";
                plot_title.text = "{custom_plot_title}";

                // This section updates cohort/metric/gender on plot
                metric_filter.group = metric_select.value;
                cohort_filter.group = cohort_select.value;

                // Covert stupid indicies output to list of active values
                var active_y_types = []
                for (let j = 0; j < y_type_list.length; j++) {{
                    let y_type = y_type_list[j]
                    if (y_type_select.active.includes(Number(j))) {{
                        active_y_types.push(y_type)
                    }}
                }}

                // This section is to select routes and update y-axis
                // Hide categories on the y-axis if there is no starts in that cohort
                const indices = [] // List to store indicies of values to show
                const new_y_range = [] // List to store categories to show on y-axis
                for (let i = 0; i < source.get_length(); i++) {{
                    let route_value = source.data[route][i]
                    let y_value = source.data[y][i]
                    let y_type_value = source.data[y_type][i]
                    let cohort_value = source.data[cohort]
                    if (
                        (
                            route_select.value.includes(route_value)
                            ||
                            route_value == route_total_name
                        )
                        &&
                        active_y_types.includes(y_type_value)
                    ) {{
                        indices.push(i) // This index should be shown
                        let cohort_value = source.data[cohort][i]
                        let sum_value = 0;
                        for (let j = 0; j < categories.length; j++) {{
                            let cat = categories[j]
                            if(cohort_value == cohort_select.value) {{
                                sum_value = sum_value + source.data[cat][i]
                            }}
                        }}
                        // If sum value is greater than 1, then this needs to be added to y-axis
                        // Avoid duplication in new_y_range with 2nd condition
                        if ((sum_value > 0) && (!new_y_range.includes(y_value))) {{
                            new_y_range.push(y_value)
                        }}
                    }}
                }}
                route_and_y_type_filter.indices = indices // Filter based on indicies collected in loop
                new_y_range.reverse() // Reverse as hbar plots from bottom to top
                plot_y_range.factors = new_y_range // Update y_range

                source.change.emit()
                table_source.change.emit()
                ''',
        )
        metric_select.js_on_change('value', callback)
        route_select.js_on_change('value', callback)
        cohort_select.js_on_change('value', callback)
        y_type_select.js_on_change('active', callback)

        return metric_select, route_select, cohort_select, y_type_select

    def get_plot(self, source, data, view):
        """
        Build horizontal bar plot and set it up for the inital view.
        The interactions for this plot will be done in widgets.

        Args:
            source (bokeh.ColumnDataSource): The bokeh data source used by plot
            data (pd.df): stacked_data used to build plot
            view (bokeh.CDSView): A bokeh view is data with filters applied.

        Returns:
            bokeh.plotting.figure: A plot that can be shown on page.
        """

        self.plot_title = f'{self.initial_metric} by {self.category_name} : {self.data_guidance_text_short}'
        self.selector_text = f'(Cohort = {self.initial_cohort})'
        self.x_label = f'{self.initial_metric} {self.selector_text}'

        ## Encode in that not only certain y_types should be shown initially
        y_range = list(
            data.loc[lambda df: df[self.y_type_name].isin(self.y_types_active)][
                self.y
            ].unique()
        )

        plot = plot_funcs.plot_hbar_with_categories(
            source,
            data,
            self.y,
            self.y_name,
            self.category_values,
            self.initial_metric,
            title=self.plot_title,
            tools=self.tools,
            disclosure_control_suffix=data_funcs.DISCLOSURE_CONTROL_SUFFIX,
            metric_name=self.metric_name,
            view=view,
            total_bar_height=0.7,
            legend_outside=True,
            y_range=y_range,
        )

        plot.xaxis[0].ticker.desired_num_ticks = 11

        return plot

    def get_filters(self):
        """Get filters that can be applied to a source (a bokeh data-frame).
        The value of the filter can updated in a widget.

        Returns:
            list of bokeh.filters: Filters used in dashboard
        """

        metric_filter = bm.GroupFilter(
            column_name=self.metric_name, group=self.initial_metric
        )
        cohort_filter = bm.GroupFilter(
            column_name=self.cohort, group=self.cohort_total_name
        )

        route_and_y_type_filter = bm.IndexFilter()

        filters = [metric_filter, cohort_filter, route_and_y_type_filter]
        table_filters = [metric_filter, route_and_y_type_filter]

        return (filters, table_filters)

    def get_bokeh_elements(self):
        """
        Master function on all bokeh pages that will create all bokeh elements
        and then order them within the page.

        Returns:
            script, div: These outputs are used when creating the page.
        """

        ## Get data in different forms
        plot_data, download_data, table_data = self.get_data()

        ## Get sources for different components
        plot_source = self.get_source(plot_data)
        download_source = self.get_source(download_data)
        table_source = self.get_source(table_data)

        ## Get views
        filters, table_filters = self.get_filters()
        plot_view = self.get_view(plot_source, filters)
        table_view = self.get_view(table_source, table_filters)

        # Get Bokeh Components
        plot = self.get_plot(plot_source, plot_data, plot_view)
        (metric_select, route_select, cohort_select, y_type_select) = self.get_widgets(
            plot_data, plot_source, table_source, filters, plot,
        )

        filename = self.get_download_filename('gender_diversity')

        download_button = self.get_download_button(
            download_data, download_source, filename
        )

        table = self.get_table(
            table_source, table_data, view=table_view, width=1000, height=200,
        )

        metric_descriptions = self.create_metric_description_table(
            self.metrics + self.result_metric_types
        )

        # Set Bokeh Structure
        script, div = components(
            column(
                row(
                    column(metric_select, width=350),
                    self.blank_col(20),
                    column(cohort_select, width=150),
                    self.blank_col(20),
                    self.format_widget_with_title(
                        widget=y_type_select,
                        title='Show/Hide Aggregation Level',
                        width=250,
                    ),
                    self.blank_col(20),
                    column(
                        self.blank_row(18), row(download_button, width=150), width=150,
                    ),
                ),
                row(column(route_select, height=100, sizing_mode='stretch_width'),),
                row(plot, sizing_mode='stretch_width'),
                self.blank_row(15),
                row(table, sizing_mode='stretch_width'),
                self.blank_row(10),
                row(metric_descriptions, sizing_mode='stretch_width'),
                self.blank_row(5),
            ),
            wrap_script=False,
        )
        return script, div
