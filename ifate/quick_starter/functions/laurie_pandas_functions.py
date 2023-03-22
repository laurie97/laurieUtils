"""
Functions to manipulate pandas dfs
"""
import os
import re
from typing import Set
from pathlib import Path
import pandas as pd
from IPython.core.display import display, HTML
from stringcase import snakecase # https://pypi.org/project/stringcase/

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import seaborn as sns


def display_full(df, force=False):
    """
    Run IPython.core.display.display on pandas df, except force jupyter to show all rows.
    If you want to run on more than 200 rows use force.

    Args:
    - df: pandas df
    - force: bool, If false this function will return an error if n_rows > 200
    """

    max_rows_before_force = 200 ## Constant of function.

    n_rows = df.shape[0]    

    if (n_rows > max_rows_before_force) and not force:
        print(f'This is {n_rows:,.0f} rows, which is more than {max_rows_before_force:,.0f}')
        print('Are you sure you want to display full?. If so, use the force option')
        return

    try:
        pd.set_option('display.max_rows', n_rows)
        display(df)
    except:
        print('Something went wrong with display')
    finally:
        pd.reset_option('display.max_rows')


def apply_snake_case_to_df(df_in):
    """
    Returns a data-frame with snake-case used in column names

    Arg:
    - df_in: pandas df that where columns use any naming convention.

    Returns:
    - df_snake: pandas df where columns follow snake case
    """

    snake_columns = [
        col.lower().replace(' ', '_') if col.isupper() else snakecase(col.replace(' ', '_'))
        for col in df_in.columns
    ]

    df_snake = df_in.copy()
    df_snake.columns = snake_columns
    return df_snake


def remove_multilevel_columns(df_in):
    """
    Replaces a multilevel column with a flat column
    Useful after a group by and agg

    Cols Before:      Cols After:
    starts            starts_mode  starts_mean 
    mode    mean

    Args:
    df_in, pandas df with a multi-level column

    Returns:
    df_out, pandas df with single-level columns seperated by '_'
    """
    
    df_out = df_in.copy()
    df_out.columns = ["_".join(col) for col in df_out.columns.ravel()]    
    return df_out


def get_lauries_table_styles():
    """
    Get a table style object that can be used to show pandas dfs
    in a more readable way using the style functionality.
    e.g.
        df.style.set_table_styles(lauries_table_styles)  

    More detail/ambition for this function
    https://pandas.pydata.org/pandas-docs/dev/user_guide/style.html#Table-Styles

    Returns:
        lauries_table_styles: list
    """

    lauries_table_styles = [
        {'selector': 'th',
         'props': [
                    ('background-color','rgb(230,230,230)'),
                    ('border', '0.9px black solid')
                    ]
        },
        {'selector': 'th:hover',
         'props': [
                    ('background-color','#dcecfc'),
                    ('border', '1px black solid')
                    ]
        },
        {'selector': 'td:hover',
         'props': [
                    ('border', '1px black solid')
                    ]
        },
        {'selector': 'tr',
        'props': [('background-color','white')]
        },
        {'selector': 'tr:hover',
        'props': [
                    ('background-color','#dcecfc')
                    ]
        },
        {'selector': 'td',
        'props': [('border', '0.75px black solid') ]
        }
    ]

    return lauries_table_styles


