from datetime import date

from pydantic import UUID4
from app.database.services.analytics.common import add_tenant_and_role_checks, get_role_id, tenant_check
from app.modules.data_sync.connectors import get_analytics_db_connector
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: analytics_basics: get_all_registered_users")
async def get_all_registered_users(tenant_id: UUID4|None, start_date: date, end_date: date) -> int:
    try:
        connector = get_analytics_db_connector()
        query = f"""
            SELECT
                COUNT(*) as user_count
            FROM users
            WHERE
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
            """
        query = query.replace("__TENANT_ID_CHECK__", tenant_check(tenant_id))
        result = connector.execute_read_query(query)
        total_users = result[0]['user_count']
        return total_users
    except Exception as e:
        print(e)
        return 0

@trace_span("service: analytics_basics: get_all_registered_patients")
async def get_all_registered_patients(tenant_id: UUID4|None, start_date: date, end_date: date) -> int:

    role_id = get_role_id()
    try:
        connector = get_analytics_db_connector()
        query = f"""
            SELECT
                COUNT(*) as user_count
            FROM users
            WHERE
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = False)
        result = connector.execute_read_query(query)
        total_patients = result[0]['user_count']
        return total_patients
    except Exception as e:
        print(e)
        return 0


@trace_span("service: analytics_basics: get_current_active_patients")
async def get_current_active_patients(tenant_id: UUID4|None) -> int:

        role_id = get_role_id()
        try:
            connector = get_analytics_db_connector()
            query = f"""
                SELECT
                    COUNT(*) as user_count
                FROM users
                WHERE
                    DeletedAt IS NULL
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
                """
            query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = False)
            result = connector.execute_read_query(query)
            active_patients = result[0]['user_count']
            return active_patients
        except Exception as e:
            print(e)
            return 0

@trace_span("service: analytics_basics: get_patient_registration_history")
async def get_patient_registration_hisory_by_months(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
            SELECT
                DATE_FORMAT(RegistrationDate, '%Y-%m') as month,
                COUNT(*) as user_count
            FROM users
            WHERE
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY month
            ORDER BY month
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = False)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics_basics: get_patient_deregistration_history")
async def get_patient_deregistration_history_by_months(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
            SELECT
                DATE_FORMAT(DeletedAt, '%Y-%m') as month,
                COUNT(*) as user_count
            FROM users
            WHERE
                DeletedAt BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY month
            ORDER BY month
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = False)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics_basics: get_patient_age_demographics")
async def get_patient_age_demographics(tenant_id: UUID4|None, start_date:date, end_date: date) -> list:
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
                user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY age_group
            ORDER BY FIELD(age_group, '0-18', '19-30', '31-45', '46-60', '61-75', '76-90', '91-105', '106-120', 'Unknown');
            """

        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics_basics: get_patient_gender_demographics")
async def get_patient_gender_demographics(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
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
                user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY gender;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics_basics: get_patient_ethnicity_demographics")
async def get_patient_ethnicity_demographics(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
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
                user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY ethnicity;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics_basics: get_patient_race_demographics")
async def get_patient_race_demographics(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
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
                user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY race;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics_basics: get_patient_healthsystem_distribution")
async def get_patient_healthsystem_distribution(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
            SELECT CASE
                    WHEN HealthSystem IS NULL THEN 'Unknown'
                    ELSE HealthSystem
                END AS health_system,
                COUNT(*) AS count
            FROM user_metadata
            INNER JOIN users as user ON user_metadata.UserId = user.id
            WHERE
                user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
            GROUP BY health_system;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics_basics: get_patient_hospital_distribution")
async def get_patient_hospital_distribution(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
                SELECT CASE
                        WHEN Hospital IS NULL THEN 'Unknown'
                        ELSE Hospital
                    END AS hospital,
                    COUNT(*) AS count
                FROM user_metadata
                INNER JOIN users as user ON user_metadata.UserId = user.id
                WHERE
                    user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
                GROUP BY hospital;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []

@trace_span("service: analytics_basics: get_patient_survivor_or_caregiver_distribution")
async def get_patient_survivor_or_caregiver_distribution(tenant_id: UUID4|None, start_date: date, end_date: date) -> list:
    try:
        role_id = get_role_id()
        connector = get_analytics_db_connector()
        query = f"""
                SELECT CASE
                        WHEN IsCareGiver IS NULL THEN 'Unknown'
                        WHEN IsCareGiver = 1 THEN 'Yes'
                        WHEN IsCareGiver = 0 THEN 'No'
                        ELSE 'Unknown'
                    END AS caregiver_status,
                    COUNT(*) AS count
                FROM user_metadata
                INNER JOIN users as user ON user_metadata.UserId = user.id
                WHERE
                    user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
                GROUP BY caregiver_status;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []
