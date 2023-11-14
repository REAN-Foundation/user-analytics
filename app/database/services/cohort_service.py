import datetime as dt
import uuid
from app.common.utils import print_colorized_json
from app.database.models.cohort import Cohort
from app.database.models.cohort_users import CohortUsers
from app.database.models.user import User
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc
from app.domain_types.schemas.cohort import CohortCreateModel, CohortResponseModel, CohortSearchResults, CohortSearchFilter
from app.telemetry.tracing import trace_span

@trace_span("service: create_cohort")
def create_cohort(session: Session, model: CohortCreateModel) -> CohortResponseModel:
    model_dict = model.dict()
    db_model = Cohort(**model_dict)
    db_model.UpdatedAt = dt.datetime.now()
    session.add(db_model)
    session.commit()
    temp = session.refresh(db_model)
    cohort = db_model

    return cohort.__dict__

@trace_span("service: get_cohort_by_id")
def get_cohort_by_id(session: Session, cohort_id: str) -> CohortResponseModel:
    cohort = session.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort:
        raise NotFound(f"cohort with id {cohort_id} not found")
    return cohort.__dict__

@trace_span("service: delete_cohort")
def delete_cohort(session: Session, cohort_id: str):
    cohort = session.query(Cohort).filter(Cohort.id == cohort_id).first()
    if not cohort:
        raise NotFound(f"cohort with id {cohort_id} not found")
    session.delete(cohort)
    session.commit()
    return True

@trace_span("service: search_cohorts")
def search_cohorts(session: Session, filter: CohortSearchFilter) -> CohortSearchResults:

    query = session.query(Cohort)

    if filter.DisplayCode:
        query = query.filter(Cohort.DisplayCode.like(f'%{filter.DisplayCode}%'))
    if filter.InvoiceNumber:
        query = query.filter(Cohort.InvoiceNumber == filter.InvoiceNumber)
    if filter.BankTransactionId:
        query = query.filter(Cohort.BankTransactionId == filter.BankTransactionId)
    if filter.CustomerId:
        query = query.filter(Cohort.CustomerId.like(f'%{filter.CustomerId}%'))
    if filter.OrderId:
        query = query.filter(Cohort.OrderId.like(f'%{filter.OrderId}%'))
    if filter.PaymentMode:
        query = query.filter(Cohort.PaymentMode.like(f'%{filter.PaymentMode}%'))
    if filter.PaymentAmount:
        query = query.filter(Cohort.PaymentAmount.like(f'%{filter.PaymentAmount}%'))
    if filter.IsRefund:
        query = query.filter(Cohort.IsRefund == filter.IsRefund)
    if filter.InitiatedDate:
        query = query.filter(Cohort.InitiatedDate == filter.InitiatedDate)

    if filter.OrderBy == None:
        filter.OrderBy = "CreatedAt"
    else:
        if not hasattr(Cohort, filter.OrderBy):
            filter.OrderBy = "CreatedAt"
    orderBy = getattr(Cohort, filter.OrderBy)

    if filter.OrderByDescending:
        query = query.order_by(desc(orderBy))
    else:
        query = query.order_by(asc(orderBy))

    query = query.offset(filter.PageIndex * filter.ItemsPerPage).limit(filter.ItemsPerPage)

    paymentTransactions = query.all()

    items = list(map(lambda x: x.__dict__, paymentTransactions))

    results = CohortSearchResults(
        TotalCount=len(paymentTransactions),
        ItemsPerPage=filter.ItemsPerPage,
        PageIndex=filter.PageIndex,
        OrderBy=filter.OrderBy,
        OrderByDescending=filter.OrderByDescending,
        Items=items
    )

    return results