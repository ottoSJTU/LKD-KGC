---
title: first steps
sort_rank: 3
---
first steps with prometheus
welcome to prometheus! prometheus is a monitoring platform that collects metrics from monitored targets by scraping metrics http endpoints on these targets. this guide will show you how to install, configure and monitor our first resource with prometheus. you'll download, install and run prometheus. you'll also download and install an exporter, tools that expose time series data on hosts and services. our first exporter will be prometheus itself, which provides a wide variety of host-level metrics about memory usage, garbage collection, and more.
downloading prometheus
[download the latest release](/download) of prometheus for your platform, then
extract it:
```language-bash
tar xvfz prometheus-*.tar.gz
cd prometheus-*
```
the prometheus server is a single binary called `prometheus` (or `prometheus.exe` on microsoft windows). we can run the binary and see help on its options by passing the `--help` flag.
```language-bash
./prometheus --help
usage: prometheus [<flags>]
the prometheus monitoring server
. . .
```
before starting prometheus, let's configure it.
configuring prometheus
prometheus configuration is [yaml](). the prometheus download comes with a sample configuration in a file called `prometheus.yml` that is a good place to get started.
we've stripped out most of the comments in the example file to make it more succinct (comments are the lines prefixed with a `
`).
```language-yaml
global:
  scrape_interval:     15s
  evaluation_interval: 15s
rule_files:
- "first.rules"
- "second.rules"
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ['localhost:9090']
```
there are three blocks of configuration in the example configuration file: `global`, `rule_files`, and `scrape_configs`.
the `global` block controls the prometheus server's global configuration. we have two options present. the first, `scrape_interval`, controls how often prometheus will scrape targets. you can override this for individual targets. in this case the global setting is to scrape every 15 seconds. the `evaluation_interval` option controls how often prometheus will evaluate rules. prometheus uses rules to create new time series and to generate alerts.
the `rule_files` block specifies the location of any rules we want the prometheus server to load. for now we've got no rules.
the last block, `scrape_configs`, controls what resources prometheus monitors. since prometheus also exposes data about itself as an http endpoint it can scrape and monitor its own health. in the default configuration there is a single job, called `prometheus`, which scrapes the time series data exposed by the prometheus server. the job contains a single, statically configured, target, the `localhost` on port `9090`. prometheus expects metrics to be available on targets on a path of `/metrics`. so this default job is scraping via the url: 
the time series data returned will detail the state and performance of the prometheus server.
for a complete specification of configuration options, see the
[configuration documentation](/docs/operating/configuration).
starting prometheus
to start prometheus with our newly created configuration file, change to the directory containing the prometheus binary and run:
```language-bash
./prometheus --config.file=prometheus.yml
```
prometheus should start up. you should also be able to browse to a status page about itself at  give it about 30 seconds to collect data about itself from its own http metrics endpoint.
you can also verify that prometheus is serving metrics about itself by
navigating to its own metrics endpoint:
using the expression browser
let us try looking at some data that prometheus has collected about itself. to
use prometheus's built-in expression browser, navigate to
 and choose the "table" view within the "graph"
tab.
as you can gather from , one metric that
prometheus exports about itself is called
`promhttp_metric_handler_requests_total` (the total number of `/metrics` requests the prometheus server has served). go ahead and enter this into the expression console:
```
promhttp_metric_handler_requests_total
```
this should return a number of different time series (along with the latest value recorded for each), all with the metric name `promhttp_metric_handler_requests_total`, but with different labels. these labels designate different requests statuses.
if we were only interested in requests that resulted in http code `200`, we could use this query to retrieve that information:
```
promhttp_metric_handler_requests_total{code="200"}
```
to count the number of returned time series, you could write:
```
count(promhttp_metric_handler_requests_total)
```
for more about the expression language, see the
[expression language documentation](/docs/querying/basics/).
using the graphing interface
to graph expressions, navigate to  and use the "graph" tab.
for example, enter the following expression to graph the per-second http request rate returning status code 200 happening in the self-scraped prometheus:
```
rate(promhttp_metric_handler_requests_total{code="200"}[1m])
```
you can experiment with the graph range parameters and other settings.
monitoring other targets
collecting metrics from prometheus alone isn't a great representation of prometheus' capabilities. to get a better sense of what prometheus can do, we recommend exploring documentation about other exporters. the [monitoring linux or macos host metrics using a node exporter](/docs/guides/node-exporter) guide is a good place to start.
summary
in this guide, you installed prometheus, configured a prometheus instance to monitor resources, and learned some basics of working with time series data in prometheus' expression browser. to continue learning about prometheus, check out the [overview](/docs/introduction/overview) for some ideas about what to explore next.