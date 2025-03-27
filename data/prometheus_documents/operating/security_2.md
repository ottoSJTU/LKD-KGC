build process
the build pipeline for prometheus runs on third-party providers to which many
members of the prometheus development team and the staff of those providers
have access. if you are concerned about the exact provenance of your binaries,
it is recommended to build them yourself rather than relying on the
pre-built binaries provided by the project.
prometheus-community
the repositories under the [prometheus-community]()
organization are supported by third-party maintainers.
if you find a _security bug_ in the [prometheus-community]() organization,
please report it privately to the maintainers listed in the maintainers of the
relevant repository and cc 
some repositories under that organization might have a different security model
than the ones presented in this document. in such a case, please refer to the
documentation of those repositories.
external audits
* in 2018, [cncf]() sponsored an external security audit by
[cure53]() which ran from april 2018 to june 2018. for more
details, please read the [final report of the audit](/assets/downloads/2018-06-11--cure53_security_audit.pdf).
* in 2020, cncf sponsored a
[second audit by cure53](/assets/downloads/2020-07-21--cure53_security_audit_node_exporter.pdf)
of node exporter.
* in 2023, cncf sponsored a
[software supply chain security assessment of prometheus](/assets/downloads/2023-04-19--chainguard_supply_chain_assessment.pdf)
by chainguard.