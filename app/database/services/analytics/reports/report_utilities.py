
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from tabulate import tabulate

###############################################################################

def save_figure(
        fig: plt.Figure,
        name: str
    ):
    fig.savefig(f'./basic_statistics/{name}.png', dpi=300, bbox_inches='tight')
    plt.close(fig)

def plot_bar_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        x_label: str,
        y_label: str,
        palette: str,
        file_name: str,
        rotation: int = 45
    ):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=x_col, y=y_col, data=df, palette=palette, ax=ax, legend=False)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.tick_params(axis='x', rotation=rotation)
    save_figure(fig, file_name)


def plot_pie_chart(
        df: pd.DataFrame,
        value_col: str,
        label_col: str,
        title: str,
        palette: str,
        file_name: str
    ):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(df[value_col], labels=df[label_col], autopct='%1.1f%%', colors=sns.color_palette(palette))
    ax.set_title(title)
    save_figure(fig, file_name)


def plot_line_chart(
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str,
        x_label: str,
        y_label: str,
        palette: str,
        file_name: str,
        rotation: int = 45
    ):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x=x_col, y=y_col, data=df, palette=palette, ax=ax, legend=False)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    save_figure(fig, file_name)

###############################################################################

def reindex_dataframe_to_all_dates(
        df: pd.DataFrame,
        date_col: str,
        fill_col: str,
        freq: str,
        date_format: str = '%Y-%m-%d',
        fill_value: int = 0
    ) -> pd.DataFrame:
    df[date_col] = pd.to_datetime(df[date_col], format=date_format, errors='coerce')  # Handle invalid date formats
    start_date = df[date_col].min()
    end_date = df[date_col].max()
    all_dates = pd.date_range(start=start_date, end=end_date, freq=freq)
    all_dates_df = pd.DataFrame({date_col: all_dates})
    df_reindexed = pd.merge(all_dates_df, df, on=date_col, how='left').fillna({fill_col: fill_value})
    return df_reindexed

###############################################################################
