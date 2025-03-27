---
title: alerting based on metrics.
sort_rank: 5
---
alerting based on metrics
in this tutorial we will create alerts on the `ping_request_count` metric that we instrumented earlier in the
[instrumenting http server written in go](../instrumenting_http_server_in_go/) tutorial.
for the sake of this tutorial we will alert when the `ping_request_count` metric is greater than 5, checkout real world [best practices](../../practices/alerting) to learn more about alerting principles.
download the latest release of alertmanager for your operating system from [here]()
alertmanager supports various receivers like `email`, `webhook`, `pagerduty`, `slack` etc through which it can notify when an alert is firing. you can find the list of receivers and how to configure them [here](../../alerting/latest/configuration). we will use `webhook` as a receiver for this tutorial, head over to [webhook.site]() and copy the webhook url which we will use later to configure the alertmanager.
first let's setup alertmanager with webhook receiver.
> alertmanager.yml
```yaml
global:
  resolve_timeout: 5m
route:
  receiver: webhook_receiver
receivers:
    - name: webhook_receiver
      webhook_configs:
        - url: '<insert-your-webhook>'
          send_resolved: false
```
replace `<insert-your-webhook>` with the webhook that we copied earlier in the alertmanager.yml file and run the alertmanager using the following command.
`alertmanager --config.file=alertmanager.yml`
once the alertmanager is up and running navigate to []() and you should be able to access it.
<iframe width="560" height="315" src="" frameborder="0" allowfullscreen></iframe>
now that we have configured the alertmanager with webhook receiver let's add the rules to the prometheus config.
> prometheus.yml
```yaml
global:
 scrape_interval: 15s
 evaluation_interval: 10s
rule_files:
  - rules.yml
alerting:
  alertmanagers:
  - static_configs:
    - targets:
       - localhost:9093
scrape_configs:
 - job_name: prometheus
   static_configs:
       - targets: ["localhost:9090"]
 - job_name: simple_server
   static_configs:
       - targets: ["localhost:8090"]
```
if you notice the `evaluation_interval`,`rule_files` and `alerting` sections are added to the prometheus config, the `evaluation_interval` defines the intervals at which the rules are evaluated, `rule_files` accepts an array of yaml files that defines the rules and the `alerting` section defines the alertmanager configuration. as mentioned in the beginning of this tutorial we will create a basic rule where we want to
raise an alert when the `ping_request_count` value is greater than 5.
> rules.yml
```yaml
groups:
 - name: count greater than 5
   rules:
   - alert: countgreaterthan5
     expr: ping_request_count > 5
     for: 10s
```
now let's run prometheus using the following command.
`prometheus --config.file=./prometheus.yml`
open []() in your browser to see the rules. next run the instrumented ping server and visit the []() endpoint and refresh the page atleast 6 times. you can check the ping count by navigating to []() endpoint. to see the status of the alert visit [](). once the condition `ping_request_count > 5` is true for more than 10s the `state` will become `firing`. now if you navigate back to your `webhook.site` url you will see the alert message.
<iframe width="560" height="315" src="" frameborder="0" allowfullscreen></iframe>
similarly alertmanager can be configured with other receivers to notify when an alert is firing.