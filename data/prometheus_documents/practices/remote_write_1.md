---
title: remote write tuning
sort_rank: 8
---
remote write tuning
prometheus implements sane defaults for remote write, but many users have
different requirements and would like to optimize their remote settings.
this page describes the tuning parameters available via the [remote write
configuration.](/docs/prometheus/latest/configuration/configuration/
remote_write)
remote write characteristics
each remote write destination starts a queue which reads from the write-ahead
log (wal), writes the samples into an in memory queue owned by a shard, which
then sends a request to the configured endpoint. the flow of data looks like:
```
      |-->  queue (shard_1)   --> remote endpoint
wal --|-->  queue (shard_...) --> remote endpoint
      |-->  queue (shard_n)   --> remote endpoint
```
when one shard backs up and fills its queue, prometheus will block reading from
the wal into any shards. failures will be retried without loss of data unless
the remote endpoint remains down for more than 2 hours. after 2 hours, the wal
will be compacted and data that has not been sent will be lost.
during operation, prometheus will continuously calculate the optimal number of
shards to use based on the incoming sample rate, number of outstanding samples
not sent, and time taken to send each sample.
resource usage
using remote write increases the memory footprint of prometheus. most users
report ~25% increased memory usage, but that number is dependent on the shape
of the data. for each series in the wal, the remote write code caches a mapping
of series id to label values, causing large amounts of series churn to
significantly increase memory usage.
in addition to the series cache, each shard and its queue increases memory
usage. shard memory is proportional to the `number of shards * (capacity +
max_samples_per_send)`. when tuning, consider reducing `max_shards` alongside
increases to `capacity` and `max_samples_per_send` to avoid inadvertently
running out of memory. the default values for `capacity: 10000` and
`max_samples_per_send: 2000` will constrain shard memory usage to less than 2
mb per shard.
remote write will also increase cpu and network usage. however, for the same
reasons as above, it is difficult to predict by how much. it is generally a
good practice to check for cpu and network saturation if your prometheus server
falls behind sending samples via remote write
(`prometheus_remote_storage_samples_pending`).
parameters
all the relevant parameters are found under the `queue_config` section of the
remote write configuration.
`capacity`
capacity controls how many samples are queued in memory per shard before
blocking reading from the wal. once the wal is blocked, samples cannot be
appended to any shards and all throughput will cease.
capacity should be high enough to avoid blocking other shards in most
cases, but too much capacity can cause excess memory consumption and longer
times to clear queues during resharding. it is recommended to set capacity
to 3-10 times `max_samples_per_send`.
`max_shards`
max shards configures the maximum number of shards, or parallelism, prometheus
will use for each remote write queue. prometheus will try not to use too many
shards, but if the queue falls behind the remote write component will increase
the number of shards up to max shards to increase throughput. unless remote
writing to a very slow endpoint, it is unlikely that `max_shards` should be
increased beyond the default. however, it may be necessary to reduce max shards
if there is potential to overwhelm the remote endpoint, or to reduce memory
usage when data is backed up.
`min_shards`
min shards configures the minimum number of shards used by prometheus, and is
the number of shards used when remote write starts. if remote write falls
behind, prometheus will automatically scale up the number of shards so most
users do not have to adjust this parameter. however, increasing min shards will
allow prometheus to avoid falling behind at the beginning while calculating the
required number of shards.
`max_samples_per_send`
max samples per send can be adjusted depending on the backend in use. many
systems work very well by sending more samples per batch without a significant
increase in latency. other backends will have issues if trying to send a large
number of samples in each request. the default value is small enough to work for
most systems.
`batch_send_deadline`
batch send deadline sets the maximum amount of time between sends for a single
shard. even if the queued shards has not reached `max_samples_per_send`, a
request will be sent. batch send deadline can be increased for low volume
systems that are not latency sensitive in order to increase request efficiency.
`min_backoff`
min backoff controls the minimum amount of time to wait before retrying a failed
request. increasing the backoff spreads out requests when a remote endpoint
comes back online. the backoff interval is doubled for each failed requests up
to `max_backoff`.
`max_backoff`
max backoff controls the maximum amount of time to wait before retrying a failed
request.