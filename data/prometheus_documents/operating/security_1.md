---
title: security
sort_rank: 4
---
security model
prometheus is a sophisticated system with many components and many integrations
with other systems. it can be deployed in a variety of trusted and untrusted
environments.
this page describes the general security assumptions of prometheus and the
attack vectors that some configurations may enable.
as with any complex system, it is near certain that bugs will be found, some of
them security-relevant. if you find a _security bug_ please report it
privately to the maintainers listed in the maintainers of the relevant
repository and cc  we will fix the issue as soon
as possible and coordinate a release date with you. you will be able to choose
if you want public acknowledgement of your effort and if you want to be
mentioned by name.
automated security scanners
special note for security scanner users: please be mindful with the reports produced.
most scanners are generic and produce lots of false positives. more and more
reports are being sent to us, and it takes a significant amount of work to go
through all of them and reply with the care you expect. this problem is particularly
bad with go and npm dependency scanners.
as a courtesy to us and our time, we would ask you not to submit raw reports.
instead, please submit them with an analysis outlining which specific results
are applicable to us and why.
prometheus is maintained by volunteers, not by a company. therefore, fixing
security issues is done on a best-effort basis. we strive to release security
fixes within 7 days for: prometheus, alertmanager, node exporter,
blackbox exporter, and pushgateway.
prometheus
it is presumed that untrusted users have access to the prometheus http endpoint
and logs. they have access to all time series information contained in the
database, plus a variety of operational/debugging information.
it is also presumed that only trusted users have the ability to change the
command line, configuration file, rule files and other aspects of the runtime
environment of prometheus and other components.
which targets prometheus scrapes, how often and with what other settings is
determined entirely via the configuration file. the administrator may
decide to use information from service discovery systems, which combined with
relabelling may grant some of this control to anyone who can modify data in
that service discovery system.
scraped targets may be run by untrusted users. it should not by default be
possible for a target to expose data that impersonates a different target.  the
`honor_labels` option removes this protection, as can certain relabelling
setups.
as of prometheus 2.0, the `--web.enable-admin-api` flag controls access to the
administrative http api which includes functionality such as deleting time
series. this is disabled by default. if enabled, administrative and mutating
functionality will be accessible under the `/api/*/admin/` paths. the
`--web.enable-lifecycle` flag controls http reloads and shutdowns of
prometheus. this is also disabled by default. if enabled they will be
accessible under the `/-/reload` and `/-/quit` paths.
in prometheus 1.x, `/-/reload` and using `delete` on `/api/v1/series` are
accessible to anyone with access to the http api. the `/-/quit` endpoint is
disabled by default, but can be enabled with the `-web.enable-remote-shutdown`
flag.
the remote read feature allows anyone with http access to send queries to the
remote read endpoint. if for example the promql queries were ending up directly
run against a relational database, then anyone with the ability to send queries
to prometheus (such as via grafana) can run arbitrary sql against that
database.
alertmanager
any user with access to the alertmanager http endpoint has access to its data.
they can create and resolve alerts. they can create, modify and delete
silences.
where notifications are sent to is determined by the configuration file. with
certain templating setups it is possible for notifications to end up at an
alert-defined destination. for example if notifications use an alert label as
the destination email address, anyone who can send alerts to the alertmanager
can send notifications to any email address. if the alert-defined destination
is a templatable secret field, anyone with access to either prometheus or
alertmanager will be able to view the secrets.
any secret fields which are templatable are intended for routing notifications
in the above use case. they are not intended as a way for secrets to be
separated out from the configuration files using the template file feature. any
secrets stored in template files could be exfiltrated by anyone able to
configure receivers in the alertmanager configuration file. for example in
large setups, each team might have an alertmanager configuration file fragment
which they fully control, that are then combined into the full final
configuration file.
pushgateway
any user with access to the pushgateway http endpoint can create, modify and
delete the metrics contained within. as the pushgateway is usually scraped with
`honor_labels` enabled, this means anyone with access to the pushgateway can
create any time series in prometheus.
the `--web.enable-admin-api` flag controls access to the
administrative http api, which includes functionality such as wiping all the existing
metric groups. this is disabled by default. if enabled, administrative
functionality will be accessible under the `/api/*/admin/` paths.
exporters
exporters generally only talk to one configured instance with a preset set of
commands/requests, which cannot be expanded via their http endpoint.
there are also exporters such as the snmp and blackbox exporters that take
their targets from url parameters. thus anyone with http access to these
exporters can make them send requests to arbitrary endpoints. as they also
support client-side authentication, this could lead to a leak of secrets such
as http basic auth passwords or snmp community strings. challenge-response
authentication mechanisms such as tls are not affected by this.
client libraries
client libraries are intended to be included in users' applications.
if using a client-library-provided http handler, it should not be possible for
malicious requests that reach that handler to cause issues beyond those
resulting from additional load and failed scrapes.
authentication, authorization, and encryption
prometheus, and most exporters, support tls. including authentication of clients
via tls client certificates. details on configuring prometheus are [`here`]().
the go projects share the same tls library, based on the
go [crypto/tls]() library.
we default to tls 1.2 as minimum version. our policy regarding this is based on
[qualys ssl labs]() recommendations, where we strive to
achieve a grade 'a' with a default configuration and correctly provided
certificates, while sticking as closely as possible to the upstream go defaults.
achieving that grade provides a balance between perfect security and usability.
tls will be added to java exporters in the future.
if you have special tls needs, like a different cipher suite or older tls
version, you can tune the minimum tls version and the ciphers, as long as the
cipher is not [marked as insecure](
insecureciphersuites)
in the [crypto/tls]() library. if that still
does not suit you, the current tls settings enable you to build a secure tunnel
between the servers and reverse proxies with more special requirements.
http basic authentication is also supported. basic authentication can be
used without tls, but it will then expose usernames and passwords in cleartext
over the network.
on the server side, basic authentication passwords are stored as hashes with the
[bcrypt]() algorithm. it is your
responsibility to pick the number of rounds that matches your security
standards. more rounds make brute-force more complicated at the cost of more cpu
power and more time to authenticate the requests.
various prometheus components support client-side authentication and
encryption. if tls client support is offered, there is often also an option
called `insecure_skip_verify` which skips ssl verification.
api security
as administrative and mutating endpoints are intended to be accessed via simple
tools such as curl, there is no built in
[csrf](_request_forgery) protection as
that would break such use cases. accordingly when using a reverse proxy, you
may wish to block such paths to prevent csrf.
for non-mutating endpoints, you may wish to set [cors
headers](
http-cors-protocol) such as
`access-control-allow-origin` in your reverse proxy to prevent
[xss](_scripting).
if you are composing promql queries that include input from untrusted users
(e.g. url parameters to console templates, or something you built yourself) who
are not meant to be able to run arbitrary promql queries make sure any
untrusted input is appropriately escaped to prevent injection attacks. for
example `up{job="<user_input>"}` would become `up{job=""} or
some_metric{zzz=""}` if the `<user_input>` was `"} or some_metric{zzz="`.
for those using grafana note that [dashboard permissions are not data source
permissions](
data-source-permissions),
so do not limit a user's ability to run arbitrary queries in proxy mode.
secrets
non-secret information or fields may be available via the http api and/or logs.
in prometheus, metadata retrieved from service discovery is not considered
secret. throughout the prometheus system, metrics are not considered secret.
fields containing secrets in configuration files (marked explicitly as such in
the documentation) will not be exposed in logs or via the http api. secrets
should not be placed in other configuration fields, as it is common for
components to expose their configuration over their http endpoint. it is the
responsibility of the user to protect files on disk from unwanted reads and
writes.
secrets from other sources used by dependencies (e.g. the `aws_secret_key`
environment variable as used by ec2 service discovery) may end up exposed due to
code outside of our control or due to functionality that happens to expose
wherever it is stored.
denial of service
there are some mitigations in place for excess load or expensive queries.
however, if too many or too expensive queries/metrics are provided components
will fall over. it is more likely that a component will be accidentally taken
out by a trusted user than by malicious action.
it is the responsibility of the user to ensure they provide components with
sufficient resources including cpu, ram, disk space, iops, file descriptors,
and bandwidth.
it is recommended to monitor all components for failure, and to have them
automatically restart on failure.
libraries
this document considers vanilla binaries built from the stock source code.
information presented here does not apply if you modify prometheus source code,
or use prometheus internals (beyond the official client library apis) in your
own code.