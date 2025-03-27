---
title: "prometheus remote-write 2.0 [experimental]"
sort_rank: 4
---
prometheus remote-write specification
* version: 2.0-rc.3
* status: **experimental**
* date: may 2024
the remote-write specification, in general, is intended to document the standard for how prometheus and prometheus remote-write compatible senders send data to prometheus or prometheus remote-write compatible receivers.
this document is intended to define a second version of the [prometheus remote-write](./remote_write_spec.md) api with minor changes to protocol and semantics. this second version adds a new protobuf message with new features enabling more use cases and wider adoption on top of performance and cost savings. the second version also deprecates the previous protobuf message from a [1.0 remote-write specification](/docs/specs/remote_write_spec/
protocol) and adds mandatory [`x-prometheus-remote-write-*-written` http response headers](
required-written-response-headers)for reliability purposes. finally, this spec outlines how to implement backwards-compatible senders and receivers (even under a single endpoint) using existing basic content negotiation request headers. more advanced, automatic content negotiation mechanisms might come in a future minor version if needed. for the rationales behind the 2.0 specification, see [the formal proposal]().
the key words "must", "must not", "required", "shall", "shall not", "should", "should not", "recommended",  "may", and "optional" in this document are to be interpreted as described in [rfc 2119]().
> note: this is a release candidate for remote-write 2.0 specification. this means that this specification is currently in an experimental state--no major changes are expected, but we reserve the right to break the compatibility if it's necessary, based on the early adopters' feedback. the potential feedback, questions and suggestions should be added as comments to the [pr with the open proposal]().
introduction
background
the remote-write protocol is designed to make it possible to reliably propagate samples in real-time from a sender to a receiver, without loss.
<!---
for the detailed rationales behind each 2.0 remote-write decision, see: _remote-write-20.md
-->
the remote-write protocol is designed to be stateless; there is strictly no inter-message communication. as such the protocol is not considered "streaming". to achieve a streaming effect multiple messages should be sent over the same connection using e.g. http/1.1 or http/2. "fancy" technologies such as grpc were considered, but at the time were not widely adopted, and it was challenging to expose grpc services to the internet behind load balancers such as an aws ec2 elb.
the remote-write protocol contains opportunities for batching, e.g. sending multiple samples for different series in a single request. it is not expected that multiple samples for the same series will be commonly sent in the same request, although there is support for this in the protobuf message.
a test suite can be found at _write_sender. the compliance tests for remote write 2.0 compatibility are still [in progress]().
glossary
in this document, the following definitions are followed:
* `remote-write` is the name of this prometheus protocol.
* a `protocol` is a communication specification that enables the client and server to transfer metrics.
* a `protobuf message` (or proto message) refers to the [content type](
name-content-type) definition of the data structure for this protocol. since the specification uses [google protocol buffers ("protobuf")]() exclusively, the schema is defined in a ["proto" file]() and represented by a single protobuf ["message"](
simple).
* a `wire format` is the format of the data as it travels on the wire (i.e. in a network). in the case of remote-write, this is always the compressed binary protobuf format.
* a `sender` is something that sends remote-write data.
* a `receiver` is something that receives (writes) remote-write data. the meaning of `written` is up to the receiver e.g. usually it means storing received data in a database, but also just validating, splitting or enhancing it.
* `written` refers to data the `receiver` has received and is accepting. whether or not it has ingested this data to persistent storage, written it to a wal, etc. is up to the `receiver`. the only distinction is that the `receiver` has accepted this data rather than explicitly rejecting it with an error response.
* a `sample` is a pair of (timestamp, value).
* a `histogram` is a pair of (timestamp, [histogram value](_histograms.md)).
* a `label` is a pair of (key, value).
* a `series` is a list of samples, identified by a unique set of labels.
definitions
protocol
the remote-write protocol must consist of rpcs with the request body serialized using a google protocol buffers and then compressed.
<!---
rationales: _remote-write-20.md
a-new-protobuf-message-identified-by-fully-qualified-name-old-one-deprecated
-->
the protobuf serialization must use either of the following protobuf messages:
* the `prometheus.writerequest` introduced in [the remote-write 1.0 specification](./remote_write_spec.md
protocol). as of 2.0, this message is deprecated. it should be used only for compatibility reasons. senders and receivers may not support the `prometheus.writerequest`.
* the `io.prometheus.write.v2.request` introduced in this specification and defined [below](
protobuf-message). senders and receivers should use this message when possible. senders and receivers must support the `io.prometheus.write.v2.request`.
protobuf message must use binary wire format. then, must be compressed with [google’s snappy](). snappy's [block format](_description.txt) must be used -- [the framed format](_format.txt) must not be used.
senders must send a serialized and compressed protobuf message in the body of an http post request and send it to the receiver via http at the provided url path. receivers may specify any http url path to receive metrics.
<!---
rationales: _remote-write-20.md
basic-content-negotiation-built-on-what-we-have
-->
senders must send the following reserved headers with the http request:
- `content-encoding`
- `content-type`
- `x-prometheus-remote-write-version`
- `user-agent`
senders may allow users to add custom http headers; they must not allow users to configure them in such a way as to send reserved headers.
content-encoding
```
content-encoding: <compression>
```
<!---
rationales: _remote-write-20.md
no-new-compression-added--yet-
-->
content encoding request header must follow [the rfc 9110](
name-content-encoding). senders must use the `snappy` value. receivers must support `snappy` compression. new, optional compression algorithms might come in 2.x or beyond.
content-type
```
content-type: application/x-protobuf
content-type: application/x-protobuf;proto=<fully qualified name>
```
content type request header must follow [the rfc 9110](
name-content-type). senders must use `application/x-protobuf` as the only media type. senders may add `;proto=` parameter to the header's value to indicate the fully qualified name of the protobuf message that was used, from the two mentioned above. as a result, senders must send any of the three supported header values:
for the deprecated message introduced in prw 1.0, identified by `prometheus.writerequest`:
* `content-type: application/x-protobuf`
* `content-type: application/x-protobuf;proto=prometheus.writerequest`
for the message introduced in prw 2.0, identified by `io.prometheus.write.v2.request`:
* `content-type: application/x-protobuf;proto=io.prometheus.write.v2.request`
when talking to 1.x receivers, senders should use `content-type: application/x-protobuf` for backward compatibility. otherwise, senders should use `content-type: application/x-protobuf;proto=io.prometheus.write.v2.request`. more protobuf messages might come in 2.x or beyond.
receivers must use the content type header to identify the protobuf message schema to use. accidental wrong schema choices may result in non-deterministic behaviour (e.g. corruptions).
> note: thanks to reserved fields in [`io.prometheus.write.v2.request`](
protobuf-message), receiver accidental use of wrong schema with `prometheus.writerequest` will result in empty message. this is generally for convenience to avoid surprising errors, but don't rely on it -- future protobuf messages might not have this feature.
x-prometheus-remote-write-version
```
x-prometheus-remote-write-version: <remote-write spec major and minor version>
```
when talking to 1.x receivers, senders must use `x-prometheus-remote-write-version: 0.1.0` for backward compatibility. otherwise, senders should use the newest remote-write version it is compatible with e.g. `x-prometheus-remote-write-version: 2.0.0`.
user-agent
```
user-agent: <name & version of the sender>
```
senders must include a user agent header that should follow [the rfc 9110 user-agent header format](
name-user-agent).
response
receivers that written all data successfully must return a [success 2xx http status code](
name-successful-2xx). in such a successful case, the response body from the receiver should be empty and the status code should be [204 http no content](
name-204-no-content); senders must ignore the response body. the response body is reserved for future use.
receivers must not return a 2xx http status code if any of the pieces of sent data known to the receiver (e.g. samples, histograms, exemplars) were not written successfully (both [partial write](
partial-write) or full write rejection). in such a case, the receiver must provide a human-readable error message in the response body. the receiver's error should contain information about the amount of the samples being rejected and for what reasons. senders must not try and interpret the error message and should log it as is.
the following subsections specify sender and receiver semantics around headers and different write error cases.