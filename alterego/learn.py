
from alterego.ai import markov


class AELearn(object):
    def __init__(self, config):
        self._config = config

    def learn(self, args):
        parser = markov.Markov(self._config)
        parser.parse(' '.join(args))
