errors of quantile estimation
quantiles, whether calculated client-side or server-side, are
estimated. it is important to understand the errors of that
estimation.
continuing the histogram example from above, imagine your usual
request durations are almost all very close to 220ms, or in other
words, if you could plot the "true" histogram, you would see a very
sharp spike at 220ms. in the prometheus histogram metric as configured
above, almost all observations, and therefore also the 95th percentile,
will fall into the bucket labeled `{le="0.3"}`, i.e. the bucket from
200ms to 300ms. the histogram implementation guarantees that the true
95th percentile is somewhere between 200ms and 300ms. to return a
single value (rather than an interval), it applies linear
interpolation, which yields 295ms in this case. the calculated
quantile gives you the impression that you are close to breaching the
slo, but in reality, the 95th percentile is a tiny bit above 220ms,
a quite comfortable distance to your slo.
next step in our thought experiment: a change in backend routing
adds a fixed amount of 100ms to all request durations. now the request
duration has its sharp spike at 320ms and almost all observations will
fall into the bucket from 300ms to 450ms. the 95th percentile is
calculated to be 442.5ms, although the correct value is close to
320ms. while you are only a tiny bit outside of your slo, the
calculated 95th quantile looks much worse.
a summary would have had no problem calculating the correct percentile
value in both cases, at least if it uses an appropriate algorithm on
the client side (like the [one used by the go
client](~graham/pubs/slides/bquant-long.pdf)).
unfortunately, you cannot use a summary if you need to aggregate the
observations from a number of instances.
luckily, due to your appropriate choice of bucket boundaries, even in
this contrived example of very sharp spikes in the distribution of
observed values, the histogram was able to identify correctly if you
were within or outside of your slo. also, the closer the actual value
of the quantile is to our slo (or in other words, the value we are
actually most interested in), the more accurate the calculated value
becomes.
let us now modify the experiment once more. in the new setup, the
distributions of request durations has a spike at 150ms, but it is not
quite as sharp as before and only comprises 90% of the
observations. 10% of the observations are evenly spread out in a long
tail between 150ms and 450ms. with that distribution, the 95th
percentile happens to be exactly at our slo of 300ms. with the
histogram, the calculated value is accurate, as the value of the 95th
percentile happens to coincide with one of the bucket boundaries. even
slightly different values would still be accurate as the (contrived)
even distribution within the relevant buckets is exactly what the
linear interpolation within a bucket assumes.
the error of the quantile reported by a summary gets more interesting
now. the error of the quantile in a summary is configured in the
dimension of φ. in our case we might have configured 0.95±0.01,
i.e. the calculated value will be between the 94th and 96th
percentile. the 94th quantile with the distribution described above is
270ms, the 96th quantile is 330ms. the calculated value of the 95th
percentile reported by the summary can be anywhere in the interval
between 270ms and 330ms, which unfortunately is all the difference
between clearly within the slo vs. clearly outside the slo.
the bottom line is: if you use a summary, you control the error in the
dimension of φ. if you use a histogram, you control the error in the
dimension of the observed value (via choosing the appropriate bucket
layout). with a broad distribution, small changes in φ result in
large deviations in the observed value. with a sharp distribution, a
small interval of observed values covers a large interval of φ.
two rules of thumb:
  1. if you need to aggregate, choose histograms.
  2. otherwise, choose a histogram if you have an idea of the range
     and distribution of values that will be observed. choose a
     summary if you need an accurate quantile, no matter what the
     range and distribution of the values is.
what can i do if my client library does not support the metric type i need?
implement it! [code contributions are welcome](/community/). in general, we
expect histograms to be more urgently needed than summaries. histograms are
also easier to implement in a client library, so we recommend to implement
histograms first, if in doubt.