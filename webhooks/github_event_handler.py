"""
Handler processing github events and triggers Jenkins jobs
"""
import json
import logging
import jenkinsapi.jenkins as Jenkins

from pkg_resources import resource_filename
from .config import Config

# log to stderr
logger = logging.getLogger('jenkins-webhooks')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class GithubEventHandler(object):

    def __init__(self, config, jenkins):
        self.__config = config
        self.__jenkins = jenkins

        # read the config and setup Jenkins API
        if self.__config is None:
            config_file = resource_filename(__package__, 'config.yaml')
            self.__config = Config.from_yaml(config_file)

        if self.__jenkins is None:
            self.__jenkins = Jenkins.Jenkins(config.get_jenkins_host())

    @staticmethod
    def get_metadata(event_type, payload):
        # decode the payload
        # @see examples/*.json
        # @see https://developer.github.com/v3/activity/events/types/#pushevent
        if event_type == "push":
            meta = {
                'owner': payload['repository']['owner'].get('name'),
                'repo_name': payload['repository']['full_name'],
                'branch': payload['ref'].replace('refs/heads/', ''),
                'author': payload['head_commit']['author']['name'],
                'email': payload['head_commit']['author']['email'],
                'commit': payload['head_commit']['id']
            }
        if event_type == "pull_request":
            meta = {
                'owner': payload['repository']['owner'].get('name'),
                'repo_name': payload['repository']['full_name'],
                'branch': payload['pull_request']['head']['ref'],
                'commit': payload['pull_request']['head']['sha'],
                'comment': payload['pull_request']['body']
            }
        if event_type == "pull_request_review_comment":
            meta = {
                'owner': payload['repository']['owner'].get('name'),
                'repo_name': payload['repository']['full_name'],
                'branch': payload['pull_request']['head']['ref'],
                'commit': payload['pull_request']['head']['sha'],
                'comment': payload['comment']['body']
            }

        return meta

    def process_github_event(self, event_type, payload):
        meta = self.get_metadata(event_type, payload)
        logger.info("Event received: %s", json.dumps(meta))

        # try to match the push with list of rules from the config file
        match = self.__config.get_match(meta['repo_name'], meta['branch'], event_type, meta.get('comment'))

        if match is not None:
            logger.info("Event matches: %s", json.dumps(match))

            # run jobs
            job_params = {
                'branch': meta['branch'],
                'commit': meta['commit'],
            }
            if 'author' in meta:
                job_params['author'] = meta['author']
            if 'email' in meta:
                job_params['email'] = meta['email']

            if 'jobs' in match:
                for job_name in match['jobs']:
                    logger.info("Running %s with params: %s", job_name, job_params)
                    self.__jenkins.build_job(job_name, job_params)
        else:
            logger.info("No match found")

        return 'OK'
