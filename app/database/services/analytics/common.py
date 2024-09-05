
from datetime import datetime
import os
from pydantic import UUID4
from app.modules.data_sync.data_synchronizer import DataSynchronizer

###############################################################################

REPORTS_DIR = "analytics_reports"

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

def get_report_folder_path():
    cwd = os.getcwd()
    today = datetime.today()
    date_timestamp = today.strftime("%Y%m%d")
    reports_path = os.path.join(cwd, 'temp', REPORTS_DIR, date_timestamp)
    if not os.path.exists(reports_path):
        os.makedirs(reports_path, exist_ok=True)
    return reports_path


###############################################################################
