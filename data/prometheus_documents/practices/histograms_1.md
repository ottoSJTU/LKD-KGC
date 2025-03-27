---
title: histograms and summaries
sort_rank: 4
---
note: this document predates native histograms (added as an experimental
feature in prometheus v2.40). once native histograms are closer to becoming a
stable feature, this document will be thoroughly updated.
histograms and summaries
histograms and summaries are more complex metric types. not only does
a single histogram or summary create a multitude of time series, it is
also more difficult to use these metric types correctly. this section
helps you to pick and configure the appropriate metric type for your
use case.
library support
first of all, check the library support for
[histograms](/docs/concepts/metric_types/
histogram) and
[summaries](/docs/concepts/metric_types/
summary).
some libraries support only one of the two types, or they support summaries
only in a limited fashion (lacking [quantile calculation](
quantiles)).
count and sum of observations
histograms and summaries both sample observations, typically request
durations or response sizes. they track the number of observations
*and* the sum of the observed values, allowing you to calculate the
*average* of the observed values. note that the number of observations
(showing up in prometheus as a time series with a `_count` suffix) is
inherently a counter (as described above, it only goes up). the sum of
observations (showing up as a time series with a `_sum` suffix)
behaves like a counter, too, as long as there are no negative
observations. obviously, request durations or response sizes are
never negative. in principle, however, you can use summaries and
histograms to observe negative values (e.g. temperatures in
centigrade). in that case, the sum of observations can go down, so you
cannot apply `rate()` to it anymore. in those rare cases where you need to
apply `rate()` and cannot avoid negative observations, you can use two
separate summaries, one for positive and one for negative observations
(the latter with inverted sign), and combine the results later with suitable
promql expressions.
to calculate the average request duration during the last 5 minutes
from a histogram or summary called `http_request_duration_seconds`,
use the following expression:
      rate(http_request_duration_seconds_sum[5m])
    /
      rate(http_request_duration_seconds_count[5m])
apdex score
a straight-forward use of histograms (but not summaries) is to count
observations falling into particular buckets of observation
values.
you might have an slo to serve 95% of requests within 300ms. in that
case, configure a histogram to have a bucket with an upper limit of
0.3 seconds. you can then directly express the relative amount of
requests served within 300ms and easily alert if the value drops below
0.95. the following expression calculates it by job for the requests
served in the last 5 minutes. the request durations were collected with
a histogram called `http_request_duration_seconds`.
      sum(rate(http_request_duration_seconds_bucket{le="0.3"}[5m])) by (job)
    /
      sum(rate(http_request_duration_seconds_count[5m])) by (job)
you can approximate the well-known [apdex
score]() in a similar way. configure
a bucket with the target request duration as the upper bound and
another bucket with the tolerated request duration (usually 4 times
the target request duration) as the upper bound. example: the target
request duration is 300ms. the tolerable request duration is 1.2s. the
following expression yields the apdex score for each job over the last
5 minutes:
    (
      sum(rate(http_request_duration_seconds_bucket{le="0.3"}[5m])) by (job)
    +
      sum(rate(http_request_duration_seconds_bucket{le="1.2"}[5m])) by (job)
    ) / 2 / sum(rate(http_request_duration_seconds_count[5m])) by (job)
note that we divide the sum of both buckets. the reason is that the histogram
buckets are
[cumulative](
cumulative_histogram). the
`le="0.3"` bucket is also contained in the `le="1.2"` bucket; dividing it by 2
corrects for that.
the calculation does not exactly match the traditional apdex score, as it
includes errors in the satisfied and tolerable parts of the calculation.
quantiles
you can use both summaries and histograms to calculate so-called φ-quantiles,
where 0 ≤ φ ≤ 1. the φ-quantile is the observation value that ranks at number
φ*n among the n observations. examples for φ-quantiles: the 0.5-quantile is
known as the median. the 0.95-quantile is the 95th percentile.
the essential difference between summaries and histograms is that summaries
calculate streaming φ-quantiles on the client side and expose them directly,
while histograms expose bucketed observation counts and the calculation of
quantiles from the buckets of a histogram happens on the server side using the
[`histogram_quantile()`
function](/docs/prometheus/latest/querying/functions/
histogram_quantile).
the two approaches have a number of different implications:
|   | histogram | summary
|---|-----------|---------
| required configuration | pick buckets suitable for the expected range of observed values. | pick desired φ-quantiles and sliding window. other φ-quantiles and sliding windows cannot be calculated later.
| client performance | observations are very cheap as they only need to increment counters. | observations are expensive due to the streaming quantile calculation.
| server performance | the server has to calculate quantiles. you can use [recording rules](/docs/prometheus/latest/configuration/recording_rules/
recording-rules) should the ad-hoc calculation take too long (e.g. in a large dashboard). | low server-side cost.
| number of time series (in addition to the `_sum` and `_count` series) | one time series per configured bucket. | one time series per configured quantile.
| quantile error (see below for details) | error is limited in the dimension of observed values by the width of the relevant bucket. | error is limited in the dimension of φ by a configurable value.
| specification of φ-quantile and sliding time-window | ad-hoc with [prometheus expressions](/docs/prometheus/latest/querying/functions/
histogram_quantile). | preconfigured by the client.
| aggregation | ad-hoc with [prometheus expressions](/docs/prometheus/latest/querying/functions/
histogram_quantile). | in general [not aggregatable]().
note the importance of the last item in the table. let us return to
the slo of serving 95% of requests within 300ms. this time, you do not
want to display the percentage of requests served within 300ms, but
instead the 95th percentile, i.e. the request duration within which
you have served 95% of requests. to do that, you can either configure
a summary with a 0.95-quantile and (for example) a 5-minute decay
time, or you configure a histogram with a few buckets around the 300ms
mark, e.g. `{le="0.1"}`, `{le="0.2"}`, `{le="0.3"}`, and
`{le="0.45"}`. if your service runs replicated with a number of
instances, you will collect request durations from every single one of
them, and then you want to aggregate everything into an overall 95th
percentile. however, aggregating the precomputed quantiles from a
summary rarely makes sense. in this particular case, averaging the
quantiles yields statistically nonsensical values.
    avg(http_request_duration_seconds{quantile="0.95"}) // bad!
using histograms, the aggregation is perfectly possible with the
[`histogram_quantile()`
function](/docs/prometheus/latest/querying/functions/
histogram_quantile).
    histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) // good.
furthermore, should your slo change and you now want to plot the 90th
percentile, or you want to take into account the last 10 minutes
instead of the last 5 minutes, you only have to adjust the expression
above and you do not need to reconfigure the clients.