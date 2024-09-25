from typing import List
import pandas as pd

from app.database.services.analytics.reports.report_utilities import add_table_to_markdown, reindex_dataframe_to_all_dates
from app.domain_types.schemas.analytics import EngagementMetrics, FeatureEngagementMetrics

def generate_all_feature_engagement_markdown(
        feature_engagements: List[FeatureEngagementMetrics]) -> str:
    all_feature_engagement_str = ""
    for feature in feature_engagements:
        all_feature_engagement_str += feature_metrics_markdown(feature)
    return all_feature_engagement_str

def feature_metrics_markdown(feature: FeatureEngagementMetrics) -> str:
    image_width = 1300
    access_frequency_table = ""
    access_frequency_chart_str = ""
    engagement_rate_table = ""
    engagement_rate_chart_str = ""
    retention_in_specific_days_table = ""
    retention_in_specific_days_chart_str = ""
    retention_in_specific_intervals_table = ""
    retention_in_specific_intervals_chart_str = ""
    
    feature_name = feature.Feature
    feature_name_ = feature_name.replace("-", " ")
    feature_name_title = feature_name_.title()
    
    if len(feature.AccessFrequency) > 0:
        access_frequency_df = pd.DataFrame(feature.AccessFrequency)
        access_frequency_df = reindex_dataframe_to_all_dates(
            data_frame  = access_frequency_df,
            date_column = 'month',
            fill_column = 'access_frequency',
            frequency   = 'MS',
            date_format = '%Y-%m'
        )
        access_frequency_chart_str =  f"""<img src="./{feature_name}_access_frequency_by_month.png" width="{image_width}">"""
        access_frequency_table = add_table_to_markdown(
           data_frame = access_frequency_df, 
           rename_columns = {'month': 'Month', 'access_frequency': 'Access Frequency'}
        )
    else:
        access_frequency_table = "Data Not Available" 
        
    if len(feature.EngagementRate) > 0:
        engagement_rate_df = pd.DataFrame(feature.EngagementRate)
        engagement_rate_df = reindex_dataframe_to_all_dates(
            data_frame  = engagement_rate_df,
            date_column = 'month',
            fill_column = 'engagement_rate',
            frequency   = 'MS',
            date_format = '%Y-%m'
        )
        engagement_rate_df['engagement_rate'] = engagement_rate_df['engagement_rate'].astype(float)
        engagement_rate_chart_str= f"""<img src="./{feature_name}_engagement_rate_by_month.png" width="{image_width}">"""
        engagement_rate_table= add_table_to_markdown(
            data_frame = engagement_rate_df,
            rename_columns = {'month': 'Month', 'engagement_rate': 'Engagement Rate (%)'}
        )  
    else:
        engagement_rate_table = "Data Not Available" 
        
    retention_on_specific_days = feature.RetentionRateOnSpecificDays['retention_on_specific_days']
    if len(retention_on_specific_days) > 0:
        retention_on_days_df = pd.DataFrame(retention_on_specific_days)
        retention_in_specific_days_chart_str = f"""<img src="./{feature_name}_retention_on_specific_days.png" width="{image_width}">"""
        retention_in_specific_days_table = add_table_to_markdown(
            data_frame = retention_on_days_df,
            rename_columns = {'day': 'Day', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'}
        )   
    else:
        retention_in_specific_days_table = "Data Not Available" 

    retention_in_specific_intervals = feature.RetentionRateInSpecificIntervals['retention_in_specific_interval']
    if len(retention_in_specific_intervals) > 0:
        retention_intervals_df = pd.DataFrame(retention_in_specific_intervals)
        retention_in_specific_intervals_chart_str= f"""<img src="./{feature_name}_retention_in_specific_intervals.png" width="{image_width}">"""
        retention_in_specific_intervals_table= add_table_to_markdown(
            data_frame = retention_intervals_df,
            rename_columns = {'interval': 'Interval', 'returning_users': 'Returning Users', 'retention_rate': 'Retention Rate'},
        )
    else:
        retention_in_specific_intervals_table = "Data Not Available" 
        
    drop_off_points = feature.DropOffPoints
         
    if len(drop_off_points) > 0:
        drop_off_points_df = pd.DataFrame(drop_off_points)
        drop_off_points_df['dropoff_rate'] = pd.to_numeric(drop_off_points_df['dropoff_rate'], errors='coerce')
        drop_off_points_df['dropoff_count'] = pd.to_numeric(drop_off_points_df['dropoff_count'], errors='coerce')
        drop_off_points_table = add_table_to_markdown(
            data_frame = drop_off_points_df,
            rename_columns = {'event_name': 'Event Name', 'dropoff_count':'Dropoff Count','total_users':'Total Users', 'dropoff_rate': 'Dropoff Rate'}
        )
    else:
        drop_off_points_table = "Data Not Available" 
        
    feature_engagement_str = f"""
### {feature_name_title} Engagement Metrics

#### Monthly {feature_name_title} Access Frequency
{access_frequency_chart_str}\n
{access_frequency_table}\n

#### {feature_name_title} Feature Engagement Rate
{engagement_rate_chart_str}\n
{engagement_rate_table}\n

#### {feature_name_title} Feature Retention Rate on Specific Days
{retention_in_specific_days_chart_str}\n
{retention_in_specific_days_table}\n

#### {feature_name_title} Feature Retention during Specific Intervals
{retention_in_specific_intervals_chart_str}\n
{retention_in_specific_intervals_table}\n

#### {feature_name_title} Feature Drop-Off Points
{drop_off_points_table}\n
"""
    return feature_engagement_str

def generate_engagement_metrics_table_content(metrics: EngagementMetrics) -> str:
    all_features_table_content = '' 
    for feature in metrics.FeatureMetrics:
        feature_name = feature.Feature
        feature_name_ = feature_name.replace("-", " ")
        feature_name_title = feature_name_.title()
        feature_table_content = f"""
  - [{feature_name_title} Engagement Metrics](#{feature_name}-engagement-metrics)
    - [Monthly {feature_name_title} Access Frequency](#monthly-{feature_name}-access-frequency)
    - [Monthly Average {feature_name_title} Usage Duration](#monthly-average-{feature_name}-usage-duration)
    - [{feature_name_title} Feature Engagement Rate](#{feature_name}-feature-engagement-rate)
    - [{feature_name_title} Feature Retention Rate on specific days](#{feature_name}-feature-retention-rate-on-specific-days)
    - [{feature_name_title} Feature Retention during specific intervals](#{feature_name}-feature-retention-during-specific-intervals)
    - [{feature_name_title} Feature Drop-Off Points](#{feature_name}-feature-drop-off-points)
"""
        all_features_table_content += feature_table_content
    
    return all_features_table_content
