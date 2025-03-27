---
title: data model
sort_rank: 1
---
---
---
data model
---
---
prometheus fundamentally stores all data as [_time
series_](_series): streams of timestamped
values belonging to the same metric and the same set of labeled dimensions.
besides stored time series, prometheus may generate temporary derived time series
as the result of queries.
metric names and labels
every time series is uniquely identified by its metric name and optional key-value pairs called labels.
***metric names:***
 * specify the general feature of a system that is measured (e.g. `http_requests_total` - the total number of http requests received). 
 * metric names may contain ascii letters, digits, underscores, and colons. it must match the regex `[a-za-z_:][a-za-z0-9_:]*`.
note: the colons are reserved for user defined recording rules. they should not be used by exporters or direct instrumentation.
***metric labels:***
 * enable prometheus's dimensional data model to identify any given combination of labels for the same metric name. it identifies a particular dimensional instantiation of that metric (for example: all http requests that used the method `post` to the `/api/tracks` handler). the query language allows filtering and aggregation based on these dimensions. 
 * the change of any label's value, including adding or removing labels, will create a new time series.
 * labels may contain ascii letters, numbers, as well as underscores. they must match the regex `[a-za-z_][a-za-z0-9_]*`. 
 * label names beginning with `__` (two "_") are reserved for internal use.
 * label values may contain any unicode characters.
 * labels with an empty label value are considered equivalent to labels that do not exist.
see also the [best practices for naming metrics and labels](/docs/practices/naming/).
samples
samples form the actual time series data. each sample consists of:
   * a float64 value
   * a millisecond-precision timestamp
note: beginning with prometheus v2.40, there is experimental support for native
histograms. instead of a simple float64, the sample value may now take the form
of a full histogram.
notation
given a metric name and a set of labels, time series are frequently identified
using this notation:
    <metric name>{<label name>=<label value>, ...}
for example, a time series with the metric name `api_http_requests_total` and
the labels `method="post"` and `handler="/messages"` could be written like
this:
    api_http_requests_total{method="post", handler="/messages"}
this is the same notation that [opentsdb]() uses.