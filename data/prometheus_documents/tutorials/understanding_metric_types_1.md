---
title: understanding metric types  
sort_rank: 2
---
types of metrics.
prometheus supports four types of metrics, which are
    - counter
    - gauge
    - histogram
    - summary
counter
counter is a metric value that can only increase or reset i.e. the value cannot reduce than the previous value. it can be used for metrics like the number of requests, no of errors, etc.
type the below query in the query bar and click execute.
<code>go\_gc\_duration\_seconds\_count</code>
[![counter](/assets/tutorial/counter_example.png)](/assets/tutorial/counter_example.png)
the rate() function in promql takes the history of metrics over a time frame and calculates how fast the value is increasing per second. rate is applicable on counter values only.
<code> rate(go\_gc\_duration\_seconds\_count[5m])</code>
[![rate counter](/assets/tutorial/rate_example.png)](/assets/tutorial/rate_example.png)
gauge
gauge is a number which can either go up or down. it can be used for metrics like the number of pods in a cluster, the number of events in a queue, etc.
<code> go\_memstats\_heap\_alloc\_bytes</code>
[![gauge](/assets/tutorial/gauge_example.png)](/assets/tutorial/gauge_example.png)
promql functions like `max_over_time`, `min_over_time` and `avg_over_time` can be used on gauge metrics
histogram
histogram is a more complex metric type when compared to the previous two. histogram can be used for any calculated value which is counted based on bucket values. bucket boundaries can be configured by the developer. a common example would be the time it takes to reply to a request, called latency.
example: let's assume we want to observe the time taken to process api requests. instead of storing the request time for each request, histograms allow us to store them in buckets. we define buckets for time taken, for example `lower or equal 0.3`, `le 0.5`, `le 0.7`, `le 1`, and `le 1.2`. so these are our buckets and once the time taken for a request is calculated it is added to the count of all the buckets whose bucket boundaries are higher than the measured value.
let's say request 1 for endpoint “/ping” takes 0.25 s. the count values for the buckets will be.
> /ping
| bucket    | count |
| --------- | ----- |
| 0 - 0.3   | 1     |
| 0 - 0.5   | 1     |
| 0 - 0.7   | 1     |
| 0 - 1     | 1     |
| 0 - 1.2   | 1     |
| 0 - +inf  | 1     |
note: +inf bucket is added by default.
(since the histogram is a cumulative frequency 1 is added to all the buckets that are greater than the value)
request 2 for endpoint “/ping” takes 0.4s the count values for the buckets will be this.
> /ping
| bucket    | count |
| --------- | ----- |
| 0 - 0.3   | 1     |
| 0 - 0.5   | 2     |
| 0 - 0.7   | 2     |
| 0 - 1     | 2     |
| 0 - 1.2   | 2     |
| 0 - +inf  | 2     |
since 0.4 is below 0.5, all buckets up to that boundary increase their counts.
let's explore a histogram metric from the prometheus ui and apply a few functions.
<code>prometheus\_http\_request\_duration\_seconds\_bucket{handler="/graph"}</code>
[![histogram](/assets/tutorial/histogram_example.png)](/assets/tutorial/histogram_example.png)
`histogram_quantile()` function can be used to calculate quantiles from a histogram
<code>histogram\_quantile(0.9,prometheus\_http\_request\_duration\_seconds\_bucket{handler="/graph"})</code>
[![histogram quantile](/assets/tutorial/histogram_quantile_example.png)](/assets/tutorial/histogram_quantile_example.png)
the graph shows that the 90th percentile is 0.09, to find the histogram_quantile over the last 5m you can use the rate() and time frame
<code>histogram_quantile(0.9, rate(prometheus\_http\_request\_duration\_seconds\_bucket{handler="/graph"}[5m]))</code>
[![histogram quantile rate](/assets/tutorial/histogram_rate_example.png)](/assets/tutorial/histogram_rate_example.png)
summary
summaries also measure events and are an alternative to histograms. they are cheaper but lose more data. they are calculated on the application level hence aggregation of metrics from multiple instances of the same process is not possible. they are used when the buckets of a metric are not known beforehand, but it is highly recommended to use histograms over summaries whenever possible.
in this tutorial, we covered the types of metrics in detail and a few promql operations like rate, histogram_quantile, etc.