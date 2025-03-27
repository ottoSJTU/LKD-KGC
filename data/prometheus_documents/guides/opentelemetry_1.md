---
title: opentelemetry
---
using prometheus as your opentelemetry backend
prometheus supports [otlp]() (aka "opentelemetry protocol") ingestion through [http](
otlphttp).
enable the otlp receiver
by default, the otlp receiver is disabled. this is because prometheus can work without any authentication, so it would not be safe to accept incoming traffic unless explicitly configured.
to enable the receiver you need to toggle the flag `--web.enable-otlp-receiver`.
```shell
$ prometheus --web.enable-otlp-receiver
```
send opentelemetry metrics to the prometheus server
opentelemetry sdks and instrumentation libraries can be configured via [standard environment variables](). the following are the opentelemetry variables needed to send opentelemetry metrics to a prometheus server on localhost:
```shell
export otel_exporter_otlp_protocol=http/protobuf
export otel_exporter_otlp_metrics_endpoint=
```
turn off traces and logs:
```shell
export otel_traces_exporter=none
export otel_logs_exporter=none
```
the default push interval for opentelemetry metrics is 60 seconds. the following will set a 15 second push interval:
```shell
export otel_metric_export_interval=15000
```
if your instrumentation library does not provide `service.name` and `service.instance.id` out-of-the-box, it is highly recommended to set them.
```shell
export otel_service_name="my-example-service"
export otel_resource_attributes="service.instance.id=$(uuidgen)"
```
the above assumes that `uuidgen` command is available on your system. make sure that `service.instance.id` is unique for each instance, and that a new `service.instance.id` is generated whenever a resource attribute chances. the [recommended]() way is to generate a new uuid on each startup of an instance.
enable out-of-order ingestion
there are multiple reasons why you might want to enable out-of-order ingestion.
for example, the opentelemetry collector encourages batching and you could have multiple replicas of the collector sending data to prometheus. because there is no mechanism ordering those samples they could get out-of-order.
to enable out-of-order ingestion you need to extend the prometheus configuration file with the following:
```shell
storage:
  tsdb:
    out_of_order_time_window: 30m
```
30 minutes of out-of-order have been enough for most cases but don't hesitate to adjust this value to your needs.
promoting resource attributes
based on experience and conversations with our community, we've found that out of all the commonly seen resource attributes, these are the ones that are most frequently promoted by our users:
```yaml
- service.instance.id
- service.name
- service.namespace
- cloud.availability_zone
- cloud.region
- container.name
- deployment.environment
- k8s.cluster.name
- k8s.container.name
- k8s.cronjob.name
- k8s.daemonset.name
- k8s.deployment.name
- k8s.job.name
- k8s.namespace.name
- k8s.pod.name
- k8s.replicaset.name
- k8s.statefulset.name
```
by default prometheus won't be promoting any attributes. if you'd like to promote any of them, you can do so in this section of the prometheus configuration file:
```yaml
otlp:
  resource_attributes:
    - service.instance.id
    - deployment.environment
    - k8s.cluster.name
    - ...
```
including resource attributes at query time
an alternative to promoting resource attributes, as described in the previous section, is to add labels from the `target_info` metric when querying.
this is conceptually known as a "join" query.
an example of such a query can look like the following:
```promql
rate(http_server_request_duration_seconds_count[2m])
* on (job, instance) group_left (k8s_cluster_name)
target_info
```
what happens in this query is that the time series resulting from `rate(http_server_request_duration_seconds_count[2m])` are augmented with the `k8s_cluster_name` label from the `target_info` series that share the same `job` and `instance` labels.
in other words, the `job` and `instance` labels are shared between `http_server_request_duration_seconds_count` and `target_info`, akin to sql foreign keys.
the `k8s_cluster_name` label, on the other hand, corresponds to the otel resource attribute `k8s.cluster.name` (prometheus converts dots to underscores).
so, what is the relation between the `target_info` metric and otel resource attributes?
when prometheus processes an otlp write request, and provided that contained resources include the attributes `service.instance.id` and/or `service.name`, prometheus generates the info metric `target_info` for every (otel) resource.
it adds to each such `target_info` series the label `instance` with the value of the `service.instance.id` resource attribute, and the label `job` with the value of the `service.name` resource attribute.
if the resource attribute `service.namespace` exists, it's prefixed to the `job` label value (i.e., `<service.namespace>/<service.name>`).
the rest of the resource attributes are also added as labels to the `target_info` series, names converted to prometheus format (e.g. dots converted to underscores).
if a resource lacks both `service.instance.id` and `service.name` attributes, no corresponding `target_info` series is generated.
for each of a resource's otel metrics, prometheus converts it to a corresponding prometheus time series, and (if `target_info` is generated) adds the right `instance` and `job` labels.
utf-8
the utf-8 support for prometheus is not ready yet so both the prometheus remote write exporter and the otlp ingestion endpoint still rely on the [prometheus normalization translator package from opentelemetry]().
so if you are sending non-valid characters to prometheus, they will be replaced with an underscore `_` character.
once the utf-8 feature is merged into prometheus, we will revisit this.
delta temporality
the [opentelemetry specification says](
temporality) that both delta temporality and cumulative temporality are supported.
while delta temporality is common in systems like statsd and graphite, cumulative temporality is the default temporality for prometheus.
today prometheus does not have support for delta temporality but we are learning from the opentelemetry community and we are considering adding support for it in the future.
if you are coming from a delta temporality system we recommend that you use the [delta to cumulative processor]() in your otel pipeline.