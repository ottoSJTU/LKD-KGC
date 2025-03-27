---
title: exposition formats
sort_rank: 6
---
exposition formats
metrics can be exposed to prometheus using a simple [text-based](
text-based-format)
exposition format. there are various [client libraries](/docs/instrumenting/clientlibs/)
that implement this format for you. if your preferred language doesn't have a client
library you can [create your own](/docs/instrumenting/writing_clientlibs/).
text-based format
as of prometheus version 2.0, all processes that expose metrics to prometheus need to use
a text-based format. in this section you can find some [basic information](
basic-info)
about this format as well as a more [detailed breakdown](
text-format-details) of the
format.
basic info
| aspect | description |
|--------|-------------|
| **inception** | april 2014  |
| **supported in** |  prometheus version `>=0.4.0` |
| **transmission** | http |
| **encoding** | utf-8, `\n` line endings |
| **http `content-type`** | `text/plain; version=0.0.4` (a missing `version` value will lead to a fall-back to the most recent text format version.) |
| **optional http `content-encoding`** | `gzip` |
| **advantages** | <ul><li>human-readable</li><li>easy to assemble, especially for minimalistic cases (no nesting required)</li><li>readable line by line (with the exception of type hints and docstrings)</li></ul> |
| **limitations** | <ul><li>verbose</li><li>types and docstrings not integral part of the syntax, meaning little-to-nonexistent metric contract validation</li><li>parsing cost</li></ul>|
| **supported metric primitives** | <ul><li>counter</li><li>gauge</li><li>histogram</li><li>summary</li><li>untyped</li></ul> |
text format details
prometheus' text-based format is line oriented. lines are separated by a line
feed character (`\n`). the last line must end with a line feed character.
empty lines are ignored.
line format
within a line, tokens can be separated by any number of blanks and/or tabs (and
must be separated by at least one if they would otherwise merge with the previous
token). leading and trailing whitespace is ignored.
comments, help text, and type information
lines with a `
` as the first non-whitespace character are comments. they are
ignored unless the first token after `
` is either `help` or `type`. those
lines are treated as follows: if the token is `help`, at least one more token
is expected, which is the metric name. all remaining tokens are considered the
docstring for that metric name. `help` lines may contain any sequence of utf-8
characters (after the metric name), but the backslash and the line feed
characters have to be escaped as `\\` and `\n`, respectively. only one `help`
line may exist for any given metric name.
if the token is `type`, exactly two more tokens are expected. the first is the
metric name, and the second is either `counter`, `gauge`, `histogram`,
`summary`, or `untyped`, defining the type for the metric of that name. only
one `type` line may exist for a given metric name. the `type` line for a
metric name must appear before the first sample is reported for that metric
name. if there is no `type` line for a metric name, the type is set to
`untyped`.
the remaining lines describe samples (one per line) using the following syntax
([ebnf](_backus%e2%80%93naur_form)):
```
metric_name [
  "{" label_name "=" `"` label_value `"` { "," label_name "=" `"` label_value `"` } [ "," ] "}"
] value [ timestamp ]
```
in the sample syntax:
*  `metric_name` and `label_name` carry the usual prometheus expression language restrictions.
* `label_value` can be any sequence of utf-8 characters, but the backslash (`\`), double-quote (`"`), and line feed (`\n`) characters have to be escaped as `\\`, `\"`, and `\n`, respectively.
* `value` is a float represented as required by go's [`parsefloat()`](
parsefloat) function. in addition to standard numerical values, `nan`, `+inf`, and `-inf` are valid values representing not a number, positive infinity, and negative infinity, respectively.
* the `timestamp` is an `int64` (milliseconds since epoch, i.e. 1970-01-01 00:00:00 utc, excluding leap seconds), represented as required by go's [`parseint()`](
parseint) function.
grouping and sorting
all lines for a given metric must be provided as one single group, with
the optional `help` and `type` lines first (in no particular order). beyond
that, reproducible sorting in repeated expositions is preferred but not
required, i.e. do not sort if the computational cost is prohibitive.
each line must have a unique combination of a metric name and labels. otherwise,
the ingestion behavior is undefined.
histograms and summaries
the `histogram` and `summary` types are difficult to represent in the text
format. the following conventions apply:
* the sample sum for a summary or histogram named `x` is given as a separate sample named `x_sum`.
* the sample count for a summary or histogram named `x` is given as a separate sample named `x_count`.
* each quantile of a summary named `x` is given as a separate sample line with the same name `x` and a label `{quantile="y"}`.
* each bucket count of a histogram named `x` is given as a separate sample line with the name `x_bucket` and a label `{le="y"}` (where `y` is the upper bound of the bucket).
* a histogram _must_ have a bucket with `{le="+inf"}`. its value _must_ be identical to the value of `x_count`.
* the buckets of a histogram and the quantiles of a summary must appear in increasing numerical order of their label values (for the `le` or the `quantile` label, respectively).
text format example
below is an example of a full-fledged prometheus metric exposition, including
comments, `help` and `type` expressions, a histogram, a summary, character
escaping examples, and more.
```
help http_requests_total the total number of http requests.
type http_requests_total counter
http_requests_total{method="post",code="200"} 1027 1395066363000
http_requests_total{method="post",code="400"}    3 1395066363000
escaping in label values:
msdos_file_access_time_seconds{path="c:\\dir\\file.txt",error="cannot find file:\n\"file.txt\""} 1.458255915e9
minimalistic line:
metric_without_timestamp_and_labels 12.47
a weird metric from before the epoch:
something_weird{problem="division by zero"} +inf -3982045
a histogram, which has a pretty complex representation in the text format:
help http_request_duration_seconds a histogram of the request duration.
type http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.05"} 24054
http_request_duration_seconds_bucket{le="0.1"} 33444
http_request_duration_seconds_bucket{le="0.2"} 100392
http_request_duration_seconds_bucket{le="0.5"} 129389
http_request_duration_seconds_bucket{le="1"} 133988
http_request_duration_seconds_bucket{le="+inf"} 144320
http_request_duration_seconds_sum 53423
http_request_duration_seconds_count 144320
finally a summary, which has a complex representation, too:
help rpc_duration_seconds a summary of the rpc duration in seconds.
type rpc_duration_seconds summary
rpc_duration_seconds{quantile="0.01"} 3102
rpc_duration_seconds{quantile="0.05"} 3272
rpc_duration_seconds{quantile="0.5"} 4773
rpc_duration_seconds{quantile="0.9"} 9001
rpc_duration_seconds{quantile="0.99"} 76656
rpc_duration_seconds_sum 1.7560473e+07
rpc_duration_seconds_count 2693
```
openmetrics text format
[openmetrics]() is the an effort to standardize metric wire formatting built off of prometheus text format. it is possible to scrape targets
and it is also available to use for federating metrics since at least v2.23.0.
exemplars (experimental)
utilizing the openmetrics format allows for the exposition and querying of [exemplars](
exemplars).
exemplars provide a point in time snapshot related to a metric set for an otherwise summarized metricfamily. additionally they may have a trace id attached to them which when used to together
with a tracing system can provide more detailed information related to the specific service.
to enable this experimental feature you must have at least version v2.26.0 and add `--enable-feature=exemplar-storage` to your arguments.
protobuf format
earlier versions of prometheus supported an exposition format based on [protocol buffers]() (aka protobuf) in addition to the current text-based format. with prometheus 2.0, the protobuf format was marked as deprecated and prometheus stopped ingesting samples from said exposition format.
however, new experimental features were added to prometheus where the protobuf format was considered the most viable option. making prometheus accept protocol buffers once again.
here is a list of experimental features that, once enabled, will configure prometheus to favor the protobuf exposition format:
| feature flag | version that introduced it |
|--------------|----------------------------|
| native-histograms | 2.40.0 |
| created-timestamp-zero-ingestion | 2.50.0 |
historical versions
for details on historical format versions, see the legacy
[client data exposition format](=sharing)
document.
the current version of the original protobuf format (with the recent extensions
for native histograms) is maintained in the [prometheus/client_model
repository](_model).