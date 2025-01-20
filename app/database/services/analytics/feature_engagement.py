from app.common.utils import print_exception
from app.database.services.analytics.common import add_common_checks
from app.domain_types.schemas.analytics import AnalyticsFilters
from app.modules.data_sync.connectors import get_analytics_db_connector, get_reancare_db_connector
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
                __CHECKS__
            GROUP BY DATE_FORMAT(e.Timestamp, '%Y-%m')
            ORDER BY month ASC;
        """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print_exception(e)
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
                        __CHECKS__
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
                        __CHECKS__
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

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print_exception(e)
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
                    __CHECKS__
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

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "WHERE " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        row = result[0]
        result_ = {
            "active_users": row['active_users'],
            "retention_on_specific_days": [
                {
                    "day": 1,
                    "returning_users": row['returning_on_day_1'],
                    "retention_rate": float(row['retention_1d_rate']) if row['retention_1d_rate'] != None else 0.0
                },
                {
                    "day": 3,
                    "returning_users": row['returning_on_day_3'],
                    "retention_rate": float(row['retention_3d_rate']) if row['retention_3d_rate'] != None else 0.0
                },
                {
                    "day": 7,
                    "returning_users": row['returning_on_day_7'],
                    "retention_rate": float(row['retention_7d_rate']) if row['retention_7d_rate'] != None else 0.0
                },
                {
                    "day": 10,
                    "returning_users": row['returning_on_day_10'],
                    "retention_rate": float(row['retention_10d_rate']) if row['retention_10d_rate'] != None else 0.0
                },
                {
                    "day": 15,
                    "returning_users": row['returning_on_day_15'],
                    "retention_rate": float(row['retention_15d_rate']) if row['retention_15d_rate'] != None else 0.0
                },
                {
                    "day": 20,
                    "returning_users": row['returning_on_day_20'],
                    "retention_rate": float(row['retention_20d_rate']) if row['retention_20d_rate'] != None else 0.0
                },
                {
                    "day": 25,
                    "returning_users": row['returning_on_day_25'],
                    "retention_rate": float(row['retention_25d_rate']) if row['retention_25d_rate'] != None else 0.0
                },
                {
                    "day": 30,
                    "returning_users": row['returning_on_day_30'],
                    "retention_rate": float(row['retention_30d_rate']) if row['retention_30d_rate'] != None else 0.0
                }
            ]
        }

        return result_

    except Exception as e:
        print_exception(e)
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
                    __CHECKS__
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

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "WHERE " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        row = result[0]
        result_ = {
            "active_users": row['active_users'],
            "retention_in_specific_interval": [
                {
                    "interval": "0d-1d",
                    "returning_users": row['returning_before_day_1'],
                    "retention_rate": float(row['retention_1d_rate']) if row['retention_1d_rate'] != None else 0.0
                },
                {
                    "interval": "1d-3d",
                    "returning_users": row['returning_between_day_1_and_day_3'],
                    "retention_rate": float(row['retention_3d_rate']) if row['retention_3d_rate'] != None else 0.0
                },
                {
                    "interval": "3d-7d",
                    "returning_users": row['returning_between_day_3_and_day_7'],
                    "retention_rate": float(row['retention_7d_rate']) if row['retention_7d_rate'] != None else 0.0
                },
                {
                    "interval": "7d-10d",
                    "returning_users": row['returning_between_day_7_and_day_10'],
                    "retention_rate": float(row['retention_10d_rate']) if row['retention_10d_rate'] != None else 0.0
                },
                {
                    "interval": "10d-15d",
                    "returning_users": row['returning_between_day_10_and_day_15'],
                    "retention_rate": float(row['retention_15d_rate']) if row['retention_15d_rate'] != None else 0.0
                },
                {
                    "interval": "15d-20d",
                    "returning_users": row['returning_between_day_15_and_day_20'],
                    "retention_rate": float(row['retention_20d_rate']) if row['retention_20d_rate'] != None else 0.0
                },
                {
                    "interval": "20d-25d",
                    "returning_users": row['returning_between_day_20_and_day_25'],
                    "retention_rate": float(row['retention_25d_rate']) if row['retention_25d_rate'] != None else 0.0
                },
                {
                    "interval": "25d-30d",
                    "returning_users": row['returning_between_day_25_and_day_30'],
                    "retention_rate": float(row['retention_30d_rate']) if row['retention_30d_rate'] != None else 0.0
                }
            ]
        }

        return result_

    except Exception as e:
        print_exception(e)
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
                        e.EventCategory = '{feature}'
                        AND e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        __CHECKS__
                    GROUP BY e.UserId, e.EventCategory  -- Group by user, and feature
                ),

                -- Step 2: Calculate the duration for each feature session (in minutes)
                FeatureDurations AS (
                    SELECT
                        f.UserId,
                        f.feature,                                            -- The feature (EventCategory)
                        TIMESTAMPDIFF(MINUTE, f.first_event_time, f.last_event_time) AS duration_minutes -- Duration in minutes
                    FROM FeatureUsage f
                    WHERE f.first_event_time != NULL AND f.last_event_time != NULL  -- Ensure valid timestamps
                )

                -- Step 3: Calculate the average usage duration per feature
                SELECT
                    fd.feature,                                              -- The feature (EventCategory)
                    AVG(fd.duration_minutes) AS avg_duration_minutes         -- Average duration in minutes
                FROM FeatureDurations fd
                GROUP BY fd.feature                                          -- Group by feature
                ORDER BY avg_duration_minutes DESC;                          -- Order by longest average duration

        """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)
        if len(result) == 0:
            return 0
        row = result[0]
        average_session_length = float(row['avg_duration_minutes'])
        return average_session_length
    except Exception as e:
        print_exception(e)
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
                        __CHECKS__
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

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print_exception(e)
        return 0

