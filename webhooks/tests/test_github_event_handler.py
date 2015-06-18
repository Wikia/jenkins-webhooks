import os
import unittest
import json
import mock

from webhooks.config import Config
from webhooks.github_event_handler import GithubEventHandler


class GithubEventHandlerTestClass(unittest.TestCase):
    """
    Unit tests for Config class
    """

    def setUp(self):
        """
        Setup test cases
        """
        self.config = {
            'jenkins': 'test-host',
            'repos': [
                {
                    'repo': 'Wikia/sparrow',
                    'events': ['pull_request', 'pull_request_review_comment', 'push'],
                    'mentions': ['@WikiaSparrow'],
                    'jobs': ['job5']
                },
                {
                    'repo': 'Wikia/app',
                    'events': ['push'],
                    'jobs': ['job3']
                },
            ]
        }

    def __fixture(self, example_file_name):
        return open(os.path.dirname(os.path.realpath(__file__)) + '/../examples/' + example_file_name)

    def test_pull_request(self):
        jenkins_mock = mock.MagicMock()
        handler = GithubEventHandler(Config(self.config), jenkins_mock)
        with self.__fixture('pull_request.json') as fp:
            payload = json.load(fp)

            handler.process_github_event('pull_request', payload)
            expected_params = {
                'branch': 'test-branch',
                'commit': 'f96bc53e42b40dbbd0ceb19b68a3365e7a66f223',
                'pull_num': 31
            }
            jenkins_mock.build_job.assert_called_once_with('job5', expected_params)

    def test_pull_request_review_comment(self):
        jenkins_mock = mock.MagicMock()
        handler = GithubEventHandler(Config(self.config), jenkins_mock)
        with self.__fixture('pull_request_review_comment.json') as fp:
            payload = json.load(fp)

            handler.process_github_event('pull_request_review_comment', payload)
            expected_params = {
                'branch': 'test-branch',
                'commit': 'f96bc53e42b40dbbd0ceb19b68a3365e7a66f223',
                'pull_num': 31
            }
            jenkins_mock.build_job.assert_called_once_with('job5', expected_params)

    def test_push(self):
        jenkins_mock = mock.MagicMock()
        handler = GithubEventHandler(Config(self.config), jenkins_mock)
        with self.__fixture('push.json') as fp:
            payload = json.load(fp)

            handler.process_github_event('push', payload)
            expected_params = {
                'author': 'Kyle Daigle',
                'branch': 'wikia-logger-backtrace-for-errors',
                'commit': '4d2ab4e76d0d405d17d1a0f2b8a6071394e3ab40',
                'email': 'kyle.daigle@github.com'
            }
            jenkins_mock.build_job.assert_called_once_with('job3', expected_params)
