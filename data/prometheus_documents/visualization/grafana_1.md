---
title: grafana
sort_rank: 2
---
grafana support for prometheus
[grafana]() supports querying prometheus.
the grafana data source for prometheus is included since grafana 2.5.0 (2015-10-28).
the following shows an example grafana dashboard which queries prometheus for data:
[![grafana screenshot](/assets/grafana_prometheus.png)](/assets/grafana_prometheus.png)
installing
to install grafana see the [official grafana
documentation]().
using
by default, grafana will be listening on
[](). the default login is "admin" /
"admin".
creating a prometheus data source
to create a prometheus data source in grafana:
1. click on the "cogwheel" in the sidebar to open the configuration menu.
2. click on "data sources".
3. click on "add data source".
4. select "prometheus" as the type.
5. set the appropriate prometheus server url (for example, ``)
6. adjust other data source settings as desired (for example, choosing the right access method).
7. click "save & test" to save the new data source.
the following shows an example data source configuration:
[![data source configuration](/assets/grafana_configuring_datasource.png)](/assets/grafana_configuring_datasource.png)
creating a prometheus graph
follow the standard way of adding a new grafana graph. then:
1. click the graph title, then click "edit".
2. under the "metrics" tab, select your prometheus data source (bottom right).
3. enter any prometheus expression into the "query" field, while using the
   "metric" field to lookup metrics via autocompletion.
4. to format the legend names of time series, use the "legend format" input. for
   example, to show only the `method` and `status` labels of a returned query
   result, separated by a dash, you could use the legend format string
   `{{method}} - {{status}}`.
5. tune other graph settings until you have a working graph.
the following shows an example prometheus graph configuration:
[![prometheus graph creation](/assets/grafana_qps_graph.png)](/assets/grafana_qps_graph.png)
in grafana 7.2 and later, the `$__rate_interval` variable is
[recommended](
using-__rate_interval)
for use in the `rate`and `increase` functions.
importing pre-built dashboards from grafana.com
grafana.com maintains [a collection of shared dashboards]()
which can be downloaded and used with standalone instances of grafana.  use
the grafana.com "filter" option to browse dashboards for the "prometheus"
data source only.
you must currently manually edit the downloaded json files and correct the
`datasource:` entries to reflect the grafana data source name which you
chose for your prometheus server.  use the "dashboards" → "home" → "import"
option to import the edited dashboard file into your grafana install.