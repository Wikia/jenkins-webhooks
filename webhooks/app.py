"""
Flash app that listens for GitHub web hooks
and triggers Jenkins jobs
"""
import json
import logging
import sys

# set up Flask app
from flask import Flask, request
from .github_event_handler import GithubEventHandler, GithubEventException

# set up the logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
github_event_handler = GithubEventHandler()


@app.route("/", methods=['GET'])
def home_page():
    return "Hi!"


@app.route("/github-webhook/", methods=['POST'])
def index():
    """
    Process web hook request from GitHub
    """
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.get_json()

    logger.debug("Content-Type: %s", request.headers.get('Content-Type'))  # should be application/json
    logger.debug("JSON payload: %s", json.dumps(payload))

    logger.info("GitHub event type: %s", event_type)

    if event_type == "ping":
        return json.dumps({'msg': 'Hi!'})
    if event_type not in ("push", "pull_request", "pull_request_review_comment"):
        return json.dumps({'msg': "wrong event type"})

    try:
        jobs_started = github_event_handler.process_github_event(event_type, payload)
        return json.dumps({'jobs_started': jobs_started}), 201  # HTTP Created

    except GithubEventException as e:
        # PLATFORM-736
        #  catch "No match found" exception
        # and UnknownJob exception from Jenkins API
        logger.error('process_github_event() raised an exception', exc_info=e)
        return json.dumps({'error': e.message}), 404  # HTTP Not Found

    except Exception as e:
        # generic exceptions handler
        logger.error('process_github_event() raised an exception', exc_info=e)
        return 'Internal Error', 500  # HTTP Internal Server Error


def run():
    """
    Initialize Flask app
    """
    try:
        port_number = int(sys.argv[1])
    except (IndexError, ValueError):
        port_number = 8088

    logger.info("Starting a Flask app on port %d", port_number)

    # is_dev = os.environ.get('DEBUG', None) == '1'
    is_dev = True  # force debug mode
    if is_dev:
        logging.basicConfig(level=logging.DEBUG)

    app.run(host='0.0.0.0', port=port_number, debug=is_dev)


if __name__ == "__main__":
    run()
