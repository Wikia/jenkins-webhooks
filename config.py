import logging
import yaml

logger = logging.getLogger('jenkins-webhooks-config')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class Config(object):
    def __init__(self, dict):
        assert('jenkins' in dict)
        assert('repos' in dict)

        # Jenkins API entry point
        self.jenkins_host = dict['jenkins']

        # repos defintions
        self.repos = dict['repos']

    def get_jenkins_host(self):
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
    def from_yaml(file):
        """
        Creates an instance of Config class from given YAML file
        """
        logger.info("Reading config from %s" % file)

        with open(file, 'r') as stream:
            dict = yaml.load(stream)
            return Config(dict)
