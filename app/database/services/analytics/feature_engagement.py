from app.database.services.analytics.common import add_tenant_and_role_checks
from app.domain_types.schemas.analytics import AnalyticsFilters
from app.modules.data_sync.connectors import get_analytics_db_connector
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: analytics: feature engagement: get_feature_access_frequency")
async def get_feature_access_frequency(feature: str, filters: AnalyticsFilters):
    try:
        if not feature or len(feature) == 0:
            return None

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                DATE_FORMAT(e.Timestamp, '%Y-%m') AS month,
                COUNT(e.id) AS access_frequency
            FROM events e
            JOIN users user ON e.UserId = user.id
            WHERE
                e.EventCategory = '{feature}'
                AND e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY DATE_FORMAT(e.Timestamp, '%Y-%m')
            ORDER BY month ASC;
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print(e)
        return 0

@trace_span("service: analytics: feature engagement: get_feature_engagement_rate")
async def get_feature_engagement_rate(feature: str, filters: AnalyticsFilters):
    try:
        if not feature or len(feature) == 0:
            return None

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
                -- Step 1: Get the total number of active users per month
                WITH ActiveUsersPerMonth AS (
                    SELECT
                        DATE_FORMAT(e.Timestamp, '%Y-%m') AS month,  -- Extract year and month
                        COUNT(DISTINCT e.UserId) AS active_users     -- Count distinct active users per month
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                    GROUP BY DATE_FORMAT(e.Timestamp, '%Y-%m')
                ),

                -- Step 2: Get the number of unique users engaging with each feature per month
                FeatureUsersPerMonth AS (
                    SELECT
                        DATE_FORMAT(e.Timestamp, '%Y-%m') AS month,  -- Extract year and month
                        e.EventCategory AS feature,                  -- The feature (EventCategory)
                        COUNT(DISTINCT e.UserId) AS feature_users    -- Count distinct users engaging with the feature
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.EventCategory = '{feature}'
                        AND e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                    GROUP BY DATE_FORMAT(e.Timestamp, '%Y-%m'), e.EventCategory
                )

                -- Step 3: Calculate the feature engagement rate
                SELECT
                    fpm.month,
                    fpm.feature,
                    (fpm.feature_users / aupm.active_users) * 100 AS engagement_rate
                FROM FeatureUsersPerMonth fpm
                JOIN ActiveUsersPerMonth aupm ON fpm.month = aupm.month
                ORDER BY fpm.month DESC;
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print(e)
        return 0

