---
title: monitoring docker container metrics using cadvisor
---
monitoring docker container metrics using cadvisor
[cadvisor]() (short for **c**ontainer **advisor**) analyzes and exposes resource usage and performance data from running containers. cadvisor exposes prometheus metrics out of the box. in this guide, we will:
* create a local multi-container [docker compose]() installation that includes containers running prometheus, cadvisor, and a [redis]() server, respectively
* examine some container metrics produced by the redis container, collected by cadvisor, and scraped by prometheus
prometheus configuration
first, you'll need to [configure prometheus](/docs/prometheus/latest/configuration/configuration) to scrape metrics from cadvisor. create a `prometheus.yml` file and populate it with this configuration:
```yaml
scrape_configs:
- job_name: cadvisor
  scrape_interval: 5s
  static_configs:
  - targets:
    - cadvisor:8080
```
docker compose configuration
now we'll need to create a docker compose [configuration]() that specifies which containers are part of our installation as well as which ports are exposed by each container, which volumes are used, and so on.
in the same folder where you created the [`prometheus.yml`](
prometheus-configuration) file, create a `docker-compose.yml` file and populate it with this docker compose configuration:
```yaml
version: '3.2'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
    - 9090:9090
    command:
    - --config.file=/etc/prometheus/prometheus.yml
    volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    depends_on:
    - cadvisor
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    ports:
    - 8080:8080
    volumes:
    - /:/rootfs:ro
    - /var/run:/var/run:rw
    - /sys:/sys:ro
    - /var/lib/docker/:/var/lib/docker:ro
    depends_on:
    - redis
  redis:
    image: redis:latest
    container_name: redis
    ports:
    - 6379:6379
```
this configuration instructs docker compose to run three services, each of which corresponds to a [docker]() container:
1. the `prometheus` service uses the local `prometheus.yml` configuration file (imported into the container by the `volumes` parameter).
1. the `cadvisor` service exposes port 8080 (the default port for cadvisor metrics) and relies on a variety of local volumes (`/`, `/var/run`, etc.).
1. the `redis` service is a standard redis server. cadvisor will gather container metrics from this container automatically, i.e. without any further configuration.
to run the installation:
```bash
docker-compose up
```
if docker compose successfully starts up all three containers, you should see output like this:
```
prometheus  | level=info ts=2018-07-12t22:02:40.5195272z caller=main.go:500 msg="server is ready to receive web requests."
```
you can verify that all three containers are running using the [`ps`]() command:
```bash
docker-compose ps
```
your output will look something like this:
```
   name                 command               state           ports
----------------------------------------------------------------------------
cadvisor     /usr/bin/cadvisor -logtostderr   up      8080/tcp
prometheus   /bin/prometheus --config.f ...   up      0.0.0.0:9090->9090/tcp
redis        docker-entrypoint.sh redis ...   up      0.0.0.0:6379->6379/tcp
```
exploring the cadvisor web ui
you can access the cadvisor [web ui]() at ``. you can explore stats and graphs for specific docker containers in our installation at `<container>`. metrics for the redis container, for example, can be accessed at ``, prometheus at ``, and so on.
exploring metrics in the expression browser
cadvisor's web ui is a useful interface for exploring the kinds of things that cadvisor monitors, but it doesn't provide an interface for exploring container *metrics*. for that we'll need the prometheus [expression browser](/docs/visualization/browser), which is available at ``. you can enter prometheus expressions into the expression bar, which looks like this:
![prometheus expression bar](/assets/prometheus-expression-bar.png)
let's start by exploring the `container_start_time_seconds` metric, which records the start time of containers (in seconds). you can select for specific containers by name using the `name="<container_name>"` expression. the container name corresponds to the `container_name` parameter in the docker compose configuration. the [`container_start_time_seconds{name="redis"}`](_input=1h&g0.expr=container_start_time_seconds%7bname%3d%22redis%22%7d&g0.tab=1) expression, for example, shows the start time for the `redis` container.
note: a full listing of cadvisor-gathered container metrics exposed to prometheus can be found in the [cadvisor documentation]().
other expressions
the table below lists some other example expressions
expression | description | for
:----------|:------------|:---
[`rate(container_cpu_usage_seconds_total{name="redis"}[1m])`](_input=1h&g0.expr=rate(container_cpu_usage_seconds_total%7bname%3d%22redis%22%7d%5b1m%5d)&g0.tab=1) | the [cgroup]()'s cpu usage in the last minute | the `redis` container
[`container_memory_usage_bytes{name="redis"}`](_input=1h&g0.expr=container_memory_usage_bytes%7bname%3d%22redis%22%7d&g0.tab=1) | the cgroup's total memory usage (in bytes) | the `redis` container
[`rate(container_network_transmit_bytes_total[1m])`](_input=1h&g0.expr=rate(container_network_transmit_bytes_total%5b1m%5d)&g0.tab=1) | bytes transmitted over the network by the container per second in the last minute | all containers
[`rate(container_network_receive_bytes_total[1m])`](_input=1h&g0.expr=rate(container_network_receive_bytes_total%5b1m%5d)&g0.tab=1) | bytes received over the network by the container per second in the last minute | all containers
summary
in this guide, we ran three separate containers in a single installation using docker compose: a prometheus container scraped metrics from a cadvisor container which, in turns, gathered metrics produced by a redis container. we then explored a handful of cadvisor container metrics using the prometheus expression browser.