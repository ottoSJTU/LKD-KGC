do-not-overuse-labels).
accordingly client libraries must be very careful in how labels are offered to
users.
client libraries must not allow users to have different
label names for the same metric for gauge/counter/summary/histogram or any
other collector offered by the library.
metrics from custom collectors should almost always have consistent label
names. as there are still rare but valid use cases where this is not the case,
client libraries should not verify this.
while labels are powerful, the majority of metrics will not have labels.
accordingly the api should allow for labels but not dominate it.
a client library must allow for optionally specifying a list of label names at
gauge/counter/summary/histogram creation time. a client library should support
any number of label names. a client library must validate that label names meet
the [documented
requirements](/docs/concepts/data_model/
metric-names-and-labels).
the general way to provide access to labeled dimension of a metric is via a
`labels()` method that takes either a list of the label values or a map from
label name to label value and returns a "child". the usual
`.inc()`/`.dec()`/`.observe()` etc. methods can then be called on the child.
the child returned by `labels()` should be cacheable by the user, to avoid
having to look it up again - this matters in latency-critical code.
metrics with labels should support a `remove()` method with the same signature
as `labels()` that will remove a child from the metric no longer exporting it,
and a `clear()` method that removes all children from the metric. these
invalidate caching of children.
there should be a way to initialize a given child with the default value,
usually just calling `labels()`. metrics without labels must always be
initialized to avoid [problems with missing
metrics](/docs/practices/instrumentation/
avoid-missing-metrics).
metric names
metric names must follow the
[specification](/docs/concepts/data_model/
metric-names-and-labels). as with
label names, this must be met for uses of gauge/counter/summary/histogram and
in any other collector offered with the library.
many client libraries offer setting the name in three parts:
`namespace_subsystem_name` of which only the `name` is mandatory.
dynamic/generated metric names or subparts of metric names must be discouraged,
except when a custom collector is proxying from other
instrumentation/monitoring systems. generated/dynamic metric names are a sign
that you should be using labels instead.
metric description and help
gauge/counter/summary/histogram must require metric descriptions/help to be
provided.
any custom collectors provided with the client libraries must have
descriptions/help on their metrics.
it is suggested to make it a mandatory argument, but not to check that it’s of
a certain length as if someone really doesn’t want to write docs we’re not
going to convince them otherwise. collectors offered with the library (and
indeed everywhere we can within the ecosystem) should have good metric
descriptions, to lead by example.
exposition
clients must implement the text-based exposition format outlined in the
[exposition formats](/docs/instrumenting/exposition_formats) documentation.
reproducible order of the exposed metrics is encouraged (especially for human
readable formats) if it can be implemented without a significant resource cost.
standard and runtime collectors
client libraries should offer what they can of the standard exports, documented
below.
these should be implemented as custom collectors, and registered by default on
the default collectorregistry. there should be a way to disable these, as there
are some very niche use cases where they get in the way.
process metrics
these metrics have the prefix `process_`. if obtaining a necessary value is
problematic or even impossible with the used language or runtime, client
libraries should prefer leaving out the corresponding metric over exporting
bogus, inaccurate, or special values (like `nan`). all memory values in bytes,
all times in unixtime/seconds.
| metric name                        | help string                                            | unit             |
| ---------------------------------- | ------------------------------------------------------ | ---------------  |
| `process_cpu_seconds_total`        | total user and system cpu time spent in seconds.       | seconds          |
| `process_open_fds`                 | number of open file descriptors.                       | file descriptors |
| `process_max_fds`                  | maximum number of open file descriptors.               | file descriptors |
| `process_virtual_memory_bytes`     | virtual memory size in bytes.                          | bytes            |
| `process_virtual_memory_max_bytes` | maximum amount of virtual memory available in bytes.   | bytes            |
| `process_resident_memory_bytes`    | resident memory size in bytes.                         | bytes            |
| `process_heap_bytes`               | process heap size in bytes.                            | bytes            |
| `process_start_time_seconds`       | start time of the process since unix epoch in seconds. | seconds          |
| `process_threads`                  | number of os threads in the process.             | threads          |
runtime metrics
in addition, client libraries are encouraged to also offer whatever makes sense
in terms of metrics for their language’s runtime (e.g. garbage collection
stats), with an appropriate prefix such as `go_`, `hotspot_` etc.
unit tests
client libraries should have unit tests covering the core instrumentation
library and exposition.
client libraries are encouraged to offer ways that make it easy for users to
unit-test their use of the instrumentation code. for example, the
`collectorregistry.get_sample_value` in python.
packaging and dependencies
ideally, a client library can be included in any application to add some
instrumentation without breaking the application.
accordingly, caution is advised when adding dependencies to the client library.
for example, if you add a library that uses a prometheus client that requires
version x.y of a library but the application uses x.z elsewhere, will that have
an adverse impact on the application?
it is suggested that where this may arise, that the core instrumentation is
separated from the bridges/exposition of metrics in a given format. for
example, the java simpleclient `simpleclient` module has no dependencies, and
the `simpleclient_servlet` has the http bits.
performance considerations
as client libraries must be thread-safe, some form of concurrency control is
required and consideration must be given to performance on multi-core machines
and applications.
in our experience the least performant is mutexes.
processor atomic instructions tend to be in the middle, and generally
acceptable.
approaches that avoid different cpus mutating the same bit of ram work best,
such as the doubleadder in java’s simpleclient. there is a memory cost though.
as noted above, the result of `labels()` should be cacheable. the concurrent
maps that tend to back metric with labels tend to be relatively slow.
special-casing metrics without labels to avoid `labels()`-like lookups can help
a lot.
metrics should avoid blocking when they are being incremented/decremented/set
etc. as it’s undesirable for the whole application to be held up while a scrape
is ongoing.
having benchmarks of the main instrumentation operations, including labels, is
encouraged.
resource consumption, particularly ram, should be kept in mind when performing
exposition. consider reducing the memory footprint by streaming results, and
potentially having a limit on the number of concurrent scrapes.