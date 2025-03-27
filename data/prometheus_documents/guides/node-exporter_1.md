---
title: monitoring linux host metrics with the node exporter
---
monitoring linux host metrics with the node exporter
the prometheus [**node exporter**](_exporter) exposes a wide variety of hardware- and kernel-related metrics.
in this guide, you will:
* start up a node exporter on `localhost`
* start up a prometheus instance on `localhost` that's configured to scrape metrics from the running node exporter
note: while the prometheus node exporter is for *nix systems, there is the [windows exporter](_exporter) for windows that serves an analogous purpose.
installing and running the node exporter
the prometheus node exporter is a single static binary that you can install [via tarball](
tarball-installation). once you've downloaded it from the prometheus [downloads page](/download
node_exporter) extract it, and run it:
```bash
note: replace the url with one from the above mentioned "downloads" page.
<version>, <os>, and <arch> are placeholders.
wget _exporter/releases/download/v<version>/node_exporter-<version>.<os>-<arch>.tar.gz
tar xvfz node_exporter-*.*-amd64.tar.gz
cd node_exporter-*.*-amd64
./node_exporter
```
you should see output like this indicating that the node exporter is now running and exposing metrics on port 9100:
```
info[0000] starting node_exporter (version=0.16.0, branch=head, revision=d42bd70f4363dced6b77d8fc311ea57b63387e4f)  source="node_exporter.go:82"
info[0000] build context (go=go1.9.6,  date=20180515-15:53:28)  source="node_exporter.go:83"
info[0000] enabled collectors:                           source="node_exporter.go:90"
info[0000]  - boottime                                   source="node_exporter.go:97"
...
info[0000] listening on :9100                            source="node_exporter.go:111"
```
node exporter metrics
once the node exporter is installed and running, you can verify that metrics are being exported by curling the `/metrics` endpoint:
```bash
curl 
```
you should see output like this:
```
help go_gc_duration_seconds a summary of the gc invocation durations.
type go_gc_duration_seconds summary
go_gc_duration_seconds{quantile="0"} 3.8996e-05
go_gc_duration_seconds{quantile="0.25"} 4.5926e-05
go_gc_duration_seconds{quantile="0.5"} 5.846e-05
etc.
```
success! the node exporter is now exposing metrics that prometheus can scrape, including a wide variety of system metrics further down in the output (prefixed with `node_`). to view those metrics (along with help and type information):
```bash
curl  | grep "node_"
```
configuring your prometheus instances
your locally running prometheus instance needs to be properly configured in order to access node exporter metrics. the following [`prometheus.yml`](../../prometheus/latest/configuration/configuration/) example configuration file will tell the prometheus instance to scrape, and how frequently, from the node exporter via `localhost:9100`:
<a id="config"></a>
```yaml
global:
  scrape_interval: 15s
scrape_configs:
- job_name: node
  static_configs:
  - targets: ['localhost:9100']
```
to install prometheus, [download the latest release](/download) for your platform and untar it:
```bash
wget */prometheus-*.*-amd64.tar.gz
tar xvf prometheus-*.*-amd64.tar.gz
cd prometheus-*.*
```
once prometheus is installed you can start it up, using the `--config.file` flag to point to the prometheus configuration that you created [above](
config):
```bash
./prometheus --config.file=./prometheus.yml
```
exploring node exporter metrics through the prometheus expression browser
now that prometheus is scraping metrics from a running node exporter instance, you can explore those metrics using the prometheus ui (aka the [expression browser](/docs/visualization/browser)). navigate to `localhost:9090/graph` in your browser and use the main expression bar at the top of the page to enter expressions. the expression bar looks like this:
![prometheus expressions browser](/assets/prometheus-expression-bar.png)
metrics specific to the node exporter are prefixed with `node_` and include metrics like `node_cpu_seconds_total` and `node_exporter_build_info`.
click on the links below to see some example metrics:
metric | meaning
:------|:-------
[`rate(node_cpu_seconds_total{mode="system"}[1m])`](_input=1h&g0.expr=rate(node_cpu_seconds_total%7bmode%3d%22system%22%7d%5b1m%5d)&g0.tab=1) | the average amount of cpu time spent in system mode, per second, over the last minute (in seconds)
[`node_filesystem_avail_bytes`](_input=1h&g0.expr=node_filesystem_avail_bytes&g0.tab=1) | the filesystem space available to non-root users (in bytes)
[`rate(node_network_receive_bytes_total[1m])`](_input=1h&g0.expr=rate(node_network_receive_bytes_total%5b1m%5d)&g0.tab=1) | the average network traffic received, per second, over the last minute (in bytes)