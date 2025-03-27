---
title: prometheus remote-write 1.0
sort_rank: 5
---
prometheus remote-write specification
- version: 1.0
- status: published
- date: april 2023
this document is intended to define and standardise the api, wire format, protocol and semantics of the existing, widely and organically adopted protocol, and not to propose anything new.
the remote write specification is intended to document the standard for how prometheus and prometheus remote-write-compatible agents send data to a prometheus or prometheus remote-write compatible receiver.
the key words "must", "must not", "required", "shall", "shall not", "should", "should not", "recommended",  "may", and "optional" in this document are to be interpreted as described in [rfc 2119]().
introduction
background
the remote write protocol is designed to make it possible to reliably propagate samples in real-time from a sender to a receiver, without loss.
the remote-write protocol is designed to be stateless; there is strictly no inter-message communication. as such the protocol is not considered "streaming". to achieve a streaming effect multiple messages should be sent over the same connection using e.g. http/1.1 or http/2. "fancy" technologies such as grpc were considered, but at the time were not widely adopted, and it was challenging to expose grpc services to the internet behind load balancers such as an aws ec2 elb.
the remote write protocol contains opportunities for batching, e.g. sending multiple samples for different series in a single request.  it is not expected that multiple samples for the same series will be commonly sent in the same request, although there is support for this in the protocol.
the remote write protocol is not intended for use by applications to push metrics to prometheus remote-write-compatible receivers.  it is intended that a prometheus remote-write-compatible sender scrapes instrumented applications or exporters and sends remote write messages to a server.
a test suite can be found at
glossary
for the purposes of this document the following definitions must be followed:
- a "sender" is something that sends prometheus remote write data.
- a "receiver" is something that receives prometheus remote write data.
- a "sample" is a pair of (timestamp, value).
- a "label" is a pair of (key, value).
- a "series" is a list of samples, identified by a unique set of labels.
definitions
protocol
the remote write protocol must consist of rpcs with the following signature:
```
func send(writerequest)
message writerequest {
  repeated timeseries timeseries = 1;
  // cortex uses this field to determine the source of the write request.
  // we reserve it to avoid any compatibility issues.
  reserved  2;
  // prometheus uses this field to send metadata, but this is
  // omitted from v1 of the spec as it is experimental.
  reserved  3;
}
message timeseries {
  repeated label labels   = 1;
  repeated sample samples = 2;
}
message label {
  string name  = 1;
  string value = 2;
}
message sample {
  double value    = 1;
  int64 timestamp = 2;
}
```
remote write senders must encode the write request in the body of a http post request and send it to the receivers via http at a provided url path.  the receiver may specify any http url path to receive metrics.
timestamps must be int64 counted as milliseconds since the unix epoch.  values must be float64.
the following headers must be sent with the http request:
- `content-encoding: snappy`
- `content-type: application/x-protobuf`
- `user-agent: <name & version of the sender>`
- `x-prometheus-remote-write-version: 0.1.0`
clients may allow users to send custom http headers; they must not allow users to configure them in such a way as to send reserved headers.  for more info see 
the remote write request in the body of the http post must be compressed with [google’s snappy]().  the block format must be used - the framed format must not be used.
the remote write request must be encoded using google protobuf 3, and must use the schema defined above.  note [the prometheus implementation]() uses [gogoproto optimisations]() - for receivers written in languages other than golang the gogoproto types may be substituted for line-level equivalents.
the response body from the remote write receiver should be empty; clients must ignore the response body. the response body is reserved for future use.
backward and forward compatibility
the protocol follows [semantic versioning 2.0](): any 1.x compatible receivers must be able to read any 1.x compatible sender and so on.  breaking/backwards incompatible changes will result in a 2.x version of the spec.
the proto format itself is forward / backward compatible, in some respects:
- removing fields from the proto will mean a major version bump.
- adding (optional) fields will be a minor version bump.
negotiation:
- senders must send the version number in a headers.
- receivers may return the highest version number they support in a response header ("x-prometheus-remote-write-version").
- senders who wish to send in a format >1.x must start by sending an empty 1.x, and see if the response says the receiver supports something else.  the sender may use any supported version .  if there is no version header in the response, senders must assume 1.x compatibility only.
labels
the complete set of labels must be sent with each sample. whatsmore, the label set associated with samples:
- should contain a `__name__` label.
- must not contain repeated label names.
- must have label names sorted in lexicographical order.
- must not contain any empty label names or values.
senders must only send valid metric names, label names, and label values:
- metric names must adhere to the regex `[a-za-z_:]([a-za-z0-9_:])*`.
- label names must adhere to the regex `[a-za-z_]([a-za-z0-9_])*`.
- label values may be any sequence of utf-8 characters .
receivers may impose limits on the number and length of labels, but this will be receiver-specific and is out of scope for this document.
label names beginning with "__" are reserved for system usage and should not be used, see [prometheus data model](_model/).
remote write receivers may ingest valid samples within a write request that otherwise contains invalid samples. receivers must return a http 400 status code ("bad request") for write requests that contain any invalid samples. receivers should provide a human readable error message in the response body. senders must not try and interpret the error message, and should log it as is.
ordering
prometheus remote write compatible senders must send samples for any given series in timestamp order. prometheus remote write compatible senders may send multiple requests for different series in parallel.
retries & backoff
prometheus remote write compatible senders must retry write requests on http 5xx responses and must use a backoff algorithm to prevent overwhelming the server. they must not retry write requests on http 2xx and 4xx responses other than 429. they may retry on http 429 responses, which could result in senders "falling behind" if the server cannot keep up. this is done to ensure data is not lost when there are server side errors, and progress is made when there are client side errors.
prometheus remote write compatible receivers must respond with a http 2xx status code when the write is successful. they must respond with http status code 5xx when the write fails and should be retried. they must respond with http status code 4xx when the request is invalid, will never be able to succeed and should not be retried.
stale markers
prometheus remote write compatible senders must send stale markers when a time series will no longer be appended to.
stale markers must be signalled by  the special nan value 0x7ff0000000000002. this value must not be used otherwise.
typically the sender can detect when a time series will no longer be appended to using the following techniques:
1. detecting, using service discovery, that the target exposing the series has gone away
1. noticing the target is no longer exposing the time series between successive scrapes
1. failing to scrape the target that originally exposed a time series
1. tracking configuration and evaluation for recording and alerting rules
out of scope
this document does not intend to explain all the features required for a fully prometheus-compatible monitoring system.  in particular, the following areas are out of scope for the first version of the spec:
**the "up" metric** the definition and semantics of the "up" metric are beyond the scope of the remote write protocol and should be documented separately.
**http path** the path for http handler can be anything - and must be provided by the sender.  generally we expect the whole url to be specified in config.
**persistence** it is recommended that prometheus remote write compatible senders should persistently buffer sample data in the event of outages in the receiver. 
**authentication & encryption** as remote write uses http, we consider authentication & encryption to be a transport-layer problem.  senders and receivers should support all the usual suspects (basic auth, tls etc) and are free to add potentially custom authentication options.  support for custom authentication in the prometheus remote write sender and eventual agent should not be assumed, but we will endeavour to support common and widely used auth protocols, where feasible.
**remote read** this is a separate interface that has already seen some iteration, and is less widely used.
**sharding** the current sharding scheme in prometheus for remote write parallelisation is very much an implementation detail, and isn’t part of the spec.  when senders do implement parallelisation they must preserve per-series sample ordering.
**backfill** the specification does not place a limit on how old series can be pushed, however server/implementation specific constraints may exist.
**limits** limits on the number and length of labels, batch sizes etc are beyond the scope of this document, however it is expected that implementation will impose reasonable limits.
**push-based prometheus** applications pushing metrics to prometheus remote write compatible receivers was not a design goal of this system, and should be explored in a separate doc.
**labels** every series may include a "job" and/or "instance" label, as these are typically added by service discovery in the sender. these are not mandatory.