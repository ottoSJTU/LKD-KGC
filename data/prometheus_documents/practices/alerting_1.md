---
title: alerting
sort_rank: 5
---
alerting
we recommend that you read [my philosophy on alerting]()
based on rob ewaschuk's observations at google.
to summarize: keep alerting simple, alert on symptoms, have good consoles to
allow pinpointing causes, and avoid having pages where there is nothing to do.
naming
there are no strict restrictions regarding the naming of alerting rules, as alert names may contain any number of unicode characters, just like any other label value. however, [the community has rallied around]() using [camel case](_case) for their alert names.
what to alert on
aim to have as few alerts as possible, by alerting on symptoms that are
associated with end-user pain rather than trying to catch every possible way
that pain could be caused. alerts should link to relevant consoles
and make it easy to figure out which component is at fault.
allow for slack in alerting to accommodate small blips.
online serving systems
typically alert on high latency and error rates as high up in the stack as possible.
only page on latency at one point in a stack. if a lower-level component is
slower than it should be, but the overall user latency is fine, then there is
no need to page.
for error rates, page on user-visible errors. if there are errors further down
the stack that will cause such a failure, there is no need to page on them
separately. however, if some failures are not user-visible, but are otherwise
severe enough to require human involvement (for example, you are losing a lot of
money), add pages to be sent on those.
you may need alerts for different types of request if they have different
characteristics, or problems in a low-traffic type of request would be drowned
out by high-traffic requests.
offline processing
for offline processing systems, the key metric is how long data takes to get
through the system, so page if that gets high enough to cause user impact.
batch jobs
for batch jobs it makes sense to page if the batch job has not succeeded
recently enough, and this will cause user-visible problems.
this should generally be at least enough time for 2 full runs of the batch job.
for a job that runs every 4 hours and takes an hour, 10 hours would be a
reasonable threshold. if you cannot withstand a single run failing, run the
job more frequently, as a single failure should not require human intervention.
capacity
while not a problem causing immediate user impact, being close to capacity
often requires human intervention to avoid an outage in the near future.
metamonitoring
it is important to have confidence that monitoring is working. accordingly, have
alerts to ensure that prometheus servers, alertmanagers, pushgateways, and
other monitoring infrastructure are available and running correctly.
as always, if it is possible to alert on symptoms rather than causes, this helps
to reduce noise. for example, a blackbox test that alerts are getting from
pushgateway to prometheus to alertmanager to email is better than individual
alerts on each.
supplementing the whitebox monitoring of prometheus with external blackbox
monitoring can catch problems that are otherwise invisible, and also serves as
a fallback in case internal systems completely fail.