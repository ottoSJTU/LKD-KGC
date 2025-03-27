---
title: query log
sort_rank: 1
---
using the prometheus query log
prometheus has the ability to log all the queries run by the engine to a log
file, as of 2.16.0. this guide demonstrates how to use that log file, which
fields it contains, and provides advanced tips about how to operate the log
file.
enable the query log
the query log can be toggled at runtime. it can therefore be activated when you
want to investigate slownesses or high load on your prometheus instance.
to enable or disable the query log, two steps are needed:
1. adapt the configuration to add or remove the query log configuration.
1. reload the prometheus server configuration.
logging all the queries to a file
this example demonstrates how to log all the queries to
a file called `/prometheus/query.log`. we will assume that `/prometheus` is the
data directory and that prometheus has write access to it.
first, adapt the `prometheus.yml` configuration file:
```yaml
global:
  scrape_interval:     15s
  evaluation_interval: 15s
  query_log_file: /prometheus/query.log
scrape_configs:
- job_name: 'prometheus'
  static_configs:
  - targets: ['localhost:9090']
```
then, [reload](/docs/prometheus/latest/management_api/
reload) the prometheus configuration:
```shell
$ curl -x post 
```
or, if prometheus is not launched with `--web.enable-lifecycle`, and you're not
running on windows, you can trigger the reload by sending a sighup to the
prometheus process.
the file `/prometheus/query.log` should now exist and all the queries
will be logged to that file.
to disable the query log, repeat the operation but remove `query_log_file` from
the configuration.
verifying if the query log is enabled
prometheus conveniently exposes metrics that indicates if the query log is
enabled and working:
```
help prometheus_engine_query_log_enabled state of the query log.
type prometheus_engine_query_log_enabled gauge
prometheus_engine_query_log_enabled 0
help prometheus_engine_query_log_failures_total the number of query log failures.
type prometheus_engine_query_log_failures_total counter
prometheus_engine_query_log_failures_total 0
```
the first metric, `prometheus_engine_query_log_enabled` is set to 1 of the
query log is enabled, and 0 otherwise.
the second one, `prometheus_engine_query_log_failures_total`, indicates the
number of queries that could not be logged.
format of the query log
the query log is a json-formatted log. here is an overview of the fields
present for a query:
```
{
    "params": {
        "end": "2020-02-08t14:59:50.368z",
        "query": "up == 0",
        "start": "2020-02-08t13:59:50.368z",
        "step": 5
    },
    "stats": {
        "timings": {
            "evaltotaltime": 0.000447452,
            "execqueuetime": 7.599e-06,
            "exectotaltime": 0.000461232,
            "innerevaltime": 0.000427033,
            "querypreparationtime": 1.4177e-05,
            "resultsorttime": 6.48e-07
        }
    },
    "ts": "2020-02-08t14:59:50.387z"
}
```
- `params`: the query. the start and end timestamp, the step and the actual
  query statement.
- `stats`: statistics. currently, it contains internal engine timers.
- `ts`: the timestamp when the query ended.
additionally, depending on what triggered the request, you will have additional
fields in the json lines.
api queries and consoles
http requests contain the client ip, the method, and the path:
```
{
    "httprequest": {
        "clientip": "127.0.0.1",
        "method": "get",
        "path": "/api/v1/query_range"
    }
}
```
the path will contain the web prefix if it is set, and can also point to a
console.
the client ip is the network ip address and does not take into consideration the
headers like `x-forwarded-for`. if you wish to log the original caller behind a
proxy, you need to do so in the proxy itself.
recording rules and alerts
recording rules and alerts contain a rulegroup element which contains the path
of the file and the name of the group:
```
{
    "rulegroup": {
        "file": "rules.yml",
        "name": "partners"
    }
}
```
rotating the query log
prometheus will not rotate the query log itself. instead, you can use external
tools to do so.
one of those tools is logrotate. it is enabled by default on most linux
distributions.
here is an example of file you can add as
`/etc/logrotate.d/prometheus`:
```
/prometheus/query.log {
    daily
    rotate 7
    compress
    delaycompress
    postrotate
        killall -hup prometheus
    endscript
}
```
that will rotate your file daily and keep one week of history.