@trace_span("service: analytics: feature engagement: get_feature_retention_rate_on_specific_days")
async def get_feature_retention_rate_on_specific_days(feature: str, filters: AnalyticsFilters):
    try:
        if not feature or len(feature) == 0:
            return None

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()
        query = f"""
                WITH registered_users AS (
                    SELECT user.id
                    FROM users as user
                    WHERE
                        __TENANT_ID_CHECK__
                        AND
                        __ROLE_ID_CHECK__
                ),

                retention_1d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users as user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 1 DAY)
                ),

                retention_3d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users as user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 3 DAY)
                ),

                retention_7d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 7 DAY)
                ),

                retention_10d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 10 DAY)
                ),

                retention_15d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 15 DAY)
                ),

                retention_20d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 20 DAY)
                ),

                retention_25d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 25 DAY)
                ),

                retention_30d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 30 DAY)
                )

                SELECT
                    (SELECT COUNT(*) FROM registered_users) AS active_users,

                    (SELECT COUNT(*) FROM retention_1d) AS returning_on_day_1,
                    (SELECT COUNT(*) FROM retention_1d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_1d_rate,

                    (SELECT COUNT(*) FROM retention_3d) AS returning_on_day_3,
                    (SELECT COUNT(*) FROM retention_3d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_3d_rate,

                    (SELECT COUNT(*) FROM retention_7d) AS returning_on_day_7,
                    (SELECT COUNT(*) FROM retention_7d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_7d_rate,

                    (SELECT COUNT(*) FROM retention_10d) AS returning_on_day_10,
                    (SELECT COUNT(*) FROM retention_10d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_10d_rate,

                    (SELECT COUNT(*) FROM retention_15d) AS returning_on_day_15,
                    (SELECT COUNT(*) FROM retention_15d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_15d_rate,

                    (SELECT COUNT(*) FROM retention_20d) AS returning_on_day_20,
                    (SELECT COUNT(*) FROM retention_20d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_20d_rate,

                    (SELECT COUNT(*) FROM retention_25d) AS returning_on_day_25,
                    (SELECT COUNT(*) FROM retention_25d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_25d_rate,

                    (SELECT COUNT(*) FROM retention_30d) AS returning_on_day_30,
                    (SELECT COUNT(*) FROM retention_30d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_30d_rate;
            """

        tenant_id_check = ""
        if tenant_id is not None:
            tenant_id_check = f"user.TenantId = '{tenant_id}'"
        role_id_check = ""
        if role_id is not None:
            role_id_check = f"user.RoleId = {role_id}"
        query = query.replace("__TENANT_ID_CHECK__", tenant_id_check)
        query = query.replace("__ROLE_ID_CHECK__", role_id_check)

        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)

        row = result[0]
        result_ = {
            "active_users": row['active_users'],
            "retention_on_specific_days": [
                {
                    "day": 1,
                    "returning_users": row['returning_on_day_1'],
                    "retention_rate": float(row['retention_1d_rate'])
                },
                {
                    "day": 3,
                    "returning_users": row['returning_on_day_3'],
                    "retention_rate": float(row['retention_3d_rate'])
                },
                {
                    "day": 7,
                    "returning_users": row['returning_on_day_7'],
                    "retention_rate": float(row['retention_7d_rate'])
                },
                {
                    "day": 10,
                    "returning_users": row['returning_on_day_10'],
                    "retention_rate": float(row['retention_10d_rate'])
                },
                {
                    "day": 15,
                    "returning_users": row['returning_on_day_15'],
                    "retention_rate": float(row['retention_15d_rate'])
                },
                {
                    "day": 20,
                    "returning_users": row['returning_on_day_20'],
                    "retention_rate": float(row['retention_20d_rate'])
                },
                {
                    "day": 25,
                    "returning_users": row['returning_on_day_25'],
                    "retention_rate": float(row['retention_25d_rate'])
                },
                {
                    "day": 30,
                    "returning_users": row['returning_on_day_30'],
                    "retention_rate": float(row['retention_30d_rate'])
                }
            ]
        }

        return result_

    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics: feature engagement: get_feature_retention_rate_in_specific_intervals")
