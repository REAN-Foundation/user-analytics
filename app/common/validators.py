from datetime import datetime
import uuid
from app.domain_types.miscellaneous.exceptions import UUIDValidationError, ValidationError
from app.domain_types.schemas.data_sync import DataSyncSearchFilter


def validate_uuid4(uuid_str):
    try:
        val = uuid.UUID(uuid_str, version=4)
    except ValueError:
        raise UUIDValidationError("{uuid_str} is not valid UUID.")
    return uuid_str

def validate_data_sync_search_filter(start_date: str, end_date: str) -> DataSyncSearchFilter|None:
    try:
        if start_date is not None:
            start_date = datetime.strptime(start_date.split('T')[0], "%Y-%m-%d")
            if end_date is not None:
                end_date = datetime.strptime(end_date.split('T')[0], "%Y-%m-%d")
            else:
                end_date = datetime.strptime(datetime.today().strftime('%Y-%m-%d'), "%Y-%m-%d")
        return DataSyncSearchFilter(StartDate = start_date, EndDate = end_date) if (start_date and end_date) else None
    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}")
    except ValidationError as e:
        raise ValueError(f"Validation error: {e}")

