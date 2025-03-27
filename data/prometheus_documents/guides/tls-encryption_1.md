---
title: tls encryption
sort_rank: 1
---
securing prometheus api and ui endpoints using tls encryption
prometheus supports [transport layer security](_layer_security) (tls) encryption for connections to prometheus instances (i.e. to the expression browser or [http api](../../prometheus/latest/querying/api)). if you would like to enforce tls for those connections, you would need to create a specific web configuration file.
note: this guide is about tls connections *to* prometheus instances. tls is also supported for connections *from* prometheus instances to [scrape targets](../../prometheus/latest/configuration/configuration/
tls_config).
pre-requisites
let's say that you already have a prometheus instance up and running, and you
want to adapt it. we will not cover the initial prometheus setup in this guide.
let's say that you want to run a prometheus instance served with tls, available at the `example.com` domain (which you own).
let's also say that you've generated the following using [openssl]() or an analogous tool:
* an ssl certificate at `/home/prometheus/certs/example.com/example.com.crt`
* an ssl key at `/home/prometheus/certs/example.com/example.com.key`
you can generate a self-signed certificate and private key using this command:
```bash
mkdir -p /home/prometheus/certs/example.com && cd /home/prometheus/certs/certs/example.com
openssl req \
  -x509 \
  -newkey rsa:4096 \
  -nodes \
  -keyout example.com.key \
  -out example.com.crt
```
fill out the appropriate information at the prompts, and make sure to enter `example.com` at the `common name` prompt.
prometheus configuration
below is an example [`web-config.yml`]() configuration file. with this configuration, prometheus will serve all its endpoints behind tls.
```yaml
tls_server_config:
  cert_file: /home/prometheus/certs/example.com/example.com.crt
  key_file: /home/prometheus/certs/example.com/example.com.key
```
to make prometheus use this config, you will need to call it with the flag
`--web.config.file`.
```bash
prometheus \
  --config.file=/path/to/prometheus.yml \
  --web.config.file=/path/to/web-config.yml \
  --web.external-url=
```
the `--web.external-url=` flag is optional here.
testing
if you'd like to test out tls locally using the `example.com` domain, you can add an entry to your `/etc/hosts` file that re-routes `example.com` to `localhost`:
```
127.0.0.1     example.com
```
you can then use curl to interact with your local prometheus setup:
```bash
curl --cacert /home/prometheus/certs/example.com/example.com.crt \
```
you can connect to the prometheus server without specifying certs using the `--insecure` or `-k` flag:
```bash
curl -k 
```