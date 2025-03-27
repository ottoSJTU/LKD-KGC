---
title: overview
sort_rank: 1
---
overview
what is prometheus?
[prometheus]() is an open-source systems
monitoring and alerting toolkit originally built at
[soundcloud](). since its inception in 2012, many
companies and organizations have adopted prometheus, and the project has a very
active developer and user [community](/community). it is now a standalone open source project
and maintained independently of any company. to emphasize this, and to clarify
the project's governance structure, prometheus joined the
[cloud native computing foundation]() in 2016
as the second hosted project, after [kubernetes]().
prometheus collects and stores its metrics as time series data, i.e. metrics information is stored with the timestamp at which it was recorded, alongside optional key-value pairs called labels.
for more elaborate overviews of prometheus, see the resources linked from the
[media](/docs/introduction/media/) section.
features
prometheus's main features are:
* a multi-dimensional [data model](/docs/concepts/data_model/) with time series data identified by metric name and key/value pairs
* promql, a [flexible query language](/docs/prometheus/latest/querying/basics/)
  to leverage this dimensionality
* no reliance on distributed storage; single server nodes are autonomous
* time series collection happens via a pull model over http
* [pushing time series](/docs/instrumenting/pushing/) is supported via an intermediary gateway
* targets are discovered via service discovery or static configuration
* multiple modes of graphing and dashboarding support
what are metrics?
metrics are numerical measurements in layperson terms. the term time series refers to the recording of changes over time. what users want to measure differs from application to application. for a web server, it could be request times; for a database, it could be the number of active connections or active queries, and so on.
metrics play an important role in understanding why your application is working in a certain way. let's assume you are running a web application and discover that it is slow. to learn what is happening with your application, you will need some information. for example, when the number of requests is high, the application may become slow. if you have the request count metric, you can determine the cause and increase the number of servers to handle the load.
components
the prometheus ecosystem consists of multiple components, many of which are
optional:
* the main [prometheus server]() which scrapes and stores time series data
* [client libraries](/docs/instrumenting/clientlibs/) for instrumenting application code
* a [push gateway]() for supporting short-lived jobs
* special-purpose [exporters](/docs/instrumenting/exporters/) for services like haproxy, statsd, graphite, etc.
* an [alertmanager]() to handle alerts
* various support tools
most prometheus components are written in [go](), making
them easy to build and deploy as static binaries.
architecture
this diagram illustrates the architecture of prometheus and some of
its ecosystem components:
![prometheus architecture](/assets/architecture.png)
prometheus scrapes metrics from instrumented jobs, either directly or via an
intermediary push gateway for short-lived jobs. it stores all scraped samples
locally and runs rules over this data to either aggregate and record new time
series from existing data or generate alerts. [grafana]() or
other api consumers can be used to visualize the collected data.
when does it fit?
prometheus works well for recording any purely numeric time series. it fits
both machine-centric monitoring as well as monitoring of highly dynamic
service-oriented architectures. in a world of microservices, its support for
multi-dimensional data collection and querying is a particular strength.
prometheus is designed for reliability, to be the system you go to
during an outage to allow you to quickly diagnose problems. each prometheus
server is standalone, not depending on network storage or other remote services.
you can rely on it when other parts of your infrastructure are broken, and
you do not need to setup extensive infrastructure to use it.
when does it not fit?
prometheus values reliability. you can always view what statistics are
available about your system, even under failure conditions. if you need 100%
accuracy, such as for per-request billing, prometheus is not a good choice as
the collected data will likely not be detailed and complete enough. in such a
case you would be best off using some other system to collect and analyze the
data for billing, and prometheus for the rest of your monitoring.