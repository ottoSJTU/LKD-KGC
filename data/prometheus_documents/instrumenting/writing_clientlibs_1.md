---
title: writing client libraries
sort_rank: 2
---
writing client libraries
this document covers what functionality and api prometheus client libraries
should offer, with the aim of consistency across libraries, making the easy use
cases easy and avoiding offering functionality that may lead users down the
wrong path.
there are [10 languages already supported](/docs/instrumenting/clientlibs) at
the time of writing, so we’ve gotten a good sense by now of how to write a
client. these guidelines aim to help authors of new client libraries produce
good libraries.
conventions
must/must not/should/should not/may have the meanings given in
[]()
in addition encouraged means that a feature is desirable for a library to have,
but it’s okay if it’s not present. in other words, a nice to have.
things to keep in mind:
* take advantage of each language’s features.
* the common use cases should be easy.
* the correct way to do something should be the easy way.
* more complex use cases should be possible.
the common use cases are (in order):
* counters without labels spread liberally around libraries/applications.
* timing functions/blocks of code in summaries/histograms.
* gauges to track current states of things (and their limits).
* monitoring of batch jobs.
overall structure
clients must be written to be callback based internally. clients should
generally follow the structure described here.
the key class is the collector. this has a method (typically called ‘collect’)
that returns zero or more metrics and their samples. collectors get registered
with a collectorregistry. data is exposed by passing a collectorregistry to a
class/method/function "bridge", which returns the metrics in a format
prometheus supports. every time the collectorregistry is scraped it must
callback to each of the collectors’ collect method.
the interface most users interact with are the counter, gauge, summary, and
histogram collectors. these represent a single metric, and should cover the
vast majority of use cases where a user is instrumenting their own code.
more advanced uses cases (such as proxying from another
monitoring/instrumentation system) require writing a custom collector. someone
may also want to write a "bridge" that takes a collectorregistry and produces
data in a format a different monitoring/instrumentation system understands,
allowing users to only have to think about one instrumentation system.
collectorregistry should offer `register()`/`unregister()` functions, and a
collector should be allowed to be registered to multiple collectorregistrys.
client libraries must be thread safe.
for non-oo languages such as c, client libraries should follow the spirit of
this structure as much as is practical.
naming
client libraries should follow function/method/class names mentioned in this
document, keeping in mind the naming conventions of the language they’re
working in. for example, `set_to_current_time()` is good for a method name in 
python, but `settocurrenttime()` is better in go and `settocurrenttime()` is
the convention in java. where names differ for technical reasons (e.g. not
allowing function overloading), documentation/help strings should point users
towards the other names.
libraries must not offer functions/methods/classes with the same or similar
names to ones given here, but with different semantics.
metrics
the counter, gauge, summary and histogram [metric
types](/docs/concepts/metric_types/) are the primary interface by users.
counter and gauge must be part of the client library. at least one of summary
and histogram must be offered.
these should be primarily used as file-static variables, that is, global
variables defined in the same file as the code they’re instrumenting. the
client library should enable this. the common use case is instrumenting a piece
of code overall, not a piece of code in the context of one instance of an
object. users shouldn’t have to worry about plumbing their metrics throughout
their code, the client library should do that for them (and if it doesn’t,
users will write a wrapper around the library to make it "easier" - which
rarely tends to go well).
there must be a default collectorregistry, the standard metrics must by default
implicitly register into it with no special work required by the user. there
must be a way to have metrics not register to the default collectorregistry,
for use in batch jobs and unittests. custom collectors should also follow this.
exactly how the metrics should be created varies by language. for some (java,
go) a builder approach is best, whereas for others (python) function arguments
are rich enough to do it in one call.
for example in the java simpleclient we have:
```java
class yourclass {
  static final counter requests = counter.build()
      .name("requests_total")
      .help("requests.").register();
}
```
this will register requests with the default collectorregistry. by calling
`build()` rather than `register()` the metric won’t be registered (handy for
unittests), you can also pass in a collectorregistry to `register()` (handy for
batch jobs).
counter
[counter](/docs/concepts/metric_types/
counter) is a monotonically increasing
counter. it must not allow the value to decrease, however it may be reset to 0
(such as by server restart).
a counter must have the following methods:
* `inc()`: increment the counter by 1
* `inc(double v)`: increment the counter by the given amount. must check that v >= 0.
a counter is encouraged to have:
a way to count exceptions throw/raised in a given piece of code, and optionally
only certain types of exceptions. this is count_exceptions in python.
counters must start at 0.
gauge
[gauge](/docs/concepts/metric_types/
gauge) represents a value that can go up
and down.
a gauge must have the following methods:
* `inc()`: increment the gauge by 1
* `inc(double v)`: increment the gauge by the given amount
* `dec()`: decrement the gauge by 1
* `dec(double v)`: decrement the gauge by the given amount
* `set(double v)`: set the gauge to the given value
gauges must start at 0, you may offer a way for a given gauge to start at a
different number.
a gauge should have the following methods:
* `set_to_current_time()`: set the gauge to the current unixtime in seconds.
a gauge is encouraged to have:
a way to track in-progress requests in some piece of code/function. this is
`track_inprogress` in python.
a way to time a piece of code and set the gauge to its duration in seconds.
this is useful for batch jobs. this is starttimer/setduration in java and the
`time()` decorator/context manager in python. this should match the pattern in
summary/histogram (though `set()` rather than `observe()`).
summary
a [summary](/docs/concepts/metric_types/
summary) samples observations (usually
things like request durations) over sliding windows of time and provides
instantaneous insight into their distributions, frequencies, and sums.
a summary must not allow the user to set "quantile" as a label name, as this is
used internally to designate summary quantiles. a summary is encouraged to
offer quantiles as exports, though these can’t be aggregated and tend to be
slow. a summary must allow not having quantiles, as just `_count`/`_sum` is
quite useful and this must be the default.
a summary must have the following methods:
* `observe(double v)`: observe the given amount
a summary should have the following methods:
some way to time code for users in seconds. in python this is the `time()`
decorator/context manager. in java this is starttimer/observeduration. units
other than seconds must not be offered (if a user wants something else, they
can do it by hand). this should follow the same pattern as gauge/histogram.
summary `_count`/`_sum` must start at 0.
histogram
[histograms](/docs/concepts/metric_types/
histogram) allow aggregatable
distributions of events, such as request latencies. this is at its core a
counter per bucket.
a histogram must not allow `le` as a user-set label, as `le` is used internally
to designate buckets.
a histogram must offer a way to manually choose the buckets. ways to set
buckets in a `linear(start, width, count)` and `exponential(start, factor,
count)` fashion should be offered. count must include the `+inf` bucket.
a histogram should have the same default buckets as other client libraries.
buckets must not be changeable once the metric is created.
a histogram must have the following methods:
* `observe(double v)`: observe the given amount
a histogram should have the following methods:
some way to time code for users in seconds. in python this is the `time()`
decorator/context manager. in java this is `starttimer`/`observeduration`.
units other than seconds must not be offered (if a user wants something else,
they can do it by hand). this should follow the same pattern as gauge/summary.
histogram  `_count`/`_sum` and the buckets must start at 0.
**further metrics considerations**
providing additional functionality in metrics beyond what’s documented above as
makes sense for a given language is encouraged.
if there’s a common use case you can make simpler then go for it, as long as it
won’t encourage undesirable behaviours (such as suboptimal metric/label
layouts, or doing computation in the client).
labels
labels are one of the [most powerful
aspects](/docs/practices/instrumentation/
use-labels) of prometheus, but
[easily abused](/docs/practices/instrumentation/