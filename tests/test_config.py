import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class ConfigTestClass(unittest.TestCase):
    def setUp(self):
        self.hostname = 'http://example.com'
        self.repos = [
            {
                'repo': 'foo/bar',
                'branches': ['tests', 'a-feature'],
                'tests': ['job1', 'job2']
            },
            {
                'repo': 'foo/bar',
                'branches_not': ['tests'],
                'tests': ['job3', 'job4']
            },
            {
                'repo': 'foo/tests',
                'branches_not': ['tests', 'a-feature'],
                'tests': ['job5']
            },
            # match all pushes to foo/test2
            {
                'repo': 'foo/test2',
                'tests': ['job5']
            }
        ]

    def test_jenkins_host(self):
        config = Config({
            'jenkins': self.hostname,
            'repos': []
        })

        assert(config.get_jenkins_host() == self.hostname)

    def test_match(self):
        cases = [
            {
                'repo': 'foo/bar',
                'branch': 'tests',
                'index': 0
            },
            {
                'repo': 'foo/bar',
                'branch': 'foo-feature',
                'index': 1
            },
            {
                'repo': 'foo/tests',
                'branch': 'tests',
                'index': None
            },
            {
                'repo': 'foo/test2',
                'branch': 'tests',
                'index': 3
            },
            {
                'repo': 'foo/tests',
                'branch': 'dev',
                'index': 2
            }
        ]

        config = Config({
            'jenkins': None,
            'repos': self.repos
        })

        for item in cases:
            self.check_match(config, item)

    def check_match(self, config, item):
        match = config.get_match(item['repo'], item['branch'])
        expected = item['index']

        #import json;  print json.dumps(item); print json.dumps(match); print ''

        if expected is None:
            assert(match is None)
        else:
            assert(match is self.repos[expected])