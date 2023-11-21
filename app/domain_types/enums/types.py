from enum import Enum

class EventTypes(str, Enum):
    user_action = "User Action"
    system      = "System"
    unspecified = "Unspecified"

class Operators(str, Enum):
    equal                 = 'eq'
    not_equal             = 'neq'
    contains              = 'contains'
    does_not_contain      = 'does_not_contain'
    true                  = 'true'
    false                 = 'false'
    greater_than          = 'gt'
    less_than             = 'lt'
    greater_than_or_equal = 'gte'
    less_than_or_equal    = 'lte'
    before                = 'bf'
    after                 = 'af'


class CompositeOperators(str, Enum):
    all = 'all'
    any = 'any'

class DataTypes(str, Enum):
    string     = 'string'
    integer    = 'integer'
    decimal    = 'decimal'
    boolean    = 'boolean'
    datetime   = 'datetime'
    uuid       = 'uuid'
    array      = 'array'
    dictionary = 'dictionary'

class SortOrder(str, Enum):
    ascending  = 'asc'
    descending = 'desc'

class Duration(str, Enum):
    last_1_day    = 'last-1-day'
    last_7_days   = 'last-7-days'
    last_1_month  = 'last-1-month'
    last_quarter  = 'last-quarter'
    last_6_months = 'last-6-months'
    last_year     = 'last-year'

class Frequency(str, Enum):
    per_day        = 'per-day'
    per_week       = 'per-week'
    per_month      = 'per-month'
    per_quarter    = 'per-quarter'
    per_six_months = 'per-six-months'
    per_year       = 'per-year'

class AnalysisType(str, Enum):
    stickiness                       = 'stickiness'
    retained_users                   = 'retained-users'
    churned_users                    = 'churned-users'
    total_users                      = 'total-users'
    active_users                     = 'active-users'
    page_views_count_per_unique_user = 'page-views-count-per-unique-user'
    events_count_per_unique_user     = 'events-counts-per-unique-user'
    all_page_views                   = 'all-page-views'
    top_page_views                   = 'top-page-views'
    top_events                       = 'top-events'
    top_users                        = 'top-users'
    top_devices                      = 'top-devices'
    top_browsers                     = 'top-browsers'
    top_versions                     = 'top-versions'
    top_tenants                      = 'top-tenants'
    user_active_days                 = 'user-active-days' # Number of days a given user was active
    goal_completions                 = 'goal-completions' # Number of times a given goal was completed
    avg_goal_completion_time         = 'avg-goal-completion-time' # Average time it took to complete a given goal
    avg_session_duration             = 'avg-session-duration'
    top_onboarding_sources           = 'top-onboarding-sources'
    installations                    = 'installations'
    exits                            = 'exits'
    device_count_per_user            = 'device-count-per-user'
    browser_count_per_user           = 'browser-count-per-user'

