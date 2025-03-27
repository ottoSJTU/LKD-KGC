---
title: metric and label naming
sort_rank: 1
---
metric and label naming
the metric and label conventions presented in this document are not required
for using prometheus, but can serve as both a style-guide and a collection of
best practices. individual organizations may want to approach some of these
practices, e.g. naming conventions, differently.
metric names
a metric name...
* ...must comply with the [data model](/docs/concepts/data_model/
metric-names-and-labels) for valid characters.
* ...should have a (single-word) application prefix relevant to the domain the
  metric belongs to. the prefix is sometimes referred to as `namespace` by
  client libraries. for metrics specific to an application, the prefix is
  usually the application name itself. sometimes, however, metrics are more
  generic, like standardized metrics exported by client libraries. examples:
 * <code><b>prometheus</b>\_notifications\_total</code>
   (specific to the prometheus server)
 * <code><b>process</b>\_cpu\_seconds\_total</code>
   (exported by many client libraries)
 * <code><b>http</b>\_request\_duration\_seconds</code>
   (for all http requests)
* ...must have a single unit (i.e. do not mix seconds with milliseconds, or seconds with bytes).
* ...should use base units (e.g. seconds, bytes, meters - not milliseconds, megabytes, kilometers). see below for a list of base units.
* ...should have a suffix describing the unit, in plural form. note that an accumulating count has `total` as a suffix, in addition to the unit if applicable.
 * <code>http\_request\_duration\_<b>seconds</b></code>
 * <code>node\_memory\_usage\_<b>bytes</b></code>
 * <code>http\_requests\_<b>total</b></code>
   (for a unit-less accumulating count)
 * <code>process\_cpu\_<b>seconds\_total</b></code>
   (for an accumulating count with unit)
 * <code>foobar_build<b>\_info</b></code>
   (for a pseudo-metric that provides [metadata]() about the running binary)
 * <code>data\_pipeline\_last\_record\_processed\_<b>timestamp_seconds</b></code>
  (for a timestamp that tracks the time of the latest record processed in a data processing pipeline)
* ...should represent the same logical thing-being-measured across all label
  dimensions.
 * request duration
 * bytes of data transfer
 * instantaneous resource usage as a percentage
as a rule of thumb, either the `sum()` or the `avg()` over all dimensions of a
given metric should be meaningful (though not necessarily useful). if it is not
meaningful, split the data up into multiple metrics. for example, having the
capacity of various queues in one metric is good, while mixing the capacity of a
queue with the current number of elements in the queue is not.
labels
use labels to differentiate the characteristics of the thing that is being measured:
 * `api_http_requests_total` - differentiate request types: `operation="create|update|delete"`
 * `api_request_duration_seconds` - differentiate request stages: `stage="extract|transform|load"`
do not put the label names in the metric name, as this introduces redundancy
and will cause confusion if the respective labels are aggregated away.
caution: remember that every unique combination of key-value label
pairs represents a new time series, which can dramatically increase the amount
of data stored. do not use labels to store dimensions with high cardinality
(many different label values), such as user ids, email addresses, or other
unbounded sets of values.
base units
prometheus does not have any units hard coded. for better compatibility, base
units should be used. the following lists some metrics families with their base unit.
the list is not exhaustive.
| family | base unit | remark |
| -------| --------- | ------ |
| time   | seconds   |        |
| temperature | celsius | _celsius_ is preferred over _kelvin_ for practical reasons. _kelvin_ is acceptable as a base unit in special cases like color temperature or where temperature has to be absolute. |
| length | meters | |
| bytes  | bytes | |
| bits   | bytes | to avoid confusion combining different metrics, always use _bytes_, even where _bits_ appear more common. |
| percent | ratio | values are 0–1 (rather than 0–100). `ratio` is only used as a suffix for names like `disk_usage_ratio`. the usual metric name follows the pattern `a_per_b`. |
| voltage | volts | |
| electric current | amperes | |
| energy | joules | |
| power  | | prefer exporting a counter of joules, then `rate(joules[5m])` gives you power in watts. |
| mass   | grams | _grams_ is preferred over _kilograms_ to avoid issues with the _kilo_ prefix. |