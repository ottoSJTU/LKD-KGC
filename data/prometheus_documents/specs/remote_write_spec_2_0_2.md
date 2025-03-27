required `written` response headers
<!---
rationales: 
-->
upon a successful content negotiation, receivers process (write) the received batch of data. once completed (with success or failure) for each important piece of data (currently samples, histograms and exemplars) receivers must send a dedicated http `x-prometheus-remote-write-*-written` response header with the precise number of successfully written elements.
each header value must be a single 64-bit integer. the header names must be as follows:
```
x-prometheus-remote-write-samples-written <count of all successfully written samples>
x-prometheus-remote-write-histograms-written <count of all successfully written histogram samples>
x-prometheus-remote-write-exemplars-written <count of all successfully written exemplars>
```
upon receiving a 2xx or a 4xx status code, senders can assume that any missing `x-prometheus-remote-write-*-written` response header means no element from this category (e.g. sample) was written by the receiver (count of `0`). senders must not assume the same when using the deprecated `prometheus.writerequest` protobuf message due to the risk of hitting 1.0 receiver without this feature.
senders may use those headers to confirm which parts of data were successfully written by the receiver. common use cases:
* better handling of the [partial write](
partial-write) failure situations: senders may use those headers for more accurate client instrumentation and error handling.
* detecting broken 1.0 receiver implementations: senders should assume [415 http unsupported media type](
name-415-unsupported-media-type) status code when sending the data using `io.prometheus.write.v2.request` request and receiving 2xx http status code, but none of the `x-prometheus-remote-write-*-written` response headers from the receiver. this is a common issue for the 1.0 receivers that do not check the `content-type` request header; accidental decoding of the `io.prometheus.write.v2.request` payload with `prometheus.writerequest` schema results in empty result and no decoding errors.
* detecting other broken implementations or issues: senders may use those headers to detect broken sender and receiver implementations or other problems.
senders must not assume what remote write specification version the receiver implements from the remote write response headers.
more (optional) headers might come in the future, e.g. when more entities or fields are added and worth confirming.
partial write
<!---
rationales: _remote-write-20.md
partial-writes
-->
senders should use remote-write to send samples for multiple series in a single request. as a result, receivers may write valid samples within a write request that also contains some invalid or otherwise unwritten samples, which represents a partial write case. in such a case, the receiver must return non-2xx status code following the [invalid samples](
invalid-samples) and [retry on partial writes](
retries-on-partial-writes) sections.
unsupported request content
receivers must return [415 http unsupported media type](
name-415-unsupported-media-type) status code if they don't support a given content type or encoding provided by senders.
senders should expect [400 http bad request](
name-400-bad-request) for the above reasons from 1.x receivers, for backwards compatibility.
invalid samples
receivers may not support certain metric types or samples (e.g. a receiver might reject sample without metadata type specified or without created timestamp, while another receiver might accept such sample.). it’s up to the receiver what sample is invalid. receivers must return a [400 http bad request](
name-400-bad-request) status code for write requests that contain any invalid samples unless the [partial retriable write](
retries-on-partial-writes) occurs.
senders must not retry on a 4xx http status codes (other than [429]()), which must be used by receivers to indicate that the write operation will never be able to succeed and should not be retried. senders may retry on the 415 http status code with a different content type or encoding to see if the receiver supports it.
retries & backoff
receivers may return a [429 http too many requests]() status code to indicate the overloaded server situation. receivers may return [the retry-after](
name-retry-after) header to indicate the time for the next write attempt. receivers may return a 5xx http status code to represent internal server errors.
senders may retry on a 429 http status code. senders must retry write requests on 5xx http. senders must use a backoff algorithm to prevent overwhelming the server. senders may handle [the retry-after response header](
name-retry-after) to estimate the next retry time.
the difference between 429 vs 5xx handling is due to the potential situation of a sender “falling behind” when the receiver cannot keep up with the request volume, or the receiver choosing to rate limit the sender to protect its availability. as a result, senders has the option to not retry on 429, which allows progress to be made when there are sender side errors (e.g. too much traffic), while the data is not lost when there are receiver side errors (5xx).
retries on partial writes
receivers may return a 5xx http or 429 http status code on partial write or [partial invalid sample cases](
partial-write) when it expects senders to retry the whole request. in that case, the receiver must support idempotency as senders may retry with the same request.
backward and forward compatibility
the protocol follows [semantic versioning 2.0](): any 2.x compatible receiver must be able to read any 2.x compatible senders and vice versa. breaking or backwards incompatible changes will result in a 3.x version of the spec.
the protobuf messages (in wire format) themselves are forward / backward compatible, in some respects:
* removing fields from the protobuf message requires a major version bump.
* adding (optional) fields can be done in a minor version bump.
in other words, this means that future minor versions of 2.x may add new optional fields to `io.prometheus.write.v2.request`, new compressions, protobuf messages and negotiation mechanisms, as long as they are backwards compatible (e.g. optional to both receiver and sender).
2.x vs 1.x compatibility
the 2.x protocol is breaking compatibility with 1.x by introducing a new, mandatory `io.prometheus.write.v2.request` protobuf message and deprecating the `prometheus.writerequest`.
2.x senders may support 1.x receivers by allowing users to configure what content type senders should use. 2.x senders also may automatically fall back to different content types, if the receiver returns 415 http status code.
protobuf message
`io.prometheus.write.v2.request`
the `io.prometheus.write.v2.request` references the new protobuf message that's meant to replace and deprecate the remote-write 1.0's `prometheus.writerequest` message.
<!---
todo(bwplotka): move link to the one on prometheus main or even buf.
-->
the full schema and source of the truth is in prometheus repository in [`prompb/io/prometheus/write/v2/types.proto`](
l32). the `gogo` dependency and options can be ignored ([will be removed eventually]()). they are not part of the specification as they don't impact the serialized format.
the simplified version of the new `io.prometheus.write.v2.request` is presented below.
```
// request represents a request to write the given timeseries to a remote destination.
message request {
  // since request supersedes 1.0 spec's prometheus.writerequest, we reserve the top-down message
  // for the deterministic interop between those two.
  // generally it's not needed, because receivers must use the content-type header, but we want to
  // be sympathetic to adopters with mistaken implementations and have deterministic error (empty
  // message if you use the wrong proto schema).
  reserved 1 to 3;
  // symbols contains a de-duplicated array of string elements used for various
  // items in a request message, like labels and metadata items. for the sender's convenience
  // around empty values for optional fields like unit_ref, symbols array must start with
  // empty string.
  //
  // to decode each of the symbolized strings, referenced, by "ref(s)" suffix, you
  // need to lookup the actual string by index from symbols array. the order of
  // strings is up to the sender. the receiver should not assume any particular encoding.
  repeated string symbols = 4;
  // timeseries represents an array of distinct series with 0 or more samples.
  repeated timeseries timeseries = 5;
}
// timeseries represents a single series.
message timeseries {
  // labels_refs is a list of label name-value pair references, encoded
  // as indices to the request.symbols array. this list's length is always
  // a multiple of two, and the underlying labels should be sorted lexicographically.
  //
  // note that there might be multiple timeseries objects in the same
  // requests with the same labels e.g. for different exemplars, metadata
  // or created timestamp.
  repeated uint32 labels_refs = 1;
  // timeseries messages can either specify samples or (native) histogram samples
  // (histogram field), but not both. for a typical sender (real-time metric
  // streaming), in healthy cases, there will be only one sample or histogram.
  //
  // samples and histograms are sorted by timestamp (older first).
  repeated sample samples = 2;
  repeated histogram histograms = 3;
  // exemplars represents an optional set of exemplars attached to this series' samples.
  repeated exemplar exemplars = 4;
  // metadata represents the metadata associated with the given series' samples.
  metadata metadata = 5;
  // created_timestamp represents an optional created timestamp associated with
  // this series' samples in ms format, typically for counter or histogram type
  // metrics. created timestamp represents the time when the counter started
  // counting (sometimes referred to as start timestamp), which can increase
  // the accuracy of query results.
  //
  // note that some receivers might require this and in return fail to
  // write such samples within the request.
  //
  // for go, see github.com/prometheus/prometheus/model/timestamp/timestamp.go
  // for conversion from/to time.time to prometheus timestamp.
  //
  // note that the "optional" keyword is omitted due to
  // _patterns.md