def agg_df_by_cols(
    df_in,
    groupby_cols,
    sum_cols=None,
    output_col_names=None,
    sort_by_cols=False,
    return_df = None,
    display_df = False,
    do_pct = True,
    do_total=True,
    total_name = 'Total',
    set_cols = None,
    output_set_name = 'set',
    do_set_total = False,
    set_total_name = 'Total'
):
    """
    Helper function to do a groupby and count or sum with some helpful features.
    
    Args:
        df_in: pandas df which will have group by applied to it
        groupby_cols: list (or str), name(s) of column(s) to group by on
        sum_cols: list (or str), name(s) of column(s) to sum over. If not set will do a count instead
        output_col_names: list (or str), name(s) of column(s) to output from agg. Must be same length as sum_cols
        sort_by_cols: bool, if True sort by groupby cols. If false sort by values (ascending)
        display_df: bool, if True display formatted df.
        return_df: bool, if True return result of group by. If None (default value), return_df is set to opposite of display_df.
        do_pct: bool, if True add percentage column based on count or sum_cols
        do_total: bool, if True will add a total column at end of groupby
        total_name: str, name of row that is result of total
        set_cols: list (or str), Columns that are included in the groupby, but a % will be calculated within each set
        set_total_name: str, name of row that will contain total over set
        output_set_name: str, name of set to be used in the output % name
        do_set_total: bool, Add total within each set
    
    Returns:
        If return_df = True
        - pandas df, result of groupby and count/sum.
        
    TO DO:
    - Add cumulative %
    """
    
    ## Allow for input of either str or list for certain columns
    if isinstance(groupby_cols,str):
        groupby_cols = [groupby_cols]
    if set_cols and isinstance(set_cols, str):
        set_cols = [set_cols]        
    if sum_cols and isinstance(sum_cols, str):
        sum_cols = [sum_cols]        
    if output_col_names and isinstance(output_col_names,str):
        output_col_names = [output_col_names]

    ## If return_df is not passed, make it opposite of display_df
    if return_df == None:
        return_df = bool(1 - display_df)
        
    ## Check values given make sense
    if return_df == False and display_df == False:
        raise ValueError('Either return_df or display_df should be True')        
    if sum_cols and output_col_names and len(output_col_names) != len(sum_cols):
        raise ValueError('If inputted Length of output_col_names should be the same as output_col_names')
    if do_set_total and not set_cols:
         raise ValueError('Cannot set do_set_total to True if no  set_cols are passed to function')

    df_to_group = df_in.copy()

    ## Trick to add total column to pandas after groupby
    if do_total:
        dict_assign_total = {col: total_name for col in groupby_cols}
        df_to_group = (
            pd.concat([df_to_group.assign(**dict_assign_total), df_to_group])  )  
    if set_cols and do_set_total:
        dict_assign_set_total = {col: set_total_name for col in set_cols}
        df_to_group = (
            pd.concat([df_to_group.assign(**dict_assign_set_total), df_to_group])  )
       
    ## Create Dictionary That Defines Aggregate Aggregate function
    if not sum_cols:
        df_to_group = df_to_group.assign(dummy = 1)
        sum_cols = ['dummy']
        if not output_col_names:
            output_col_names = ['rows']
    elif not output_col_names:
        output_col_names = sum_cols
    dict_agg = {output_col_name: (sum_col, 'sum')
                   for output_col_name, sum_col in zip(output_col_names, sum_cols)
               }
    
    if set_cols:
        set_and_groupby_cols = set_cols + groupby_cols
    else:
        set_and_groupby_cols = groupby_cols


    ## Do group by
    df_grouped = (
        df_to_group        
        .groupby(set_and_groupby_cols)
        .agg(**dict_agg)
        .reset_index()
    )

    ## Add percentage column.
    if not set_cols:
        filter_not_total = lambda df: df[groupby_cols[0]] != total_name ## Needs to be removed from denominator
    else:
        filter_not_total = lambda df: (df[groupby_cols[0]] != total_name) & (df[set_cols[0]] != total_name)
        df_grouped['set_total'] = df_grouped[groupby_cols[0]] == total_name

    if do_pct:
        ## If there are no set cols this becomes easy job of adding a pct]
        dict_pct ={}
        
        for output_col_name in output_col_names:
            dict_pct[f'pct_{output_col_name}'] = lambda df: (
                    100.0 * df[output_col_name] / 
                    df.loc[filter_not_total, output_col_name].sum() 
            )
        
        if set_cols:
                                    
            for output_col_name in output_col_names:
                dict_pct[f'pct_{output_col_name}_within_{output_set_name}'] = lambda df: (
                    100.0 * df[output_col_name] / 
                    df.groupby(['set_total'] + set_cols)[output_col_name].transform(sum)
                )

            ## Add these as they are useful for ordering df later
            for output_col_name in output_col_names:
                dict_pct[f'{output_col_name}_within_{output_set_name}'] = lambda df: (
                     df.groupby(['set_total'] + set_cols)[output_col_name].transform(sum)
                )
  
        df_grouped = df_grouped.assign(**dict_pct)

    set_sum_cols = []
    for output_col_name in output_col_names:
        set_sum_cols.append(f'{output_col_name}_within_{output_set_name}')
        
    ## Sort Columns in consistent way
    if sort_by_cols:
        sort_by_cols = set_and_groupby_cols
    elif set_cols:
        sort_by_cols =  set_sum_cols + output_col_names
    else:
        sort_by_cols = output_col_names

    ascending_sort_by_cols = [False if (col in output_col_names or col in set_sum_cols) else True for col in sort_by_cols ]
    df_grouped = df_grouped.sort_values(sort_by_cols, ascending=ascending_sort_by_cols)

    ## Drop Ugly cols needed for set groupings
    if set_cols:
        df_grouped = (
            df_grouped
            .drop('set_total',axis=1)
            .drop(set_sum_cols, axis = 1)
        )

    ## Index nicely
    df_grouped = df_grouped.reset_index(drop=True)
    
    # Display DF in pretty setup
    if display_df:
        dict_format = {}
        for key in dict_agg:
            dict_format[key] = '{:,.0f}'
        if do_pct:
            for key in dict_pct:
                if 'pct_' in key:
                    dict_format[key] = '{:,.1f}%'
                else:
                    dict_format[key] = '{:,.0f}'

        
        lauries_table_styles = get_lauries_table_styles()
        
        display(
            df_grouped
            .set_index(set_and_groupby_cols)
            .style
            .format(dict_format)
            .set_table_styles(lauries_table_styles)
        )
  
    if return_df:
        return df_grouped


