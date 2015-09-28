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
                # 0
                'repo': 'foo/bar',
                'branches': ['tests', 'a-feature'],
                'events': ['pull_request', 'pull_request_review_comment', 'push'],
                'mentions': ['@TestTag1', '@TestTag2'],
                'jobs': ['job5']
            },
            {
                # 1
                'repo': 'foo/bar',
                'branches': ['tests', 'a-feature'],
                'events': ['push'],
                'jobs': ['job1', 'job2']
            },
            {
                # 2
                'repo': 'foo/bar',
                'branches_not': ['tests'],
                'jobs': ['job3', 'job4']
            },
            {
                # 3
                'repo': 'foo/tests',
                'branches_not': ['tests', 'a-feature'],
                'jobs': ['job5']
            },
            # match all pushes to foo/test2
            {
                # 4
                'repo': 'foo/test2',
                'jobs': ['job5']
            },
            {
                # 5
                'repo': 'foo/test3',
                'events': ['pull_request'],
                'mentions': ['@TestTag3'],
                'jobs': ['job6a'],
                'name': 'test3-mention'
            },
            {
                # 6
                'repo': 'foo/test3',
                'events': ['pull_request'],
                'jobs': ['job6b'],
                'ifnot': 'test3-mention'
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
                'event_type': 'push',
                'index': 1
            },
            {
                'repo': 'foo/bar',
                'branch': 'foo-feature',
                'event_type': 'push',
                'index': 2
            },
            {
                'repo': 'foo/tests',
                'branch': 'tests',
                'event_type': 'push',
                'index': None
            },
            {
                'repo': 'foo/test2',
                'branch': 'tests',
                'event_type': 'push',
                'index': 4
            },
            {
                'repo': 'foo/tests',
                'branch': 'dev',
                'event_type': 'push',
                'index': 3
            },
            {
                'repo': 'foo/bar',
                'branch': 'tests',
                'comment': "test @TestTag1",
                'event_type': 'push',
                'index': [0, 1]
            },
            {
                'repo': 'foo/bar',
                'branch': 'a-feature',
                'comment': 'test @TestTag1',
                'event_type': 'pull_request',
                'index': [0, 2]
            },
            {
                'repo': 'foo/bar',
                'branch': 'tests',
                'comment': 'test @NonExistent',
                'event_type': 'pull_request',
                'index': None
            },
            {
                'repo': 'foo/test3',
                'branch': 'master',
                'comment': 'test @NonExistent',
                'event_type': 'pull_request',
                'index': 6
            },
            {
                'repo': 'foo/test3',
                'branch': 'master',
                'comment': 'test @TestTag3',
                'event_type': 'pull_request',
                'index': 5
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
        matches = config.get_matches(item['repo'], item['branch'], item.get('event_type'), item.get('comment'))
        expected = item['index']

        if expected is None:
            assert len(matches) == 0
        else:
            if type(expected) is int:
                expected = [expected]
            expected = set(expected)
            actual = set([self.repos.index(match) for match in matches])
            assert expected == actual
