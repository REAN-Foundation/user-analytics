
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
