---
title: integrations
sort_rank: 5
---
integrations
in addition to [client libraries](/docs/instrumenting/clientlibs/) and
[exporters and related libraries](/docs/instrumenting/exporters/), there are
numerous other generic integration points in prometheus. this page lists some
of the integrations with these.
not all integrations are listed here, due to overlapping functionality or still
being in development. the [exporter default
port]()
wiki page also happens to include a few non-exporter integrations that fit in
these categories.
file service discovery
for service discovery mechanisms not natively supported by prometheus,
[file-based service discovery](/docs/operating/configuration/
%3cfile_sd_config%3e) provides an interface for integrating.
 * [kuma]()
 * [lightsail]()
 * [netbox]()
 * [packet]()
 * [scaleway]()
remote endpoints and storage
the [remote write](/docs/operating/configuration/
remote_write) and [remote read](/docs/operating/configuration/
remote_read)
features of prometheus allow transparently sending and receiving samples. this
is primarily intended for long term storage. it is recommended that you perform
careful evaluation of any solution in this space to confirm it can handle your
data volumes.
  * [appoptics](): write
  * [aws timestream](): read and write
  * [azure data explorer](): read and write
  * [azure event hubs](): write
  * [chronix](): write
  * [cortex](): read and write
  * [cratedb](_adapter): read and write
  * [elasticsearch](_write.html): write
  * [gnocchi](): write
  * [google bigquery](_bigquery_remote_storage_adapter): read and write
  * [google cloud spanner](): read and write
  * [grafana mimir](): read and write
  * [graphite](_storage/remote_storage_adapter): write
  * [greptimedb](): read and write
  * [influxdb](_protocols/prometheus): read and write
  * [instana](
remote-write): write
  * [irondb](): read and write
  * [kafka](): write
  * [m3db](): read and write
  * [mezmo](): write
  * [new relic](): write
  * [opentsdb](_storage/remote_storage_adapter): write
  * [quasardb](): read and write
  * [signalfx](
prometheus): write
  * [splunk](): read and write
  * [sysdig monitor](): write
  * [tikv](): read and write
  * [thanos](): read and write
  * [victoriametrics](): write
  * [wavefront](): write
[prom-migrator]() is a tool for migrating data between remote storage systems.
alertmanager webhook receiver
for notification mechanisms not natively supported by the alertmanager, the
[webhook receiver](/docs/alerting/configuration/
webhook_config) allows for integration.
  * [alertmanager-webhook-logger](): logs alerts
  * [alertsnitch](): saves alerts to a mysql database
  * [all quiet](): on-call & incident management
  * [asana]()
  * [aws sns]()
  * [better uptime]()
  * [canopsis]()
  * [dingtalk]()
  * [discord]()
  * [gitlab](
external-prometheus-instances)
  * [gotify](_gotify_bridge)
  * [gelf]()
  * [heii on-call]()
  * [icinga2]()
  * [ilert]()
  * [irc bot]()
  * [jiralert]()
  * [matrix]()
  * [phabricator / maniphest]()
  * [prom2teams](): forwards notifications to microsoft teams
  * [ansible tower](): call ansible tower (awx) api on alerts (launch jobs etc.)
  * [signal]()
  * [signl4](_item/prometheus-alertmanager-mobile-alert-notification-duty-schedule-escalation)
  * [simplepush]()
  * [sms](): supports [multiple providers]()
  * [snmp traps](_notifier)
  * [squadcast]()
  * [stomp]()
  * [telegram bot](_bot)
  * [xmatters]()
  * [xmpp bot]()
  * [zenduty]()
  * [zoom]()
management
prometheus does not include configuration management functionality, allowing
you to integrate it with your existing systems or build on top of it.
  * [prometheus operator](): manages prometheus on top of kubernetes
  * [promgen](): web ui and configuration generator for prometheus and alertmanager
other
  * [alert analysis](): stores alerts into a clickhouse database and provides alert analysis dashboards
  * [karma](): alert dashboard
  * [pushprox](): proxy to transverse nat and similar network setups
  * [promdump](): kubectl plugin to dump and restore data blocks
  * [promregator](): discovery and scraping for cloud foundry applications
  * [pint](): prometheus rule linter