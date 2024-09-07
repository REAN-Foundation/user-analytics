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

        # Please note that we do not use user's login session Id to track this.
        # We simply track the first and last event times for each feature session per user.

        query = f"""
                -- Step 1: Get the first and last event times for each feature session per user
                WITH FeatureUsage AS (
                    SELECT
                        e.UserId,
                        e.EventCategory AS feature,                  -- The feature (EventCategory)
                        MIN(e.Timestamp) AS first_event_time,        -- First event timestamp (start of feature interaction)
                        MAX(e.Timestamp) AS last_event_time          -- Last event timestamp (end of feature interaction)
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        AND e.EventCategory = '{feature}'
                        AND e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                    GROUP BY e.UserId, e.EventCategory  -- Group by user, and feature
                ),

                -- Step 2: Calculate the duration for each feature session (in minutes)
                FeatureDurations AS (
                    SELECT
                        f.UserId,
                        f.feature,                                            -- The feature (EventCategory)
                        TIMESTAMPDIFF(MINUTE, f.first_event_time, f.last_event_time) AS duration_minutes -- Duration in minutes
                    FROM FeatureUsage f
                    WHERE f.first_event_time IS NOT NULL AND f.last_event_time IS NOT NULL  -- Ensure valid timestamps
                )

                -- Step 3: Calculate the average usage duration per feature
                SELECT
                    fd.feature,                                              -- The feature (EventCategory)
                    AVG(fd.duration_minutes) AS avg_duration_minutes         -- Average duration in minutes
                FROM FeatureDurations fd
                GROUP BY fd.feature                                          -- Group by feature
                ORDER BY avg_duration_minutes DESC;                          -- Order by longest average duration

        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return 0

@trace_span("service: analytics: feature engagement: get_feature_drop_off_points")
async def get_feature_drop_off_points(
    feature: str, tenant_id: UUID4|None, start_date: date, end_date: date, top_n: int):
    try:
        if not feature or len(feature) == 0:
            return None

        role_id = get_role_id()
        connector = get_analytics_db_connector()

        # We are identifying a feature by event category. For example, 'Medication' feature

        query = f"""
                -- Step 1: Track user event sequences within a feature (EventCategory)
                WITH UserEventFlow AS (
                    SELECT
                        e.UserId,
                        e.EventCategory,
                        e.EventName AS event_name,              -- Capture the event name (e.g., screen-entry, button-click, etc.)
                        e.Timestamp                             -- Timestamp to order events
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.EventCategory = '{feature}'           -- Filter for a specific feature/event category
                        AND e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                    ORDER BY e.UserId, e.Timestamp -- Order by user, and time
                ),

                -- Step 2: Identify the next event for each user within the feature
                NextEvent AS (
                    SELECT
                        f1.UserId,
                        f1.event_name AS current_event,                                                         -- Current event (e.g., 'screen-entry')
                        LEAD(f1.event_name) OVER (PARTITION BY f1.UserId ORDER BY f1.Timestamp) AS next_event   -- Next event in the sequence
                    FROM UserEventFlow f1
                ),

                -- Step 3: Calculate drop-off points and rates for each event within the feature
                DropOffs AS (
                    SELECT
                        ne.current_event,                       -- The event where we check for drop-offs
                        COUNT(ne.UserId) AS total_users,        -- Total users who interacted with the current event
                        SUM(CASE WHEN ne.next_event IS NULL THEN 1 ELSE 0 END) AS dropoff_count  -- Users who dropped off after the current event
                    FROM NextEvent ne
                    GROUP BY ne.current_event                  -- Group by the current event
                )

                -- Step 4: Calculate drop-off rate per event
                SELECT
                    d.current_event AS event_name,
                    d.dropoff_count,
                    d.total_users,
                    (d.dropoff_count / d.total_users) * 100 AS dropoff_rate  -- Drop-off rate in percentage
                FROM DropOffs d
                ORDER BY dropoff_rate DESC;                                  -- Order by the highest drop-off rate
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return 0

