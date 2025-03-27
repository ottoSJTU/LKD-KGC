---
title: docker swarm
sort_rank: 1
---
docker swarm
prometheus can discover targets in a [docker swarm][swarm] cluster, as of
v2.20.0. this guide demonstrates how to use that service discovery mechanism.
docker swarm service discovery architecture
the [docker swarm service discovery][swarmsd] contains 3 different roles: nodes, services,
and tasks.
the first role, **nodes**, represents the hosts that are part of the swarm. it
can be used to automatically monitor the docker daemons or the node exporters
who run on the swarm hosts.
the second role, **tasks**, represents any individual container deployed in the
swarm. each task gets its associated service labels. one service can be backed by
one or multiple tasks.
the third one, **services**, will discover the services deployed in the
swarm. it will discover the ports exposed by the services. usually you will want
to use the tasks role instead of this one.
prometheus will only discover tasks and service that expose ports.
note: the rest of this post assumes that you have a swarm running.
setting up prometheus
for this guide, you need to [setup prometheus][setup]. we will assume that
prometheus runs on a docker swarm manager node and has access to the docker
socket at `/var/run/docker.sock`.
monitoring docker daemons
let's dive into the service discovery itself.
docker itself, as a daemon, exposes [metrics][dockermetrics] that can be
ingested by a prometheus server.
you can enable them by editing `/etc/docker/daemon.json` and setting the
following properties:
```json
{
  "metrics-addr" : "0.0.0.0:9323",
  "experimental" : true
}
```
instead of `0.0.0.0`, you can set the ip of the docker swarm node.
a restart of the daemon is required to take the new configuration into account.
the [docker documentation][dockermetrics] contains more info about this.
then, you can configure prometheus to scrape the docker daemon, by providing the
following `prometheus.yml` file:
```yaml
scrape_configs:
make prometheus scrape itself for metrics.
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']
create a job for docker daemons.
  - job_name: 'docker'
    dockerswarm_sd_configs:
      - host: unix:///var/run/docker.sock
        role: nodes
    relabel_configs:
fetch metrics on port 9323.
      - source_labels: [__meta_dockerswarm_node_address]
        target_label: __address__
        replacement: $1:9323
set hostname as instance label
      - source_labels: [__meta_dockerswarm_node_hostname]
        target_label: instance
```
for the nodes role, you can also use the `port` parameter of
`dockerswarm_sd_configs`. however, using `relabel_configs` is recommended as it
enables prometheus to reuse the same api calls across identical docker swarm
configurations.
monitoring containers
let's now deploy a service in our swarm. we will deploy [cadvisor][cad], which
exposes container resources metrics:
```shell
docker service create --name cadvisor -l prometheus-job=cadvisor \
    --mode=global --publish target=8080,mode=host \
    --mount type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock,ro \
    --mount type=bind,src=/,dst=/rootfs,ro \
    --mount type=bind,src=/var/run,dst=/var/run \
    --mount type=bind,src=/sys,dst=/sys,ro \
    --mount type=bind,src=/var/lib/docker,dst=/var/lib/docker,ro \
    google/cadvisor -docker_only
```
this is a minimal `prometheus.yml` file to monitor it:
```yaml
scrape_configs:
make prometheus scrape itself for metrics.
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']
create a job for docker swarm containers.
  - job_name: 'dockerswarm'
    dockerswarm_sd_configs:
      - host: unix:///var/run/docker.sock
        role: tasks
    relabel_configs:
only keep containers that should be running.
      - source_labels: [__meta_dockerswarm_task_desired_state]
        regex: running
        action: keep
only keep containers that have a `prometheus-job` label.
      - source_labels: [__meta_dockerswarm_service_label_prometheus_job]
        regex: .+
        action: keep
use the prometheus-job swarm label as prometheus job label.
      - source_labels: [__meta_dockerswarm_service_label_prometheus_job]
        target_label: job
```
let's analyze each part of the [relabel configuration][rela].
```yaml
- source_labels: [__meta_dockerswarm_task_desired_state]
  regex: running
  action: keep
```
docker swarm exposes the desired [state of the tasks][state] over the api. in
out example, we only **keep** the targets that should be running. it prevents
monitoring tasks that should be shut down.
```yaml
- source_labels: [__meta_dockerswarm_service_label_prometheus_job]
  regex: .+
  action: keep
```
when we deployed our cadvisor, we have added a label `prometheus-job=cadvisor`.
as prometheus fetches the tasks labels, we can instruct it to **only** keep the
targets which have a `prometheus-job` label.
```yaml
- source_labels: [__meta_dockerswarm_service_label_prometheus_job]
  target_label: job
```
that last part takes the label `prometheus-job` of the task and turns it into
a target label, overwriting the default `dockerswarm` job label that comes from
the scrape config.
discovered labels
the [prometheus documentation][swarmsd] contains the full list of labels, but
here are other relabel configs that you might find useful.
scraping metrics via a certain network only
```yaml
- source_labels: [__meta_dockerswarm_network_name]
  regex: ingress
  action: keep
```
scraping global tasks only
global tasks run on every daemon.
```yaml
- source_labels: [__meta_dockerswarm_service_mode]
  regex: global
  action: keep
- source_labels: [__meta_dockerswarm_task_port_publish_mode]
  regex: host
  action: keep
```
adding a docker_node label to the targets
```yaml
- source_labels: [__meta_dockerswarm_node_hostname]
  target_label: docker_node
```
connecting to the docker swarm
the above `dockerswarm_sd_configs` entries have a field host:
```yaml
host: unix:///var/run/docker.sock
```
that is using the docker socket. prometheus offers [additional configuration
options][swarmsd] to connect to swarm using http and https, if you prefer that
over the unix socket.
conclusion
there are many discovery labels you can play with to better determine which
targets to monitor and how, for the tasks, there is more than 25 labels
available. don't hesitate to look at the "service discovery" page of your
prometheus server (under the "status" menu) to see all the discovered labels.
the service discovery makes no assumptions about your swarm stack, in such a way
that given proper configuration, this should be pluggable to any existing stack.
[state]:
[rela]:
relabel_config
[swarm]:
[swarmsd]:
dockerswarm_sd_config
[dockermetrics]:
[cad]:
[setup]:_started/