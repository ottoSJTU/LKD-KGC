---
title: comparison to alternatives
sort_rank: 4
---
comparison to alternatives
prometheus vs. graphite
scope
[graphite]() focuses on being a
passive time series database with a query language and graphing features. any
other concerns are addressed by external components.
prometheus is a full monitoring and trending system that includes built-in and
active scraping, storing, querying, graphing, and alerting based on time series
data. it has knowledge about what the world should look like (which endpoints
should exist, what time series patterns mean trouble, etc.), and actively tries
to find faults.
data model
graphite stores numeric samples for named time series, much like prometheus
does. however, prometheus's metadata model is richer: while graphite metric
names consist of dot-separated components which implicitly encode dimensions,
prometheus encodes dimensions explicitly as key-value pairs, called labels, attached
to a metric name. this allows easy filtering, grouping, and matching by these
labels via the query language.
further, especially when graphite is used in combination with
[statsd](), it is common to store only
aggregated data over all monitored instances, rather than preserving the
instance as a dimension and being able to drill down into individual
problematic instances.
for example, storing the number of http requests to api servers with the
response code `500` and the method `post` to the `/tracks` endpoint would
commonly be encoded like this in graphite/statsd:
```
stats.api-server.tracks.post.500 -> 93
```
in prometheus the same data could be encoded like this (assuming three api-server instances):
```
api_server_http_requests_total{method="post",handler="/tracks",status="500",instance="<sample1>"} -> 34
api_server_http_requests_total{method="post",handler="/tracks",status="500",instance="<sample2>"} -> 28
api_server_http_requests_total{method="post",handler="/tracks",status="500",instance="<sample3>"} -> 31
```
storage
graphite stores time series data on local disk in the
[whisper]() format, an
rrd-style database that expects samples to arrive at regular intervals. every
time series is stored in a separate file, and new samples overwrite old ones
after a certain amount of time.
prometheus also creates one local file per time series, but allows storing
samples at arbitrary intervals as scrapes or rule evaluations occur. since new
samples are simply appended, old data may be kept arbitrarily long. prometheus
also works well for many short-lived, frequently changing sets of time series.
summary
prometheus offers a richer data model and query language, in addition to being
easier to run and integrate into your environment. if you want a clustered
solution that can hold historical data long term, graphite may be a better
choice.
prometheus vs. influxdb
[influxdb]() is an open-source time series database,
with a commercial option for scaling and clustering. the influxdb project was
released almost a year after prometheus development began, so we were unable to
consider it as an alternative at the time. still, there are significant
differences between prometheus and influxdb, and both systems are geared
towards slightly different use cases.
scope
for a fair comparison, we must also consider
[kapacitor]() together with influxdb, as
in combination they address the same problem space as prometheus and the
alertmanager.
the same scope differences as in the case of
[graphite](
prometheus-vs-graphite) apply here for influxdb itself. in addition
influxdb offers continuous queries, which are equivalent to prometheus
recording rules.
kapacitor’s scope is a combination of prometheus recording rules, alerting
rules, and the alertmanager's notification functionality. prometheus offers [a
more powerful query language for graphing and
alerting]().
the prometheus alertmanager additionally offers grouping, deduplication and
silencing functionality.
data model / storage
like prometheus, the influxdb data model has key-value pairs as labels, which
are called tags. in addition, influxdb has a second level of labels called
fields, which are more limited in use. influxdb supports timestamps with up to
nanosecond resolution, and float64, int64, bool, and string data types.
prometheus, by contrast, supports the float64 data type with limited support for
strings, and millisecond resolution timestamps.
influxdb uses a variant of a [log-structured merge tree for storage with a write ahead log](_engine/),
sharded by time. this is much more suitable to event logging than prometheus's
append-only file per time series approach.
[logs and metrics and graphs, oh my!]()
describes the differences between event logging and metrics recording.
architecture
prometheus servers run independently of each other and only rely on their local
storage for their core functionality: scraping, rule processing, and alerting.
the open source version of influxdb is similar.
the commercial influxdb offering is, by design, a distributed storage cluster
with storage and queries being handled by many nodes at once.
this means that the commercial influxdb will be easier to scale horizontally,
but it also means that you have to manage the complexity of a distributed
storage system from the beginning. prometheus will be simpler to run, but at
some point you will need to shard servers explicitly along scalability
boundaries like products, services, datacenters, or similar aspects.
independent servers (which can be run redundantly in parallel) may also give
you better reliability and failure isolation.
kapacitor's open-source release has no built-in distributed/redundant options for 
rules,  alerting, or notifications.  the open-source release of kapacitor can 
be scaled via manual sharding by the user, similar to prometheus itself.
influx offers [enterprise kapacitor](_kapacitor), which supports an 
ha/redundant alerting system.
prometheus and the alertmanager by contrast offer a fully open-source redundant 
option via running redundant replicas of prometheus and using the alertmanager's 
[high availability](
high-availability)
mode.
summary
there are many similarities between the systems. both have labels (called tags
in influxdb) to efficiently support multi-dimensional metrics. both use
basically the same data compression algorithms. both have extensive
integrations, including with each other. both have hooks allowing you to extend
them further, such as analyzing data in statistical tools or performing
automated actions.
where influxdb is better:
  * if you're doing event logging.
  * commercial option offers clustering for influxdb, which is also better for long term data storage.
  * eventually consistent view of data between replicas.
