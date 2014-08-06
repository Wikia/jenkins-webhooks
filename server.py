#!/usr/bin/env python
# Flash app that listens for GitHub web hooks
# and triggers Jenkins jobs
import jenkinsapi.jenkins as Jenkins
import json
import logging
import os
import sys

from flask import Flask, request
app = Flask(__name__)

from config import Config

# log to stderr
logger = logging.getLogger('jenkins-webhooks')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# read the config and setup Jenkins API
cwd = os.path.dirname(os.path.abspath(__file__))
config = Config.from_yaml(cwd + '/config.yaml')
jenkins = Jenkins.Jenkins(config.get_jenkins_host())


@app.route("/github-webhook/", methods=['POST'])
def index():
    """
    Process web hook request from GitHub
    """
    if request.headers.get('X-GitHub-Event') == "ping":
        return json.dumps({'msg': 'Hi!'})
    if request.headers.get('X-GitHub-Event') != "push":
        return json.dumps({'msg': "wrong event type"})

    # decode the payload
    # @see examples/push.json
    # @see https://developer.github.com/v3/activity/events/types/#pushevent
    payload = json.loads(request.data)
    meta = {
        'owner': payload['repository']['owner']['name'],
        'name': payload['repository']['name'],
        'branch': payload['ref'].replace('refs/heads/', ''),
        'author': payload['head_commit']['author']['name'],
        'commit': payload['head_commit']['id']
    }

    logger.info("Push received: %s" % json.dumps(meta))

    # try to match the push with list of rules from the config file
    repo = '%s/%s' % (meta['owner'], meta['name'])
    match = config.get_match(repo, meta['branch'])

    if match is not None:
        logger.info("Push matches: %s" % json.dumps(match))

        # run jobs
        job_params = {
            'branch': meta['branch'],
            'commit': meta['commit'],
            'author': meta['author']
        }

        if 'jobs' in match:
            for job_name in match['jobs']:
                logger.info("Running %s with params: %s" % (job_name, job_params))
                jenkins.build_job(job_name, job_params)
    else:
        logger.info("No match found")

    return 'OK'

if __name__ == "__main__":
    try:
        port_number = int(sys.argv[1])
    except:
        port_number = 8088

    logger.info("Starting a Flask app on port %d" % port_number)

    is_dev = os.environ.get('DEBUG', None) == '1'
    app.run(host='0.0.0.0', port=port_number, debug=is_dev)
