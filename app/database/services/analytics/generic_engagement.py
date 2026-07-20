from app.common.utils import print_exception
from app.database.services.analytics.common import add_common_checks, find_matching_first_chars
from app.database.services.analytics.sql_dialect import (
    add_days, current_date, day_str, diff_seconds, month_str, ratio_pct,
    week_end, week_start, yearweek,
)
from app.domain_types.enums.event_categories import EventCategory
from app.domain_types.enums.event_types import EventType
from app.domain_types.schemas.analytics import AnalyticsFilters
from app.modules.data_sync.connectors import get_analytics_db_connector
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: analytics: user engagement: get_daily_active_patients")
async def get_daily_active_patients(filters: AnalyticsFilters):
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                DATE(e.Timestamp) AS activity_date, COUNT(DISTINCT e.UserId) AS daily_active_users
            FROM events e
            JOIN users u ON e.UserId = u.id
            WHERE
                e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                __CHECKS__
            GROUP BY DATE(e.Timestamp)
            ORDER BY activity_date;
        """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        result_ = []
        for row in result:
            result_.append({
                "activity_date": str(row['activity_date']),
                "daily_active_users": row['daily_active_users']
            })
        return result_

    except Exception as e:
        print_exception(e)
        return 0

@trace_span("service: analytics: user engagement: get_weekly_active_patients")
async def get_weekly_active_patients(filters: AnalyticsFilters):
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        # query_week_number = f"""
        #     SELECT
        #         YEARWEEK(e.Timestamp, 1) AS activity_week, COUNT(DISTINCT e.UserId) AS weekly_active_users
        #     FROM events e
        #     JOIN users u ON e.UserId = u.id
        #     WHERE
        #         e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
        #         __CHECKS__
        #     GROUP BY YEARWEEK(e.Timestamp, 1)
        #     ORDER BY activity_week;
        # """

        is_postgres = connector.is_postgres
        week_start_str = day_str(week_start('e.Timestamp', is_postgres), is_postgres)
        week_end_str = day_str(week_end('e.Timestamp', is_postgres), is_postgres)
        query = f"""
            SELECT
                {week_start_str} AS week_start_date,
                {week_end_str} AS week_end_date,
                COUNT(DISTINCT e.UserId) AS weekly_active_users
            FROM events e
            JOIN users u ON e.UserId = u.id
            WHERE
                e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                __CHECKS__
            GROUP BY {week_start_str},
                    {week_end_str}
            ORDER BY week_start_date;
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

@trace_span("service: analytics: user engagement: get_monthly_active_patients")
async def get_monthly_active_patients(filters: AnalyticsFilters):
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        is_postgres = connector.is_postgres
        month_expr = month_str('e.Timestamp', is_postgres)
        query = f"""
            SELECT {month_expr} AS activity_month, COUNT(DISTINCT e.UserId) AS monthly_active_users
            FROM events e
            JOIN users u ON e.UserId = u.id
            WHERE
                e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                __CHECKS__
            GROUP BY {month_expr}
            ORDER BY activity_month;
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

