---
title: faq
sort_rank: 5
toc: full-width
---
frequently asked questions
general
what is prometheus?
prometheus is an open-source systems monitoring and alerting toolkit
with an active ecosystem.
it is the only system directly supported by [kubernetes]() and the de facto standard across the [cloud native ecosystem]().
see the [overview](/docs/introduction/overview/).
how does prometheus compare against other monitoring systems?
see the [comparison](/docs/introduction/comparison/) page.
what dependencies does prometheus have?
the main prometheus server runs standalone as a single monolithic binary and has no external dependencies.
is this cloud native?
yes.
cloud native is a flexible operating model, breaking up old service boundaries to allow for more flexible and scalable deployments.
prometheus's [service discovery]() integrates with most tools and clouds. its dimensional data model and scale into the tens of millions of active series allows it to monitor large cloud-native deployments.
there are always trade-offs to make when running services, and prometheus values reliably getting alerts out to humans above all else.
can prometheus be made highly available?
yes, run identical prometheus servers on two or more separate machines.
identical alerts will be deduplicated by the [alertmanager]().
alertmanager supports [high availability](
high-availability) by interconnecting multiple alertmanager instances to build an alertmanager cluster. instances of a cluster communicate using a gossip protocol managed via [hashicorp's memberlist]() library.
i was told prometheus “doesn't scale”.
this is often more of a marketing claim than anything else.
a single instance of prometheus can be more performant than some systems positioning themselves as long term storage solution for prometheus.
you can run prometheus reliably with tens of millions of active series.
if you need more than that, there are several options. [scaling and federating prometheus]() on the robust perception blog is a good starting point, as are the long storage systems listed on our [integrations page](
remote-endpoints-and-storage).
what language is prometheus written in?
most prometheus components are written in go. some are also written in java,
python, and ruby.
how stable are prometheus features, storage formats, and apis?
all repositories in the prometheus github organization that have reached
version 1.0.0 broadly follow
[semantic versioning](). breaking changes are indicated by
increments of the major version. exceptions are possible for experimental
components, which are clearly marked as such in announcements.
even repositories that have not yet reached version 1.0.0 are, in general, quite
stable. we aim for a proper release process and an eventual 1.0.0 release for
each repository. in any case, breaking changes will be pointed out in release
notes (marked by `[change]`) or communicated clearly for components that do not
have formal releases yet.
why do you pull rather than push?
pulling over http offers a number of advantages:
* you can start extra monitoring instances as needed, e.g. on your laptop when developing changes.
* you can more easily and reliably tell if a target is down.
* you can manually go to a target and inspect its health with a web browser.
overall, we believe that pulling is slightly better than pushing, but it should
not be considered a major point when considering a monitoring system.
for cases where you must push, we offer the [pushgateway](/docs/instrumenting/pushing/).
how to feed logs into prometheus?
short answer: don't! use something like [grafana loki]() or [opensearch]() instead.
longer answer: prometheus is a system to collect and process metrics, not an
event logging system. the grafana blog post
[logs and metrics and graphs, oh my!]()
provides more details about the differences between logs and metrics.
if you want to extract prometheus metrics from application logs, grafana loki is designed for just that. see loki's [metric queries](_queries/) documentation.
who wrote prometheus?
prometheus was initially started privately by
[matt t. proud]() and
[julius volz](). the majority of its
initial development was sponsored by [soundcloud]().
it's now maintained and extended by a wide range of [companies](=1) and [individuals]().
what license is prometheus released under?
prometheus is released under the
[apache 2.0]() license.
what is the plural of prometheus?
after [extensive research](_cdeyrqxjq), it has been determined
that the correct plural of 'prometheus' is 'prometheis'.
if you can not remember this, "prometheus instances" is a good workaround.
can i reload prometheus's configuration?
yes, sending `sighup` to the prometheus process or an http post request to the
`/-/reload` endpoint will reload and apply the configuration file. the
various components attempt to handle failing changes gracefully.
can i send alerts?
yes, with the [alertmanager]().
we support sending alerts through [email, various native integrations](), and a [webhook system anyone can add integrations to](
alertmanager-webhook-receiver).
can i create dashboards?
yes, we recommend [grafana](/docs/visualization/grafana/) for production
usage. there are also [console templates](/docs/visualization/consoles/).
can i change the timezone? why is everything in utc?
to avoid any kind of timezone confusion, especially when the so-called
daylight saving time is involved, we decided to exclusively use unix
time internally and utc for display purposes in all components of
prometheus. a carefully done timezone selection could be introduced
into the ui. contributions are welcome. see
[issue
500]()
for the current state of this effort.
instrumentation
which languages have instrumentation libraries?
there are a number of client libraries for instrumenting your services with
prometheus metrics. see the [client libraries](/docs/instrumenting/clientlibs/)
documentation for details.
if you are interested in contributing a client library for a new language, see
the [exposition formats](/docs/instrumenting/exposition_formats/).
can i monitor machines?
yes, the [node exporter](_exporter) exposes
an extensive set of machine-level metrics on linux and other unix systems such
as cpu usage, memory, disk utilization, filesystem fullness, and network
bandwidth.
can i monitor network devices?
yes, the [snmp exporter](_exporter) allows
monitoring of devices that support snmp.
for industrial networks, there's also a [modbus exporter](_exporter).
can i monitor batch jobs?
yes, using the [pushgateway](/docs/instrumenting/pushing/). see also the
[best practices](/docs/practices/instrumentation/
batch-jobs) for monitoring batch
jobs.
what applications can prometheus monitor out of the box?
see [the list of exporters and integrations](/docs/instrumenting/exporters/).
can i monitor jvm applications via jmx?
yes, for applications that you cannot instrument directly with the java client, you can use the [jmx exporter](_exporter)
either standalone or as a java agent.
what is the performance impact of instrumentation?
performance across client libraries and languages may vary. for java,
[benchmarks](_java/blob/master/benchmarks/readme.md)
indicate that incrementing a counter/gauge with the java client will take
12-17ns, depending on contention. this is negligible for all but the most
latency-critical code.
implementation
why are all sample values 64-bit floats?
we restrained ourselves to 64-bit floats to simplify the design. the
[ieee 754 double-precision binary floating-point
format](_floating-point_format)
supports integer precision for values up to 2<sup>53</sup>. supporting
native 64 bit integers would (only) help if you need integer precision
above 2<sup>53</sup> but below 2<sup>63</sup>. in principle, support
for different sample value types (including some kind of big integer,
supporting even more than 64 bit) could be implemented, but it is not
a priority right now. a counter, even if incremented one million times per
second, will only run into precision issues after over 285 years.