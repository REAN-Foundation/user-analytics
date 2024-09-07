from datetime import date
from pydantic import UUID4
from app.database.services.analytics.common import add_tenant_and_role_checks, get_role_id, tenant_check
from app.domain_types.enums.event_types import EventType
from app.modules.data_sync.connectors import get_analytics_db_connector
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: analytics: feature engagement: get_feature_access_frequency")
async def get_feature_access_frequency(feature: str, tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
        if not feature or len(feature) == 0:
            return None

        role_id = get_role_id()
        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                DATE(e.Timestamp) AS activity_date, COUNT(DISTINCT e.UserId) AS daily_active_users
            FROM events e
            JOIN users as user ON e.UserId = user.id
            WHERE
                e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY DATE(e.Timestamp)
            ORDER BY activity_date;
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        result_ = []
        for row in result:
            result_.append({
                "activity_date": str(row['activity_date']),
                "daily_active_users": row['daily_active_users']
            })
        return result_
    except Exception as e:
        print(e)
        return 0

@trace_span("service: analytics: feature engagement: get_feature_engagement_rate")
async def get_feature_engagement_rate(feature: str, tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
        if not feature or len(feature) == 0:
            return None

        role_id = get_role_id()
        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                e.UserId, COUNT(e.UserId) AS engagement_count
            FROM events e
            JOIN users as user ON e.UserId = user.id
            WHERE
                e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                AND e.EventName = '{feature}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY e.UserId;
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return 0

@trace_span("service: analytics: feature engagement: get_feature_retention_rate_on_specific_days")
async def get_feature_retention_rate_on_specific_days(feature: str, tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
        if not feature or len(feature) == 0:
            return None

        role_id = get_role_id()
        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                e.UserId, COUNT(e.UserId) AS engagement_count
            FROM events e
            JOIN users as user ON e.UserId = user.id
            WHERE
                e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                AND e.EventName = '{feature}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY e.UserId;
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return 0

@trace_span("service: analytics: feature engagement: get_feature_retention_rate_in_specific_intervals")
async def get_feature_retention_rate_in_specific_intervals(feature: str, tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
        if not feature or len(feature) == 0:
            return None

        role_id = get_role_id()
        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                e.UserId, COUNT(e.UserId) AS engagement_count
            FROM events e
            JOIN users as user ON e.UserId = user.id
            WHERE
                e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                AND e.EventName = '{feature}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY e.UserId;
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return 0


# The first and last events recorded for a user are considered as
# the start and end of the user's engagement with the feature.
@trace_span("service: analytics: feature engagement: get_feature_average_usage_duration_minutes")
async def get_feature_average_usage_duration_minutes(
    feature: str, tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
        if not feature or len(feature) == 0:
            return None

        role_id = get_role_id()
        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                e.UserId, COUNT(e.UserId) AS engagement_count
            FROM events e
            JOIN users as user ON e.UserId = user.id
            WHERE
                e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                AND e.EventName = '{feature}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY e.UserId;
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return 0

@trace_span("service: analytics: feature engagement: get_feature_drop_off_points_top_n")
async def get_feature_drop_off_points_top_n(
    feature: str, tenant_id: UUID4|None, start_date: date, end_date: date, top_n: int):
    try:
        if not feature or len(feature) == 0:
            return None

        role_id = get_role_id()
        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                e.UserId, COUNT(e.UserId) AS engagement_count
            FROM events e
            JOIN users as user ON e.UserId = user.id
            WHERE
                e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                AND e.EventName = '{feature}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY e.UserId;
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return 0

