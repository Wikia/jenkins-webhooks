jenkins-webhooks
================

Flask app for triggering Jenkins builds by GitHub webhooks

## Links

* [Internal docs](https://one.wikia-inc.com/wiki/QA/Jenkins_for_pull_requests)

## Installation

* clone the repository
* run

```
virtualenv env
source env/bin/activate
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
$ ./env/bin/webhooks-server
```

```
$ curl -v "http://127.0.0.1:8088/github-webhook/" -d @webhooks/examples/push.json -H "X-GitHub-Event: push" -H "Content-Type: application/json"
```

## Responses

`HTTP 201`: Jenkins jobs were triggered (the list can be empty if there was no match)

```json
{
  "jobs_started": [
    {
      "params": {
        "repo": "Wikia/app",
        "commit": "4d2ab4e76d0d405d17d1a0f2b8a6071394e3ab40",
        "email": "kyle.daigle@github.com",
        "branch": "wikia-logger-backtrace-for-errors",
        "author": "Kyle Daigle"
      },
      "name": "sparrow_runner"
    }
  ]
}
```

`HTTP 404`: Jenkins job specified in `config.yaml` was not found on Jenkins

```json
{
  "error": "Jenkins job was not found: foo_bar"
}
```

`HTTP 501`: internal error
