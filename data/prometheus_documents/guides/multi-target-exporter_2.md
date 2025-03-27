configuring modules
the modules are predefined in a file inside the docker container called `config.yml` which is a copy of [blackbox.yml](_exporter/blob/master/blackbox.yml) in the github repo.
we will copy this file, [adapt](_exporter/blob/master/configuration.md) it to our own needs and tell the exporter to use our config file instead of the one included in the container.  
first download the file using curl or your browser:
```bash
curl -o blackbox.yml _exporter/master/blackbox.yml
```
open it in an editor. the first few lines look like this:
```yaml
modules:
  http_2xx:
    prober: http
  http_post_2xx:
    prober: http
    http:
      method: post
```
[yaml]() uses whitespace indentation to express hierarchy, so you can recognise that two `modules` named `http_2xx` and `http_post_2xx` are defined, and that they both have a prober `http` and for one the method value is specifically set to `post`.  
you will now change the module `http_2xx` by setting the `preferred_ip_protocol` of the prober `http` explicitly to the string `ip4`.
```yaml
modules:
  http_2xx:
    prober: http
    http:
      preferred_ip_protocol: "ip4"
  http_post_2xx:
    prober: http
    http:
      method: post
```
if you want to know more about the available probers and options check out the [documentation](_exporter/blob/master/configuration.md).
now we need to tell the blackbox exporter to use our freshly changed file. you can do that with the flag `--config.file="blackbox.yml"`. but because we are using docker, we first must make this file [available]() inside the container using the `--mount` command.  
note: if you are using macos you first need to allow the docker daemon to access the directory in which your `blackbox.yml` is. you can do that by clicking on the little docker whale in menu bar and then on `preferences`->`file sharing`->`+`. afterwards press `apply & restart`.
first you stop the old container by changing into its terminal and press `ctrl+c`.
make sure you are in the directory containing your `blackbox.yml`.
then you run this command. it is long, but we will explain it:
<a name="run-exporter"></a>
```bash
docker \
  run -p 9115:9115 \
  --mount type=bind,source="$(pwd)"/blackbox.yml,target=/blackbox.yml,readonly \
  prom/blackbox-exporter \
  --config.file="/blackbox.yml"
```
with this command, you told `docker` to:
1. `run` a container with the port `9115` outside the container mapped to the port `9115` inside of the container.
1. `mount` from your current directory (`$(pwd)` stands for print working directory) the file `blackbox.yml` into `/blackbox.yml` in `readonly` mode.
1. use the image `prom/blackbox-exporter` from [docker hub]().
1. run the blackbox-exporter with the flag `--config.file` telling it to use `/blackbox.yml` as config file.
if everything is correct, you should see something like this:
```
level=info ts=2018-10-19t12:40:51.650462756z caller=main.go:213 msg="starting blackbox_exporter" version="(version=0.12.0, branch=head, revision=4a22506cf0cf139d9b2f9cde099f0012d9fcabde)"
level=info ts=2018-10-19t12:40:51.653357722z caller=main.go:220 msg="loaded config file"
level=info ts=2018-10-19t12:40:51.65349635z caller=main.go:324 msg="listening on address" address=:9115
```
now you can try our new ipv4-using module `http_2xx` in a terminal:
```bash
curl 'localhost:9115/probe?target=prometheus.io&module=http_2xx'
```
which should return prometheus metrics like this:
```
help probe_dns_lookup_time_seconds returns the time taken for probe dns lookup in seconds
type probe_dns_lookup_time_seconds gauge
probe_dns_lookup_time_seconds 0.02679421
help probe_duration_seconds returns how long the probe took to complete in seconds
type probe_duration_seconds gauge
probe_duration_seconds 0.461619124
help probe_failed_due_to_regex indicates if probe failed due to regex
type probe_failed_due_to_regex gauge
probe_failed_due_to_regex 0
help probe_http_content_length length of http content response
type probe_http_content_length gauge
probe_http_content_length -1
help probe_http_duration_seconds duration of http request by phase, summed over all redirects
type probe_http_duration_seconds gauge
probe_http_duration_seconds{phase="connect"} 0.062076202999999996
probe_http_duration_seconds{phase="processing"} 0.23481845699999998
probe_http_duration_seconds{phase="resolve"} 0.029594103
probe_http_duration_seconds{phase="tls"} 0.163420078
probe_http_duration_seconds{phase="transfer"} 0.002243199
help probe_http_redirects the number of redirects
type probe_http_redirects gauge
probe_http_redirects 1
help probe_http_ssl indicates if ssl was used for the final redirect
type probe_http_ssl gauge
probe_http_ssl 1
help probe_http_status_code response http status code
type probe_http_status_code gauge
probe_http_status_code 200
help probe_http_uncompressed_body_length length of uncompressed response body
type probe_http_uncompressed_body_length gauge
probe_http_uncompressed_body_length 14516
help probe_http_version returns the version of http of the probe response
type probe_http_version gauge
probe_http_version 1.1
help probe_ip_protocol specifies whether probe ip protocol is ip4 or ip6
type probe_ip_protocol gauge
probe_ip_protocol 4
help probe_ssl_earliest_cert_expiry returns earliest ssl cert expiry in unixtime
type probe_ssl_earliest_cert_expiry gauge
probe_ssl_earliest_cert_expiry 1.581897599e+09
help probe_success displays whether or not the probe was a success
type probe_success gauge
probe_success 1
help probe_tls_version_info contains the tls version used
type probe_tls_version_info gauge
probe_tls_version_info{version="tls 1.3"} 1
```
you can see that the probe was successful and get many useful metrics, like latency by phase, status code, ssl status or certificate expiry in [unix time](_time).  
the blackbox exporter also offers a tiny web interface at [localhost:9115]() for you to check out the last few probes, the loaded config and debug information. it even offers a direct link to probe `prometheus.io`. handy if you are wondering why something does not work.
querying multi-target exporters with prometheus
so far, so good. congratulate yourself. the blackbox exporter works and you can manually tell it to query a remote target. you are almost there. now you need to tell prometheus to do the queries for us.  
below you find a minimal prometheus config. it is telling prometheus to scrape the exporter itself as we did [before](
query-exporter) using `curl 'localhost:9115/metrics'`:
note: if you use docker for mac or docker for windows, you can’t use `localhost:9115` in the last line, but must use `host.docker.internal:9115`. this has to do with the virtual machines used to implement docker on those operating systems. you should not use this in production.
`prometheus.yml` for linux:
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
```
`prometheus.yml` for macos and windows:
```yaml
global:
  scrape_interval: 5s
