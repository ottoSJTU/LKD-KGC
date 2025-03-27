---
title: getting started with prometheus
sort_rank: 1
---
what is prometheus ?
prometheus is a system monitoring and alerting system. it was opensourced by soundcloud in 2012 and is the second project both to join and to graduate within cloud native computing foundation after kubernetes. prometheus stores all metrics data as time series, i.e metrics information is stored along with the timestamp at which it was recorded, optional key-value pairs called as labels can also be stored along with metrics.
what are metrics and why is it important?
metrics in layperson terms is a standard for measurement. what we want to measure depends from application to application. for a web server it can be request times, for a database it can be cpu usage or number of active connections etc.
metrics play an important role in understanding why your application is working in a certain way. if you run a web application and someone comes up to you and says that the application is slow, you will need some information to find out what is happening with your application. for example the application can become slow when the number of requests are high. if you have the request count metric you can spot the reason and increase the number of servers to handle the heavy load. whenever you are defining the metrics for your application you must put on your detective hat and ask this question **what all information will be important for me to debug if any issue occurs in my application?**
basic architecture of prometheus
the basic components of a prometheus setup are:
- prometheus server (the server which scrapes and stores the metrics data).
- targets to be scraped, for example an instrumented application that exposes its metrics, or an exporter that exposes metrics of another application.
- alertmanager to raise alerts based on preset rules.
(note: apart from this prometheus has push_gateway which is not covered here).
[![architecture](/assets/tutorial/architecture.png)](/assets/tutorial/architecture.png)
let's consider a web server as an example application and we want to extract a certain metric like the number of api calls processed by the web server. so we add certain instrumentation code using the prometheus client library and expose the metrics information. now that our web server exposes its metrics we can configure prometheus to scrape it. now prometheus is configured to fetch the metrics from the web server which is listening on xyz ip address port 7500 at a specific time interval, say, every minute.
at 11:00:00 when i make the server public for consumption, the application calculates the request count and exposes it, prometheus simultaneously scrapes the count metric and stores the value as 0.
by 11:01:00 one request is processed. the instrumentation logic in the server increments the count to 1. when prometheus scrapes the metric the value of count is 1 now.
by 11:02:00 two more requests are processed and the request count is 1+2 = 3 now. similarly metrics are scraped and stored.
the user can control the frequency at which metrics are scraped by prometheus.
| time stamp | request count (metric) |
| ---------- | ---------------------- |
| 11:00:00   | 0                      |
| 11:01:00   | 1                      |
| 11:02:00   | 3                      |
(note: this table is just a representation for understanding purposes. prometheus doesn’t store the values in this exact format)
prometheus also has an api which allows to query metrics which have been stored by scraping. this api is used to query the metrics, create dashboards/charts on it etc. promql is used to query these metrics.
a simple line chart created on the request count metric will look like this
[![graph](/assets/tutorial/sample_graph.png)](/assets/tutorial/sample_graph.png)
one can scrape multiple useful metrics to understand what is happening in the application and create multiple charts on them. group the charts into a dashboard and use it to get an overview of the application.
show me how it is done
let’s get our hands dirty and setup prometheus. prometheus is written using [go]() and all you need is the binary compiled for your operating system. download the binary corresponding to your operating system from [here]() and add the binary to your path.
prometheus exposes its own metrics which can be consumed by itself or another prometheus server.
now that we have prometheus installed, the next step is to run it. all that we need is just the binary and a configuration file. prometheus uses yaml files for configuration.
```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]
```
in the above configuration file we have mentioned the `scrape_interval`, i.e how frequently we want prometheus to scrape the metrics. we have added `scrape_configs` which has a name and target to scrape the metrics from. prometheus by default listens on port 9090. so add it to targets.
> prometheus --config.file=prometheus.yml
<iframe width="560" height="315" src="" frameborder="0" allowfullscreen></iframe>
now we have prometheus up and running and scraping its own metrics every 15s. prometheus has standard exporters available to export metrics. next we will run a node exporter which is an exporter for machine metrics and scrape the same using prometheus. ([download node metrics exporter.](
node_exporter))
run the node exporter in a terminal.
<code>./node_exporter</code>
[![node exporter](/assets/tutorial/node_exporter.png)](/assets/tutorial/node_exporter.png)
next, add node exporter to the list of scrape_configs:
```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: node_exporter
    static_configs:
      - targets: ["localhost:9100"]
```
<iframe width="560" height="315" src="" frameborder="0" allowfullscreen></iframe>
in this tutorial we discussed what are metrics and why they are important, basic architecture of prometheus and how to
run prometheus.