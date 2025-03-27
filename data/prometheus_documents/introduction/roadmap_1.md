---
title: roadmap
sort_rank: 6
---
roadmap
the following is only a selection of some of the major features we plan to
implement in the near future. to get a more complete overview of planned
features and current work, see the issue trackers for the various repositories,
for example, the [prometheus
server]().
server-side metric metadata support
at this time, metric types and other metadata are only used in the
client libraries and in the exposition format, but not persisted or
utilized in the prometheus server. we plan on making use of this
metadata in the future. the first step is to aggregate this data in-memory
in prometheus and provide it via an experimental api endpoint.
adopt openmetrics
the openmetrics working group is developing a new standard for metric exposition.
we plan to support this format in our client libraries and prometheus itself.
retroactive rule evaluations		
add support for retroactive rule evaluations making use of backfill.
tls and authentication in http serving endpoints
tls and authentication are currently being rolled out to the prometheus,
alertmanager, and the official exporters. adding this support will make it
easier for people to deploy prometheus components securely without requiring a
reverse proxy to add those features externally.
support the ecosystem
prometheus has a range of client libraries and exporters. there are always more
languages that could be supported, or systems that would be useful to export
metrics from. we will support the ecosystem in creating and expanding these.