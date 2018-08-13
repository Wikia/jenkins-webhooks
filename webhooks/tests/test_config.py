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
        self.jenkins = {
                           'url': self.hostname,
                           'user': 'dummy',
                           'pass': 'dummy_pass'
                       }
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
            # name/ifnot
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
            },
            # target_branches, target_branches_not
            {
                # 7
                'repo': 'foo/test4',
                'events': ['pull_request'],
                'target_branches_not': ['dev'],
                'jobs': ['job7a'],
            },
            {
                # 8
                'repo': 'foo/test4',
                'events': ['pull_request'],
                'target_branches': ['master'],
                'jobs': ['job7b'],
            },
            # glob patterns for branch names matching
            {
                # 9
                'repo': 'foo/test5',
                'events': ['push'],
                'branches': ['glob*'],
                'jobs': ['job9']
            },
            {
                # 10
                'repo': 'foo/test5',
                'events': ['push'],
                'branches_not': ['*xglob'],
                'jobs': ['job10']
            },
            {
                # 11
                'repo': 'foo/test5',
                'events': ['push'],
                'target_branches': ['tglob*'],
                'jobs': ['job11']
            },
            {
                # 12
                'repo': 'foo/test5',
                'events': ['push'],
                'target_branches_not': ['*yglob'],
                'jobs': ['job12']
            },
            {
                # 13
                'repo': 'foo/test6',
                'events': ['push'],
                'branches': ['exact?'],
                'target_branches': ['exact?'],
                'jobs': ['job13']
            },
            {
                # 14
                'repo': 'foo/repo-with-actions',
                'events': ['pull_request'],
                'jobs': ['any-job'],
                'actions': ['opened']
            },
            {
                # 15
                'repo': 'foo/repo-with-actions',
                'events': ['pull_request'],
                'jobs': ['any-job'],
                'actions': ['opened', 'unlabeled']
            }
        ]

    def test_jenkins_host(self):
        """
        Test config.get_jenkins_host method
        """
        config = Config({
            'jenkins': {
                'url': self.hostname,
                'user': 'dummy',
                'pass': 'dummy_pass'},
            'repos': []
        })

        assert config.get_jenkins_url() == self.hostname

    def test_match(self):
        """
        Data provider for config.match method test
        """
        cases = [
            {
                'repo': 'foo/repo-with-actions',
                'branch': 'any-branch',
                'target_branch': 'any-target-branch',
                'event_type': 'pull_request',
                'index': [14, 15],
                'action': 'opened'
            },
            {
                'repo': 'foo/repo-with-actions',
                'branch': 'any-branch',
                'target_branch': 'any-target-branch',
                'event_type': 'pull_request',
                'index': 15,
                'action': 'unlabeled'
            },
            {
                'repo': 'foo/repo-with-actions',
                'branch': 'any-branch',
                'target_branch': 'any-target-branch',
                'event_type': 'pull_request',
                'index': [],
                'action': 'any-un-matched-action'
            },
            {
                'repo': 'foo/bar',
                'branch': 'tests',
                'target_branch': 'tests',
                'event_type': 'push',
                'index': 1
            },
            {
                'repo': 'foo/bar',
                'branch': 'foo-feature',
                'target_branch': 'foo-feature',
                'event_type': 'push',
                'index': 2
            },
            {
                'repo': 'foo/tests',
                'branch': 'tests',
                'target_branch': 'tests',
                'event_type': 'push',
                'index': None
            },
            {
                'repo': 'foo/test2',
                'branch': 'tests',
                'target_branch': 'tests',
                'event_type': 'push',
                'index': 4
            },
            {
                'repo': 'foo/tests',
                'branch': 'dev',
                'target_branch': 'dev',
                'event_type': 'push',
                'index': 3
            },
            {
                'repo': 'foo/bar',
                'branch': 'tests',
                'target_branch': 'tests',
                'comment': "test @TestTag1",
                'event_type': 'push',
                'index': [0, 1]
            },
            {
                'repo': 'foo/bar',
                'branch': 'a-feature',
                'target_branch': 'dev',
                'comment': 'test @TestTag1',
                'event_type': 'pull_request',
                'index': [0, 2]
            },
            {
                'repo': 'foo/bar',
                'branch': 'tests',
                'target_branch': 'dev',
                'comment': 'test @NonExistent',
                'event_type': 'pull_request',
                'index': None
            },
            # name/ifnot
            {
                'repo': 'foo/test3',
                'branch': 'some-branch',
                'target_branch': 'master',
                'comment': 'test @NonExistent',
                'event_type': 'pull_request',
                'index': 6
            },
            {
                'repo': 'foo/test3',
                'branch': 'some-branch',
                'target_branch': 'master',
                'comment': 'test @TestTag3',
                'event_type': 'pull_request',
                'index': 5
            },
            # target_branch
            {
                'repo': 'foo/test4',
                'branch': 'a-feature',
                'target_branch': 'dev',
                'comment': 'test @TestTag3',
                'event_type': 'pull_request',
                'index': None
            },
            {
                'repo': 'foo/test4',
                'branch': 'a-feature',
                'target_branch': 'master',
                'comment': 'test @TestTag3',
                'event_type': 'pull_request',
                'index': [7, 8]
            },
            {
                'repo': 'foo/test4',
                'branch': 'a-feature',
                'target_branch': 'release-001',
                'comment': 'test @TestTag3',
                'event_type': 'pull_request',
                'index': 7
            },
            # glob patterns
            {
                'repo': 'foo/test5',
                'branch': 'glob123xglob',
                'target_branch': 'yglob',
                'event_type': 'push',
                'index': 9
            },
            {
                'repo': 'foo/test5',
                'branch': 'glob123sglob',
                'target_branch': 'yglob',
                'event_type': 'push',
                'index': [ 9, 10 ]
            },
            {
                'repo': 'foo/test5',
                'branch': 'xglob',
                'target_branch': 'tglob123yglob',
                'event_type': 'push',
                'index': 11
            },
            {
                'repo': 'foo/test5',
                'branch': 'xglob',
                'target_branch': 'tglob123sglob',
                'event_type': 'push',
                'index': [ 11, 12 ]
            },
            {
                'repo': 'foo/test6',
                'branch': 'exact1',
                'target_branch': 'exact2',
                'event_type': 'push',
                'index': 13
            },
            {
                'repo': 'foo/test6',
                'branch': 'exact11',
                'target_branch': 'exact22',
                'event_type': 'push',
                'index': None
            },
        ]

        config = Config({
            'jenkins': self.jenkins,
            'repos': self.repos
        })

        for item in cases:
            self.check_match(config, item)

    def check_match(self, config, item):
        """
        Test config.match method
        """
        matches = config.get_matches(
            item.get('event_type'),
            {
                'repo': item['repo'],
                'branch': item['branch'],
                'target_branch': item['target_branch'],
                'comment': item.get('comment'),
                'action': item.get('action')
            }
        )
        expected = item['index']
        if expected is None:
            expected = []
        if type(expected) is int:
            expected = [expected]
        expected = set(expected)

        actual = set([self.repos.index(match) for match in matches])
        assert expected == actual, '{} != {} :: {}'.format(expected,actual,item)
