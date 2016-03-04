"""
Handler processing github events and triggers Jenkins jobs
"""
import json
import logging

from jenkinsapi.jenkins import Jenkins
from jenkinsapi.custom_exceptions import JenkinsAPIException, NotFound

from pkg_resources import resource_filename
from .config import Config
from .requestor import PersistentRequester


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
            requester = PersistentRequester(
                self.__config.get_jenkins_user(),
                self.__config.get_jenkins_pass(),
                baseurl=self.__config.get_jenkins_url(),
            )

            self.__jenkins = Jenkins(
                baseurl=self.__config.get_jenkins_url(),
                username=self.__config.get_jenkins_user(),
                password=self.__config.get_jenkins_pass(),
                requester=requester
            )

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
                'target_branch': '',
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
                'target_branch': payload['pull_request']['base']['ref'],
                'comment': payload['pull_request']['body'],
                'pull_num': payload['pull_request']['number'],
            }
        if event_type == "pull_request_review_comment":
            meta = {
                'owner': payload['repository']['owner'].get('name'),
                'repo': payload['repository']['full_name'],
                'branch': payload['pull_request']['head']['ref'],
                'commit': payload['pull_request']['head']['sha'],
                'target_branch': payload['pull_request']['base']['ref'],
                'comment': payload['comment']['body'],
                'pull_num': payload['pull_request']['number'],
            }

        return meta

    def process_github_event(self, event_type, payload):
        # delete branch events are missing crucial information, skip throwing an error in such cases
        if payload.get('deleted') is True:
            return 0

        meta = self.get_metadata(event_type, payload)
        job_param_keys = 'repo branch commit author email pull_num'.split(' ')

        self._logger.info("Event received: %s", json.dumps(meta))

        # try to match the push with list of rules from the config file
        matches = self.__config.get_matches(meta['repo'], meta['branch'], meta['target_branch'], event_type, meta.get('comment'))

        job_default_params = dict([
            (k, v)
            for k, v in meta.items()
            if k in job_param_keys
        ])

        jobs_started = []

        for match in matches:
            self._logger.info("Event matches: %s", json.dumps(match))

            job_params = job_default_params.copy()
            if 'job_params' in match:
                job_params.update(match['job_params'])

            if 'jobs' in match:
                try:
                    for job_name in match['jobs']:
                        self._logger.info("Running %s with params: %s", job_name, job_params)
                        self.__jenkins[job_name].invoke(
                            build_params=job_params,
                            invoke_pre_check_delay=0
                        )
                        self._logger.info("Run of %s job scheduled", job_name)

                        jobs_started.append({'name': job_name, 'params': job_params})
                except NotFound as e:
                    self._logger.info("Jenkins job was not found", exc_info=True)
                    raise GithubEventException("Jenkins job was not found: {}".format(e.message))
                except JenkinsAPIException as e:
                    self._logger.info("Jenkins refused to queue a job: {}".format(e.message), exc_info=True)
                    pass
            else:
                raise GithubEventException("No match found")

        return jobs_started
