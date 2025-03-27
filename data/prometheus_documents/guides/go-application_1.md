---
title: instrumenting a go application
---
instrumenting a go application for prometheus
prometheus has an official [go client library](_golang) that you can use to instrument go applications. in this guide, we'll create a simple go application that exposes prometheus metrics via http.
note: for comprehensive api documentation, see the [godoc](_golang) for prometheus' various go libraries.
installation
you can install the `prometheus`, `promauto`, and `promhttp` libraries necessary for the guide using [`go get`](_command.html):
```bash
go get github.com/prometheus/client_golang/prometheus
go get github.com/prometheus/client_golang/prometheus/promauto
go get github.com/prometheus/client_golang/prometheus/promhttp
```
how go exposition works
to expose prometheus metrics in a go application, you need to provide a `/metrics` http endpoint. you can use the [`prometheus/promhttp`](_golang/prometheus/promhttp) library's http [`handler`](_golang/prometheus/promhttp
handler) as the handler function.
this minimal application, for example, would expose the default metrics for go applications via ``:
```go
package main
import (
        "net/http"
        "github.com/prometheus/client_golang/prometheus/promhttp"
)
func main() {
        http.handle("/metrics", promhttp.handler())
        http.listenandserve(":2112", nil)
}
```
to start the application:
```bash
go run main.go
```
to access the metrics:
```bash
curl 
```
adding your own metrics
the application [above](
how-go-exposition-works) exposes only the default go metrics. you can also register your own custom application-specific metrics. this example application exposes a `myapp_processed_ops_total` [counter](/docs/concepts/metric_types/
counter) that counts the number of operations that have been processed thus far. every 2 seconds, the counter is incremented by one.
```go
package main
import (
        "net/http"
        "time"
        "github.com/prometheus/client_golang/prometheus"
        "github.com/prometheus/client_golang/prometheus/promauto"
        "github.com/prometheus/client_golang/prometheus/promhttp"
)
func recordmetrics() {
        go func() {
                for {
                        opsprocessed.inc()
                        time.sleep(2 * time.second)
                }
        }()
}
var (
        opsprocessed = promauto.newcounter(prometheus.counteropts{
                name: "myapp_processed_ops_total",
                help: "the total number of processed events",
        })
)
func main() {
        recordmetrics()
        http.handle("/metrics", promhttp.handler())
        http.listenandserve(":2112", nil)
}
```
to run the application:
```bash
go run main.go
```
to access the metrics:
```bash
curl 
```
in the metrics output, you'll see the help text, type information, and current value of the `myapp_processed_ops_total` counter:
```
help myapp_processed_ops_total the total number of processed events
type myapp_processed_ops_total counter
myapp_processed_ops_total 5
```
you can [configure](/docs/prometheus/latest/configuration/configuration/
scrape_config) a locally running prometheus instance to scrape metrics from the application. here's an example `prometheus.yml` configuration:
```yaml
scrape_configs:
- job_name: myapp
  scrape_interval: 10s
  static_configs:
  - targets:
    - localhost:2112
```
other go client features
in this guide we covered just a small handful of features available in the prometheus go client libraries. you can also expose other metrics types, such as [gauges](_golang/prometheus
gauge) and [histograms](_golang/prometheus
histogram), [non-global registries](_golang/prometheus
registry), functions for [pushing metrics](_golang/prometheus/push) to prometheus [pushgateways](/docs/instrumenting/pushing/), bridging prometheus and [graphite](_golang/prometheus/graphite), and more.
summary
in this guide, you created two sample go applications that expose metrics to prometheus---one that exposes only the default go metrics and one that also exposes a custom prometheus counter---and configured a prometheus instance to scrape metrics from those applications.