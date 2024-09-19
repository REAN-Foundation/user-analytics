
from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from tabulate import tabulate

###############################################################################

def save_figure(
        figure: plt.Figure,
        name: str
    ):
    image = f'{name}.png'
    figure.savefig(image, dpi=300, bbox_inches='tight')
    plt.close(figure)

def plot_bar_chart(
        data_frame: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str,
        x_label: str,
        y_label: str,
        color_palette: str,
        file_path: str,
        rotation: int = 45,
        show_every_nth: int = 5
    ):
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        x=x_column,
        y=y_column,
        data=data_frame,
        palette=sns.color_palette("Spectral"), #sns.husl_palette(as_cmap=True),#
        ax=ax,
        legend=False)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.tick_params(axis='x', rotation=rotation)
    ax.xaxis.set_major_locator(plt.MaxNLocator(show_every_nth))
    save_figure(fig, file_path)

def plot_pie_chart(
        data_frame: pd.DataFrame,
        value_column: str,
        label_column: str,
        title: str,
        color_palette: str,
        file_path: str
    ):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        data_frame[value_column],
        labels=data_frame[label_column],
        wedgeprops=dict(width=0.5),
        autopct='%1.1f%%',
        colors=sns.color_palette(color_palette))
    ax.set_title(title)
    save_figure(fig, file_path)

def plot_line_chart(
        data_frame: pd.DataFrame,
        x_column: str,
        y_column: str,
        title: str,
        x_label: str,
        y_label: str,
        color_palette: str,
        file_name: str,
        rotation: int = 45
    ):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(
        x=x_column,
        y=y_column,
        data=data_frame,
        palette=color_palette,
        ax=ax,
        legend=False)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    save_figure(fig, file_name)

###############################################################################

def reindex_dataframe_to_all_dates(
        data_frame: pd.DataFrame,
        date_column: str,
        fill_column: str,
        frequency: str,
        date_format: str = '%Y-%m-%d',
        fill_value: int = 0
    ) -> pd.DataFrame:
    data_frame[date_column] = pd.to_datetime(data_frame[date_column], format=date_format, errors='coerce')  # Handle invalid date formats
    start_date   = data_frame[date_column].min()
    end_date     = data_frame[date_column].max()
    all_dates    = pd.date_range(start=start_date, end=end_date, freq=frequency)
    all_dates_df = pd.DataFrame({date_column: all_dates})
    df_reindexed = pd.merge(all_dates_df, data_frame, on=date_column, how='left').fillna({fill_column: fill_value})
    df_reindexed[date_column] = df_reindexed[date_column].dt.strftime(date_format)
    return df_reindexed

###############################################################################

def write_data_to_excel(
    data_frame: pd.DataFrame, 
    sheet_name: str, 
    start_row: int, 
    start_col: int, 
    writer: pd.ExcelWriter, 
    title: str, 
    rename_columns: dict[str, str] = None
) -> pd.DataFrame:
    title_format = writer.book.add_format({'bold': True, 'font_size': 14, 'align': 'left'})
    data_format = writer.book.add_format({'align': 'left'})
    header_format = writer.book.add_format({'border': 0, 'bold': True})

    worksheet = writer.sheets[sheet_name]
    worksheet.write(start_row - 2, start_col, title, title_format)
    
    if rename_columns:
        data_frame.rename(columns=rename_columns, inplace=True)

    data_frame.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row, startcol=start_col)
    
    for i, col in enumerate(data_frame.columns):
        worksheet.write(start_row, start_col + i, col, header_format)
        
    for i, col in enumerate(data_frame.columns):
        max_len = max(data_frame[col].astype(str).map(len).max(), len(col))
        worksheet.set_column(start_col + i, start_col + i, max_len, data_format)
    
    return data_frame

def create_chart(
    workbook, 
    chart_type: str, 
    series_name: str, 
    sheet_name: str, 
    start_row: int, 
    start_col: int, 
    df_len: int, 
    value_col: int, 
    x_axis: str = '', 
    y_axis: str = ''
):
    chart = workbook.add_chart({'type': chart_type})
    chart.add_series({
        'name': series_name,
        'categories': [sheet_name, start_row + 1, start_col, start_row + df_len, start_col],
        'values': [sheet_name, start_row + 1, value_col, start_row + df_len, value_col],
    })
    chart.set_title({'name': f'{series_name}'})
    
    if chart_type != 'pie':
        chart.set_x_axis({
            'name': x_axis,
            'major_gridlines': {
                'visible': True,
                'line': {'color': '#CCCCCC', 'dash_type': 'dot', 'transparency': 0.8}
            }
        })
        chart.set_y_axis({
            'name': y_axis,
            'major_gridlines': {
                'visible': True,
                'line': {'color': '#CCCCCC', 'dash_type': 'dot', 'transparency': 0.8}
            }
        })
        chart.set_legend({'none': True})
    
    if chart_type == 'pie':
        chart.set_legend({
            'position': 'right',
            'font': {'bold': True, 'size': 10}
        })
    
    return chart

def reindex_dataframe_to_all_missing_dates(
    data_frame: pd.DataFrame,
    date_col: Optional[str] = None,
    fill_col: str = '',
    frequency: str = 'month',
    start_date_col: Optional[str] = None,
    end_date_col: Optional[str] = None,
    fill_value: float = 0.0,
    date_format: Optional[str] = None
) -> pd.DataFrame:

    if date_format is None:
        if frequency == 'month':
            date_format = '%Y-%m'
        elif frequency == 'daily':
            date_format = '%Y-%m-%d'
        elif frequency == 'weekly':
            date_format = '%Y-%m-%d'

    if frequency == 'weekly' and start_date_col and end_date_col:
        data_frame[start_date_col] = pd.to_datetime(data_frame[start_date_col], format=date_format)
        data_frame[end_date_col] = pd.to_datetime(data_frame[end_date_col], format=date_format)
        min_date = data_frame[start_date_col].min()
        max_date = data_frame[start_date_col].max()
        all_weeks_start = pd.date_range(start=min_date, end=max_date, freq='W-MON')
        all_weeks_end = all_weeks_start + pd.DateOffset(days=6) 

        all_weeks_df = pd.DataFrame({
            start_date_col: all_weeks_start,
            end_date_col: all_weeks_end
        })

        df_reindexed = pd.merge(all_weeks_df, data_frame, on=[start_date_col, end_date_col], how='left').fillna({fill_col: fill_value})
        df_reindexed[start_date_col] = df_reindexed[start_date_col].dt.strftime(date_format)
        df_reindexed[end_date_col] = df_reindexed[end_date_col].dt.strftime(date_format)
    
    else:
        data_frame[date_col] = pd.to_datetime(data_frame[date_col], format=date_format)
        if frequency == 'month':
            all_dates = pd.date_range(start=data_frame[date_col].min(), end=data_frame[date_col].max(), freq='MS')  # Monthly frequency
        elif frequency == 'daily':
            all_dates = pd.date_range(start=data_frame[date_col].min(), end=data_frame[date_col].max(), freq='D')   # Daily frequency
        else:
            raise ValueError("Invalid frequency. Use 'month', 'daily', or 'weekly'.")
        
        all_dates_df = pd.DataFrame({date_col: all_dates})

        df_reindexed = pd.merge(all_dates_df, data_frame, on=date_col, how='left').fillna({fill_col: fill_value})
        df_reindexed[date_col] = df_reindexed[date_col].dt.strftime(date_format)

    return df_reindexed
