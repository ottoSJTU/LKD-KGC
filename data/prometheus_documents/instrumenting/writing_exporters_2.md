things-to-watch-out-for) on
labels.
avoid `type` as a label name, it’s too generic and often meaningless.
you should also try where possible to avoid names that are likely to
clash with target labels, such as `region`, `zone`, `cluster`,
`availability_zone`, `az`, `datacenter`, `dc`, `owner`, `customer`,
`stage`, `service`, `environment` and `env`. if, however, that’s what
the application calls some resource, it’s best not to cause confusion by
renaming it.
avoid the temptation to put things into one metric just because they
share a prefix. unless you’re sure something makes sense as one metric,
multiple metrics is safer.
the label `le` has special meaning for histograms, and `quantile` for
summaries. avoid these labels generally.
read/write and send/receive are best as separate metrics, rather than as
a label. this is usually because you care about only one of them at a
time, and it is easier to use them that way.
the rule of thumb is that one metric should make sense when summed or
averaged.  there is one other case that comes up with exporters, and
that’s where the data is fundamentally tabular and doing otherwise would
require users to do regexes on metric names to be usable. consider the
voltage sensors on your motherboard, while doing math across them is
meaningless, it makes sense to have them in one metric rather than
having one metric per sensor. all values within a metric should
(almost) always have the same unit, for example consider if fan speeds
were mixed in with the voltages, and you had no way to automatically
separate them.
don’t do this:
<pre>
my_metric{label="a"} 1
my_metric{label="b"} 6
<b>my_metric{label="total"} 7</b>
</pre>
or this:
<pre>
my_metric{label="a"} 1
my_metric{label="b"} 6
<b>my_metric{} 7</b>
</pre>
the former breaks for people who do a `sum()` over your metric, and the
latter breaks sum and is quite difficult to work with. some client
libraries, for example go, will actively try to stop you doing the
latter in a custom collector, and all client libraries should stop you
from doing the latter with direct instrumentation. never do either of
these, rely on prometheus aggregation instead.
if your monitoring exposes a total like this, drop the total. if you
have to keep it around for some reason, for example the total includes
things not counted individually, use different metric names.
instrumentation labels should be minimal, every extra label is one more
that users need to consider when writing their promql. accordingly,
avoid having instrumentation labels which could be removed without
affecting the uniqueness of the time series. additional information
around a metric can be added via an info metric, for an example see
below how to handle version numbers.
however, there are cases where it is expected that virtually all users of
a metric will want the additional information. if so, adding a
non-unique label, rather than an info metric, is the right solution. for
example the
[mysqld_exporter](_exporter)'s
`mysqld_perf_schema_events_statements_total`'s `digest` label is a hash
of the full query pattern and is sufficient for uniqueness. however, it
is of little use without the human readable `digest_text` label, which
for long queries will contain only the start of the query pattern and is
thus not unique. thus we end up with both the `digest_text` label for
humans and the `digest` label for uniqueness.
target labels, not static scraped labels
if you ever find yourself wanting to apply the same label to all of your
metrics, stop.
there’s generally two cases where this comes up.
the first is for some label it would be useful to have on the metrics
such as the version number of the software. instead, use the approach
described at
[]().
the second case is when a label is really a target label. these are
things like region, cluster names, and so on, that come from your
infrastructure setup rather than the application itself. it’s not for an
application to say where it fits in your label taxonomy, that’s for the
person running the prometheus server to configure and different people
monitoring the same application may give it different names.
accordingly, these labels belong up in the scrape configs of prometheus
via whatever service discovery you’re using. it’s okay to apply the
concept of machine roles here as well, as it’s likely useful information
for at least some people scraping it.
types
you should try to match up the types of your metrics to prometheus
types. this usually means counters and gauges. the `_count` and `_sum`
of summaries are also relatively common, and on occasion you’ll see
quantiles. histograms are rare, if you come across one remember that the
exposition format exposes cumulative values.
often it won’t be obvious what the type of metric is, especially if
you’re automatically processing a set of metrics. in general `untyped`
is a safe default.
counters can’t go down, so if you have a counter type coming from
another instrumentation system that can be decremented, for example
dropwizard metrics then it's not a counter, it's a gauge. `untyped` is
probably the best type to use there, as `gauge` would be misleading if
it were being used as a counter.
help strings
when you’re transforming metrics it’s useful for users to be able to
track back to what the original was, and what rules were in play that
caused that transformation. putting in the name of the
collector or exporter, the id of any rule that was applied and the
name and details of the original metric into the help string will greatly
aid users.
prometheus doesn’t like one metric having different help strings. if
you’re making one metric from many others, choose one of them to put in
the help string.
for examples of this, the snmp exporter uses the oid and the jmx
exporter puts in a sample mbean name. the [haproxy
exporter](_exporter) has
hand-written strings. the [node
exporter](_exporter) also has a wide
variety of examples.
drop less useful statistics
some instrumentation systems expose 1m, 5m, 15m rates, average rates since
application start (these are called `mean` in dropwizard metrics for
example) in addition to minimums, maximums and standard deviations.
these should all be dropped, as they’re not very useful and add clutter.
prometheus can calculate rates itself, and usually more accurately as
the averages exposed are usually exponentially decaying. you don’t know
what time the min or max were calculated over, and the standard deviation
is statistically useless and you can always expose sum of squares,
`_sum` and `_count` if you ever need to calculate it.
quantiles have related issues, you may choose to drop them or put them
in a summary.
dotted strings
many monitoring systems don’t have labels, instead doing things like
`my.class.path.mymetric.labelvalue1.labelvalue2.labelvalue3`.
the [graphite](_exporter) and
[statsd](_exporter) exporters share
a way of transforming these with a small configuration language. other
exporters should implement the same. the transformation is currently
implemented only in go, and would benefit from being factored out into a
separate library.
collectors
when implementing the collector for your exporter, you should never use
the usual direct instrumentation approach and then update the metrics on
each scrape.
rather create new metrics each time. in go this is done with
[mustnewconstmetric](_golang/prometheus
mustnewconstmetric)
in your `collect()` method. for python see
[_python
custom-collectors](_python/collector/custom/)
and for java generate a `list<metricfamilysamples>` in your collect
method, see
[standardexports.java](_java/blob/master/simpleclient_hotspot/src/main/java/io/prometheus/client/hotspot/standardexports.java)
for an example.
the reason for this is two-fold. firstly, two scrapes could happen at
the same time, and direct instrumentation uses what are effectively
file-level global variables, so you’ll get race conditions. secondly, if
a label value disappears, it’ll still be exported.
instrumenting your exporter itself via direct instrumentation is fine,
e.g. total bytes transferred or calls performed by the exporter across
all scrapes.  for exporters such as the [blackbox
exporter](_exporter) and [snmp
exporter](_exporter), which aren’t
tied to a single target, these should only be exposed on a vanilla
`/metrics` call, not on a scrape of a particular target.
metrics about the scrape itself
sometimes you’d like to export metrics that are about the scrape, like
how long it took or how many records you processed.
these should be exposed as gauges as they’re about an event, the scrape,
and the metric name prefixed by the exporter name, for example
`jmx_scrape_duration_seconds`. usually the `_exporter` is excluded and
if the exporter also makes sense to use as just a collector, then
definitely exclude it.
machine and process metrics
many systems, for example elasticsearch, expose machine metrics such as
cpu, memory and filesystem information. as the [node
exporter](_exporter) provides these in
the prometheus ecosystem, such metrics should be dropped.
in the java world, many instrumentation frameworks expose process-level
and jvm-level stats such as cpu and gc. the java client and jmx exporter
already include these in the preferred form via
[defaultexports.java](_java/blob/master/simpleclient_hotspot/src/main/java/io/prometheus/client/hotspot/defaultexports.java),
so these should also be dropped.
similarly with other languages and frameworks.