where prometheus is better:
  * if you're primarily doing metrics.
  * more powerful query language, alerting, and notification functionality.
  * higher availability and uptime for graphing and alerting.
influxdb is maintained by a single commercial company following the open-core
model, offering premium features like closed-source clustering, hosting and
support. prometheus is a [fully open source and independent project](/community/), maintained
by a number of companies and individuals, some of whom also offer commercial services and support.
prometheus vs. opentsdb
[opentsdb]() is a distributed time series database based on
[hadoop]() and [hbase]().
scope
the same scope differences as in the case of
[graphite](/docs/introduction/comparison/
prometheus-vs-graphite) apply here.
data model
opentsdb's data model is almost identical to prometheus's: time series are
identified by a set of arbitrary key-value pairs (opentsdb tags are
prometheus labels). all data for a metric is 
[stored together](_guide/writing/index.html
time-series-cardinality),
limiting the cardinality of metrics. there are minor differences though: prometheus
allows arbitrary characters in label values, while opentsdb is more restrictive. 
opentsdb also lacks a full query language, only allowing simple aggregation and math via its api.
storage
[opentsdb]()'s storage is implemented on top of
[hadoop]() and [hbase](). this
means that it is easy to scale opentsdb horizontally, but you have to accept
the overall complexity of running a hadoop/hbase cluster from the beginning.
prometheus will be simpler to run initially, but will require explicit sharding
once the capacity of a single node is exceeded.
summary
prometheus offers a much richer query language, can handle higher cardinality
metrics, and forms part of a complete monitoring system. if you're already
running hadoop and value long term storage over these benefits, opentsdb is a
good choice.
prometheus vs. nagios
[nagios]() is a monitoring system that originated in the
1990s as netsaint.
scope
nagios is primarily about alerting based on the exit codes of scripts. these are 
called “checks”. there is silencing of individual alerts, however no grouping, 
routing or deduplication.
there are a variety of plugins. for example, piping the few kilobytes of
perfdata plugins are allowed to return [to a time series database such as graphite]() or using nrpe to [run checks on remote machines]().
data model
nagios is host-based. each host can have one or more services and each service
can perform one check.
there is no notion of labels or a query language.
storage
nagios has no storage per-se, beyond the current check state.
there are plugins which can store data such as [for visualisation]().
architecture
nagios servers are standalone. all configuration of checks is via file.
summary
nagios is suitable for basic monitoring of small and/or static systems where
blackbox probing is sufficient.
if you want to do whitebox monitoring, or have a dynamic or cloud based
environment, then prometheus is a good choice.
prometheus vs. sensu
[sensu]() is an open source monitoring and observability pipeline with a commercial distribution which offers additional features for scalability. it can reuse existing nagios plugins.
scope
sensu is an observability pipeline that focuses on processing and alerting of observability data as a stream of [events](). it provides an extensible framework for event [filtering](), aggregation, [transformation](), and [processing]() – including sending alerts to other systems and storing events in third-party systems. sensu's event processing capabilities are similar in scope to prometheus alerting rules and alertmanager.
data model
sensu [events]() represent service health and/or [metrics](
metric-attributes) in a structured data format identified by an [entity]() name (e.g. server, cloud compute instance, container, or service), an event name, and optional [key-value metadata](
metadata-attributes) called "labels" or "annotations". the sensu event payload may include one or more metric [`points`](