@trace_span("service: analytics: medication management matrix: get_medication_management_matrix")
async def get_medication_management_matrix(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
                SELECT 

                    COUNT(
                    CASE WHEN medication_consumption.DeletedAt IS NULL THEN 1 END) AS total_medications,
                    
                    COUNT(
                    CASE WHEN medication_consumption.DeletedAt IS NOT NULL THEN 1 END) AS total_deleted_medications,
                    
                    COUNT(
                    CASE WHEN medication_consumption.IsTaken = 1 
                    AND medication_consumption.TakenAt IS NOT NULL 
                    AND medication_consumption.DeletedAt IS NULL 
                    AND medication_consumption.IsMissed = 0 THEN 1 END) AS medication_taken_count,
                    
                    COUNT(
                    CASE WHEN medication_consumption.IsMissed = 1 
                    AND medication_consumption.IsTaken = 0 
                    AND medication_consumption.TakenAt IS null 
                    AND medication_consumption.DeletedAt IS NULL THEN 1 END) AS medication_missed_count,

                    COUNT(
                    CASE WHEN medication_consumption.IsMissed = 0 
                    AND medication_consumption.IsTaken = 0 
                    AND medication_consumption.TakenAt IS null 
                    AND medication_consumption.DeletedAt IS NULL THEN 1 END) AS medication_not_answered_count,
                    
                    (COUNT(
                    CASE WHEN medication_consumption.IsTaken = 1 
                    AND medication_consumption.TakenAt IS NOT NULL 
                    AND medication_consumption.DeletedAt IS NULL 
                    AND medication_consumption.IsMissed = 0 THEN 1 END) * 100.0 / 
                    COUNT(
                    CASE WHEN medication_consumption.DeletedAt IS NULL THEN 1 END)) AS medication_taken_percentage,
                    
                    (COUNT(
                    CASE WHEN medication_consumption.IsMissed = 1 
                    AND medication_consumption.IsTaken = 0 
                    AND medication_consumption.TakenAt IS null 
                    AND medication_consumption.DeletedAt IS NULL THEN 1 END) * 100.0 / 
                    COUNT(
                    CASE WHEN medication_consumption.DeletedAt IS NULL THEN 1 END)) AS medication_missed_percentage
                
                FROM medication_consumptions AS medication_consumption
                JOIN users user ON user.id = medication_consumption.PatientUserId
                WHERE
                    user.IsTestUser = 0
                    AND
                    medication_consumption.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
                    __CHECKS__
                """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print_exception(e)
        return 0

@trace_span("service: analytics: health journey: get_health_journey_completed_task_count")
async def get_health_journey_completed_task_count(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
            SELECT count(*) as health_journey_completed_task_count
            FROM user_tasks AS userTask
            JOIN users u ON u.id = userTask.UserId
            JOIN careplan_activities careplanActivity ON userTask.ActionId = careplanActivity.id
            WHERE 
                userTask.ActionType = 'Careplan' 
                AND
                userTask.StartedAt IS NOT NULL
                AND
                userTask.FinishedAt IS NOT NULL
                AND
                u.IsTestUser = 0
                AND
                u.RoleId = '{role_id}'
                AND
                userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
                AND
                userTask.ScheduledEndTime BETWEEN '{start_date}' and now();
            """

        result = connector.execute_read_query(query)
        return result
    
    except Exception as e:  
        print_exception(e)
        return 0

@trace_span("service: analytics: patient task: get_patient_completed_task_count")
async def get_patient_completed_task_count(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT count(*) as patient_completed_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        WHERE 
            userTask.StartedAt IS NOT NULL
            AND
            userTask.FinishedAt IS NOT NULL
            AND
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.DeletedAt IS NULL
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now();
        """

        result = connector.execute_read_query(query)
        return result
    
    except Exception as e:  
        print_exception(e)
        return 0

@trace_span("service: analytics: patient task: get_category_wise_patient_completed_task_count")
async def get_category_wise_patient_completed_task_count(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT userTask.Category AS task_category, count(*) as patient_completed_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        WHERE 
            userTask.StartedAt IS NOT NULL
            AND
            userTask.FinishedAt IS NOT NULL
            AND
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.DeletedAt IS NULL
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now()
        GROUP BY
            userTask.Category;
        """

        result = connector.execute_read_query(query)
        return result
    
    except Exception as e:  
        print_exception(e)
        return 0
     
@trace_span("service: analytics: health journey: get_health_journey_specific_completed_task_count")    
async def get_health_journey_specific_completed_task_count(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT 
            careplanActivity.PlanCode AS careplan_code, 
            count(*) as careplan_completed_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        JOIN careplan_activities careplanActivity ON userTask.ActionId = careplanActivity.id
        WHERE 
            userTask.ActionType = 'Careplan' 
            AND
            userTask.StartedAt IS NOT NULL
            AND
            userTask.FinishedAt IS NOT NULL
            AND
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now()
        GROUP BY
            careplanActivity.PlanCode;
        """

        result = connector.execute_read_query(query)
        return result
    
    except Exception as e:  
        print_exception(e)
        return 0

@trace_span("service: analytics: health journey: get_health_journey_specific_completed_task_count")
async def get_health_journey_specific_completed_task_count(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT 
            careplanActivity.PlanCode AS careplan_code, 
            count(*) as careplan_completed_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        JOIN careplan_activities careplanActivity ON userTask.ActionId = careplanActivity.id
        WHERE 
            userTask.ActionType = 'Careplan' 
            AND
            userTask.StartedAt IS NOT NULL
            AND
            userTask.FinishedAt IS NOT NULL
            AND
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now()
        GROUP BY
            careplanActivity.PlanCode;
        """

        result = connector.execute_read_query(query)
        return result
    
    except Exception as e:  
        print_exception(e)
        return 0

@trace_span("service: analytics: health journey: get_user_wise_health_journey_completed_task_count")
async def get_user_wise_health_journey_completed_task_count(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT careplanActivity.PatientUserId, userTask.Category, careplanActivity.PlanCode AS careplan_code, count(*) as careplan_completed_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        JOIN careplan_activities careplanActivity ON userTask.ActionId = careplanActivity.id
        WHERE 
            userTask.ActionType = 'Careplan' 
            AND
            userTask.StartedAt IS NOT NULL
            AND
            userTask.FinishedAt IS NOT NULL
            AND
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now()
        GROUP BY
            careplanActivity.PatientUserId,
            userTask.Category,
            careplanActivity.PlanCode;
        """

        result = connector.execute_read_query(query)
        return result
    
    except Exception as e:  
        print_exception(e)
        return 0

@trace_span("service: analytics: health journey: get_category_wise_health_journey_task_count")
async def get_category_wise_health_journey_task_count(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT careplanActivity.PatientUserId ,careplanActivity.Category, careplanActivity.PlanCode, count(*) as careplan_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        JOIN careplan_activities careplanActivity ON userTask.ActionId = careplanActivity.id
        WHERE 
            userTask.ActionType = 'Careplan' 
            AND
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now()
        GROUP BY
            careplanActivity.PatientUserId,
            userTask.Category,
            careplanActivity.PlanCode
        """
        
        result = connector.execute_read_query(query)
        return result
    
    except Exception as e:  
        print_exception(e)
        return 0

@trace_span("service: analytics: health journey: get_health_journey_custom_assessment_completed_task_count")
async def get_health_journey_custom_assessment_completed_task_count(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT count(*) as custom_assessment_careplan_completed_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        JOIN assessments assessment ON assessment.id = userTask.ActionId
        WHERE 
            userTask.ActionType = 'Careplan' 
            AND
            userTask.StartedAt IS NOT NULL
            AND
            userTask.FinishedAt IS NOT NULL
            AND
            assessment.FinishedAt IS NOT NULL
            AND
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now();
        """
        
        result = connector.execute_read_query(query)
        return result

    except Exception as e:  
        print_exception(e)
        return 0

@trace_span("service: analytics: health journey: get_health_journey_task_count") 
async def get_health_journey_task_count(filters: AnalyticsFilters):
    try:
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT count(*) as careplan_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        JOIN careplan_activities careplanActivity ON userTask.ActionId = careplanActivity.id
        WHERE 
            userTask.ActionType = 'Careplan' 
            AND
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now();
        """

        result = connector.execute_read_query(query)
        return result

    except Exception as e:
        print_exception(e)
        return None

@trace_span("service: analytics: patient task: get_patient_task_count") 
async def get_patient_task_count(filters: AnalyticsFilters):
    try:
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT count(*) as patient_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        WHERE 
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
			userTask.DeletedAt IS NULL
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now();
        """

        result = connector.execute_read_query(query)
        return result

    except Exception as e:
        print_exception(e)
        return None
    
@trace_span("service: analytics: patient task: get_category_wise_patient_task_count") 
async def get_category_wise_patient_task_count(filters: AnalyticsFilters):
    try:
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT userTask.Category AS task_category, count(*) as user_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        WHERE 
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.DeletedAt IS NULL
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now()
        GROUP BY
            userTask.Category
        """

        result = connector.execute_read_query(query)
        return result

    except Exception as e:
        print_exception(e)
        return None
    
@trace_span("service: analytics: health journey: get_health_journey_specific_task_count")
async def get_health_journey_specific_task_count(filters: AnalyticsFilters):
    try:
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT careplanActivity.PlanCode, count(*) as careplan_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        JOIN careplan_activities careplanActivity ON userTask.ActionId = careplanActivity.id
        WHERE 
            userTask.ActionType = 'Careplan' 
            AND
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now()
        GROUP BY
            careplanActivity.PlanCode
        """

        result = connector.execute_read_query(query)
        return result

    except Exception as e:
        print_exception(e)
        return None


@trace_span("service: analytics: health journey: get_health_journey_custom_assessment_task_count")  
async def get_health_journey_custom_assessment_task_count(filters: AnalyticsFilters):
    try:
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT count(*) as custom_assessment_careplan_task_count
        FROM user_tasks AS userTask
        JOIN users u ON u.id = userTask.UserId
        JOIN assessments assessment ON assessment.id = userTask.ActionId
        WHERE 
            userTask.ActionType = 'Careplan' 
            AND
            u.IsTestUser = 0
            AND
            u.RoleId = '{role_id}'
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now();
        """
        result = connector.execute_read_query(query)
        return result

    except Exception as e:
        print_exception(e)
        return None

@trace_span("service: analytics: vital matrix: get_vitals_manual_and_device_add_entry_count")
async def get_vitals_manual_and_device_add_entry_count(filters: AnalyticsFilters, vital_name: str):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
        SELECT 
            COUNT(*) AS add_event_count,
            COUNT(CASE WHEN Attributes LIKE "%'Provider': None%" THEN 1 END) AS manual_entry_add_event_count,
            COUNT(CASE WHEN Attributes NOT LIKE "%'Provider': None%" THEN 1 END) AS device_entry_add_event_count
        FROM events e
        JOIN users user ON e.UserId = user.id
        WHERE
            e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
            __CHECKS__
            AND
            ResourceType = 'biometric'
            AND EventName = 'vitals-add'
            AND EventCategory = 'vitals'
            AND EventSubject = 'vitals-{vital_name}';
        """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)
        
        result = connector.execute_read_query(query)
        if result is not None or len(result) > 0:
            features = {
                'vital_name': vital_name,
            }
            features = {**features, **result[0]}
            return features
        return result
    
    except Exception as e:  
        print_exception(e)
        return None

@trace_span("service: analytics: vital matrix: get_vitals_manual_add_entry_count")
async def get_vitals_manual_add_entry_count(filters: AnalyticsFilters, vital_name: str):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
        SELECT 
            COUNT(*) AS add_event_count
        FROM events e
        JOIN users user ON e.UserId = user.id
        WHERE
            e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
            __CHECKS__
            AND
            ResourceType = 'biometric'
            AND EventName = 'vitals-add'
            AND EventCategory = 'vitals'
            AND EventSubject = 'vitals-{vital_name}';
        """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)
        
        result = connector.execute_read_query(query)
        if result is not None or len(result) > 0:
            features = {
                'vital_name': vital_name,
                'manual_entry_add_event_count' : result[0]['add_event_count'],
                'device_entry_add_event_count' : 0
            }
            features = {**features, **result[0]}
            return features
        return result
    
    except Exception as e:  
        print_exception(e)
        return None
    
@trace_span("service: analytics: assessment matrix: get_custom_assessment_completion_count")
async def get_custom_assessment_completion_count(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
        SELECT 
            ActionType AS action_type,
            COUNT(*) AS assessment_count,
            COUNT(CASE WHEN assessment.StartedAt IS NOT NULL AND assessment.FinishedAt IS NULL THEN 1 END) AS in_progress_assessment_count,
            COUNT(CASE WHEN assessment.StartedAt IS NOT NULL AND assessment.FinishedAt IS NOT NULL THEN 1 END) AS completed_assessment_count,
            COUNT(CASE WHEN assessment.StartedAt IS NULL AND assessment.FinishedAt IS NULL THEN 1 END) AS assessment_not_started_count
        FROM 
            user_tasks userTask
        JOIN users user ON user.id = userTask.UserId
        JOIN assessments assessment ON assessment.id = userTask.ActionId
        WHERE 
            userTask.Category = 'Assessment'
            AND
            user.IsTestUser = 0 
            AND
            userTask.ScheduledEndTime < now()
            AND
            userTask.DeletedAt IS NULL
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now()
        __CHECKS__
        GROUP BY 
            userTask.ActionType;
        """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)
        return result

    except Exception as e:
        print_exception(e)
        return None
    
@trace_span("service: analytics: assessment matrix: get_care_plan_wise_assessment_completion_count")
async def get_care_plan_wise_assessment_completion_count(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
       SELECT 
            ActionType AS action_type ,
            careplanActivity.PlanCode AS care_plan_code,
            COUNT(*) AS assessment_count,
            COUNT(CASE WHEN assessment.StartedAt IS NOT NULL AND assessment.FinishedAt IS NULL THEN 1 END) AS in_progress_assessment_count,
            COUNT(CASE WHEN userTask.StartedAt IS NOT NULL AND userTask.FinishedAt IS NOT NULL THEN 1 END) AS completed_assessment_count,
            COUNT(CASE WHEN userTask.StartedAt IS NULL AND userTask.FinishedAt IS NULL THEN 1 END) AS assessment_not_started_count
        FROM 
            user_tasks userTask
        JOIN users user ON user.id = userTask.UserId
        JOIN careplan_activities careplanActivity ON careplanActivity.id = userTask.ActionId
        JOIN assessments assessment ON assessment.UserTaskId = userTask.id
        WHERE 
            userTask.Category = 'Assessment'
            AND
            user.IsTestUser = 0 
            AND
            userTask.ScheduledEndTime < now()
            AND
            userTask.DeletedAt IS NULL
            AND
            userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
            AND
            userTask.ScheduledEndTime BETWEEN '{start_date}' and now()
        __CHECKS__
        GROUP BY 
            userTask.ActionType,
            careplanActivity.PlanCode;
        """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)
        return result

    except Exception as e:
        print_exception(e)
        return None

@trace_span("service: analytics: assessment matrix: get_assessment_query_response_details")
async def get_assessment_query_response_details(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
                SELECT
                    at.id AS assessment_template_id,
                    an.id AS node_id,
                    at.Title AS assessment_template_title,
                    an.Title AS node_title,
                    aqr.Type AS query_response_type,
                    -- Use CASE to select the appropriate response column
                    CASE 
                        WHEN aqr.Type = 'Single Choice Selection' THEN CAST(aqr.IntegerValue AS CHAR) 
                        WHEN aqr.Type IN ('Text', 'Multi Choice Selection') THEN aqr.TextValue
                        ELSE NULL
                    END AS response,
                    COUNT(*) AS response_count,
                    aqo.Text AS response_option_text
                FROM 
                    assessment_templates at
                LEFT JOIN 
                    assessment_nodes an ON at.id = an.TemplateId
                LEFT JOIN 
                    assessment_query_responses aqr ON an.id = aqr.NodeId
                LEFT JOIN 
                    assessment_query_options aqo ON an.id = aqo.NodeId 
                    AND (
                        (aqr.Type = 'Single Choice Selection' AND aqo.Sequence = aqr.IntegerValue) 
                        OR 
                        (aqr.Type IN ('Text', 'Multi Choice Selection') AND aqo.Sequence = CAST(aqr.TextValue AS UNSIGNED))
                    )
                WHERE
                    an.NodeType <> 'Node list'
                    AND 
                    aqr.Type IS NOT NULL
                    AND 
                    at.DeletedAt IS NULL
                GROUP BY 
                    at.id, 
                    an.id, 
                    aqr.Type, 
                    response, 
                    aqo.Text
                ORDER BY 
                    at.id, 
                    an.id, 
                    response_count DESC;
                """

        result = connector.execute_read_query(query)
        return result

    except Exception as e:
        print_exception(e)
        return None

@trace_span("service: analytics: assessment matrix: get_multiple_choice_response_option_text")     
async def get_multiple_choice_response_option_text(filters: AnalyticsFilters):
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate    
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
                SELECT
                    aqo.NodeId AS node_id,
                    at.Title AS assessment_template_title,
                    an.Title AS node_title,
                    an.Sequence AS node_sequence,
                    an.QueryResponseType AS query_response_type,
                    aqo.Text AS option_text,
                    aqo.Sequence AS option_sequence
                FROM 
                    assessment_templates at
                LEFT JOIN 
                    assessment_nodes an ON at.id = an.TemplateId
                LEFT JOIN 
                    assessment_query_options aqo ON an.id = aqo.NodeId
                WHERE 
                    an.QueryResponseType = 'Multi Choice Selection'
                    AND at.DeletedAt IS NULL
                    AND an.DeletedAt IS NULL
                ORDER BY 
                    at.id, 
                    an.Sequence, 
                    aqo.Sequence;
                """

        result = connector.execute_read_query(query)
        return result

    except Exception as e:
        print_exception(e)
        return None
    
@trace_span("service: analytics: patient task: get_quarter_wise_task_completion_metrics")
async def get_quarter_wise_task_completion_metrics(filters: AnalyticsFilters):
    try:
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_reancare_db_connector()

        query = f"""
                SELECT 
                    UserId as user_id,
                    ROUND((SUM(CASE WHEN Finished = 1 THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS task_completion_percentage
                FROM 
                    user_tasks userTask
                JOIN
                    users user ON user.id = userTask.UserId
                WHERE 
                    user.IsTestUser = 0
                    AND user.RoleId = '{role_id}'
                    AND userTask.DeletedAt IS NULL
                    AND userTask.CreatedAt BETWEEN '{start_date}' AND '{end_date}'
                    AND userTask.ScheduledEndTime BETWEEN '{start_date}' AND NOW()
                GROUP BY 
                    userTask.UserId;
                """
        result = connector.execute_read_query(query)
        ranges = {'0-25%': 0, '25-50%': 0, '50-75%': 0, '75-100%': 0}
        for row in result:
            percentage = row['task_completion_percentage']
            if 0 <= percentage <= 25:
                ranges['0-25%'] += 1
            elif 25 < percentage <= 50:
                ranges['25-50%'] += 1
            elif 50 < percentage <= 75:
                ranges['50-75%'] += 1
            elif 75< percentage <= 100:
                ranges['75-100%'] += 1

        filteredData = [{'percentage_range': key, 'user_count': value} for key, value in ranges.items()]
        return filteredData

    except Exception as e:
        print_exception(e)
        return None