scrape_configs:
- job_name: blackbox
to get metrics about the exporter itself
  metrics_path: /metrics
  static_configs:
    - targets:
      - host.docker.internal:9115
```
now run a prometheus container and tell it to mount our config file from above. because of the way networking on the host is addressable from the container you need to use a slightly different command on linux than on macos and windows.:
<a name=run-prometheus></a>
run prometheus on linux (don’t use `--network="host"` in production):
```bash
docker \
  run --network="host"\
  --mount type=bind,source="$(pwd)"/prometheus.yml,target=/prometheus.yml,readonly \
  prom/prometheus \
  --config.file="/prometheus.yml"
```
run prometheus on macos and windows:
```bash
docker \
  run -p 9090:9090 \
  --mount type=bind,source="$(pwd)"/prometheus.yml,target=/prometheus.yml,readonly \
  prom/prometheus \
  --config.file="/prometheus.yml"
```
this command works similarly to [running the blackbox exporter using a config file](
run-exporter).
if everything worked, you should be able to go to [localhost:9090/targets]() and see under `blackbox` an endpoint with the state `up` in green. if you get a red `down` make sure that the blackbox exporter you started [above](
run-exporter) is still running. if you see nothing or a yellow `unknown` you are really fast and need to give it a few more seconds before reloading your browser’s tab.
to tell prometheus to query `"localhost:9115/probe?target=prometheus.io&module=http_2xx"` you add another scrape job `blackbox-http` where you set the `metrics_path` to `/probe` and the parameters under `params:` in the prometheus config file `prometheus.yml`:
<a name="prometheus-config"></a>
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
    target: [prometheus.io]
  static_configs:
    - targets:
      - localhost:9115
for windows and macos replace with - host.docker.internal:9115
```
after saving the config file switch to the terminal with your prometheus docker container and stop it by pressing `ctrl+c` and start it again to reload the configuration by using the existing [command](
run-prometheus).
the terminal should return the message `"server is ready to receive web requests."` and after a few seconds you should start to see colourful graphs in [your prometheus](_input=5m&g0.stacked=0&g0.expr=probe_http_duration_seconds&g0.tab=0).
this works, but it has a few disadvantages:
1. the actual targets are up in the param config, which is very unusual and hard to understand later.
1. the `instance` label has the value of the blackbox exporter’s address which is technically true, but not what we are interested in.
1. we can’t see which url we probed. this is unpractical and will also mix up different metrics into one if we probe several urls.
to fix this, we will use [relabeling](/docs/prometheus/latest/configuration/configuration/