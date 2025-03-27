---
title: visualizing metrics using grafana
sort_rank: 4
---
visualizing metrics.
in this tutorial we will create a simple dashboard using [grafana]() to visualize the `ping_request_count` metric that we instrumented in the [previous tutorial](../instrumenting_http_server_in_go).
if you are wondering why one should use a tool like grafana when one can query and see the graphs using prometheus, the answer is that the graph that we see when we run queries on prometheus is to run ad-hoc queries. 
grafana and [console templates]() are two recommended ways of creating graphs.
installing and setting up grafana.
install and run grafana by following the steps from [here](
supported-operating-systems) for your operating system.
once grafana is installed and run, navigate to []() in your browser. use the default credentials, username as `admin` and password as `admin` to log in and setup new credentials.
adding prometheus as a data source in grafana.
let's add a datasource to grafana by clicking on the gear icon in the side bar and select `data sources`
> ⚙ > data sources
in the data sources screen you can see that grafana supports multiple data sources like graphite, postgresql etc. select prometheus to set it up.
enter the url as []() under the http section and click on `save and test`.
<iframe width="560" height="315" src="_h9lo" frameborder="0" allowfullscreen></iframe>
creating our first dashboard.
now we have successfully added prometheus as a data source, next we will create our first dashboard for the `ping_request_count` metric that we instrumented in the previous tutorial.
1. click on the `+` icon in the side bar and select `dashboard`.
2. in the next screen, click on the `add new panel` button.
3. in the `query` tab type the promql query, in this case just type `ping_request_count`.
4. access the `ping` endpoint few times and refresh the graph to verify if it is working as expected.
4. in the right hand section under `panel options` set the `title` as `ping request count`.
5. click on the save icon in the right corner to save the dashboard.
<iframe width="560" height="315" src="" frameborder="0" allowfullscreen></iframe>