---
title: consoles and dashboards
sort_rank: 3
---
consoles and dashboards
it can be tempting to display as much data as possible on a dashboard, especially
when a system like prometheus offers the ability to have such rich
instrumentation of your applications. this can lead to consoles that are
impenetrable due to having too much information, that even an expert in the
system would have difficulty drawing meaning from.
instead of trying to represent every piece of data you have, for operational
consoles think of what are the most likely failure modes and how you would use the
consoles to differentiate them. take advantage of the structure of your
services. for example, if you have a big tree of services in an online-serving
system, latency in some lower service is a typical problem. rather than showing
every service's information on a single large dashboard, build separate dashboards
for each service that include the latency and errors for each service they talk
to. you can then start at the top and work your way down to the problematic
service.
we have found the following guidelines very effective:
* have no more than 5 graphs on a console.
* have no more than 5 plots (lines) on each graph. you can get away with more if it is a stacked/area graph.
* when using the provided console template examples, avoid more than 20-30 entries in the right-hand-side table.
if you find yourself exceeding these, it could make sense to demote the visibility of
less important information, possibly splitting out some subsystems to a new console.
for example, you could graph aggregated rather than broken-down data, move
it to the right-hand-side table, or even remove data completely if it is rarely
useful - you can always look at it in the [expression browser](/docs/visualization/browser/)!
finally, it is difficult for a set of consoles to serve more than one master.
what you want to know when oncall (what is broken?) tends to be very different
from what you want when developing features (how many people hit corner
case x?). in such cases, two separate sets of consoles can be useful.