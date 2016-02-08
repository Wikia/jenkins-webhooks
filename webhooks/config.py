"""
YAML config handler
"""
import logging
import re
import yaml


class Config(object):
    """
    A wrapper around YAML config file and rules matcher
    """
    def __init__(self, config):
        assert 'jenkins' in config
        assert 'repos' in config

        # Jenkins API entry point
        self.jenkins_host = config['jenkins']

        # repos definitions
        self.repos = config['repos']

        # jenkins credentials for authentication
        self.jenkins_user = config['user']
        self.jenkins_pass = config['pass']

    def get_jenkins_host(self):
        """
        Returns Jenkins API entry point
        """
        return self.jenkins_host

    def get_jenkins_user(self):
        """
        Returns Jenkins API entry point
        """
        return self.jenkins_user

    def get_jenkins_pass(self):
        """
        Returns Jenkins API entry point
        """
        return self.jenkins_pass

    def glob_list(self, l):
        """
        Returns a compiled regex from a list of glob-like patterns (supports * and ?)
        """
        def glob_item_re(item):
            if '*' not in item and '?' not in item:
                return re.escape(item)
            return ''.join([
                '.*' if c == '*' else
                '.' if c == '?' else
                re.escape(c)
                for c in item
            ])
        pat = ''.join([
            '^(',
            '|'.join([glob_item_re(item) for item in l]),
            ')$',
        ])
        return re.compile(pat)

    def get_matches(self, repo, branch, target_branch, event_type, comment):
        """
        Return list of matches for given: repo, branch, event_type, comment
        """
        matches = []
        scheduled = set()

        for item in self.repos:
            # match by repo name - FooInc/bar
            if repo != item['repo']:
                continue

            #if events specified check if supported
            if 'events' in item and event_type not in item['events']:
                continue

            #if mentions specified, check if exists in the comments
            if 'mentions' in item:
                found = False
                if comment is not None:
                    for mentions in item['mentions']:
                        if mentions in comment:
                            found = True
                            break
                if not found:
                    continue

            # match for branch
            if 'branches' in item:
                if not self.glob_list(item['branches']).match(branch):
                    continue
            # inverse match for branch
            elif 'branches_not' in item:
                if self.glob_list(item['branches_not']).match(branch):
                    continue

            # match for target_branch
            if 'target_branches' in item:
                if not self.glob_list(item['target_branches']).match(target_branch):
                    continue
            # inverse match for target_branch
            elif 'target_branches_not' in item:
                if self.glob_list(item['target_branches_not']).match(target_branch):
                    continue

            if 'ifnot' in item and item['ifnot'] in scheduled:
                continue

            if 'name' in item:
                scheduled.add(item['name'])

            matches.append(item)

        return matches

    @staticmethod
    def from_yaml(file_name):
        """
        Creates an instance of Config class from given YAML file
        """
        logger = logging.getLogger(__name__)
        logger.info("Reading config from %s", file_name)

        with open(file_name, 'r') as stream:
            return Config(yaml.load(stream))
