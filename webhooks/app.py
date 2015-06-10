"""
Flash app that listens for GitHub web hooks
and triggers Jenkins jobs
"""
import json
import logging
import sys

from flask import Flask, request

from .github_event_handler import GithubEventHandler

app = Flask(__name__)

github_event_handler = GithubEventHandler()

# log to stderr
logger = logging.getLogger('jenkins-webhooks')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

@app.route("/github-webhook/", methods=['POST'])
def index():
    """
    Process web hook request from GitHub
    """
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.get_json()

    # logger.info("Content-Type: %s", request.headers.get('Content-Type'))  # should be application/json
    logger.info("GitHub event type: %s", event_type)
    # logger.info("JSON payload: %s", json.dumps(payload))

    if event_type == "ping":
        return json.dumps({'msg': 'Hi!'})
    if event_type not in ("push", "pull_request", "pull_request_review_comment"):
        return json.dumps({'msg': "wrong event type"})

    return github_event_handler.process_github_event(event_type, payload)


def run():
    """
    Initialize Flask app
    """
    try:
        port_number = int(sys.argv[1])
    except:
        port_number = 8088

    logger.info("Starting a Flask app on port %d", port_number)

    # is_dev = os.environ.get('DEBUG', None) == '1'
    is_dev = True  # force debug mode
    if is_dev:
        logging.basicConfig(level=logging.DEBUG)

    app.run(host='0.0.0.0', port=port_number, debug=is_dev)

if __name__ == "__main__":
    run()
