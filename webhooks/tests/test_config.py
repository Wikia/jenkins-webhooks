import unittest

from webhooks.config import Config


class ConfigTestClass(unittest.TestCase):
    """
    Unit tests for Config class
    """
    def setUp(self):
        """
        Setup test cases
        """
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
        """
        Test config.get_jenkins_host method
        """
        config = Config({
            'jenkins': self.hostname,
            'repos': []
        })

        assert config.get_jenkins_host() == self.hostname

    def test_match(self):
        """
        Data provider for config.match method test
        """
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
        """
        Test config.match method
        """
        match = config.get_match(item['repo'], item['branch'])
        expected = item['index']

        if expected is None:
            assert match is None
        else:
            assert match is self.repos[expected]
