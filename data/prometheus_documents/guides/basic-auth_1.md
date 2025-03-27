---
title: basic auth
---
securing prometheus api and ui endpoints using basic auth
prometheus supports [basic authentication](_access_authentication) (aka "basic auth") for connections to the prometheus [expression browser](/docs/visualization/browser) and [http api](/docs/prometheus/latest/querying/api).
note: this tutorial covers basic auth connections *to* prometheus instances. basic auth is also supported for connections *from* prometheus instances to [scrape targets](../../prometheus/latest/configuration/configuration/
scrape_config).
hashing a password
let's say that you want to require a username and password from all users accessing the prometheus instance. for this example, use `admin` as the username and choose any password you'd like.
first, generate a [bcrypt]() hash of the password.
to generate a hashed password, we will use python3-bcrypt.
let's install it by running `apt install python3-bcrypt`, assuming you are
running a debian-like distribution. other alternatives exist to generate hashed
passwords; for testing you can also use [bcrypt generators on the
web]().
here is a python script which uses python3-bcrypt to prompt for a password and
hash it:
```python
import getpass
import bcrypt
password = getpass.getpass("password: ")
hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
print(hashed_password.decode())
```
save that script as `gen-pass.py` and run it:
```shell
$ python3 gen-pass.py
```
that should prompt you for a password:
```
password:
$2b$12$hnf2lssxfm0.i4a.1kvpsovybcfib51vrjgbuyv6kdnytlgwj81ay
```
in this example, i used "test" as password.
save that password somewhere, we will use it in the next steps!
creating web.yml
let's create a web.yml file
([documentation]()),
with the following content:
```yaml
basic_auth_users:
    admin: $2b$12$hnf2lssxfm0.i4a.1kvpsovybcfib51vrjgbuyv6kdnytlgwj81ay
```
you can validate that file with `promtool check web-config web.yml`
```shell
$ promtool check web-config web.yml
web.yml success
```
you can add multiple users to the file.
launching prometheus
you can launch prometheus with the web configuration file as follows:
```shell
$ prometheus --web.config.file=web.yml
```
testing
you can use curl to interact with your setup. try this request:
```bash
curl --head 
```
this will return a `401 unauthorized` response because you've failed to supply a valid username and password.
to successfully access prometheus endpoints using basic auth, for example the `/metrics` endpoint, supply the proper username using the `-u` flag and supply the password when prompted:
```bash
curl -u admin 
enter host password for user 'admin':
```
that should return prometheus metrics output, which should look something like this:
```
help go_gc_duration_seconds a summary of the gc invocation durations.
type go_gc_duration_seconds summary
go_gc_duration_seconds{quantile="0"} 0.0001343
go_gc_duration_seconds{quantile="0.25"} 0.0002032
go_gc_duration_seconds{quantile="0.5"} 0.0004485
...
```
summary
in this guide, you stored a username and a hashed password in a `web.yml` file, launched prometheus with the parameter required to use the credentials in that file to authenticate users accessing prometheus' http endpoints.