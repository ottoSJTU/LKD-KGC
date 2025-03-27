---
title: understanding and using the multi-target exporter pattern
---
understanding and using the multi-target exporter pattern
this guide will introduce you to the multi-target exporter pattern. to achieve this we will:
* describe the multi-target exporter pattern and why it is used,
* run the [blackbox](_exporter) exporter as an example of the pattern,
* configure a custom query module for the blackbox exporter,
* let the blackbox exporter run basic metric queries against the prometheus [website](),
* examine a popular pattern of configuring prometheus to scrape exporters using relabeling.
the multi-target exporter pattern?
by multi-target [exporter](/docs/instrumenting/exporters/) pattern we refer to a specific design, in which:
* the exporter will get the target’s metrics via a network protocol.
* the exporter does not have to run on the machine the metrics are taken from.
* the exporter gets the targets and a query config string as parameters of prometheus’ get request.
* the exporter subsequently starts the scrape after getting prometheus’ get requests and once it is done with scraping.
* the exporter can query multiple targets.
this pattern is only used for certain exporters, such as the [blackbox](_exporter) and the [snmp exporter](_exporter).
the reason is that we either can’t run an exporter on the targets, e.g. network gear speaking snmp, or that we are explicitly interested in the distance, e.g. latency and reachability of a website from a specific point outside of our network, a common use case for the [blackbox](_exporter) exporter.
running multi-target exporters
multi-target exporters are flexible regarding their environment and can be run in many ways. as regular programs, in containers, as background services, on baremetal, on virtual machines. because they are queried and do query over network they do need appropriate open ports. otherwise they are frugal.
now let’s try it out for yourself!
use [docker]() to start a blackbox exporter container by running this in a terminal. depending on your system configuration you might need to prepend the command with a `sudo`:
```bash
docker run -p 9115:9115 prom/blackbox-exporter
```
you should see a few log lines and if everything went well the last one should report `msg="listening on address"` as seen here:
```
level=info ts=2018-10-17t15:41:35.4997596z caller=main.go:324 msg="listening on address" address=:9115
```
basic querying of multi-target exporters
there are two ways of querying:
1. querying the exporter itself. it has its own metrics, usually available at `/metrics`.
1. querying the exporter to scrape another target. usually available at a "descriptive" endpoint, e.g. `/probe`. this is likely what you are primarily interested in, when using multi-target exporters.
you can manually try the first query type with curl in another terminal or use this [link]():
<a name="query-exporter"></a>
```bash
curl 'localhost:9115/metrics'
```
the response should be something like this:
```
help blackbox_exporter_build_info a metric with a constant '1' value labeled by version, revision, branch, and goversion from which blackbox_exporter was built.
type blackbox_exporter_build_info gauge
blackbox_exporter_build_info{branch="head",goversion="go1.10",revision="4a22506cf0cf139d9b2f9cde099f0012d9fcabde",version="0.12.0"} 1
help go_gc_duration_seconds a summary of the gc invocation durations.
type go_gc_duration_seconds summary
go_gc_duration_seconds{quantile="0"} 0
go_gc_duration_seconds{quantile="0.25"} 0
go_gc_duration_seconds{quantile="0.5"} 0
go_gc_duration_seconds{quantile="0.75"} 0
go_gc_duration_seconds{quantile="1"} 0
go_gc_duration_seconds_sum 0
go_gc_duration_seconds_count 0
help go_goroutines number of goroutines that currently exist.
type go_goroutines gauge
go_goroutines 9
[…]
help process_cpu_seconds_total total user and system cpu time spent in seconds.
type process_cpu_seconds_total counter
process_cpu_seconds_total 0.05
help process_max_fds maximum number of open file descriptors.
type process_max_fds gauge
process_max_fds 1.048576e+06
help process_open_fds number of open file descriptors.
type process_open_fds gauge
process_open_fds 7
help process_resident_memory_bytes resident memory size in bytes.
type process_resident_memory_bytes gauge
process_resident_memory_bytes 7.8848e+06
help process_start_time_seconds start time of the process since unix epoch in seconds.
type process_start_time_seconds gauge
process_start_time_seconds 1.54115492874e+09
help process_virtual_memory_bytes virtual memory size in bytes.
type process_virtual_memory_bytes gauge
process_virtual_memory_bytes 1.5609856e+07
```
those are metrics in the prometheus [format](/docs/instrumenting/exposition_formats/
text-format-example). they come from the exporter’s [instrumentation](/docs/practices/instrumentation/) and tell us about the state of the exporter itself while it is running. this is called whitebox monitoring and very useful in daily ops practice. if you are curious, try out our guide on how to [instrument your own applications]().
for the second type of querying we need to provide a target and module as parameters in the http get request. the target is a uri or ip and the module must defined in the exporter’s configuration. the blackbox exporter container comes with a meaningful default configuration.  
we will use the target `prometheus.io` and the predefined module `http_2xx`. it tells the exporter to make a get request like a browser would if you go to `prometheus.io` and to expect a [200 ok](_of_http_status_codes
2xx_success) response.
you can now tell your blackbox exporter to query `prometheus.io` in the terminal with curl:
```bash
curl 'localhost:9115/probe?target=prometheus.io&module=http_2xx'
```
this will return a lot of metrics:
```
help probe_dns_lookup_time_seconds returns the time taken for probe dns lookup in seconds
type probe_dns_lookup_time_seconds gauge
probe_dns_lookup_time_seconds 0.061087943
help probe_duration_seconds returns how long the probe took to complete in seconds
type probe_duration_seconds gauge
probe_duration_seconds 0.065580871
help probe_failed_due_to_regex indicates if probe failed due to regex
type probe_failed_due_to_regex gauge
probe_failed_due_to_regex 0
help probe_http_content_length length of http content response
type probe_http_content_length gauge
probe_http_content_length 0
help probe_http_duration_seconds duration of http request by phase, summed over all redirects
type probe_http_duration_seconds gauge
probe_http_duration_seconds{phase="connect"} 0
probe_http_duration_seconds{phase="processing"} 0
probe_http_duration_seconds{phase="resolve"} 0.061087943
probe_http_duration_seconds{phase="tls"} 0
probe_http_duration_seconds{phase="transfer"} 0
help probe_http_redirects the number of redirects
type probe_http_redirects gauge
probe_http_redirects 0
help probe_http_ssl indicates if ssl was used for the final redirect
type probe_http_ssl gauge
probe_http_ssl 0
help probe_http_status_code response http status code
type probe_http_status_code gauge
probe_http_status_code 0
help probe_http_version returns the version of http of the probe response
type probe_http_version gauge
probe_http_version 0
help probe_ip_protocol specifies whether probe ip protocol is ip4 or ip6
type probe_ip_protocol gauge
probe_ip_protocol 6
help probe_success displays whether or not the probe was a success
type probe_success gauge
probe_success 0
```
notice that almost all metrics have a value of `0`. the last one reads `probe_success 0`. this means the prober could not successfully reach `prometheus.io`. the reason is hidden in the metric `probe_ip_protocol` with the value `6`. by default the prober uses [ipv6]() until told otherwise. but the docker daemon blocks ipv6 until told otherwise. hence our blackbox exporter running in a docker container can’t connect via ipv6.
we could now either tell docker to allow ipv6 or the blackbox exporter to use ipv4. in the real world both can make sense and as so often the answer to the question "what is to be done?" is "it depends". because this is an exporter guide we will change the exporter and take the opportunity to configure a custom module.