relabel_config).
relabeling is useful here because behind the scenes many things in prometheus are configured with internal labels.
the details are complicated and out of scope for this guide. hence we will limit ourselves to the necessary. but if you want to know more check out this [talk](=b5-svvz7awi). for now it suffices if you understand this:
* all labels starting with `__` are dropped after the scrape. most internal labels start with `__`.
* you can set internal labels that are called `__param_<name>`. those set url parameter with the key `<name>` for the scrape request.
* there is an internal label `__address__` which is set by the `targets` under `static_configs` and whose value is the hostname for the scrape request. by default it is later used to set the value for the label `instance`, which is attached to each metric and tells you where the metrics came from.
here is the config you will use to do that. don’t worry if this is a bit much at once, we will go through it step by step:
```yaml
global:
  scrape_interval: 5s
scrape_configs:
- job_name: blackbox
to get metrics about the exporter itself
  metrics_path: /metrics
  static_configs:
    - targets:
      - localhost:9115
for windows and macos replace with - host.docker.internal:9115
- job_name: blackbox-http
to get metrics about the exporter’s targets
  metrics_path: /probe
  params:
    module: [http_2xx]
  static_configs:
    - targets:
      -
target to probe with http
      -
target to probe with https
      -
target to probe with http on port 8080
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
    - source_labels: [__param_target]
      target_label: instance
    - target_label: __address__
      replacement: localhost:9115
the blackbox exporter’s real hostname:port. for windows and macos replace with - host.docker.internal:9115
```
so what is new compared to the [last config](
prometheus-config)?
`params` does not include `target` anymore. instead we add the actual targets under `static configs:` `targets`. we also use several because we can do that now:
```yaml
  params:
    module: [http_2xx]
  static_configs:
    - targets:
      -
target to probe with http
      -
target to probe with https
      -
target to probe with http on port 8080
```
`relabel_configs` contains the new relabeling rules:
```yaml
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
    - source_labels: [__param_target]
      target_label: instance
    - target_label: __address__
      replacement: localhost:9115
the blackbox exporter’s real hostname:port. for windows and macos replace with - host.docker.internal:9115
```
before applying the relabeling rules, the uri of a request prometheus would make would look like this:
`"=http_2xx"`. after relabeling it will look like this `"=&module=http_2xx"`.
now let us explore how each rule does that:
first we take the values from the label `__address__` (which contain the values from `targets`) and write them to a new label `__param_target` which will add a parameter `target` to the prometheus scrape requests:
```yaml
  relabel_configs:
    - source_labels: [__address__]
      target_label: __param_target
```
after this our imagined prometheus request uri has now a target parameter: `"=&module=http_2xx"`.
then we take the values from the label `__param_target` and create a label instance with the values.
```yaml
  relabel_configs:
    - source_labels: [__param_target]
      target_label: instance
```
our request will not change, but the metrics that come back from our request will now bear a label `instance=""`.
after that we write the value `localhost:9115` (the uri of our exporter) to the label `__address__`. this will be used as the hostname and port for the prometheus scrape requests. so that it queries the exporter and not the target uri directly.
```yaml
  relabel_configs:
    - target_label: __address__
      replacement: localhost:9115
the blackbox exporter’s real hostname:port. for windows and macos replace with - host.docker.internal:9115
```
our request is now `"localhost:9115/probe?target=&module=http_2xx"`. this way we can have the actual targets there, get them as `instance` label values while letting prometheus make a request against the blackbox exporter.
often people combine these with a specific service discovery. check out the [configuration documentation](/docs/prometheus/latest/configuration/configuration) for more information. using them is no problem, as these write into the `__address__` label just like `targets` defined under `static_configs`.
that is it. restart the prometheus docker container and look at your [metrics](_input=30m&g0.stacked=0&g0.expr=probe_http_duration_seconds&g0.tab=0). pay attention that you selected the period of time when the metrics were actually collected.
summary
in this guide, you learned how the multi-target exporter pattern works, how to run a blackbox exporter with a customised module, and to configure prometheus using relabeling to scrape metrics with prober labels.