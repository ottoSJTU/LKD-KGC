---
title: pushing metrics
sort_rank: 3
---
pushing metrics
occasionally you will need to monitor components which cannot be scraped. the
[prometheus pushgateway]() allows you
to push time series from [short-lived service-level batch
jobs](/docs/practices/pushing/) to an intermediary job which prometheus can
scrape. combined with prometheus's simple text-based exposition format, this
makes it easy to instrument even shell scripts without a client library.
 * for more information on using the pushgateway and use from a unix shell, see the project's
[readme.md]().
 * for use from java see the
[pushgateway documentation](_java/exporters/pushgateway/).
 * for use from go see the [push](_golang/prometheus/push
pusher.push) and [add](_golang/prometheus/push
pusher.add) methods.
 * for use from python see [exporting to a pushgateway](_python/exporting/pushgateway/).
 * for use from ruby see the [pushgateway documentation](_ruby
pushgateway).
* to find out about pushgateway support of [client libraries maintained outside of the prometheus project](/docs/instrumenting/clientlibs/), refer to their respective documentation.