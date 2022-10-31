# Presto / Trino notes

Presto was open-sourced as Trino. Trino has more up-to-date documentaiton (even for Presto!):

- https://trino.io/docs/current/functions/datetime.html

```sql
{% macro ts_to_local(ts, tz) %}
    (cast(from_iso8601_timestamp(date_format(AT_TIMEZONE(FROM_UNIXTIME({{ ts }}), {{ tz }}), '%Y-%m-%dT%H:%i:%s')) as timestamp))
{% endmacro %}
```


```sql
, tbl3 as
(
select
    *
      -- this crazy thing is just to export a local-tz-aware timestamp properly (unfortunately, this needs to be done by casting it as a tz-non-aware timestamp)
    , from_unixtime(to_unixtime(from_iso8601_timestamp(date_format(at_timezone(ts_utc, (select * from tbl_tz)), '%Y-%m-%dT%H:%i:%s'))))
        as ts_local
from
    tbl2
)
```
