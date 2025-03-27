---
title: instrumenting http server written in go  
sort_rank: 3
---
in this tutorial we will create a simple go http server and instrumentation it by adding a counter
metric to keep count of the total number of requests processed by the server.
here we have a simple http server with `/ping` endpoint which returns `pong` as response.
```go
package main
import (
   "fmt"
   "net/http"
)
func ping(w http.responsewriter, req *http.request){
   fmt.fprintf(w,"pong")
}
func main() {
   http.handlefunc("/ping",ping)
   http.listenandserve(":8090", nil)
}
```
compile and run the server
```bash
go build server.go
./server
```
now open `` in your browser and you must see `pong`.
[![server](/assets/tutorial/server.png)](/assets/tutorial/server.png)
now lets add a metric to the server which will instrument the number of requests made to the ping endpoint,the counter metric type is suitable for this as we know the request count doesn’t go down and only increases.
create a prometheus counter
```go
var pingcounter = prometheus.newcounter(
   prometheus.counteropts{
       name: "ping_request_count",
       help: "no of request handled by ping handler",
   },
)
```
next lets update the ping handler to increase the count of the counter using `pingcounter.inc()`.
```go
func ping(w http.responsewriter, req *http.request) {
   pingcounter.inc()
   fmt.fprintf(w, "pong")
}
```
then register the counter to the default register and expose the metrics.
```go
func main() {
   prometheus.mustregister(pingcounter)
   http.handlefunc("/ping", ping)
   http.handle("/metrics", promhttp.handler())
   http.listenandserve(":8090", nil)
}
```
the `prometheus.mustregister` function registers the pingcounter to the default register.
to expose the metrics the go prometheus client library provides the promhttp package.
`promhttp.handler()` provides a `http.handler` which exposes the metrics registered in the default register.
the sample code depends on the  
```go
package main
import (
   "fmt"
   "net/http"
   "github.com/prometheus/client_golang/prometheus"
   "github.com/prometheus/client_golang/prometheus/promhttp"
)
var pingcounter = prometheus.newcounter(
   prometheus.counteropts{
       name: "ping_request_count",
       help: "no of request handled by ping handler",
   },
)
func ping(w http.responsewriter, req *http.request) {
   pingcounter.inc()
   fmt.fprintf(w, "pong")
}
func main() {
   prometheus.mustregister(pingcounter)
   http.handlefunc("/ping", ping)
   http.handle("/metrics", promhttp.handler())
   http.listenandserve(":8090", nil)
}
```
run the example
```sh
go mod init prom_example
go mod tidy
go run server.go
```
now hit the localhost:8090/ping endpoint a couple of times and sending a request to localhost:8090 will provide the metrics.
[![ping metric](/assets/tutorial/ping_metric.png)](/assets/tutorial/ping_metric.png)
here the `ping_request_count` shows that `/ping` endpoint was called 3 times.
the default register comes with a collector for go runtime metrics and that is why we see other metrics like `go_threads`, `go_goroutines` etc.
we have built our first metric exporter. let’s update our prometheus config to scrape the metrics from our server.
```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: simple_server
    static_configs:
      - targets: ["localhost:8090"]
```
<code>prometheus --config.file=prometheus.yml</code>
<iframe width="560" height="315" src="" frameborder="0" allowfullscreen></iframe>