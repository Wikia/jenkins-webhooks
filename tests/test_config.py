import unittest
from config import Config


class ConfigTestClass(unittest.TestCase):
    def setUp(self):
        self.hostname = 'http://example.com'
        self.repos = [
            {
                'repo': 'foo/bar',
                'branches': ['test', 'a-feature'],
                'test': ['job1', 'job2']
            },
            {
                'repo': 'foo/bar',
                'branches_not': ['test'],
                'test': ['job3', 'job4']
            },
            {
                'repo': 'foo/test',
                'branches_not': ['test', 'a-feature'],
                'test': ['job5']
            },
            # match all pushes to foo/test2
            {
                'repo': 'foo/test2',
                'test': ['job5']
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
                'branch': 'test',
                'index': 0
            },
            {
                'repo': 'foo/bar',
                'branch': 'foo-feature',
                'index': 1
            },
            {
                'repo': 'foo/test',
                'branch': 'test',
                'index': None
            },
            {
                'repo': 'foo/test2',
                'branch': 'test',
                'index': 3
            },
            {
                'repo': 'foo/test',
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

        import json;  print json.dumps(item); print json.dumps(match); print ''

        if expected is None:
            assert(match is None)
        else:
            assert(match is self.repos[expected])