from datetime import date
from pydantic import UUID4
from app.database.services.analytics.common import add_tenant_and_role_checks, get_role_id, role_check, tenant_check
from app.domain_types.enums.event_types import EventType
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
        query = add_tenant_and_role_checks(tenant_id, role_id, query_week_by_start_end_dates, on_joined_user = True)
        result = connector.execute_read_query(query)
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

@trace_span("service: analytics: user engagement: get_patients_average_session_length_in_minutes")
async def get_patients_average_session_length_in_minutes(
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
                    AVG(session_length) AS avg_session_length_seconds
                FROM (
                    SELECT
                        e.SessionId,
                        TIMESTAMPDIFF(SECOND, MIN(e.Timestamp), MAX(e.Timestamp)) AS session_length
                    FROM events e
                    JOIN users AS user ON e.UserId = user.id
                        WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.SessionId IS NOT NULL
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                    GROUP BY e.SessionId
                ) AS session_durations;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        row = result[0]
        average_session_length = float(row['avg_session_length_seconds']) / 60
        return average_session_length
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics: user engagement: get_patients_login_frequency")
async def get_patients_login_frequency(
    tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        event_name = EventType.UserLogin.value
        query = f"""
                SELECT
                    DATE_FORMAT(e.Timestamp, '%Y-%m') AS month,
                    COUNT(e.EventName) AS login_count
                FROM events e
                JOIN users AS user ON e.UserId = user.id
                WHERE
                    e.EventName = '{event_name}'
                    AND e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
                GROUP BY month
                ORDER BY month ASC;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []


# Retention rate on specific days = (returning users on specific day / active users) * 100
# PLESE NOTE THAT - This retention rate (on specific days) is calculated based on the number of unique users returning
# on specific days (Not during the interval between registration day and that day).
@trace_span("service: analytics: user engagement: get_patients_retention_rate_on_specific_days")
async def get_patients_retention_rate_on_specific_days(tenant_id: UUID4|None, start_date:date, end_date: date):
    try:
        role_id = get_role_id()
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
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 1 DAY)
                ),

                retention_3d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users as user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 3 DAY)
                ),

                retention_7d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 7 DAY)
                ),

                retention_10d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 10 DAY)
                ),

                retention_15d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 15 DAY)
                ),

                retention_20d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 20 DAY)
                ),

                retention_25d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = DATE_ADD(DATE(user.RegistrationDate), INTERVAL 25 DAY)
                ),

                retention_30d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users user ON e.UserId = user.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
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

# Retention rate in a specific time interval = (returning users in the interval / active users) * 100
# PLESE NOTE THAT - This retention rate (in a specific time interval) is calculated based on the number of unique users returning
# in the interval between the start and end dates after their registration date.
@trace_span("service: analytics: user engagement: get_patients_retention_rate_in_specific_time_interval")
async def get_patients_retention_rate_in_specific_time_interval(tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
        role_id = get_role_id()
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

@trace_span("service: analytics: user engagement: get_patient_stickiness_dau_mau")
async def get_patient_stickiness_dau_mau(tenant_id: UUID4|None, start_date: date, end_date: date):
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
                    WITH ActiveUsers AS (
                        SELECT
                            DATE_FORMAT(e.Timestamp, '%Y-%m-%d') AS event_date,
                            COUNT(DISTINCT e.UserId) AS daily_active_users,
                            DATE_FORMAT(e.Timestamp, '%Y-%m') AS month
                        FROM events e
                        JOIN users user ON e.UserId = user.id
                        WHERE
                            user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                            __TENANT_ID_CHECK__
                            __ROLE_ID_CHECK__
                        GROUP BY event_date, month
                    ),
                    MonthlyActiveUsers AS (
                        SELECT
                            DATE_FORMAT(e.Timestamp, '%Y-%m') AS month,
                            COUNT(DISTINCT e.UserId) AS monthly_active_users
                        FROM events e
                        JOIN users user ON e.UserId = user.id
                        WHERE
                            user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                            __TENANT_ID_CHECK__
                            __ROLE_ID_CHECK__
                        GROUP BY month
                    )
                    SELECT
                        a.month,
                        ROUND(AVG(a.daily_active_users), 0) AS avg_dau,
                        m.monthly_active_users AS mau,
                        ROUND((AVG(a.daily_active_users) / m.monthly_active_users) * 100, 2) AS stickiness
                    FROM ActiveUsers a
                    JOIN MonthlyActiveUsers m ON a.month = m.month
                    GROUP BY a.month, m.monthly_active_users
                    ORDER BY a.month ASC;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        result_ = []
        for row in result:
            result_.append({
                "month": row['month'],
                "avg_dau": float(row['avg_dau']),
                "mau": row['mau'],
                "stickiness": float(row['stickiness'])
            })
        return result_
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
                    -- Step 1: Aggregate feature usage (EventCategory) by month
                    SELECT t1.month, t1.feature, t1.feature_usage_count
                    FROM (
                        SELECT
                            DATE_FORMAT(e.Timestamp, '%Y-%m') AS month,
                            e.EventCategory AS feature,
                            COUNT(e.id) AS feature_usage_count
                        FROM events e
                        JOIN
                        users user ON e.UserId = user.id
                        WHERE
                            e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                            __TENANT_ID_CHECK__
                            __ROLE_ID_CHECK__
                        GROUP BY month, feature
                        ORDER BY feature_usage_count DESC
                    ) AS t1
                    WHERE (
                        SELECT COUNT(*)
                        FROM (
                            SELECT
                                DATE_FORMAT(e.Timestamp, '%Y-%m') AS month,
                                e.EventCategory AS feature,
                                COUNT(e.id) AS feature_usage_count
                            FROM events e
                            GROUP BY month, feature
                            ORDER BY feature_usage_count DESC
                            LIMIT {top_features_count}
                        ) AS top_features
                    )
                    ORDER BY month, feature_usage_count DESC;
        """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics: user engagement: get_patients_most_commonly_visited_screens")
async def get_patients_most_commonly_visited_screens(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()

        top_screens_count = 10
        event_category = 'app-screen-visit' # EventCategory for screen visits
        event_name = 'screen-entry' # EventName for screen-entry events
        # Please note that we are treating the EventSubject as the screen name in this case.

        query = f"""
                SELECT
                    sv.month,
                    sv.screen_name,
                    sv.screen_visit_count
                FROM (
                    SELECT
                        DATE_FORMAT(e.Timestamp, '%Y-%m') AS month,
                        e.EventSubject AS screen_name,
                        COUNT(e.id) AS screen_visit_count
                    FROM events e
                    JOIN users AS user ON e.UserId = user.id
                    WHERE
                        e.EventCategory = '{event_category}'
                        AND e.EventName = '{event_name}'
                        AND e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        __TENANT_ID_CHECK__
                        __ROLE_ID_CHECK__
                    GROUP BY month, screen_name
                    ORDER BY screen_visit_count DESC
                ) AS sv
                GROUP BY sv.month, sv.screen_name
                HAVING COUNT(*) <= {top_screens_count}
                ORDER BY sv.month ASC, sv.screen_visit_count DESC;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []
