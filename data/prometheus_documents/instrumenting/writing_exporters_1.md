---
title: writing exporters
sort_rank: 5
---
writing exporters
if you are instrumenting your own code, the [general rules of how to
instrument code with a prometheus client
library](/docs/practices/instrumentation/) should be followed. when
taking metrics from another monitoring or instrumentation system, things
tend not to be so black and white.
this document contains things you should consider when writing an
exporter or custom collector. the theory covered will also be of
interest to those doing direct instrumentation.
if you are writing an exporter and are unclear on anything here, please
contact us on irc (
prometheus on libera) or the [mailing
list](/community).
maintainability and purity
the main decision you need to make when writing an exporter is how much
work you’re willing to put in to get perfect metrics out of it.
if the system in question has only a handful of metrics that rarely
change, then getting everything perfect is an easy choice, a good
example of this is the [haproxy
exporter](_exporter).
on the other hand, if you try to get things perfect when the system has
hundreds of metrics that change frequently with new versions, then
you’ve signed yourself up for a lot of ongoing work. the [mysql
exporter](_exporter) is on this end
of the spectrum.
the [node exporter](_exporter) is a
mix of these, with complexity varying by module. for example, the
`mdadm` collector hand-parses a file and exposes metrics created
specifically for that collector, so we may as well get the metrics
right. for the `meminfo` collector the results vary across kernel
versions so we end up doing just enough of a transform to create valid
metrics.
configuration
when working with applications, you should aim for an exporter that
requires no custom configuration by the user beyond telling it where the
application is.  you may also need to offer the ability to filter out
certain metrics if they may be too granular and expensive on large
setups, for example the [haproxy
exporter](_exporter) allows
filtering of per-server stats. similarly, there may be expensive metrics
that are disabled by default.
when working with other monitoring systems, frameworks and protocols you
will often need to provide additional configuration or customization to
generate metrics suitable for prometheus. in the best case scenario, a
monitoring system has a similar enough data model to prometheus that you
can automatically determine how to transform metrics. this is the case
for [cloudwatch](_exporter),
[snmp](_exporter) and
[collectd](_exporter). at most, we
need the ability to let the user select which metrics they want to pull
out.
in other cases, metrics from the system are completely non-standard,
depending on the usage of the system and the underlying application.  in
that case the user has to tell us how to transform the metrics. the [jmx
exporter](_exporter) is the worst
offender here, with the
[graphite](_exporter) and
[statsd](_exporter) exporters also
requiring configuration to extract labels.
ensuring the exporter works out of the box without configuration, and
providing a selection of example configurations for transformation if
required, is advised.
yaml is the standard prometheus configuration format, all configuration
should use yaml by default.
metrics
naming
follow the [best practices on metric naming](/docs/practices/naming).
generally metric names should allow someone who is familiar with
prometheus but not a particular system to make a good guess as to what a
metric means.  a metric named `http_requests_total` is not extremely
useful - are these being measured as they come in, in some filter or
when they get to the user’s code?  and `requests_total` is even worse,
what type of requests?
with direct instrumentation, a given metric should exist within exactly
one file. accordingly, within exporters and collectors, a metric should
apply to exactly one subsystem and be named accordingly.
metric names should never be procedurally generated, except when writing
a custom collector or exporter.
metric names for applications should generally be prefixed by the
exporter name, e.g. `haproxy_up`.
metrics must use base units (e.g. seconds, bytes) and leave converting
them to something more readable to graphing tools. no matter what units
you end up using, the units in the metric name must match the units in
use. similarly, expose ratios, not percentages. even better, specify a
counter for each of the two components of the ratio.
metric names should not include the labels that they’re exported with,
e.g. `by_type`, as that won’t make sense if the label is aggregated
away.
the one exception is when you’re exporting the same data with different
labels via multiple metrics, in which case that’s usually the sanest way
to distinguish them. for direct instrumentation, this should only come
up when exporting a single metric with all the labels would have too
high a cardinality.
prometheus metrics and label names are written in `snake_case`.
converting `camelcase` to `snake_case` is desirable, though doing so
automatically doesn’t always produce nice results for things like
`mytcpexample` or `isnan` so sometimes it’s best to leave them as-is.
exposed metrics should not contain colons, these are reserved for user
defined recording rules to use when aggregating.
only `[a-za-z0-9:_]` are valid in metric names.
the `_sum`, `_count`, `_bucket` and `_total` suffixes are used by
summaries, histograms and counters. unless you’re producing one of
those, avoid these suffixes.
`_total` is a convention for counters, you should use it if you’re using
the counter type.
the `process_` and `scrape_` prefixes are reserved. it’s okay to add
your own prefix on to these if they follow matching semantics.
for example, prometheus has `scrape_duration_seconds` for how long a
scrape took, it's good practice to also have an exporter-centric metric,
e.g. `jmx_scrape_duration_seconds`, saying how long the specific
exporter took to do its thing. for process stats where you have access
to the pid, both go and python offer collectors that’ll handle this for
you. a good example of this is the [haproxy
exporter](_exporter).
when you have a successful request count and a failed request count, the
best way to expose this is as one metric for total requests and another
metric for failed requests. this makes it easy to calculate the failure
ratio. do not use one metric with a failed or success label. similarly,
with hit or miss for caches, it’s better to have one metric for total and
another for hits.
consider the likelihood that someone using monitoring will do a code or
web search for the metric name. if the names are very well-established
and unlikely to be used outside of the realm of people used to those
names, for example snmp and network engineers, then leaving them as-is
may be a good idea. this logic doesn’t apply for all exporters, for
example the mysql exporter metrics may be used by a variety of people,
not just dbas. a `help` string with the original name can provide most
of the same benefits as using the original names.
labels
read the [general
advice](/docs/practices/instrumentation/