---
title: recording rules
sort_rank: 6
---
recording rules
a consistent naming scheme for [recording rules](/docs/prometheus/latest/configuration/recording_rules/)
makes it easier to interpret the meaning of a rule at a glance. it also avoids
mistakes by making incorrect or meaningless calculations stand out.
this page documents proper naming conventions and aggregation for recording rules.
naming 
* recording rules should be of the general form `level:metric:operations`.
* `level` represents the aggregation level and labels of the rule output.
* `metric` is the metric name and should be unchanged other than stripping `_total` off counters when using `rate()` or `irate()`.
* `operations` is a list of operations that were applied to the metric, newest operation first.
keeping the metric name unchanged makes it easy to know what a metric is and
easy to find in the codebase.
to keep the operations clean, `_sum` is omitted if there are other operations,
as `sum()`. associative operations can be merged (for example `min_min` is the
same as `min`).
if there is no obvious operation to use, use `sum`.  when taking a ratio by
doing division, separate the metrics using `_per_` and call the operation
`ratio`.
aggregation
* when aggregating up ratios, aggregate up the numerator and denominator
separately and then divide.
* do not take the average of a ratio or average of an
average, as that is not statistically valid.
* when aggregating up the `_count` and `_sum` of a summary and dividing to
calculate average observation size, treating it as a ratio would be unwieldy.
instead keep the metric name without the `_count` or `_sum` suffix and replace
the `rate` in the operation with `mean`. this represents the average
observation size over that time period.
* always specify a `without` clause with the labels you are aggregating away.
this is to preserve all the other labels such as `job`, which will avoid
conflicts and give you more useful metrics and alerts.
examples
_note the indentation style with outdented operators on their own line between
two vectors. to make this style possible in yaml, [block quotes with an
indentation indicator](
style/block/scalar)
(e.g. `|2`) are used._
aggregating up requests per second that has a `path` label:
```
- record: instance_path:requests:rate5m
  expr: rate(requests_total{job="myjob"}[5m])
- record: path:requests:rate5m
  expr: sum without (instance)(instance_path:requests:rate5m{job="myjob"})
```
calculating a request failure ratio and aggregating up to the job-level failure ratio:
```
- record: instance_path:request_failures:rate5m
  expr: rate(request_failures_total{job="myjob"}[5m])
- record: instance_path:request_failures_per_requests:ratio_rate5m
  expr: |2
      instance_path:request_failures:rate5m{job="myjob"}
    /
      instance_path:requests:rate5m{job="myjob"}
aggregate up numerator and denominator, then divide to get path-level ratio.
- record: path:request_failures_per_requests:ratio_rate5m
  expr: |2
      sum without (instance)(instance_path:request_failures:rate5m{job="myjob"})
    /
      sum without (instance)(instance_path:requests:rate5m{job="myjob"})
no labels left from instrumentation or distinguishing instances,
so we use 'job' as the level.
- record: job:request_failures_per_requests:ratio_rate5m
  expr: |2
      sum without (instance, path)(instance_path:request_failures:rate5m{job="myjob"})
    /
      sum without (instance, path)(instance_path:requests:rate5m{job="myjob"})
```
calculating average latency over a time period from a summary:
```
- record: instance_path:request_latency_seconds_count:rate5m
  expr: rate(request_latency_seconds_count{job="myjob"}[5m])
- record: instance_path:request_latency_seconds_sum:rate5m
  expr: rate(request_latency_seconds_sum{job="myjob"}[5m])
- record: instance_path:request_latency_seconds:mean5m
  expr: |2
      instance_path:request_latency_seconds_sum:rate5m{job="myjob"}
    /
      instance_path:request_latency_seconds_count:rate5m{job="myjob"}
aggregate up numerator and denominator, then divide.
- record: path:request_latency_seconds:mean5m
  expr: |2
      sum without (instance)(instance_path:request_latency_seconds_sum:rate5m{job="myjob"})
    /
      sum without (instance)(instance_path:request_latency_seconds_count:rate5m{job="myjob"})
```
calculating the average query rate across instances and paths is done using the
`avg()` function:
```
- record: job:request_latency_seconds_count:avg_rate5m
  expr: avg without (instance, path)(instance:request_latency_seconds_count:rate5m{job="myjob"})
```
notice that when aggregating that the labels in the `without` clause are removed
from the level of the output metric name compared to the input metric names.
when there is no aggregation, the levels always match. if this is not the case
a mistake has likely been made in the rules.