---
title: console templates
sort_rank: 3
---
console templates
console templates allow for creation of arbitrary consoles using the [go
templating language](). these are served
from the prometheus server.
console templates are the most powerful way to create templates that can be
easily managed in source control. there is a learning curve though, so users new
to this style of monitoring should try out
[grafana](/docs/visualization/grafana/) first.
getting started
prometheus comes with an example set of consoles to get you going. these can be
found at `/consoles/index.html.example` on a running prometheus and will
display node exporter consoles if prometheus is scraping node exporters with a
`job="node"` label.
the example consoles have 5 parts:
1. a navigation bar on top
1. a menu on the left
1. time controls on the bottom
1. the main content in the center, usually graphs
1. a table on the right
the navigation bar is for links to other systems, such as other prometheis
<sup>[1](/docs/introduction/faq/
what-is-the-plural-of-prometheus)</sup>,
documentation, and whatever else makes sense to you. the menu is for navigation
inside the same prometheus server, which is very useful to be able to quickly
open a console in another tab to correlate information. both are configured in
`console_libraries/menu.lib`.
the time controls allow changing of the duration and range of the graphs.
console urls can be shared and will show the same graphs for others.
the main content is usually graphs. there is a configurable javascript graphing
library provided that will handle requesting data from prometheus, and rendering
it via [rickshaw]().
finally, the table on the right can be used to display statistics in a more
compact form than graphs.
example console
this is a basic console. it shows the number of tasks, how many of them are up,
the average cpu usage, and the average memory usage in the right-hand-side
table. the main content has a queries-per-second graph.
```
{{template "head" .}}
{{template "prom_right_table_head"}}
<tr>
  <th>myjob</th>
  <th>{{ template "prom_query_drilldown" (args "sum(up{job='myjob'})") }}
      / {{ template "prom_query_drilldown" (args "count(up{job='myjob'})") }}
  </th>
</tr>
<tr>
  <td>cpu</td>
  <td>{{ template "prom_query_drilldown" (args
      "avg by(job)(rate(process_cpu_seconds_total{job='myjob'}[5m]))"
      "s/s" "humanizenosmallprefix") }}
  </td>
</tr>
<tr>
  <td>memory</td>
  <td>{{ template "prom_query_drilldown" (args
       "avg by(job)(process_resident_memory_bytes{job='myjob'})"
       "b" "humanize1024") }}
  </td>
</tr>
{{template "prom_right_table_tail"}}
{{template "prom_content_head" .}}
<h1>myjob</h1>
<h3>queries</h3>
<div id="querygraph"></div>
<script>
new promconsole.graph({
  node: document.queryselector("
querygraph"),
  expr: "sum(rate(http_query_count{job='myjob'}[5m]))",
  name: "queries",
  yaxisformatter: promconsole.numberformatter.humanizenosmallprefix,
  yhoverformatter: promconsole.numberformatter.humanizenosmallprefix,
  yunits: "/s",
  ytitle: "queries"
})
</script>
{{template "prom_content_tail" .}}
{{template "tail"}}
```
the `prom_right_table_head` and `prom_right_table_tail` templates contain the
right-hand-side table. this is optional.
`prom_query_drilldown` is a template that will evaluate the expression passed to it, format it,
and link to the expression in the [expression browser](/docs/visualization/browser/). the first
argument is the expression. the second argument is the unit to use. the third
argument is how to format the output. only the first argument is required.
valid output formats for the third argument to `prom_query_drilldown`:
* not specified: default go display output.
* `humanize`: display the result using [metric prefixes](_prefix).
* `humanizenosmallprefix`: for absolute values greater than 1, display the
  result using [metric prefixes](_prefix). for
  absolute values less than 1, display 3 significant digits. this is useful
  to avoid units such as milliqueries per second that can be produced by
  `humanize`.
* `humanize1024`: display the humanized result using a base of 1024 rather than 1000.
  this is usually used with `b` as the second argument to produce units such as `kib` and `mib`.
* `printf.3g`: display 3 significant digits.
custom formats can be defined. see
[prom.lib](_libraries/prom.lib) for examples.
graph library
the graph library is invoked as:
```
<div id="querygraph"></div>
<script>
new promconsole.graph({
  node: document.queryselector("
querygraph"),
  expr: "sum(rate(http_query_count{job='myjob'}[5m]))"
})
</script>
```
the `head` template loads the required javascript and css.
parameters to the graph library:
| name          | description
| ------------- | -------------
| expr          | required. expression to graph. can be a list.
| node          | required. dom node to render into.
| duration      | optional. duration of the graph. defaults to 1 hour.
| endtime       | optional. unixtime the graph ends at. defaults to now.
| width         | optional. width of the graph, excluding titles. defaults to auto-detection.
| height        | optional. height of the graph, excluding titles and legends. defaults to 200 pixels.
| min           | optional. minimum x-axis value. defaults to lowest data value.
| max           | optional. maximum y-axis value. defaults to highest data value.
| renderer      | optional. type of graph. options are `line` and `area` (stacked graph). defaults to `line`.
| name          | optional. title of plots in legend and hover detail. if passed a string, `[[ label ]]` will be substituted with the label value. if passed a function, it will be passed a map of labels and should return the name as a string. can be a list.
| xtitle        | optional. title of the x-axis. defaults to `time`.
| yunits        | optional. units of the y-axis. defaults to empty.
| ytitle        | optional. title of the y-axis. defaults to empty.
| yaxisformatter | optional. number formatter for the y-axis. defaults to `promconsole.numberformatter.humanize`.
| yhoverformatter | optional. number formatter for the hover detail. defaults to `promconsole.numberformatter.humanizeexact`.
| colorscheme   | optional. color scheme to be used by the plots. can be either a list of hex color codes or one of the [color scheme names]() supported by rickshaw. defaults to `'colorwheel'`.
if both `expr` and `name` are lists, they must be of the same length. the name
will be applied to the plots for the corresponding expression.
valid options for the `yaxisformatter` and `yhoverformatter`:
* `promconsole.numberformatter.humanize`: format using [metric prefixes](_prefix).
* `promconsole.numberformatter.humanizenosmallprefix`: for absolute values
  greater than 1, format using using [metric prefixes](_prefix).
  for absolute values less than 1, format with 3 significant digits. this is
  useful to avoid units such as milliqueries per second that can be produced by
  `promconsole.numberformatter.humanize`.
* `promconsole.numberformatter.humanize1024`: format the humanized result using a base of 1024 rather than 1000.