# Get DAU, WAU, MAU in one query. Not tested yet.
@trace_span("service: analytics: user engagement: get_patients_active_dau_wau_mau")
async def get_patients_active_dau_wau_mau(filters: AnalyticsFilters):
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        is_postgres = connector.is_postgres
        yw_ts = yearweek('e.Timestamp', is_postgres)
        yw_now = yearweek(current_date(is_postgres), is_postgres)
        month_ts = month_str('e.Timestamp', is_postgres)
        month_now = month_str(current_date(is_postgres), is_postgres)
        query = f"""
                SELECT
                    DATE(e.Timestamp) AS activity_date,
                    COUNT(DISTINCT e.UserId) AS daily_active_users,
                    {yw_ts} AS activity_week,
                    COUNT(DISTINCT CASE WHEN {yw_ts} = {yw_now} THEN e.UserId END) AS weekly_active_users,
                    {month_ts} AS activity_month,
                    COUNT(DISTINCT CASE WHEN {month_ts} = {month_now} THEN e.UserId END) AS monthly_active_users
                FROM events e
                JOIN users u ON e.UserId = u.id
                WHERE
                    e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    __CHECKS__
                GROUP BY DATE(e.Timestamp), {yw_ts}, {month_ts}
                ORDER BY activity_date;
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

@trace_span("service: analytics: user engagement: get_patients_average_session_length_in_minutes")
async def get_patients_average_session_length_in_minutes(filters: AnalyticsFilters):
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()
        # calculate average session lengths by utilizing the SessionId in the events table.
        # Measure the duration of a session for each SessionId based on the difference between
        # the first and last event timestamps in that session.
        # PLEASE NOTE: Since the sessionId is not available for the existing synched data,
        # the query will return an empty list for the time being. But once we start recording sessionId
        # in the events table, this query will be able to calculate the average session length.
        is_postgres = connector.is_postgres
        session_length_expr = diff_seconds('MIN(e.Timestamp)', 'MAX(e.Timestamp)', is_postgres)
        query = f"""
                SELECT
                    AVG(session_length) AS avg_session_length_seconds
                FROM (
                    SELECT
                        {session_length_expr} AS session_length
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                        WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        __CHECKS__
                    GROUP BY u.id
                ) AS session_durations;
            """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        row = result[0]
        average_session_length = float(row['avg_session_length_seconds']) / 60.0 if row['avg_session_length_seconds'] != None else 0.0
        return average_session_length

    except Exception as e:
        print_exception(e)
        return []

@trace_span("service: analytics: user engagement: get_patients_login_frequency")
async def get_patients_login_frequency(filters: AnalyticsFilters):
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        # event_name = find_matching_first_chars(
        #         EventType.UserLoginWithPassword.value,
        #         EventType.UserLoginWithOtp.value)

        is_postgres = connector.is_postgres
        month_expr = month_str('e.Timestamp', is_postgres)
        query = f"""
                SELECT
                    {month_expr} AS month,
                    COUNT(e.EventName) AS login_count
                FROM events e
                JOIN users u ON e.UserId = u.id
                WHERE
                    e.EventName LIKE 'user-login%'
                    AND e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    __CHECKS__
                GROUP BY month
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
        return []


