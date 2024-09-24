from app.common.utils import print_exception
from app.database.services.analytics.common import add_common_checks
from app.domain_types.schemas.analytics import AnalyticsFilters
from app.modules.data_sync.connectors import get_analytics_db_connector
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: analytics_basics: get_all_registered_users")
async def get_all_registered_users(filters: AnalyticsFilters) -> int:
    try:
        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                COUNT(*) as user_count
            FROM users as user
            WHERE
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __CHECKS__
            """
        checks_str = add_common_checks(tenant_id, role_id=None)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)
        total_users = result[0]['user_count']
        return total_users

    except Exception as e:
        print_exception(e)
        return 0

@trace_span("service: analytics_basics: get_all_registered_patients")
async def get_all_registered_patients(filters: AnalyticsFilters) -> int:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                COUNT(*) as user_count
            FROM users as user
            WHERE
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __CHECKS__
            """
        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)
        total_patients = result[0]['user_count']
        return total_patients

    except Exception as e:
        print_exception(e)
        return 0


@trace_span("service: analytics_basics: get_current_active_patients")
async def get_current_active_patients(filters: AnalyticsFilters) -> int:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()
        query = f"""
            SELECT
                COUNT(*) as user_count
            FROM users as user
            WHERE
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                AND
                DeletedAt IS NULL
                __CHECKS__
            """

        checks_str = add_common_checks(tenant_id, role_id)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)

        result = connector.execute_read_query(query)
        active_patients = result[0]['user_count']

        return active_patients

    except Exception as e:
        print_exception(e)
        return 0

@trace_span("service: analytics_basics: get_patient_registration_history")
async def get_patient_registration_hisory_by_months(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                DATE_FORMAT(RegistrationDate, '%Y-%m') as month,
                COUNT(*) as user_count
            FROM users as user
            WHERE
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                __CHECKS__
            GROUP BY month
            ORDER BY month
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

@trace_span("service: analytics_basics: get_patient_deregistration_history")
async def get_patient_deregistration_history_by_months(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()

        query = f"""
            SELECT
                DATE_FORMAT(DeletedAt, '%Y-%m') as month,
                COUNT(*) as user_count
            FROM users as user
            WHERE
                DeletedAt BETWEEN '{start_date}' AND '{end_date}'
                __CHECKS__
            GROUP BY month
            ORDER BY month
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

@trace_span("service: analytics_basics: get_patient_age_demographics")
async def get_patient_age_demographics(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

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
                __CHECKS__
            GROUP BY age_group
            ORDER BY FIELD(age_group, '0-18', '19-30', '31-45', '46-60', '61-75', '76-90', '91-105', '106-120', 'Unknown');
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

@trace_span("service: analytics_basics: get_patient_gender_demographics")
async def get_patient_gender_demographics(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

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
                __CHECKS__
            GROUP BY gender;
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

@trace_span("service: analytics_basics: get_patient_ethnicity_demographics")
async def get_patient_ethnicity_demographics(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

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
                __CHECKS__
            GROUP BY ethnicity;
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

@trace_span("service: analytics_basics: get_patient_race_demographics")
async def get_patient_race_demographics(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

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
                __CHECKS__
            GROUP BY race;
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

@trace_span("service: analytics_basics: get_patient_healthsystem_distribution")
async def get_patient_healthsystem_distribution(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

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
                __CHECKS__
            GROUP BY health_system;
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

@trace_span("service: analytics_basics: get_patient_hospital_distribution")
async def get_patient_hospital_distribution(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

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
                    __CHECKS__
                GROUP BY hospital;
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

@trace_span("service: analytics_basics: get_patient_survivor_or_caregiver_distribution")
async def get_patient_survivor_or_caregiver_distribution(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

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
                    __CHECKS__
                GROUP BY caregiver_status;
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

async def get_users_distribution_by_role(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()
        query = f"""
                SELECT 
                    RoleId,
                    count(*) AS registration_count
                FROM 
                    users
                WHERE
                    RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                    __CHECKS__
                GROUP BY 
                    RoleId
                ORDER BY
                    RoleId ASC
            """

        checks_str = add_common_checks(tenant_id, None)
        if len(checks_str) > 0:
            checks_str = "AND " + checks_str
        query = query.replace("__CHECKS__", checks_str)
        result = connector.execute_read_query(query)

        return result

    except Exception as e:
        print(e)
        return []

async def get_active_users_count_at_end_of_every_month(filters: AnalyticsFilters) -> list:
    try:

        tenant_id  = filters.TenantId
        start_date = filters.StartDate
        end_date   = filters.EndDate
        role_id    = filters.RoleId

        connector = get_analytics_db_connector()
        query = f"""
                SELECT 
                    DATE_FORMAT(LAST_DAY(RegistrationDate), '%Y-%m-%d') AS month_end, 
                    COUNT(*) AS active_user_count
                FROM 
                    users as user
                WHERE 
                    RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
                    AND
                    DeletedAt IS NULL
                    __CHECKS__
                GROUP BY 
                    DATE_FORMAT(RegistrationDate, '%Y-%m')
                ORDER BY 
                    month_end
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
    