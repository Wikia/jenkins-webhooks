jenkins-webhooks
================

Flask app for triggering Jenkins builds by GitHub webhooks

## Installation

* clone the repository
* run

```
virtualenv venv
source venv/bin/activate
pip install -e .
```

## Unit tests

Can be found in ``/tests`` and run via:

```
py.test
```

## How to run it

> The server listens on port 8088 by default

```
$ webhooks-server
```

```
$ curl -v "http://127.0.0.1:8088/github-webhook/" -d @webhooks/examples/push.json -H "X-GitHub-Event: push" -H "Content-Type: application/json"
```