# Retention rate on specific days = (returning users on specific day / active users) * 100
# Please note that - This retention rate (on specific days) is calculated based on the number
# of unique users returning on specific days (Not during the interval between registration
# day and that day).
@trace_span("service: analytics: user engagement: get_patients_retention_rate_on_specific_days")
async def get_patients_retention_rate_on_specific_days(filters: AnalyticsFilters):
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        is_postgres = connector.is_postgres
        reg = "DATE(u.RegistrationDate)"
        d = {n: add_days(reg, n, is_postgres) for n in (1, 3, 7, 10, 15, 20, 25, 30)}
        rate = {n: ratio_pct(f"SELECT COUNT(*) FROM retention_{n}d", "SELECT COUNT(*) FROM registered_users")
                for n in (1, 3, 7, 10, 15, 20, 25, 30)}
        query = f"""
                WITH registered_users AS (
                    SELECT u.id
                    FROM users u
                    __CHECKS__
                ),

                retention_1d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = {d[1]}
                ),

                retention_3d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = {d[3]}
                ),

                retention_7d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = {d[7]}
                ),

                retention_10d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = {d[10]}
                ),

                retention_15d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = {d[15]}
                ),

                retention_20d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = {d[20]}
                ),

                retention_25d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = {d[25]}
                ),

                retention_30d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) = {d[30]}
                )

                SELECT
                    (SELECT COUNT(*) FROM registered_users) AS active_users,

                    (SELECT COUNT(*) FROM retention_1d) AS returning_on_day_1,
                    {rate[1]} AS retention_1d_rate,

                    (SELECT COUNT(*) FROM retention_3d) AS returning_on_day_3,
                    {rate[3]} AS retention_3d_rate,

                    (SELECT COUNT(*) FROM retention_7d) AS returning_on_day_7,
                    {rate[7]} AS retention_7d_rate,

                    (SELECT COUNT(*) FROM retention_10d) AS returning_on_day_10,
                    {rate[10]} AS retention_10d_rate,

                    (SELECT COUNT(*) FROM retention_15d) AS returning_on_day_15,
                    {rate[15]} AS retention_15d_rate,

                    (SELECT COUNT(*) FROM retention_20d) AS returning_on_day_20,
                    {rate[20]} AS retention_20d_rate,

                    (SELECT COUNT(*) FROM retention_25d) AS returning_on_day_25,
                    {rate[25]} AS retention_25d_rate,

                    (SELECT COUNT(*) FROM retention_30d) AS returning_on_day_30,
                    {rate[30]} AS retention_30d_rate;
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

# Retention rate in a specific time interval = (returning users in the interval / active users) * 100
# Please note that - This retention rate (in a specific time interval) is calculated based on the number of unique users returning
# in the interval between the start and end dates after their registration date.
@trace_span("service: analytics: user engagement: get_patients_retention_rate_in_specific_time_interval")
async def get_patients_retention_rate_in_specific_time_interval(filters: AnalyticsFilters):
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()
        is_postgres = connector.is_postgres
        reg = "DATE(u.RegistrationDate)"
        d = {n: add_days(reg, n, is_postgres) for n in (1, 3, 7, 10, 15, 20, 25, 30)}
        rate = {n: ratio_pct(f"SELECT COUNT(*) FROM retention_{n}d", "SELECT COUNT(*) FROM registered_users")
                for n in (1, 3, 7, 10, 15, 20, 25, 30)}
        query = f"""
                WITH registered_users AS (
                    SELECT u.id
                    FROM users u
                    __CHECKS__
                ),

                retention_1d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < {d[1]}
                        AND DATE(e.Timestamp) >= {reg}
                ),

                retention_3d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < {d[3]}
                        AND DATE(e.Timestamp) >= {d[1]}
                ),

                retention_7d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < {d[7]}
                        AND DATE(e.Timestamp) >= {d[3]}
                ),

                retention_10d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < {d[10]}
                        AND DATE(e.Timestamp) >= {d[7]}
                ),

                retention_15d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < {d[15]}
                        AND DATE(e.Timestamp) >= {d[10]}
                ),

                retention_20d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < {d[20]}
                        AND DATE(e.Timestamp) >= {d[15]}
                ),

                retention_25d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < {d[25]}
                        AND DATE(e.Timestamp) >= {d[20]}
                ),

                retention_30d AS (
                    SELECT DISTINCT e.UserId
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        AND e.UserId IN (SELECT id FROM registered_users)
                        AND DATE(e.Timestamp) < {d[30]}
                        AND DATE(e.Timestamp) >= {d[25]}
                )

                SELECT
                    (SELECT COUNT(*) FROM registered_users) AS active_users,

                    (SELECT COUNT(*) FROM retention_1d) AS returning_before_day_1,
                    {rate[1]} AS retention_1d_rate,

                    (SELECT COUNT(*) FROM retention_3d) AS returning_between_day_1_and_day_3,
                    {rate[3]} AS retention_3d_rate,

                    (SELECT COUNT(*) FROM retention_7d) AS returning_between_day_3_and_day_7,
                    {rate[7]} AS retention_7d_rate,

                    (SELECT COUNT(*) FROM retention_10d) AS returning_between_day_7_and_day_10,
                    {rate[10]} AS retention_10d_rate,

                    (SELECT COUNT(*) FROM retention_15d) AS returning_between_day_10_and_day_15,
                    {rate[15]} AS retention_15d_rate,

                    (SELECT COUNT(*) FROM retention_20d) returning_between_day_15_and_day_20,
                    {rate[20]} AS retention_20d_rate,

                    (SELECT COUNT(*) FROM retention_25d) AS returning_between_day_20_and_day_25,
                    {rate[25]} AS retention_25d_rate,

                    (SELECT COUNT(*) FROM retention_30d) AS returning_between_day_25_and_day_30,
                    {rate[30]} AS retention_30d_rate;
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

