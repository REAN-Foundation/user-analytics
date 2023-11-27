
from app.domain_types.enums.types import AnalysisTypeFilter, SourceTypeFilter
from app.domain_types.schemas.filter import FilterResponseModel


class QueryBuilder:
    def __init__(self, filter: FilterResponseModel):
        self.filter = filter
        self.name = filter.Name
        self.filters = filter.Filters
        self.query = None

    def build(self):
        frequency = self.filter.Fre
        q = ""
        if self.filter.AnalysisType == AnalysisTypeFilter.monthly_stickyness:
            if self.filter.Source == SourceTypeFilter.event:
                
            q = self._build_retention_query()
        elif self.filter.AnalysisType == AnalysisTypeFilter.frequency:
            q = self._build_unique_users_query()

        return self.query
    
    def __str__(self) -> str:
        return self.name
