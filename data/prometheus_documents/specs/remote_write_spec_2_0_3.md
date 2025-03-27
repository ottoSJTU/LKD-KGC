optional_primitive_fields
  // zero value means value not set. if you need to use exactly zero value for
  // the timestamp, use 1 millisecond before or after.
  int64 created_timestamp = 6;
}
// exemplar represents additional information attached to some series' samples.
message exemplar {
  // labels_refs is an optional list of label name-value pair references, encoded
  // as indices to the request.symbols array. this list's len is always
  // a multiple of 2, and the underlying labels should be sorted lexicographically.
  // if the exemplar references a trace it should use the `trace_id` label name, as a best practice.
  repeated uint32 labels_refs = 1;
  // value represents an exact example value. this can be useful when the exemplar
  // is attached to a histogram, which only gives an estimated value through buckets.
  double value = 2;
  // timestamp represents the timestamp of the exemplar in ms.
  // for go, see github.com/prometheus/prometheus/model/timestamp/timestamp.go
  // for conversion from/to time.time to prometheus timestamp.
  int64 timestamp = 3;
}
// sample represents series sample.
message sample {
  // value of the sample.
  double value = 1;
  // timestamp represents timestamp of the sample in ms.
  int64 timestamp = 2;
}
// metadata represents the metadata associated with the given series' samples.
message metadata {
  enum metrictype {
    metric_type_unspecified    = 0;
    metric_type_counter        = 1;
    metric_type_gauge          = 2;
    metric_type_histogram      = 3;
    metric_type_gaugehistogram = 4;
    metric_type_summary        = 5;
    metric_type_info           = 6;
    metric_type_stateset       = 7;
  }
  metrictype type = 1;
  // help_ref is a reference to the request.symbols array representing help
  // text for the metric. help is optional, reference should point to an empty string in
  // such a case.
  uint32 help_ref = 3;
  // unit_ref is a reference to the request.symbols array representing a unit
  // for the metric. unit is optional, reference should point to an empty string in
  // such a case.
  uint32 unit_ref = 4;
}
// a native histogram, also known as a sparse histogram.
// see
l142
// for a full message that follows the native histogram spec for both sparse
// and exponential, as well as, custom bucketing.
message histogram { ... }
```
all timestamps must be int64 counted as milliseconds since the unix epoch. sample's values must be float64.
for every `timeseries` message:
* `labels_refs` must be provided.
<!---
rationales: _remote-write-20.md
partial-writes
samples-vs-native-histogram-samples
-->
* at least one element in `samples` or in `histograms` must be provided. a `timeseries` must not include both `samples` and `histograms`. for series which (rarely) would mix float and histogram samples, a separate `timeseries` message must be used.
<!---
rationales: _remote-write-20.md
always-on-metadata
-->
* `metadata` sub-fields should be provided. receivers may reject series with unspecified `metadata.type`.
* exemplars should be provided if they exist for a series.
* `created_timestamp` should be provided for metrics that follow counter semantics (e.g. counters and histograms). receivers may reject those series without `created_timestamp` being set.
the following subsections define some schema elements in detail.
symbols
<!---
rationales: _remote-write-20.md
partial-writes
string-interning
-->
the `io.prometheus.write.v2.request` protobuf message is designed to [intern all strings](_interning) for the proven additional compression and memory efficiency gains on top of the standard compressions.
the `symbols` table must be provided and it must contain deduplicated strings used in series, exemplar labels, and metadata strings. the first element of the `symbols` table must be an empty string, which is used to represent empty or unspecified values such as when `metadata.unit_ref` or `metadata.help_ref` are not provided. references must point to the existing index in the `symbols` string array.
series labels
<!---
rationales: _remote-write-20.md
labels-and-utf-8
-->
the complete set of labels must be sent with each `sample` or `histogram` sample. additionally, the label set associated with samples:
* should contain a `__name__` label.
* must not contain repeated label names.
* must have label names sorted in lexicographical order.
* must not contain any empty label names or values.
metric names, label names, and label values must be any sequence of utf-8 characters.
metric names should adhere to the regex `[a-za-z_:]([a-za-z0-9_:])*`.
label names should adhere to the regex `[a-za-z_]([a-za-z0-9_])*`.
names that do not adhere to the above, might be harder to use for promql users (see [the utf-8 proposal for more details]()).
label names beginning with "__" are reserved for system usage and should not be used, see [prometheus data model](_model/).
receivers also may impose limits on the number and length of labels, but this is receiver-specific and is out of the scope of this document.
samples and histogram samples
<!---
rationales: _remote-write-20.md
partial-writes
native-histograms
-->
senders must send `samples` (or `histograms`) for any given `timeseries` in timestamp order. senders may send multiple requests for different series in parallel.
<!---
rationales: _remote-write-20.md
partial-writes
being-pull-vs-push-agnostic
-->
senders should send stale markers when a time series will no longer be appended to.
senders must send stale markers if the discontinuation of time series is possible to detect, for example:
* for series that were pulled (scraped), unless explicit timestamp was used.
* for series that is resulted by a recording rule evaluation.
generally, not sending stale markers for series that are discontinued can lead to the receiver [non-trivial query time alignment issues](
staleness).
stale markers must be signalled by the special nan value `0x7ff0000000000002`. this value must not be used otherwise.
typically, senders can detect when a time series will no longer be appended using the following techniques:
1. detecting, using service discovery, that the target exposing the series has gone away.
1. noticing the target is no longer exposing the time series between successive scrapes.
1. failing to scrape the target that originally exposed a time series.
1. tracking configuration and evaluation for recording and alerting rules.
1. tracking discontinuation of metrics for non-scrape source of metric (e.g. in k6 when the benchmark has finished for series per benchmark, it could emit a stale marker).
metadata
metadata should follow the official prometheus guidelines for [type](_exporters/
types) and [help](_exporters/
help-strings).
metadata may follow the official openmetrics guidelines for [unit](
unit).
exemplars
each exemplar, if attached to a `timeseries`:
* must contain a value.
<!---
rationales: _remote-write-20.md
partial-writes
exemplars
-->
* may contain labels e.g. referencing trace or request id. if the exemplar references a trace it should use the `trace_id` label name, as a best practice.
* must contain a timestamp. while exemplar timestamps are optional in prometheus/open metrics exposition formats, the assumption is that a timestamp is assigned at scrape time in the same way a timestamp is assigned to the scrape sample. receivers require exemplar timestamps to reliably handle (e.g. deduplicate) incoming exemplars.
out of scope
the same as in [1.0](./remote_write_spec.md
out-of-scope).
future plans
this section contains speculative plans that are not considered part of protocol specification yet but are mentioned here for completeness. note that 2.0 specification completed [2 of 3 future plans in the 1.0](./remote_write_spec.md
future-plans).
* **transactionality** there is still no transactionality defined for 2.0 specification, mostly because it makes a scalable sender implementation difficult. prometheus sender aims at being "transactional" - i.e. to never expose a partially scraped target to a query. we intend to do the same with remote-write -- for instance, in the future we would like to "align" remote-write with scrapes, perhaps such that all the samples, metadata and exemplars for a single scrape are sent in a single remote-write request.
  however, remote-write 2.0 specification solves an important transactionality problem for [the classic histogram buckets](
heading=h.ueg7q07wymku). this is done thanks to the native histograms supporting custom bucket-ing possible with the `io.prometheus.write.v2.request` wire format. senders might translate all classic histograms to native histograms this way, but it's out of this specification to mandate this. however, for this reason, receivers may ignore certain metric types (e.g. classic histograms).
* **alternative wire formats**. the opentelemetry community has shown the validity of apache arrow (and potentially other columnar formats) for over-wire data transfer with their otlp protocol. we would like to do experiments to confirm the compatibility of a similar format with prometheus’ data model and include benchmarks of any resource usage changes. we would potentially maintain both a protobuf and columnar format long term for compatibility reasons and use our content negotiation to add different protobuf messages for this purpose.
* **global symbols**. pre-defined string dictionary for interning the protocol could pre-define a static dictionary of ref->symbol that includes strings that are considered common, e.g. “namespace”, “le”, “job”, “seconds”, “bytes”, etc. senders could refer to these without the need to include them in the request’s symbols table. this dictionary could incrementally grow with minor version releases of this protocol.
related
faq
**why did you not use grpc?**
because the 1.0 protocol does not use grpc, breaking it would increase friction in the adoption. see 1.0 [reason](./remote_write_spec.md