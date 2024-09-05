from datetime import date
from pydantic import UUID4
from app.database.services.analytics.common import add_tenant_and_role_checks, get_role_id, tenant_check
from app.modules.data_sync.connectors import get_analytics_db_connector
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: analytics: user engagement: get_daily_active_patients")
async def get_daily_active_patients(tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
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
        return result
    except Exception as e:
        print(e)
        return 0

@trace_span("service: analytics: user engagement: get_weekly_active_patients")
async def get_weekly_active_patients(tenant_id: UUID4|None, start_date: date, end_date: date):

    role_id = get_role_id()
    try:
        connector = get_analytics_db_connector()

        # query_week_number = f"""
        #     SELECT
        #         YEARWEEK(e.Timestamp, 1) AS activity_week, COUNT(DISTINCT e.UserId) AS weekly_active_users
        #     FROM events e
        #     JOIN users user ON e.UserId = user.id
        #     WHERE
        #         e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
        #         __TENANT_ID_CHECK__
        #         __ROLE_ID_CHECK__
        #     GROUP BY YEARWEEK(e.Timestamp, 1)
        #     ORDER BY activity_week;
        # """

        query_week_by_start_end_dates = f"""
            SELECT
                DATE_FORMAT(DATE_SUB(e.Timestamp, INTERVAL (WEEKDAY(e.Timestamp)) DAY), '%Y-%m-%d') AS week_start_date,
                DATE_FORMAT(DATE_ADD(DATE_SUB(e.Timestamp, INTERVAL (WEEKDAY(e.Timestamp)) DAY), INTERVAL 6 DAY), '%Y-%m-%d') AS week_end_date,
                COUNT(DISTINCT e.UserId) AS weekly_active_users
            FROM events e
            JOIN users as user ON e.UserId = user.id
            WHERE
                e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY DATE_FORMAT(DATE_SUB(e.Timestamp, INTERVAL (WEEKDAY(e.Timestamp)) DAY), '%Y-%m-%d'),
                    DATE_FORMAT(DATE_ADD(DATE_SUB(e.Timestamp, INTERVAL (WEEKDAY(e.Timestamp)) DAY), INTERVAL 6 DAY), '%Y-%m-%d')
            ORDER BY week_start_date;
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query_week_by_start_end_dates)
        return result
    except Exception as e:
        print(e)
        return 0


@trace_span("service: analytics: user engagement: get_monthly_active_patients")
async def get_monthly_active_patients(tenant_id: UUID4|None, start_date: date, end_date: date):

        role_id = get_role_id()
        try:
            connector = get_analytics_db_connector()
            query = f"""
                SELECT DATE_FORMAT(e.Timestamp, '%Y-%m') AS activity_month, COUNT(DISTINCT e.UserId) AS monthly_active_users
                FROM events e
                JOIN users as user ON e.UserId = user.id
                WHERE
                    e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
                GROUP BY DATE_FORMAT(e.Timestamp, '%Y-%m')
                ORDER BY activity_month;
            """
            query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
            result = connector.execute_read_query(query)
            return result
        except Exception as e:
            print(e)
            return 0

# Get DAU, WAU, MAU in one query. Not tested yet.
@trace_span("service: analytics: user engagement: get_patients_active_dau_wau_mau")
async def get_patients_active_dau_wau_mau(tenant_id: UUID4|None, start_date: date, end_date: date) :
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
                SELECT
                    DATE(e.Timestamp) AS activity_date,
                    COUNT(DISTINCT e.UserId) AS daily_active_users,
                    YEARWEEK(e.Timestamp, 1) AS activity_week,
                    COUNT(DISTINCT CASE WHEN YEARWEEK(e.Timestamp, 1) = YEARWEEK(CURDATE(), 1) THEN e.UserId END) AS weekly_active_users,
                    DATE_FORMAT(e.Timestamp, '%Y-%m') AS activity_month,
                    COUNT(DISTINCT CASE WHEN DATE_FORMAT(e.Timestamp, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m') THEN e.UserId END) AS monthly_active_users
                FROM events e
                JOIN users user ON e.UserId = user.id
                WHERE
                    e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
                GROUP BY DATE(e.Timestamp), YEARWEEK(e.Timestamp, 1), DATE_FORMAT(e.Timestamp, '%Y-%m')
                ORDER BY activity_date;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return None

@trace_span("service: analytics: user engagement: get_patients_average_session_length_in_hours")
async def get_patients_average_session_length_in_hours(
    tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        # calculate average session lengths by utilizing the SessionId in the events table.
        # Measure the duration of a session for each SessionId based on the difference between
        # the first and last event timestamps in that session.
        # PLEASE NOTE: Since the sessionId is not available for the existing synched data,
        # the query will return an empty list for the time being. But once we start recording sessionId
        # in the events table, this query will be able to calculate the average session length.
        query = f"""
                SELECT
                    DATE_FORMAT(DATE_SUB(e.Timestamp, INTERVAL (WEEKDAY(e.Timestamp)) DAY), '%Y-%m-%d') AS week_start_date,
                    DATE_FORMAT(DATE_ADD(DATE_SUB(e.Timestamp, INTERVAL (WEEKDAY(e.Timestamp)) DAY), INTERVAL 6 DAY), '%Y-%m-%d') AS week_end_date,
                    AVG(session_duration) AS average_session_length_seconds
                FROM (
                    SELECT
                        e.SessionId,
                        TIMESTAMPDIFF(SECOND, MIN(e.Timestamp), MAX(e.Timestamp)) AS session_duration
                    FROM events e
                    JOIN users as user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.SessionId IS NOT NULL
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                    GROUP BY e.SessionId
                ) AS sessions
                GROUP BY week_start_date, week_end_date
                ORDER BY week_start_date;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics: user engagement: get_patients_login_frequency")
async def get_patients_login_frequency(
    tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        # Count the number of distinct SessionIds in the events table,
        # which represent new sessions or user logins.
        # PLEASE NOTE: Since the sessionId is not available for the existing synched data,
        # the query will return an empty list for the time being. But once we start recording sessionId
        # in the events table, this query will be able to calculate the average session length.
        query = f"""
                SELECT
                    DATE_FORMAT(DATE_SUB(e.Timestamp, INTERVAL (WEEKDAY(e.Timestamp)) DAY), '%Y-%m-%d') AS week_start_date,
                    DATE_FORMAT(DATE_ADD(DATE_SUB(e.Timestamp, INTERVAL (WEEKDAY(e.Timestamp)) DAY), INTERVAL 6 DAY), '%Y-%m-%d') AS week_end_date,
                    COUNT(DISTINCT e.SessionId) AS login_frequency
                FROM events e
                JOIN users as user ON e.UserId = user.id
                WHERE
                    e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    AND e.SessionId IS NOT NULL
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
                GROUP BY week_start_date, week_end_date
                ORDER BY week_start_date;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

# Retention rate = (returning users / active users) * 100
# Churn rate = (1 - (returning users / active users)) * 100

@trace_span("service: analytics: user engagement: get_patients_retention_rate")
async def get_patients_retention_rate(tenant_id: UUID4|None, start_date:date, end_date: date):
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
                -- Step 1: Find users who registered during the date range
                WITH registered_users AS (
                    SELECT user.id
                    FROM users as user
                    WHERE
                        user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                ),

                -- Step 2: Calculate retention for 1-day, 7-day, and 30-day periods
                retention_1d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users as user ON e.UserId = user.id
                    WHERE
                        e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(user.RegistrationDate, INTERVAL 1 DAY)
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                ),

                retention_7d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(user.RegistrationDate, INTERVAL 7 DAY)
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                ),

                retention_30d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(user.RegistrationDate, INTERVAL 30 DAY)
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                )

                -- Step 3: Calculate retention rates
                SELECT
                    (SELECT COUNT(*) FROM retention_1d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_1d_rate,
                    (SELECT COUNT(*) FROM retention_7d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_7d_rate,
                    (SELECT COUNT(*) FROM retention_30d) / (SELECT COUNT(*) FROM registered_users) * 100 AS retention_30d_rate;
            """

        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics: user engagement: get_patient_stickiness")
async def get_patient_stickiness(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
            WITH dau AS (
                SELECT COUNT(DISTINCT e.UserId) AS daily_active_users
                FROM events e
                JOIN users as user ON e.UserId = user.id
                WHERE
                    e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
            ),
            wau AS (
                SELECT COUNT(DISTINCT e.UserId) AS weekly_active_users
                FROM events e
                JOIN users as user ON e.UserId = user.id
                WHERE
                    e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
            ),
            mau AS (
                SELECT COUNT(DISTINCT e.UserId) AS monthly_active_users
                FROM events e
                JOIN users as user ON e.UserId = user.id
                WHERE
                    e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
            )
            SELECT
                (SELECT daily_active_users FROM dau) / (SELECT weekly_active_users FROM wau) AS dau_wau_stickiness,
                (SELECT daily_active_users FROM dau) / (SELECT monthly_active_users FROM mau) AS dau_mau_stickiness;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

# Please note that we are treating the EventCategory as the feature in this case.
@trace_span("service: analytics: user engagement: get_patients_most_commonly_used_features")
async def get_patients_most_commonly_used_features(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        top_features_count = 5
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
                SELECT result.month, result.feature, result.visit_count
                FROM (
                    SELECT
                        DATE_FORMAT(e.Timestamp, '%Y-%m') AS month,
                        e.EventCategory AS feature,
                        COUNT(e.EventCategory) AS visit_count,
                        ROW_NUMBER() OVER (PARTITION BY DATE_FORMAT(e.Timestamp, '%Y-%m') ORDER BY COUNT(e.EventCategory) DESC) AS rank
                    FROM events e
                    JOIN users as user ON e.UserId = user.id
                        WHERE e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                    GROUP BY month, e.EventCategory
                ) AS result
                WHERE result.rank <= {top_features_count}
                ORDER BY result.month ASC, result.rank ASC;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

# @trace_span("service: analytics: user engagement: get_patients_most_commonly_visited_screens")
# async def get_patients_most_commonly_visited_screens(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
#     try:
#         role_id = get_role_id()
#         connector = get_analytics_db_connector()
#         query = f"""
#             """
#         query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
#         result = connector.execute_read_query(query)
#         return result
#     except Exception as e:
#         print(e)
#         return []