@trace_span("service: analytics: user engagement: get_patient_stickiness_dau_mau")
async def get_patient_stickiness_dau_mau(filters: AnalyticsFilters):
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        is_postgres = connector.is_postgres
        day_expr = day_str('e.Timestamp', is_postgres)
        month_expr = month_str('e.Timestamp', is_postgres)
        query = f"""
                    WITH ActiveUsers AS (
                        SELECT
                            {day_expr} AS event_date,
                            COUNT(DISTINCT e.UserId) AS daily_active_users,
                            {month_expr} AS month
                        FROM events e
                        JOIN users u ON e.UserId = u.id
                        WHERE
                            u.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                            __CHECKS__
                        GROUP BY event_date, month
                    ),
                    MonthlyActiveUsers AS (
                        SELECT
                            {month_expr} AS month,
                            COUNT(DISTINCT e.UserId) AS monthly_active_users
                        FROM events e
                        JOIN users u ON e.UserId = u.id
                        WHERE
                            u.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                            __CHECKS__
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

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        result_ = []
        for row in result:
            result_.append({
                "month"     : row['month'],
                "avg_dau"   : float(row['avg_dau']) if row['avg_dau'] != None else 0.0,
                "mau"       : row['mau'],
                "stickiness": float(row['stickiness']) if row['stickiness'] != None else 0.0
            })
        return result_

    except Exception as e:
        print_exception(e)
        return []

# Please note that we are treating the EventCategory as the feature in this case.
@trace_span("service: analytics: user engagement: get_patients_most_commonly_used_features")
async def get_patients_most_commonly_used_features(filters: AnalyticsFilters) -> list:
    try:

        top_features_count = 5

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        is_postgres = connector.is_postgres
        month_expr = month_str('e.Timestamp', is_postgres)
        query = f"""
                    -- Step 1: Aggregate feature usage (EventCategory) by month
                    SELECT t1.month, t1.feature, t1.feature_usage_count
                    FROM (
                        SELECT
                            {month_expr} AS month,
                            e.EventCategory AS feature,
                            COUNT(e.id) AS feature_usage_count
                        FROM events e
                        JOIN
                        users u ON e.UserId = u.id
                        WHERE
                            e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                            __CHECKS__
                        GROUP BY month, feature
                        ORDER BY feature_usage_count DESC
                    ) AS t1
                    WHERE (
                        SELECT COUNT(*)
                        FROM (
                            SELECT
                                {month_expr} AS month,
                                e.EventCategory AS feature,
                                COUNT(e.id) AS feature_usage_count
                            FROM events e
                            GROUP BY month, feature
                            ORDER BY feature_usage_count DESC
                            LIMIT {top_features_count}
                        ) AS top_features
                    ) > 0
                    ORDER BY month, feature_usage_count DESC;
        """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print_exception(e)
        return []

@trace_span("service: analytics: user engagement: get_patients_most_commonly_visited_screens")
async def get_patients_most_commonly_visited_screens(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        top_screens_count = 10
        event_category = EventCategory.AppScreenVisit.value # EventCategory for screen visits
        event_name = EventType.ScreenEntry.value # EventName for screen-entry events
        # Please note that we are treating the EventSubject as the screen name in this case.

        is_postgres = connector.is_postgres
        month_expr = month_str('e.Timestamp', is_postgres)
        query = f"""
                SELECT
                    sv.month,
                    sv.screen_name,
                    sv.screen_visit_count
                FROM (
                    SELECT
                        {month_expr} AS month,
                        e.EventSubject AS screen_name,
                        COUNT(e.id) AS screen_visit_count
                    FROM events e
                    JOIN users u ON e.UserId = u.id
                    WHERE
                        e.EventCategory = '{event_category}'
                        AND e.EventName = '{event_name}'
                        AND e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        __CHECKS__
                    GROUP BY month, screen_name
                    ORDER BY screen_visit_count DESC
                ) AS sv
                GROUP BY sv.month, sv.screen_name, sv.screen_visit_count
                HAVING COUNT(*) <= {top_screens_count}
                ORDER BY sv.month ASC, sv.screen_visit_count DESC;
            """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print_exception(e)
        return []

async def get_most_fired_events(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
                SELECT 
                    EventName, 
                    COUNT(*) AS event_count
                FROM 
                    events AS e
                JOIN
                    users u ON e.UserId = u.id
                    WHERE
                        e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                        __CHECKS__
                GROUP BY 
                    EventName
                ORDER BY 
                    event_count DESC;
            """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print(e)
        return []

async def get_most_fired_events_by_event_category(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
                SELECT 
                    EventCategory, 
                    EventName, 
                    COUNT(*) AS event_count
                FROM 
                    events e
                JOIN
                users u ON e.UserId = u.id
                WHERE
                    e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    __CHECKS__
                GROUP BY 
                    EventCategory, 
                    EventName
                ORDER BY 
                    EventCategory, 
                    event_count DESC
            """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print(e)
        return []
        
async def get_user_engagement_over_last_8_days(filters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()
        is_postgres = connector.is_postgres
        last_8_days = "NOW() - INTERVAL '8 day'" if is_postgres else "NOW() - INTERVAL 8 DAY"

        query = f"""
                SELECT
                    EventCategory as event_category,
                    EventName as event_name,
                    COUNT(*) AS event_count
                FROM
                    events e
                JOIN
                    users u ON e.UserId = u.id
                WHERE
                    e.Timestamp >= {last_8_days}
                    AND
                    e.Timestamp BETWEEN '{start_date}' AND '{end_date}'
                    __CHECKS__
                GROUP BY 
                    EventCategory, 
                    EventName
                ORDER BY 
                    EventCategory, 
                    event_count DESC
                """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print(e)
        return []
    
