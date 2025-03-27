---
title: when to use the pushgateway
sort_rank: 7
---
when to use the pushgateway
the pushgateway is an intermediary service which allows you to push metrics
from jobs which cannot be scraped. for details, see [pushing metrics](/docs/instrumenting/pushing/).
should i be using the pushgateway?
**we only recommend using the pushgateway in certain limited cases.** there are
several pitfalls when blindly using the pushgateway instead of prometheus's
usual pull model for general metrics collection:
* when monitoring multiple instances through a single pushgateway, the
  pushgateway becomes both a single point of failure and a potential
  bottleneck.
* you lose prometheus's automatic instance health monitoring via the `up`
  metric (generated on every scrape).
* the pushgateway never forgets series pushed to it and will expose them to
  prometheus forever unless those series are manually deleted via the
  pushgateway's api.
the latter point is especially relevant when multiple instances of a job
differentiate their metrics in the pushgateway via an `instance` label or
similar. metrics for an instance will then remain in the pushgateway even if
the originating instance is renamed or removed. this is because the lifecycle
of the pushgateway as a metrics cache is fundamentally separate from the
lifecycle of the processes that push metrics to it. contrast this to
prometheus's usual pull-style monitoring: when an instance disappears
(intentional or not), its metrics will automatically disappear along with it.
when using the pushgateway, this is not the case, and you would now have to
delete any stale metrics manually or automate this lifecycle synchronization
yourself.
**usually, the only valid use case for the pushgateway is for capturing the
outcome of a service-level batch job**.  a "service-level" batch job is one
which is not semantically related to a specific machine or job instance (for
example, a batch job that deletes a number of users for an entire service).
such a job's metrics should not include a machine or instance label to decouple
the lifecycle of specific machines or instances from the pushed metrics. this
decreases the burden for managing stale metrics in the pushgateway. see also
the [best practices for monitoring batch jobs](/docs/practices/instrumentation/
batch-jobs).
alternative strategies
if an inbound firewall or nat is preventing you from pulling metrics from
targets, consider moving the prometheus server behind the network barrier as
well. we generally recommend running prometheus servers on the same network as
the monitored instances.  otherwise, consider [pushprox](),
which allows prometheus to traverse a firewall or nat.
for batch jobs that are related to a machine (such as automatic
security update cronjobs or configuration management client runs), expose the
resulting metrics using the [node exporter's](_exporter)
[textfile collector](_exporter
textfile-collector) instead of the pushgateway.