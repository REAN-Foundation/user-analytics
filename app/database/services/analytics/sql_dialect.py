# MySQL <-> PostgreSQL dialect helpers for the raw analytics SQL.
#
# The analytics queries are raw SQL executed against the analytics database,
# which can be either MySQL or PostgreSQL depending on DB_DIALECT. The two
# engines differ in their date/string functions and in a few arithmetic rules,
# so the query builders ask these helpers for the right SQL fragment per
# dialect. The dialect flag is taken from the connector, e.g.
#
#     connector = get_analytics_db_connector()
#     pg = connector.is_postgres
#     query = f"SELECT {month_str('e.Timestamp', pg)} AS month FROM events ..."
#
# Each helper's MySQL branch reproduces the original hand-written SQL verbatim,
# so MySQL behaviour is unchanged; only the PostgreSQL branch is new.

###############################################################################

def month_str(column, is_postgres):
    # 'YYYY-MM' formatted month, e.g. 2024-06.
    if is_postgres:
        return f"TO_CHAR({column}, 'YYYY-MM')"
    return f"DATE_FORMAT({column}, '%Y-%m')"

def day_str(column, is_postgres):
    # 'YYYY-MM-DD' formatted date.
    if is_postgres:
        return f"TO_CHAR({column}, 'YYYY-MM-DD')"
    return f"DATE_FORMAT({column}, '%Y-%m-%d')"

def add_days(column, days, is_postgres):
    # Adds whole days to a date. `column` must be a date expression (callers
    # keep the existing DATE(...) wrap), since Postgres rejects `timestamp + int`.
    if is_postgres:
        return f"({column} + {days})"
    return f"DATE_ADD({column}, INTERVAL {days} DAY)"

def week_start(column, is_postgres):
    # Monday-anchored start of the week containing `column`. MySQL WEEKDAY() is
    # Monday=0..Sunday=6 and Postgres date_trunc('week') is also Monday-based,
    # so both anchor on the same day (do not use EXTRACT(DOW), it is Sunday=0).
    if is_postgres:
        return f"date_trunc('week', {column})"
    return f"DATE_SUB({column}, INTERVAL WEEKDAY({column}) DAY)"

def week_end(column, is_postgres):
    # Sunday-anchored end (week_start + 6 days) of the week containing `column`.
    if is_postgres:
        return f"(date_trunc('week', {column}) + INTERVAL '6 day')"
    return f"DATE_ADD(DATE_SUB({column}, INTERVAL WEEKDAY({column}) DAY), INTERVAL 6 DAY)"

def yearweek(column, is_postgres):
    # ISO year * 100 + ISO week number, e.g. 202426 (MySQL YEARWEEK(col, 1)).
    if is_postgres:
        return f"(EXTRACT(ISOYEAR FROM {column}) * 100 + EXTRACT(WEEK FROM {column}))::int"
    return f"YEARWEEK({column}, 1)"

def diff_minutes(start, end, is_postgres):
    # Whole minutes between two timestamps (expects end >= start).
    if is_postgres:
        return f"FLOOR(EXTRACT(EPOCH FROM ({end} - {start})) / 60)::int"
    return f"TIMESTAMPDIFF(MINUTE, {start}, {end})"

def diff_seconds(start, end, is_postgres):
    # Whole seconds between two timestamps (expects end >= start).
    if is_postgres:
        return f"FLOOR(EXTRACT(EPOCH FROM ({end} - {start})))::int"
    return f"TIMESTAMPDIFF(SECOND, {start}, {end})"

def datediff_days(end, start, is_postgres):
    # Whole days between two dates (MySQL DATEDIFF(end, start)). Both operands
    # are cast to ::date on Postgres, where `timestamp - timestamp` would yield
    # an interval rather than an integer day count.
    if is_postgres:
        return f"({end}::date - {start}::date)"
    return f"DATEDIFF({end}, {start})"

def last_day(column, is_postgres):
    # Last calendar day of the month containing `column`.
    if is_postgres:
        return f"(date_trunc('month', {column}) + INTERVAL '1 month - 1 day')::date"
    return f"LAST_DAY({column})"

def current_date(is_postgres):
    # Today's date.
    if is_postgres:
        return "CURRENT_DATE"
    return "CURDATE()"

def ratio_pct(numerator, denominator):
    # Percentage numerator / denominator * 100. Dialect-agnostic: the 100.0
    # forces float division (Postgres does integer division on int / int), and
    # NULLIF guards divide-by-zero so both dialects return NULL instead of
    # MySQL returning NULL while Postgres raises an error. Behaviour on MySQL is
    # unchanged from the original `numerator / denominator * 100`.
    return f"({numerator}) * 100.0 / NULLIF(({denominator}), 0)"

def field_order(column, values, is_postgres):
    # ORDER BY helper that preserves a fixed value sequence (MySQL FIELD()).
    quoted = ", ".join(f"'{v}'" for v in values)
    if is_postgres:
        return f"array_position(ARRAY[{quoted}], {column})"
    return f"FIELD({column}, {quoted})"
