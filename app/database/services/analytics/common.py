
from datetime import datetime
import os
from pydantic import UUID4
from app.modules.data_sync.data_synchronizer import DataSynchronizer

###############################################################################

REPORTS_DIR = "analytics_reports"

###############################################################################

def tenant_check(tenant_id: UUID4|None) -> str:
    if tenant_id is None:
        return ""
    return f"user.TenantId = '{tenant_id}'"

def role_check(role_id: int|None) -> str:
    if role_id is None:
        return ""
    return f"user.RoleId = {role_id}"

def event_source_check(event_source: str|None) -> str:
    if event_source is None:
        return ""
    return f"e.SourceName = '{event_source}'"

def add_common_checks(
        tenant_id: UUID4|None,
        role_id: int|None,
        event_source: str|None = None) -> str:

    checks = []

    tenant_check_str = tenant_check(tenant_id)
    if len(tenant_check_str) > 0:
        checks.append(tenant_check_str)

    role_check_str = role_check(role_id)
    if len(role_check_str) > 0:
        checks.append(role_check_str)

    event_source_check_str = event_source_check(event_source)
    if len(event_source_check_str) > 0:
        checks.append(event_source_check_str)

    checks_str = " AND ".join(checks)
    checks_str = checks_str.strip()
    return checks_str


def get_role_id(role_name: str = "Patient") -> int|None:
    role_id = None
    role = DataSynchronizer.get_role_by_name(role_name)
    if (role is not None):
        role_id = role["id"]
    return role_id

def get_analytics_template_path() -> str:
    cwd = os.getcwd()
    template_path = os.path.join(cwd, 'docs', 'analytics', 'templates')
    return template_path

def get_report_folder_path() -> str:
    cwd = os.getcwd()
    reports_path = os.path.join(cwd, 'tmp', REPORTS_DIR)
    if not os.path.exists(reports_path):
        os.makedirs(reports_path, exist_ok=True)
    return reports_path

def get_current_report_folder_temp_path() -> str:
    cwd = os.getcwd()
    today = datetime.today()
    date_timestamp = today.strftime("%Y%m%d")
    reports_path = os.path.join(cwd, 'tmp', REPORTS_DIR, date_timestamp)
    if not os.path.exists(reports_path):
        os.makedirs(reports_path, exist_ok=True)
    return reports_path

def get_current_analysis_temp_path(analysis_code: str) -> str:
    reports_path = get_current_report_folder_temp_path()
    report_folder_path = os.path.join(reports_path, f"reports_{analysis_code}")
    if not os.path.exists(report_folder_path):
        os.makedirs(report_folder_path, exist_ok=True)
    return report_folder_path

def get_storage_key_path(analysis_code: str) -> str:
    today = datetime.today()
    date_timestamp = today.strftime("%Y%m%d")
    child_folder = f"reports_{analysis_code}"
    storage_key_path = f"{REPORTS_DIR}/{date_timestamp}/{child_folder}"
    return storage_key_path

###############################################################################

def find_matching_first_chars(str1, str2):
    # Get the minimum length of the two strings
    min_len = min(len(str1), len(str2))

    # Iterate through both strings up to the length of the shortest one
    matching_chars = []
    for i in range(min_len):
        if str1[i] == str2[i]:
            matching_chars.append(str1[i])
        else:
            break

    return ''.join(matching_chars)
