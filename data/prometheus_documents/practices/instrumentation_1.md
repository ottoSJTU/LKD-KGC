---
title: instrumentation
sort_rank: 3
---
instrumentation
this page provides an opinionated set of guidelines for instrumenting your code.
how to instrument
the short answer is to instrument everything. every library, subsystem and
service should have at least a few metrics to give you a rough idea of how it is
performing.
instrumentation should be an integral part of your code. instantiate the metric
classes in the same file you use them. this makes going from alert to console to code
easy when you are chasing an error.
the three types of services
for monitoring purposes, services can generally be broken down into three types:
online-serving, offline-processing, and batch jobs. there is overlap between
them, but every service tends to fit well into one of these categories.
online-serving systems
an online-serving system is one where a human or another system is expecting an
immediate response. for example, most database and http requests fall into
this category.
the key metrics in such a system are the number of performed queries, errors,
and latency. the number of in-progress requests can also be useful.
for counting failed queries, see section [failures](
failures) below.
online-serving systems should be monitored on both the client and server side.
if the two sides see different behaviors, that is very useful information for debugging.
if a service has many clients, it is not practical for the service to track them
individually, so they have to rely on their own stats.
be consistent in whether you count queries when they start or when they end.
when they end is suggested, as it will line up with the error and latency stats,
and tends to be easier to code.
offline processing
for offline processing, no one is actively waiting for a response, and batching
of work is common. there may also be multiple stages of processing.
for each stage, track the items coming in, how many are in progress, the last
time you processed something, and how many items were sent out. if batching, you
should also track batches going in and out.
knowing the last time that a system processed something is useful for detecting if it has stalled,
but it is very localised information. a better approach is to send a heartbeat
through the system: some dummy item that gets passed all the way through
and includes the timestamp when it was inserted. each stage can export the most
recent heartbeat timestamp it has seen, letting you know how long items are
taking to propagate through the system. for systems that do not have quiet
periods where no processing occurs, an explicit heartbeat may not be needed.
batch jobs
there is a fuzzy line between offline-processing and batch jobs, as offline
processing may be done in batch jobs. batch jobs are distinguished by the
fact that they do not run continuously, which makes scraping them difficult.
the key metric of a batch job is the last time it succeeded. it is also useful to track
how long each major stage of the job took, the overall runtime and the last
time the job completed (successful or failed). these are all gauges, and should
be [pushed to a pushgateway](/docs/instrumenting/pushing/).
there are generally also some overall job-specific statistics that would be
useful to track, such as the total number of records processed.
for batch jobs that take more than a few minutes to run, it is useful to also
scrape them using pull-based monitoring. this lets you track the same metrics over time
as for other types of jobs, such as resource usage and latency when talking to other
systems. this can aid debugging if the job starts to get slow.
for batch jobs that run very often (say, more often than every 15 minutes), you should
consider converting them into daemons and handling them as offline-processing jobs.
subsystems
in addition to the three main types of services, systems have sub-parts that
should also be monitored.
libraries
libraries should provide instrumentation with no additional configuration
required by users.
if it is a library used to access some resource outside of the process (for example,
network, disk, or ipc), track the overall query count, errors (if errors are possible)
and latency at a minimum.
depending on how heavy the library is, track internal errors and
latency within the library itself, and any general statistics you think may be
useful.
a library may be used by multiple independent parts of an application against
different resources, so take care to distinguish uses with labels where
appropriate. for example, a database connection pool should distinguish the databases
it is talking to, whereas there is no need to differentiate
between users of a dns client library.
logging
as a general rule, for every line of logging code you should also have a
counter that is incremented. if you find an interesting log message, you want to
be able to see how often it has been happening and for how long.
if there are multiple closely-related log messages in the same function (for example,
different branches of an if or switch statement), it can sometimes make sense to
increment a single counter for all of them.
it is also generally useful to export the total number of info/error/warning
lines that were logged by the application as a whole, and check for significant
differences as part of your release process.
failures
failures should be handled similarly to logging. every time there is a failure, a
counter should be incremented. unlike logging, the error may also bubble up to a
more general error counter depending on how your code is structured.
when reporting failures, you should generally have some other metric
representing the total number of attempts. this makes the failure ratio easy to calculate.
threadpools
for any sort of threadpool, the key metrics are the number of queued requests, the number of
threads in use, the total number of threads, the number of tasks processed, and how long they took.
it is also useful to track how long things were waiting in the queue.
caches
the key metrics for a cache are total queries, hits, overall latency and then
the query count, errors and latency of whatever online-serving system the cache is in front of.
collectors
when implementing a non-trivial custom metrics collector, it is advised to export a
gauge for how long the collection took in seconds and another for the number of
errors encountered.
this is one of the two cases when it is okay to export a duration as a gauge
rather than a summary or a histogram, the other being batch job durations. this
is because both represent information about that particular push/scrape, rather
than tracking multiple durations over time.
things to watch out for
there are some general things to be aware of when doing monitoring, and also
prometheus-specific ones in particular.
use labels
few monitoring systems have the notion of labels and an expression language to
take advantage of them, so it takes a bit of getting used to.
when you have multiple metrics that you want to add/average/sum, they should
usually be one metric with labels rather than multiple metrics.
for example, rather than `http_responses_500_total` and `http_responses_403_total`,
create a single metric called `http_responses_total` with a `code` label
for the http response code. you can then process the entire metric as one in
rules and graphs.
as a rule of thumb, no part of a metric name should ever be procedurally
generated (use labels instead). the one exception is when proxying metrics
from another monitoring/instrumentation system.
see also the [naming](/docs/practices/naming/) section.
do not overuse labels
each labelset is an additional time series that has ram, cpu, disk, and network
costs. usually the overhead is negligible, but in scenarios with lots of
metrics and hundreds of labelsets across hundreds of servers, this can add up
quickly.
as a general guideline, try to keep the cardinality of your metrics below 10,
and for metrics that exceed that, aim to limit them to a handful across your
whole system. the vast majority of your metrics should have no labels.
if you have a metric that has a cardinality over 100 or the potential to grow
that large, investigate alternate solutions such as reducing the number of
dimensions or moving the analysis away from monitoring and to a general-purpose
processing system.
to give you a better idea of the underlying numbers, let's look at node\_exporter.
node\_exporter exposes metrics for every mounted filesystem. every node will have
in the tens of timeseries for, say, `node_filesystem_avail`. if you have
10,000 nodes, you will end up with roughly 100,000 timeseries for
`node_filesystem_avail`, which is fine for prometheus to handle.
if you were to now add quota per user, you would quickly reach a double digit
number of millions with 10,000 users on 10,000 nodes. this is too much for the
current implementation of prometheus. even with smaller numbers, there's an
opportunity cost as you can't have other, potentially more useful metrics on
this machine any more.
if you are unsure, start with no labels and add more labels over time as
concrete use cases arise.
counter vs. gauge, summary vs. histogram
it is important to know which of the four main metric types to use for
a given metric.
to pick between counter and gauge, there is a simple rule of thumb: if
the value can go down, it is a gauge.
counters can only go up (and reset, such as when a process restarts). they are
useful for accumulating the number of events, or the amount of something at
each event. for example, the total number of http requests, or the total number of
bytes sent in http requests. raw counters are rarely useful. use the
`rate()` function to get the per-second rate at which they are increasing.
gauges can be set, go up, and go down. they are useful for snapshots of state,
such as in-progress requests, free/total memory, or temperature. you should
never take a `rate()` of a gauge.
summaries and histograms are more complex metric types discussed in
[their own section](/docs/practices/histograms/).