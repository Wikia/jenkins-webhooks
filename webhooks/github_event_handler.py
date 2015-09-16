"""
Handler processing github events and triggers Jenkins jobs
"""
import json
import logging

from jenkinsapi.jenkins import Jenkins
from jenkinsapi.custom_exceptions import UnknownJob

from pkg_resources import resource_filename
from .config import Config


class GithubEventException(Exception):
    pass


class GithubEventHandler(object):

    def __init__(self, config=None, jenkins=None):
        self.__config = config
        self.__jenkins = jenkins

        self._logger = logging.getLogger(__name__)

        # read the config and setup Jenkins API
        if self.__config is None:
            config_file = resource_filename(__package__, 'config.yaml')
            self.__config = Config.from_yaml(config_file)

        if self.__jenkins is None:
            self.__jenkins = Jenkins(self.__config.get_jenkins_host())

    @staticmethod
    def get_metadata(event_type, payload):
        # decode the payload
        # @see examples/*.json
        # @see https://developer.github.com/v3/activity/events/types/#pushevent
        meta = {}
        if event_type == "push":
            meta = {
                'owner': payload['repository']['owner'].get('name'),
                'repo': payload['repository']['full_name'],
                'branch': payload['ref'].replace('refs/heads/', ''),
                'author': payload['head_commit']['author']['name'],
                'email': payload['head_commit']['author']['email'],
                'commit': payload['head_commit']['id']
            }
        if event_type == "pull_request":
            meta = {
                'owner': payload['repository']['owner'].get('name'),
                'repo': payload['repository']['full_name'],
                'branch': payload['pull_request']['head']['ref'],
                'commit': payload['pull_request']['head']['sha'],
                'comment': payload['pull_request']['body'],
                'pull_num': payload['pull_request']['number'],
            }
        if event_type == "pull_request_review_comment":
            meta = {
                'owner': payload['repository']['owner'].get('name'),
                'repo': payload['repository']['full_name'],
                'branch': payload['pull_request']['head']['ref'],
                'commit': payload['pull_request']['head']['sha'],
                'comment': payload['comment']['body'],
                'pull_num': payload['pull_request']['number'],
            }

        return meta

    def process_github_event(self, event_type, payload):
        meta = self.get_metadata(event_type, payload)
        job_param_keys = 'repo branch commit author email pull_num'.split(' ')

        self._logger.info("Event received: %s", json.dumps(meta))

        # try to match the push with list of rules from the config file
        matches = self.__config.get_matches(meta['repo'], meta['branch'], event_type, meta.get('comment'))

        job_params = dict([
            (k, v)
            for k, v in meta.items()
            if k in job_param_keys
        ])

        jobs_started = []

        for match in matches:
            self._logger.info("Event matches: %s", json.dumps(match))

            if 'jobs' in match:
                try:
                    for job_name in match['jobs']:
                        self._logger.info("Running %s with params: %s", job_name, job_params)
                        self.__jenkins.build_job(job_name, job_params)

                        jobs_started.append({'name': job_name, 'params': job_params})
                except UnknownJob as e:
                    raise GithubEventException("Jenkins job was not found: {}".format(e.message))
            else:
                raise GithubEventException("No match found")

        return jobs_started
