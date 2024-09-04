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
from app.telemetry.tracing import trace_span

###############################################################################

def tenant_check(tenant_id: UUID4|None) -> str:
    if tenant_id is None:
        return ""
    return f"TenantId = '{tenant_id}' AND"

###############################################################################

@trace_span("service: analytics_basics: get_all_registered_users")
def get_all_registered_users(tenant_id: UUID4|None, start_date: date, end_date: date) -> int:
    try:
        connector = get_analytics_db_connector()
        query = f"""
            SELECT
                COUNT(*) as total_users
            FROM users
            WHERE __TENANT_ID_CHECK__
                RegistrationDate BETWEEN '{start_date}' AND '{end_date}'
            """
        query = query.replace("__TENANT_ID_CHECK__", tenant_check(tenant_id))
        result = connector.execute_read_query(query)
        total_users = result[0]['total_users']
        return total_users
    except Exception as e:
        print(e)
        return 0

# @trace_span("service: analytics_basics: get_all_registered_patients")
