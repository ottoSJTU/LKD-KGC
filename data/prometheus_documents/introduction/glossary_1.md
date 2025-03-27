---
title: glossary
sort_rank: 9
---
glossary
alert
an alert is the outcome of an alerting rule in prometheus that is
actively firing. alerts are sent from prometheus to the alertmanager.
alertmanager
the [alertmanager](../../alerting/overview/) takes in alerts, aggregates them into
groups, de-duplicates, applies silences, throttles, and then sends out
notifications to email, pagerduty, slack etc.
bridge
a bridge is a component that takes samples from a client library and
exposes them to a non-prometheus monitoring system. for example, the python, go, and java clients can export metrics to graphite.
client library
a client library is a library in some language (e.g. go, java, python, ruby)
that makes it easy to directly instrument your code, write custom collectors to
pull metrics from other systems and expose the metrics to prometheus.
collector
a collector is a part of an exporter that represents a set of metrics. it may be
a single metric if it is part of direct instrumentation, or many metrics if it is pulling metrics from another system.
direct instrumentation
direct instrumentation is instrumentation added inline as part of the source code of a program, using a [client library](
client-library).
endpoint
a source of metrics that can be scraped, usually corresponding to a single process.
exporter
an exporter is a binary running alongside the application you
want to obtain metrics from. the exporter exposes prometheus metrics, commonly by converting metrics that are exposed in a non-prometheus format into a format that prometheus supports.
instance
an instance is a label that uniquely identifies a target in a job.
job
a collection of targets with the same purpose, for example monitoring a group of like processes replicated for scalability or reliability, is called a job.
notification
a notification represents a group of one or more alerts, and is sent by the alertmanager to email, pagerduty, slack etc.
promdash
promdash was a native dashboard builder for prometheus. it has been deprecated and replaced by [grafana](../../visualization/grafana/).
prometheus
prometheus usually refers to the core binary of the prometheus system. it may
also refer to the prometheus monitoring system as a whole.
promql
[promql](/docs/prometheus/latest/querying/basics/) is the prometheus query language. it allows for
a wide range of operations including aggregation, slicing and dicing, prediction and joins.
pushgateway
the [pushgateway](../../instrumenting/pushing/) persists the most recent push
of metrics from batch jobs. this allows prometheus to scrape their metrics
after they have terminated.
recording rules
recording rules precompute frequently needed or computationally expensive expressions 
and save their results as a new set of time series.
remote read
remote read is a prometheus feature that allows transparent reading of time series from
other systems (such as long term storage) as part of queries.
remote read adapter
not all systems directly support remote read. a remote read adapter sits between
prometheus and another system, converting time series requests and responses between them.
remote read endpoint
a remote read endpoint is what prometheus talks to when doing a remote read.
remote write
remote write is a prometheus feature that allows sending ingested samples on the
fly to other systems, such as long term storage.
remote write adapter
not all systems directly support remote write. a remote write adapter sits
between prometheus and another system, converting the samples in the remote
write into a format the other system can understand.
remote write endpoint
a remote write endpoint is what prometheus talks to when doing a remote write.
sample
a sample is a single value at a point in time in a time series.
in prometheus, each sample consists of a float64 value and a millisecond-precision timestamp.
silence
a silence in the alertmanager prevents alerts, with labels matching the silence, from
being included in notifications.
target
a target is the definition of an object to scrape. for example, what labels to apply, any authentication required to connect, or other information that defines how the scrape will occur.
time series
the prometheus time series are streams of timestamped values belonging to the same metric and the same set of labeled dimensions.
prometheus stores all data as time series.