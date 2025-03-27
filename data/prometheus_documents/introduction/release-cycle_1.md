---
title: long-term support
sort_rank: 10
---
long term support
prometheus lts are selected releases of prometheus that receive bugfixes for an
extended period of time.
every 6 weeks, a new prometheus minor release cycle begins. after those 6
weeks, minor releases generally no longer receive bugfixes. if a user is
impacted by a bug in a minor release, they often need to upgrade to the
latest prometheus release.
upgrading prometheus should be straightforward thanks to our [api stability
guarantees][stab]. however,
there is a risk that new features and enhancements could also bring regressions,
requiring another upgrade.
prometheus lts only receive bug, security, and documentation fixes, but over a
time window of one year. the build toolchain will also be kept up-to-date. this
allows companies that rely on prometheus to limit the upgrade risks while still
having a prometheus server maintained by the community.
list of lts releases
<table class="table table-bordered downloads">
    <thead>
        <tr>
            <th>release</th>
            <th>date</th>
            <th>end of support</th>
        </tr>
    </thead>
    <tbody>
        <tr class="danger">
            <td>prometheus 2.37</td><td>2022-07-14</td><td>2023-07-31</td>
        </tr>
        <tr class="danger">
            <td>prometheus 2.45</td><td>2023-06-23</td><td>2024-07-31</td>
        </tr>
        <tr class="success">
            <td>prometheus 2.53</td><td>2024-06-16</td><td>2025-07-31</td>
        </tr>
    </tbody>
</table>
limitations of lts support
some features are excluded from lts support:
- things listed as unstable in our [api stability guarantees][stab].
- [experimental features][fflag].
- openbsd support.
[stab]:
[fflag]:_flags/