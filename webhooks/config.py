"""
YAML config handler
"""
import logging
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

    def get_jenkins_host(self):
        """
        Returns Jenkins API entry point
        """
        return self.jenkins_host

    def get_match(self, repo, branch):
        """
        Returns a match for given repo / branch pair
        from repos collection
        """
        match = None

        for item in self.repos:
            # match by repo name - FooInc/bar
            if repo != item['repo']:
                continue

            # match by branches
            if 'branches' in item:
                if branch in item['branches']:
                    match = item
                    break

            # does not match
            elif 'branches_not' in item:
                if branch not in item['branches_not']:
                    match = item
                    break
            else:
                match = item
                break

        return match

    @staticmethod
    def from_yaml(file_name):
        """
        Creates an instance of Config class from given YAML file
        """
        logger = logging.getLogger('jenkins-webhooks-config')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

        logger.info("Reading config from %s", file_name)

        with open(file_name, 'r') as stream:
            return Config(yaml.load(stream))
