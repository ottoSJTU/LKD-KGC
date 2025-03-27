---
title: client libraries
sort_rank: 1
---
client libraries
before you can monitor your services, you need to add instrumentation to their
code via one of the prometheus client libraries. these implement the prometheus
[metric types](/docs/concepts/metric_types/).
choose a prometheus client library that matches the language in which your
application is written. this lets you define and expose internal metrics via an
http endpoint on your application’s instance:
* [go](_golang)
* [java or scala](_java)
* [python](_python)
* [ruby](_ruby)
* [rust](_rust)
unofficial third-party client libraries:
* [bash](_bash)
* [c]()
* [c++]()
* [common lisp]()
* [dart](_client)
* [delphi]()
* [elixir]()
* [erlang]()
* [haskell]()
* [julia]()
* [lua]() for nginx
* [lua]() for tarantool
* [.net / c
]()
* [node.js]()
* [ocaml]()
* [perl]()
* [php](_client_php)
* [r]()
when prometheus scrapes your instance's http endpoint, the client library
sends the current state of all tracked metrics to the server.
if no client library is available for your language, or you want to avoid
dependencies, you may also implement one of the supported [exposition
formats](/docs/instrumenting/exposition_formats/) yourself to expose metrics.
when implementing a new prometheus client library, please follow the
[guidelines on writing client libraries](/docs/instrumenting/writing_clientlibs).
note that this document is still a work in progress. please also consider
consulting the [development mailing list](
!forum/prometheus-developers).
we are happy to give advice on how to make your library as useful and
consistent as possible.