---
title: exporters and integrations
sort_rank: 4
---
exporters and integrations
there are a number of libraries and servers which help in exporting existing
metrics from third-party systems as prometheus metrics. this is useful for
cases where it is not feasible to instrument a given system with prometheus
metrics directly (for example, haproxy or linux system stats).
third-party exporters
some of these exporters are maintained as part of the official [prometheus github organization](),
those are marked as *official*, others are externally contributed and maintained.
we encourage the creation of more exporters but cannot vet all of them for
[best practices](/docs/instrumenting/writing_exporters/).
commonly, those exporters are hosted outside of the prometheus github
organization.
the [exporter default
port]()
wiki page has become another catalog of exporters, and may include exporters
not listed here due to overlapping functionality or still being in development.
the [jmx exporter](_exporter) can export from a
wide variety of jvm-based applications, for example [kafka]() and
[cassandra]().
databases
   * [aerospike exporter]()
   * [aws rds exporter]()
   * [clickhouse exporter](_exporter)
   * [consul exporter](_exporter) (**official**)
   * [couchbase exporter]()
   * [couchdb exporter]()
   * [druid exporter]()
   * [elasticsearch exporter](_exporter)
   * [eventstore exporter](_exporter)
   * [iotdb exporter]()
   * [kdb+ exporter]()
   * [memcached exporter](_exporter) (**official**)
   * [mongodb exporter](_exporter)
   * [mongodb query exporter]()
   * [mongodb node.js driver exporter]()
   * [mssql server exporter]()
   * [mysql router exporter](_exporter)
   * [mysql server exporter](_exporter) (**official**)
   * [opentsdb exporter](_exporter)
   * [oracle db exporter](_exporter)
   * [pgbouncer exporter](_exporter)
   * [postgresql exporter](_exporter)
   * [presto exporter](_exporter)
   * [proxysql exporter](_exporter)
   * [ravendb exporter](_exporter)
   * [redis exporter](_exporter)
   * [rethinkdb exporter](_exporter)
   * [sql exporter](_exporter)
   * [tarantool metric library]()
   * [twemproxy](_exporter)
hardware related
   * [apcupsd exporter](_exporter)
   * [big-ip exporter](_exporter)
   * [bosch sensortec bmp/bme exporter]()
   * [collins exporter](_exporter)
   * [dell hardware omsa exporter](_exporter)
   * [disk usage exporter](_usage_exporter)
   * [fortigate exporter](_exporter)
   * [ibm z hmc exporter]()
   * [iot edison exporter](_exporter)
   * [infiniband exporter](_exporter)
   * [ipmi exporter](_exporter)
   * [knxd exporter](_exporter)
   * [modbus exporter](_exporter)
   * [netgear cable modem exporter](_cm_exporter)
   * [netgear router exporter](_exporter)
   * [network ups tools (nut) exporter](_exporter)
   * [node/system metrics exporter](_exporter) (**official**)
   * [nvidia gpu exporter](_gpu_prometheus_exporter)
   * [prosafe exporter](_exporter)
   * [smartraid exporter]()
   * [waveplus radon sensor exporter](_exporter)
   * [weathergoose climate monitor exporter]()
   * [windows exporter](_exporter)
   * [intel® optane™ persistent memory controller exporter]()
issue trackers and continuous integration
   * [bamboo exporter]()
   * [bitbucket exporter]()
   * [confluence exporter]()
   * [jenkins exporter](_exporter)
   * [jira exporter]()
messaging systems
   * [beanstalkd exporter](_exporter)
   * [emq exporter](_exporter)
   * [gearman exporter]()
   * [ibm mq exporter](_prometheus)
   * [kafka exporter](_exporter)
   * [nats exporter]()
   * [nsq exporter](_exporter)
   * [mirth connect exporter](_exporter)
   * [mqtt blackbox exporter](_blackbox_exporter)
   * [mqtt2prometheus]()
   * [rabbitmq exporter](_exporter)
   * [rabbitmq management plugin exporter](_rabbitmq_exporter)
   * [rocketmq exporter]()
   * [solace exporter]()
storage
   * [ceph exporter](_exporter)
   * [ceph radosgw exporter](_usage_exporter)
   * [gluster exporter](_exporter)
   * [gpfs exporter](_exporter)
   * [hadoop hdfs fsimage exporter]()
   * [hpe csi info metrics provider](_driver/metrics.html)
   * [hpe storage array exporter]()
   * [lustre exporter](_exporter)
   * [netapp e-series exporter](_exporter)
   * [pure storage exporter]()
   * [scaleio exporter]()
   * [tivoli storage manager/ibm spectrum protect exporter](_exporter)
http
   * [apache exporter](_exporter)
   * [haproxy exporter](_exporter) (**official**)
   * [nginx metric library]()
   * [nginx vts exporter]()
   * [passenger exporter](_exporter)
   * [squid exporter]()
   * [tinyproxy exporter](_exporter)
   * [varnish exporter](_varnish_exporter)
   * [webdriver exporter](_exporter)
apis
   * [aws ecs exporter]()
   * [aws health exporter]()
   * [aws sqs exporter](_exporter)
   * [azure health exporter]()
   * [bigbluebutton]()
   * [cloudflare exporter](_exporter)
   * [cryptowat exporter](_exporter)
   * [digitalocean exporter](_exporter)
   * [docker cloud exporter]()
   * [docker hub exporter]()
   * [fastly exporter]()
   * [github exporter]()
   * [gmail exporter]()
   * [graphql exporter](_exporter)
   * [instaclustr exporter](_exporter)
   * [mozilla observatory exporter]()
   * [openweathermap exporter](_exporter)
   * [pagespeed exporter](_exporter)
   * [rancher exporter]()
   * [speedtest exporter](_exporter)
   * [tankerkönig api exporter](_exporter)
logging
   * [fluentd exporter](_exporter)
   * [google's mtail log data extractor]()
   * [grok exporter](_exporter)
finops
   * [aws cost exporter]()
   * [azure cost exporter]()
   * [kubernetes cost exporter]()
other monitoring systems
   * [akamai cloudmonitor exporter](_exporter)
   * [alibaba cloudmonitor exporter]()
   * [aws cloudwatch exporter](_exporter) (**official**)
   * [azure monitor exporter](_metrics_exporter)
   * [cloud foundry firehose exporter](_exporter)
   * [collectd exporter](_exporter) (**official**)
   * [google stackdriver exporter](_exporter)
   * [graphite exporter](_exporter) (**official**)
   * [heka dashboard exporter](_exporter)
   * [heka exporter](_exporter)
   * [huawei cloudeye exporter]()
   * [influxdb exporter](_exporter) (**official**)
   * [itm exporter](_exporter)
   * [java gc exporter](_exporter)
   * [javamelody exporter]()
   * [jmx exporter](_exporter) (**official**)
   * [munin exporter](_exporter)
   * [nagios / naemon exporter]()
   * [neptune apex exporter](_exporter)
   * [new relic exporter](_exporter)
   * [nrpe exporter](_exporter)
   * [osquery exporter](_exporter)
   * [otc cloudeye exporter]()
   * [pingdom exporter]()
   * [promitor (azure monitor)]()
   * [scollector exporter](_scollector)
   * [sensu exporter](_exporter)
   * [site24x7_exporter](_exporter)
   * [snmp exporter](_exporter) (**official**)
   * [statsd exporter](_exporter) (**official**)
   * [tencentcloud monitor exporter]()
   * [thousandeyes exporter](_exporter)
   * [statuspage exporter]()