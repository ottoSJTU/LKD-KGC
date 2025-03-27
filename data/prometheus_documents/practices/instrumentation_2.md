timestamps, not time since
if you want to track the amount of time since something happened, export the
unix timestamp at which it happened - not the time since it happened.
with the timestamp exported, you can use the expression `time() - my_timestamp_metric` to
calculate the time since the event, removing the need for update logic and
protecting you against the update logic getting stuck.
inner loops
in general, the additional resource cost of instrumentation is far outweighed by
the benefits it brings to operations and development.
for code which is performance-critical or called more than 100k times a second
inside a given process, you may wish to take some care as to how many metrics
you update.
a java counter takes
[12-17ns](_java/blob/master/benchmark/readme.md)
to increment depending on contention. other languages will have similar
performance. if that amount of time is significant for your inner loop, limit
the number of metrics you increment in the inner loop and avoid labels (or
cache the result of the label lookup, for example, the return value of `with()`
in go or `labels()` in java) where possible.
beware also of metric updates involving time or durations, as getting the time
may involve a syscall. as with all matters involving performance-critical code,
benchmarks are the best way to determine the impact of any given change.
avoid missing metrics
time series that are not present until something happens are difficult
to deal with, as the usual simple operations are no longer sufficient to
correctly handle them. to avoid this, export a default value such as `0` for
any time series you know may exist in advance.
most prometheus client libraries (including go, java, and python) will
automatically export a `0` for you for metrics with no labels.