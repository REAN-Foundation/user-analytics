from datetime import date, timedelta
import json
import uuid

from pydantic import UUID4
from app.common.utils import print_colorized_json
from app.database.models.cohort import Cohort
from app.database.models.cohort_users import CohortUser
from app.database.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from app.domain_types.miscellaneous.exceptions import Conflict, NotFound
from app.modules.data_sync.connectors import get_analytics_db_connector
from app.modules.data_sync.data_synchronizer import DataSynchronizer
from app.telemetry.tracing import trace_span

###############################################################################

def tenant_check(tenant_id: UUID4|None, on_joined_user = False) -> str:
    if tenant_id is None:
        return ""
    return f"TenantId = '{tenant_id}' AND" if on_joined_user == False else f"user.TenantId = '{tenant_id}' AND"

def role_check(role_id: int|None, on_joined_user = False) -> str:
    if role_id is None:
        return ""
    return f"RoleId = {role_id} AND" if on_joined_user == False else f"user.RoleId = {role_id} AND"

def add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = False):
    query = query.replace("__TENANT_ID_CHECK__", tenant_check(tenant_id, on_joined_user))
    query = query.replace("__ROLE_ID_CHECK__", role_check(role_id, on_joined_user))
    return query

def get_role_id(role_name: str = "Patient") -> int|None:
    role_id = None
    role = DataSynchronizer.get_role_by_name(role_name)
    if (role is not None):
        role_id = role["id"]
    return role_id

###############################################################################

@trace_span("service: analytics_basics: get_all_registered_users")
async def get_all_registered_users(tenant_id: UUID4|None, start_date: date, end_date: date) -> int:
    try:
        connector = get_analytics_db_connector()
        query = f"""
            SELECT
                COUNT(*) as user_count
            FROM users
            WHERE __TENANT_ID_CHECK__
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
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
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
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
                __TENANT_ID_CHECK__
                __ROLE_ID_CHECK__
                user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
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
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
                    user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
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
                    __TENANT_ID_CHECK__
                    __ROLE_ID_CHECK__
                    user.RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY caregiver_status;
            """
        query = add_tenant_and_role_checks(tenant_id, role_id, query, on_joined_user = True)
        result = connector.execute_read_query(query)
        return result
    except Exception as e:
        print(e)
        return []
