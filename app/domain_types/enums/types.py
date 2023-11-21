from enum import Enum

class EventTypes(str, Enum):
    user_action = "User Action"
    system      = "System"
    unspecified = "Unspecified"

class Operators(str, Enum):
    Equals             = 'Equals'
    NotEquals          = 'Not Equals'
    Contains           = 'Contains'
    DoesNotContain     = 'Does Not Contain'
    Truthy             = 'True'
    Falsy              = 'False'
    GreaterThan        = 'Greater Than'
    LessThan           = 'Less Than'
    GreaterThanOrEqual = 'Greater Than or Equal'
    LessThanOrEqual    = 'Less Than or Equal'
    Before             = 'Before'
    After              = 'After'
    Between            = 'Between'


class CompositeOperators(str, Enum):
    And = 'And'
    Or  = 'Or'

class DataTypes(str, Enum):
    String     = 'String'
    Integer    = 'Integer'
    Float      = 'Float'
    Boolean    = 'Boolean'
    DateTime   = 'DateTime'
    UUID       = 'UUID'
    Array      = 'Array'
    Dictionary = 'Dictionary'

class SortOrder(str, Enum):
    Ascending  = 'asc'
    Descending = 'desc'

class Duration(str, Enum):
    Yesteray    = 'Yesterday'
    LastWeek    = 'Last-week'
    LastMonth   = 'Last-month'
    LastQuarter = 'Last-quarter'
    Last6Months = 'Last-6-months'
    LastYear    = 'Last-year'

class Frequency(str, Enum):
    PerDay        = 'Per-day'
    PerWeek       = 'Per-week'
    PerMonth      = 'Per-month'
    PerQuarter    = 'Per-quarter'
    PerYear       = 'Per-year'

class AnalysisType(str, Enum):
    Stickiness                  = 'Stickiness'
    RetainedUsers               = 'Retained-users'
    ChurnedUsers                = 'Churned-users'
    TotalUsers                  = 'Total-Users'
    ActiveUsers                 = 'Active-users'
    PageViewsCountPerUniqueUser = 'Page-views-count-per-unique-user'
    EventsCountPerUniqueUser    = 'Events-counts-per-unique-user'
    AllPageViews                = 'All-page-views'
    TopPageViews                = 'Top-page-views'
    TopEvents                   = 'Top-events'
    TopUsers                    = 'Top-users'
    TopDevices                  = 'Top-devices'
    TopBrowsers                 = 'Top-browsers'
    TopVersions                 = 'Top-versions'
    TopTenants                  = 'Top-tenants'
    UserActiveDays              = 'User-active-days' # Number of days a given user was active
    GoalCompletions             = 'Goal-completions' # Number of times a given goal was completed
    AvgGoalCompletionTime       = 'Average-goal-completion-time' # Average time it took to complete a given goal
    AvgSessionDuration          = 'Average-session-duration'
    TopOnboardigSources         = 'Top-onboarding-sources'
    Installations               = 'Installations'
    Exits                       = 'Exits'
    DeviceCountPerUser          = 'Device-count-per-user'
    BrowserCountPerUser         = 'Browser-count-per-user'
