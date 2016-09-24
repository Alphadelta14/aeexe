
import csv
import re

from alterego.ai import markov
from alterego.ai.ssa import learn_ssa
from alterego.outgoing.twitter import Twitter


class AELearn(object):
    def __init__(self, config):
        self._config = config
        self.markov = markov.Markov(self._config)

    def learn(self, args):
        for arg in args:
            try:
                protocol, location = arg.split('://', 1)
            except IndexError:
                protocol = None
            if protocol == 'http':
                self.learn_web(arg)
            elif protocol == 'file':
                self.learn_file(location)
            elif protocol == 'ssa':
                for text in learn_ssa(location):
                    self.learn_text(text)
            elif protocol == 'twitter':
                for text in self.learn_twitter(location):
                    self.learn_text(text)

    def learn_text(self, text):
        self.markov.parse(text)

    def learn_file(self, location):
        with open(location) as handle:
            text = handle.read()
            self.learn_text(text)

    def learn_twitter(self, location):
        if location == 'home':
            twitter = Twitter(self._config)
            return twitter.home()
        else:
            raise ValueError('Only twitter://home is supported at this time')
