---
title: use file-based service discovery to discover scrape targets
---
use file-based service discovery to discover scrape targets
prometheus offers a variety of [service discovery options]() for discovering scrape targets, including [kubernetes](/docs/prometheus/latest/configuration/configuration/
kubernetes_sd_config), [consul](/docs/prometheus/latest/configuration/configuration/
consul_sd_config), and many others. if you need to use a service discovery system that is not currently supported, your use case may be best served by prometheus' [file-based service discovery](/docs/prometheus/latest/configuration/configuration/
file_sd_config) mechanism, which enables you to list scrape targets in a json file (along with metadata about those targets).
in this guide, we will:
* install and run a prometheus [node exporter](../node-exporter) locally
* create a `targets.json` file specifying the host and port information for the node exporter
* install and run a prometheus instance that is configured to discover the node exporter using the `targets.json` file
installing and running the node exporter
see [this section](../node-exporter
installing-and-running-the-node-exporter) of the [monitoring linux host metrics with the node exporter](../node-exporter) guide. the node exporter runs on port 9100. to ensure that the node exporter is exposing metrics:
```bash
curl 
```
the metrics output should look something like this:
```
help go_gc_duration_seconds a summary of the gc invocation durations.
type go_gc_duration_seconds summary
go_gc_duration_seconds{quantile="0"} 0
go_gc_duration_seconds{quantile="0.25"} 0
go_gc_duration_seconds{quantile="0.5"} 0
...
```
installing, configuring, and running prometheus
like the node exporter, prometheus is a single static binary that you can install via tarball. [download the latest release](/download
prometheus) for your platform and untar it:
```bash
wget */prometheus-*.*-amd64.tar.gz
tar xvf prometheus-*.*-amd64.tar.gz
cd prometheus-*.*
```
the untarred directory contains a `prometheus.yml` configuration file. replace the current contents of that file with this:
```yaml
scrape_configs:
- job_name: 'node'
  file_sd_configs:
  - files:
    - 'targets.json'
```
this configuration specifies that there is a job called `node` (for the node exporter) that retrieves host and port information for node exporter instances from a `targets.json` file.
now create that `targets.json` file and add this content to it:
```json
[
  {
    "labels": {
      "job": "node"
    },
    "targets": [
      "localhost:9100"
    ]
  }
]
```
note: in this guide we'll work with json service discovery configurations manually for the sake of brevity. in general, however, we recommend that you use some kind of json-generating process or tool instead.
this configuration specifies that there is a `node` job with one target: `localhost:9100`.
now you can start up prometheus:
```bash
./prometheus
```
if prometheus has started up successfully, you should see a line like this in the logs:
```
level=info ts=2018-08-13t20:39:24.905651509z caller=main.go:500 msg="server is ready to receive web requests."
```
exploring the discovered services' metrics
with prometheus up and running, you can explore metrics exposed by the `node` service using the prometheus [expression browser](/docs/visualization/browser). if you explore the [`up{job="node"}`](_input=1h&g0.expr=up%7bjob%3d%22node%22%7d&g0.tab=1) metric, for example, you can see that the node exporter is being appropriately discovered.
changing the targets list dynamically
when using prometheus' file-based service discovery mechanism, the prometheus instance will listen for changes to the file and automatically update the scrape target list, without requiring an instance restart. to demonstrate this, start up a second node exporter instance on port 9200. first navigate to the directory containing the node exporter binary and run this command in a new terminal window:
```bash
./node_exporter --web.listen-address=":9200"
```
now modify the config in `targets.json` by adding an entry for the new node exporter:
```json
[
  {
    "targets": [
      "localhost:9100"
    ],
    "labels": {
      "job": "node"
    }
  },
  {
    "targets": [
      "localhost:9200"
    ],
    "labels": {
      "job": "node"
    }
  }
]
```
when you save the changes, prometheus will automatically be notified of the new list of targets. the [`up{job="node"}`](_input=1h&g0.expr=up%7bjob%3d%22node%22%7d&g0.tab=1) metric should display two instances with `instance` labels `localhost:9100` and `localhost:9200`.
summary
in this guide, you installed and ran a prometheus node exporter and configured prometheus to discover and scrape metrics from the node exporter using file-based service discovery.