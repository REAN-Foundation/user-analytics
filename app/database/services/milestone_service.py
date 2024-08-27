import datetime as dt
import json
from app.common.utils import print_colorized_json
from app.database.models.milestone import Milestone
from app.database.models.user import User
from app.domain_types.schemas.milestone import MilestoneCreateModel
from app.domain_types.schemas.user import UserCreateModel, UserResponseModel, UserUpdateModel, UserSearchFilter, UserSearchResults
from sqlalchemy.orm import Session
from app.domain_types.miscellaneous.exceptions import Conflict, NotFound
from sqlalchemy import asc, desc
from app.telemetry.tracing import trace_span

###############################################################################

@trace_span("service: create_milestone")
def create_milestone(session: Session, model: MilestoneCreateModel) -> MilestoneCreateModel:
    milestone = session.query(Milestone).filter(Milestone.UserId == str(model.UserId)).first()
    if milestone != None:
        raise Conflict(f"Milestone with user id `{model.UserId}` already exists!")
    model_dict = model.dict()
    db_model = Milestone(**model_dict)
    db_model.Attributes = json.dumps(model.Attributes)
    db_model.UpdatedAt = dt.datetime.now()
    session.add(db_model)
    session.commit()
    temp = session.refresh(db_model)
    milestone = db_model
    milestone.Attributes = json.loads(milestone.Attributes)
    print_colorized_json(milestone)
    return milestone.__dict__
