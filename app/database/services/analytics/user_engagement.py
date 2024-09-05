from datetime import date
from pydantic import UUID4
from app.database.services.analytics.common import add_tenant_and_role_checks, get_role_id, tenant_check
from app.modules.data_sync.connectors import get_analytics_db_connector
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: analytics: user engagement: get_daily_active_patients")
async def get_daily_active_patients(tenant_id: UUID4|None, start_date: date, end_date: date) -> int:
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
async def get_weekly_active_patients(tenant_id: UUID4|None, start_date: date, end_date: date) -> int:

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
async def get_monthly_active_patients(tenant_id: UUID4|None) -> int:

        role_id = get_role_id()
        try:
            connector = get_analytics_db_connector()
            query = f"""
                SELECT
                    COUNT(*) as user_count
                FROM users
                WHERE
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
                    DeletedAt IS NULL
                """
            query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = False)
            result = connector.execute_read_query(query)
            active_patients = result[0]['user_count']
            return active_patients
        except Exception as e:
            print(e)
            return 0

@trace_span("service: analytics: user engagement: get_patients_average_session_length_in_hours")
async def get_patients_average_session_length_in_hours(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
            SELECT
                DATE_FORMAT(RegistrationDate, '%Y-%m') as month,
                COUNT(*) as user_count
            FROM users
            WHERE
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY month
            ORDER BY month
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = False)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics: user engagement: get_patients_login_frequency")
async def get_patients_login_frequency(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
            SELECT
                DATE_FORMAT(DeletedAt, '%Y-%m') as month,
                COUNT(*) as user_count
            FROM users
            WHERE
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
                DeletedAt BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY month
            ORDER BY month
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = False)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics: user engagement: get_patients_retention_rate")
async def get_patients_retention_rate(tenant_id: UUID4|None, start_date:date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
            SELECT CASE
                    WHEN BirthDate IS NULL THEN 'Unknown'
                    WHEN FLOOR(DATEDIFF(CURDATE(), BirthDate)/365) BETWEEN 0 AND 18 THEN '0-18'
                    WHEN FLOOR(DATEDIFF(CURDATE(), BirthDate)/365) BETWEEN 19 AND 30 THEN '19-30'
                    WHEN FLOOR(DATEDIFF(CURDATE(), BirthDate)/365) BETWEEN 31 AND 45 THEN '31-45'
                    WHEN FLOOR(DATEDIFF(CURDATE(), BirthDate)/365) BETWEEN 46 AND 60 THEN '46-60'
                    WHEN FLOOR(DATEDIFF(CURDATE(), BirthDate)/365) BETWEEN 61 AND 75 THEN '61-75'
                    WHEN FLOOR(DATEDIFF(CURDATE(), BirthDate)/365) BETWEEN 76 AND 90 THEN '76-90'
                    WHEN FLOOR(DATEDIFF(CURDATE(), BirthDate)/365) BETWEEN 91 AND 105 THEN '91-105'
                    WHEN FLOOR(DATEDIFF(CURDATE(), BirthDate)/365) BETWEEN 106 AND 120 THEN '106-120'
                    ELSE 'Unknown'
                END AS age_group,
                COUNT(*) AS count
            FROM user_metadata
            INNER JOIN users as user ON user_metadata.UserId = user.id
            WHERE
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
                user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY age_group
            ORDER BY FIELD(age_group, '0-18', '19-30', '31-45', '46-60', '61-75', '76-90', '91-105', '106-120', 'Unknown');
            """

        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics: user engagement: get_patients_churn_rate")
async def get_patients_churn_rate(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
            SELECT CASE
                    WHEN Gender IS NULL THEN 'Unknown'
                    ELSE Gender
                END AS gender,
                COUNT(*) AS count
            FROM user_metadata
            INNER JOIN users as user ON user_metadata.UserId = user.id
            WHERE
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
                user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY gender;
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
        query = f"""
            SELECT CASE
                WHEN Ethnicity IS NULL THEN 'Unknown'
                ELSE Ethnicity
            END AS ethnicity,
            COUNT(*) AS count
            FROM user_metadata
            INNER JOIN users as user ON user_metadata.UserId = user.id
            WHERE
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
                user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY ethnicity;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics: user engagement: get_patients_most_commonly_used_features")
async def get_patients_most_commonly_used_features(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
            SELECT CASE
                    WHEN Race IS NULL THEN 'Unknown'
                    ELSE Race
                END AS race,
                COUNT(*) AS count
            FROM user_metadata
            INNER JOIN users as user ON user_metadata.UserId = user.id
            WHERE
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
                user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY race;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []
