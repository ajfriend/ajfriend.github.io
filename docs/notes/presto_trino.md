# Presto / Trino notes

Presto was open-sourced as Trino. Trino has more up-to-date documentaiton (even for Presto!):

- https://trino.io/docs/current/functions/datetime.html

```sql
{% macro ts_to_local(ts, tz) %}
    (cast(from_iso8601_timestamp(date_format(AT_TIMEZONE(FROM_UNIXTIME({{ ts }}), {{ tz }}), '%Y-%m-%dT%H:%i:%s')) as timestamp))
{% endmacro %}
```