def count_n_rows_per_id(data, id_cols):
    """
    Count # Rows per ID, where id is defined by a column/list of columns.
    Will show a summary to jupyter and return a df
    
    Args:
    - data: pandas df containing 1 or more rows per id
    - id_cols: str or list, column(s) that is an id

    Returns:
    - data_with_n_rows: pandas df of data with 'n_rows_per_id' added as a column
    """
    
    df_n_rows_per_id = data.groupby(id_cols).size().rename('n_rows_per_id').reset_index()
    df_n_rows_per_id['n_rows_per_id'] = df_n_rows_per_id['n_rows_per_id'].astype(str)
    agg_df_by_cols(df_n_rows_per_id, 'n_rows_per_id', display_df=True, do_total=False)
    df_n_rows_per_id['n_rows_per_id'] = df_n_rows_per_id['n_rows_per_id'].astype(int)

    data_with_n_rows_per_id = (
        data
        .merge(
            df_n_rows_per_id,
            on=id_cols,
            how='left',
        )
    )

    return data_with_n_rows_per_id


def find_most_recent_file(dir_path, pattern, extension=None):
    """
    Find the most recent file path containing a string pattern and a date in the file name.
    Date can be in format yyyy_mm_dd, yyyymmdd or yyyy_mm.
    The date in the file name is then used to find the most recent file.
    If two files match the pattern and have the same dates within them.
    return the most recently modified.

    Args:
    - dir_path; str or path, directory to recursively search
    - pattern; str, start pattern of file to search
    - extension; str (optional), file extension to look for

    Returns:
    - file_path, Path: Path to file
    """

    date_regex = r'(\d{8}|\d{4}_\d{2}_\d{2}|\d{4}_\d{2})'

    files = [Path(dir_path, rel_path) for rel_path in os.listdir(dir_path)]
    files = sorted(files, key=os.path.getmtime, reverse=True)

    most_recent_file_path = None
    most_recent_file_date = None

    for file_path in files:

        file_path_str = str(file_path)

        file_regex = fr'({pattern}.*{date_regex}.*|{date_regex}.*{pattern}.*)'
        if extension:
            file_regex = fr'{file_regex}\.{extension}'

        # Filter to only files that match pattern
        if not os.path.isfile(file_path):
            continue
        if not re.search(file_regex, file_path_str):
            continue

        # Get date from file path and check if it is now most recent
        file_date = re.search(date_regex, file_path_str).group()
        file_date = file_date.replace('_', '')
        if (file_date > str(most_recent_file_date)) or (most_recent_file_date is None):
            most_recent_file_path = file_path
            most_recent_file_date = file_date

    return most_recent_file_path