async def get_feature_retention_rate_in_specific_intervals(feature: str, filters: AnalyticsFilters):

    try:
        if not feature or len(feature) == 0:
            return None

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
                WITH registered_users AS (
                    SELECT user.id
                    FROM users as user
                    WHERE
                        __TENANT_ID_CHECK__
                        AND
                        __ROLE_ID_CHECK__
                ),

                retention_1d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users as user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < DATE_ADD(DATE(user.RegistrationDate), INTERVAL 1 DAY)
                        AND DATE(e.Timestamp) >= DATE(user.RegistrationDate)
                ),

                retention_3d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users as user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < DATE_ADD(DATE(user.RegistrationDate), INTERVAL 3 DAY)
                        AND DATE(e.Timestamp) >= DATE_ADD(DATE(user.RegistrationDate), INTERVAL 1 DAY)
                ),

                retention_7d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < DATE_ADD(DATE(user.RegistrationDate), INTERVAL 7 DAY)
                        AND DATE(e.Timestamp) >= DATE_ADD(DATE(user.RegistrationDate), INTERVAL 3 DAY)
                ),

                retention_10d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < DATE_ADD(DATE(user.RegistrationDate), INTERVAL 10 DAY)
                        AND DATE(e.Timestamp) >= DATE_ADD(DATE(user.RegistrationDate), INTERVAL 7 DAY)
                ),

                retention_15d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < DATE_ADD(DATE(user.RegistrationDate), INTERVAL 15 DAY)
                        AND DATE(e.Timestamp) >= DATE_ADD(DATE(user.RegistrationDate), INTERVAL 10 DAY)
                ),

                retention_20d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < DATE_ADD(DATE(user.RegistrationDate), INTERVAL 20 DAY)
                        AND DATE(e.Timestamp) >= DATE_ADD(DATE(user.RegistrationDate), INTERVAL 15 DAY)
                ),

                retention_25d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < DATE_ADD(DATE(user.RegistrationDate), INTERVAL 25 DAY)
                        AND DATE(e.Timestamp) >= DATE_ADD(DATE(user.RegistrationDate), INTERVAL 20 DAY)
                ),

                retention_30d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.EventCategory = '{feature}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < DATE_ADD(DATE(user.RegistrationDate), INTERVAL 30 DAY)
                        AND DATE(e.Timestamp) >= DATE_ADD(DATE(user.RegistrationDate), INTERVAL 25 DAY)
                )

                SELECT
                    (SELECT COUNT(*) FROM registered_users) AS active_users,

                    (SELECT COUNT(*) FROM retention_1d) AS returning_before_day_1,
                    (SELECT COUNT(*) FROM retention_1d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_1d_rate,

                    (SELECT COUNT(*) FROM retention_3d) AS returning_between_day_1_and_day_3,
                    (SELECT COUNT(*) FROM retention_3d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_3d_rate,

                    (SELECT COUNT(*) FROM retention_7d) AS returning_between_day_3_and_day_7,
                    (SELECT COUNT(*) FROM retention_7d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_7d_rate,

                    (SELECT COUNT(*) FROM retention_10d) AS returning_between_day_7_and_day_10,
                    (SELECT COUNT(*) FROM retention_10d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_10d_rate,

                    (SELECT COUNT(*) FROM retention_15d) AS returning_between_day_10_and_day_15,
                    (SELECT COUNT(*) FROM retention_15d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_15d_rate,

                    (SELECT COUNT(*) FROM retention_20d) returning_between_day_15_and_day_20,
                    (SELECT COUNT(*) FROM retention_20d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_20d_rate,

                    (SELECT COUNT(*) FROM retention_25d) AS returning_between_day_20_and_day_25,
                    (SELECT COUNT(*) FROM retention_25d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_25d_rate,

                    (SELECT COUNT(*) FROM retention_30d) AS returning_between_day_25_and_day_30,
                    (SELECT COUNT(*) FROM retention_30d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_30d_rate;
            """

        tenant_id_check = ""
        if tenant_id is not None:
            tenant_id_check = f"user.TenantId = '{tenant_id}'"
        role_id_check = ""
        if role_id is not None:
            role_id_check = f"user.RoleId = {role_id}"
        query = query.replace("__TENANT_ID_CHECK__", tenant_id_check)
        query = query.replace("__ROLE_ID_CHECK__", role_id_check)

        result = connector.execute_read_query(query)

        row = result[0]
        result_ = {
            "active_users": row['active_users'],
            "retention_in_specific_interval": [
                {
                    "interval": "1d",
                    "returning_users": row['returning_before_day_1'],
                    "retention_rate": float(row['retention_1d_rate'])
                },
                {
                    "interval": "3d",
                    "returning_users": row['returning_between_day_1_and_day_3'],
                    "retention_rate": float(row['retention_3d_rate'])
                },
                {
                    "interval": "7d",
                    "returning_users": row['returning_between_day_3_and_day_7'],
                    "retention_rate": float(row['retention_7d_rate'])
                },
                {
                    "interval": "10d",
                    "returning_users": row['returning_between_day_7_and_day_10'],
                    "retention_rate": float(row['retention_10d_rate'])
                },
                {
                    "interval": "15d",
                    "returning_users": row['returning_between_day_10_and_day_15'],
                    "retention_rate": float(row['retention_15d_rate'])
                },
                {
                    "interval": "20d",
                    "returning_users": row['returning_between_day_15_and_day_20'],
                    "retention_rate": float(row['retention_20d_rate'])
                },
                {
                    "interval": "25d",
                    "returning_users": row['returning_between_day_20_and_day_25'],
                    "retention_rate": float(row['retention_25d_rate'])
                },
                {
                    "interval": "30d",
                    "returning_users": row['returning_between_day_25_and_day_30'],
                    "retention_rate": float(row['retention_30d_rate'])
                }
            ]
        }

        return result_

    except Exception as e:
        print(e)
        return []

# The first and last events recorded for a user are considered as
# the start and end of the user's engagement with the feature.
@trace_span("service: analytics: feature engagement: get_feature_average_usage_duration_minutes")
async def get_feature_average_usage_duration_minutes(feature: str, filters: AnalyticsFilters):
    try:
        if not feature or len(feature) == 0:
            return None

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

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
async def get_feature_drop_off_points(feature: str, filters: AnalyticsFilters):
    try:
        if not feature or len(feature) == 0:
            return None

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

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
