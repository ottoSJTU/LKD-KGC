points-attributes), represented as a json object containing a `name`, `tags` (key/value pairs), `timestamp`, and `value` (always a float).
storage
sensu stores current and recent event status information and real-time inventory data in an embedded database (etcd) or an external rdbms (postgresql).
architecture
all components of a sensu deployment can be clustered for high availability and improved event-processing throughput.
summary
sensu and prometheus have a few capabilities in common, but they take very different approaches to monitoring. both offer extensible discovery mechanisms for dynamic cloud-based environments and ephemeral compute platforms, though the underlying mechanisms are quite different. both provide support for collecting multi-dimensional metrics via labels and annotations. both have extensive integrations, and sensu natively supports collecting metrics from all prometheus exporters. both are capable of forwarding observability data to third-party data platforms (e.g. event stores or tsdbs). where sensu and prometheus differ the most is in their use cases.
where sensu is better: 
- if you're collecting and processing hybrid observability data (including metrics _and/or_ events)
- if you're consolidating multiple monitoring tools and need support for metrics _and_ nagios-style plugins or check scripts
- more powerful event-processing platform
where prometheus is better: 
- if you're primarily collecting and evaluating metrics
- if you're monitoring homogeneous kubernetes infrastructure (if 100% of the workloads you're monitoring are in k8s, prometheus offers better k8s integration)
- more powerful query language, and built-in support for historical data analysis 
sensu is maintained by a single commercial company following the open-core business model, offering premium features like closed-source event correlation and aggregation, federation, and support. prometheus is a fully open source and independent project, maintained by a number of companies and individuals, some of whom also offer commercial services and support.