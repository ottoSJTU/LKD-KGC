deployment
each exporter should monitor exactly one instance application,
preferably sitting right beside it on the same machine. that means for
every haproxy you run, you run a `haproxy_exporter` process. for every
machine with a mesos worker, you run the [mesos
exporter](_exporter) on it, and
another one for the master, if a machine has both.
the theory behind this is that for direct instrumentation this is what
you’d be doing, and we’re trying to get as close to that as we can in
other layouts.  this means that all service discovery is done in
prometheus, not in exporters.  this also has the benefit that prometheus
has the target information it needs to allow users probe your service
with the [blackbox
exporter](_exporter).
there are two exceptions:
the first is where running beside the application you are monitoring is
completely nonsensical. the snmp, blackbox and ipmi exporters are the
main examples of this. the ipmi and snmp exporters as the devices are
often black boxes that it’s impossible to run code on (though if you
could run a node exporter on them instead that’d be better), and the
blackbox exporter where you’re monitoring something like a dns name,
where there’s also nothing to run on. in this case, prometheus should
still do service discovery, and pass on the target to be scraped. see
the blackbox and snmp exporters for examples.
note that it is only currently possible to write this type of exporter
with the go, python and java client libraries.
the second exception is where you’re pulling some stats out of a random
instance of a system and don’t care which one you’re talking to.
consider a set of mysql replicas you wanted to run some business queries
against the data to then export. having an exporter that uses your usual
load balancing approach to talk to one replica is the sanest approach.
this doesn’t apply when you’re monitoring a system with master-election,
in that case you should monitor each instance individually and deal with
the "masterness" in prometheus. this is as there isn’t always exactly
one master, and changing what a target is underneath prometheus’s feet
will cause oddities.
scheduling
metrics should only be pulled from the application when prometheus
scrapes them, exporters should not perform scrapes based on their own
timers. that is, all scrapes should be synchronous.
accordingly, you should not set timestamps on the metrics you expose, let
prometheus take care of that. if you think you need timestamps, then you
probably need the
[pushgateway]()
instead.
if a metric is particularly expensive to retrieve, i.e. takes more than
a minute, it is acceptable to cache it. this should be noted in the
`help` string.
the default scrape timeout for prometheus is 10 seconds. if your
exporter can be expected to exceed this, you should explicitly call this
out in your user documentation.
pushes
some applications and monitoring systems only push metrics, for example
statsd, graphite and collectd.
there are two considerations here.
firstly, when do you expire metrics? collectd and things talking to
graphite both export regularly, and when they stop we want to stop
exposing the metrics.  collectd includes an expiry time so we use that,
graphite doesn’t so it is a flag on the exporter.
statsd is a bit different, as it is dealing with events rather than
metrics. the best model is to run one exporter beside each application
and restart them when the application restarts so that the state is
cleared.
secondly, these sort of systems tend to allow your users to send either
deltas or raw counters. you should rely on the raw counters as far as
possible, as that’s the general prometheus model.
for service-level metrics, e.g. service-level batch jobs, you should
have your exporter push into the pushgateway and exit after the event
rather than handling the state yourself. for instance-level batch
metrics, there is no clear pattern yet. the options are either to abuse
the node exporter’s textfile collector, rely on in-memory state
(probably best if you don’t need to persist over a reboot) or implement
similar functionality to the textfile collector.
failed scrapes
there are currently two patterns for failed scrapes where the
application you’re talking to doesn’t respond or has other problems.
the first is to return a 5xx error.
the second is to have a `myexporter_up`, e.g. `haproxy_up`, variable
that has a value of 0 or 1 depending on whether the scrape worked.
the latter is better where there’s still some useful metrics you can get
even with a failed scrape, such as the haproxy exporter providing
process stats. the former is a tad easier for users to deal with, as
[`up` works in the usual way](/docs/concepts/jobs_instances/
automatically-generated-labels-and-time-series), although you can’t distinguish between the
exporter being down and the application being down.
landing page
it’s nicer for users if visiting `` has a simple
html page with the name of the exporter, and a link to the `/metrics`
page.
port numbers
a user may have many exporters and prometheus components on the same
machine, so to make that easier each has a unique port number.
[]()
is where we track them, this is publicly editable.
feel free to grab the next free port number when developing your
exporter, preferably before publicly announcing it. if you’re not ready
to release yet, putting your username and wip is fine.
this is a registry to make our users’ lives a little easier, not a
commitment to develop particular exporters. for exporters for internal
applications we recommend using ports outside of the range of default
port allocations.
announcing
once you’re ready to announce your exporter to the world, email the
mailing list and send a pr to add it to [the list of available
exporters]().