future plans
this section contains speculative plans that are not considered part of protocol specification, but are mentioned here for completeness.
**transactionality** prometheus aims at being "transactional" - i.e. to never expose a partially scraped target to a query. we intend to do the same with remote write -  for instance, in the future we would like to "align" remote write with scrapes, perhaps such that all the samples, metadata and exemplars for a single scrape are sent in a single remote write request.  this is yet to be designed.
**metadata** and exemplars in line with above, we also send metadata (type information, help text) and exemplars along with the scraped samples. we plan to package this up in a single remote write request - future versions of the spec may insist on this.  prometheus currently has experimental support for sending metadata and exemplars.
**optimizations** we would like to investigate various optimizations to reduce message size by eliminating repetition of label names and values.
related
compatible senders and receivers
the spec is intended to describe how the following components interact (as of april 2023):
- [prometheus]() (as both a "sender" and a "receiver")
- [avalanche]() (as a "sender") - a load testing tool prometheus metrics.
- [cortex](
l20) (as a "receiver")
- [elastic agent](
prometheus-server-remote-write) (as a "receiver")
- [grafana agent]() (as both a "sender" and a "receiver")
- [greptimedb]() (as a ["receiver"](
prometheus))
- influxdata’s telegraf agent. ([as a sender](), and [as a receiver]())
- [m3](
prometheus-configuration) (as a "receiver")
- [mimir]() (as a "receiver")
- [opentelemetry collector]() (as a ["sender"](
readme) and eventually as a "receiver")
- [thanos]() (as a "receiver")
- vector (as a ["sender"](_remote_write/) and a ["receiver"](_remote_write/))
- [victoriametrics]() (as a ["receiver"](
prometheus-setup))
faq
**why did you not use grpc?**
funnily enough we initially used grpc, but switched to protos atop http as in 2016 it was hard to get them past elbs: 
**why not streaming protobuf messages?**
if you use persistent http/1.1 connections, they are pretty close to streaming…  of course headers have to be re-sent, but yes that is less expensive than a new tcp set up.
**why do we send samples in order?**
the in-order constraint comes from the encoding we use for time series data in prometheus, the implementation of which is append only. it is possible to remove this constraint, for instance by buffering samples and reordering them before encoding.  we can investigate this in future versions of the protocol.
**how can we parallelise requests with the in-order constraint?**
samples must be in-order _for a given series_.  remote write requests can be sent in parallel as long as they are for different series. in prometheus, we shard the samples by their labels into separate queues, and then writes happen sequentially in each queue.  this guarantees samples for the same series are delivered in order, but samples for different series are sent in parallel - and potentially "out of order" between different series.
we believe this is necessary as, even if the receiver could support out-of-order samples, we can't have agents sending out of order as they would never be able to send to prometheus, cortex and thanos.  we’re doing this to ensure the integrity of the ecosystem and to prevent confusing/forking the community into "prometheus-agents-that-can-write-to-prometheus" and those that can’t.