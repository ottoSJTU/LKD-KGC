---
title: metric types
sort_rank: 2
---
metric types
the prometheus client libraries offer four core metric types. these are
currently only differentiated in the client libraries (to enable apis tailored
to the usage of the specific types) and in the wire protocol. the prometheus
server does not yet make use of the type information and flattens all data into
untyped time series. this may change in the future.
counter
a _counter_ is a cumulative metric that represents a single [monotonically 
increasing counter](_function) whose
value can only increase or be reset to zero on restart. for example, you can
use a counter to represent the number of requests served, tasks completed, or
errors.
do not use a counter to expose a value that can decrease. for example, do not
use a counter for the number of currently running processes; instead use a gauge.
client library usage documentation for counters:
   * [go](_golang/prometheus
counter)
   * [java](_java
counter)
   * [python](_python/instrumenting/counter/)
   * [ruby](_ruby
counter)
   * [.net](
counters)
gauge
a _gauge_ is a metric that represents a single numerical value that can
arbitrarily go up and down.
gauges are typically used for measured values like temperatures or current
memory usage, but also "counts" that can go up and down, like the number of
concurrent requests.
client library usage documentation for gauges:
   * [go](_golang/prometheus
gauge)
   * [java](_java
gauge)
   * [python](_python/instrumenting/gauge/)
   * [ruby](_ruby
gauge)
   * [.net](
gauges)
histogram
a _histogram_ samples observations (usually things like request durations or
response sizes) and counts them in configurable buckets. it also provides a sum
of all observed values.
a histogram with a base metric name of `<basename>` exposes multiple time series
during a scrape:
  * cumulative counters for the observation buckets, exposed as `<basename>_bucket{le="<upper inclusive bound>"}`
  * the **total sum** of all observed values, exposed as `<basename>_sum`
  * the **count** of events that have been observed, exposed as `<basename>_count` (identical to `<basename>_bucket{le="+inf"}` above)
use the
[`histogram_quantile()` function](/docs/prometheus/latest/querying/functions/
histogram_quantile)
to calculate quantiles from histograms or even aggregations of histograms. a
histogram is also suitable to calculate an
[apdex score](). when operating on buckets,
remember that the histogram is
[cumulative](
cumulative_histogram). see
[histograms and summaries](/docs/practices/histograms) for details of histogram
usage and differences to [summaries](
summary).
note: beginning with prometheus v2.40, there is experimental support for native
histograms. a native histogram requires only one time series, which includes a
dynamic number of buckets in addition to the sum and count of
observations. native histograms allow much higher resolution at a fraction of
the cost. detailed documentation will follow once native histograms are closer
to becoming a stable feature.
client library usage documentation for histograms:
   * [go](_golang/prometheus
histogram)
   * [java](_java
histogram)
   * [python](_python/instrumenting/histogram/)
   * [ruby](_ruby
histogram)
   * [.net](
histogram)
summary
similar to a _histogram_, a _summary_ samples observations (usually things like
request durations and response sizes). while it also provides a total count of
observations and a sum of all observed values, it calculates configurable
quantiles over a sliding time window.
a summary with a base metric name of `<basename>` exposes multiple time series
during a scrape:
  * streaming **φ-quantiles** (0 ≤ φ ≤ 1) of observed events, exposed as `<basename>{quantile="<φ>"}`
  * the **total sum** of all observed values, exposed as `<basename>_sum`
  * the **count** of events that have been observed, exposed as `<basename>_count`
see [histograms and summaries](/docs/practices/histograms) for
detailed explanations of φ-quantiles, summary usage, and differences
to [histograms](
histogram).
client library usage documentation for summaries:
   * [go](_golang/prometheus
summary)
   * [java](_java
summary)
   * [python](_python/instrumenting/summary/)
   * [ruby](_ruby
summary)
   * [.net](
summary)