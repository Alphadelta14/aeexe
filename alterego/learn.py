
import glob
import re

from alterego.ai import markov
from alterego.ai.ssa import learn_ssa
from alterego.outgoing.twitter import Twitter


class AELearn(object):
    def __init__(self, config, dry=False):
        self._config = config
        self.dry = dry
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
                for single_location in glob.glob(location):
                    self.learn_file(single_location)
            elif protocol == 'ssa':
                for single_location in glob.glob(location):
                    for text in learn_ssa(single_location):
                        self.learn_text(text)
            elif protocol == 'twitter':
                for text in self.learn_twitter(location):
                    self.learn_text(text)

    def learn_text(self, text):
        try:
            print('Learning {}'.format(text.encode('ascii', 'ignore')))
        except UnicodeDecodeError:
            print('Learning <something>')
        self.markov.parse(text)

    def learn_file(self, location):
        with open(location) as handle:
            text = handle.read()
            self.learn_text(text)

    def learn_twitter(self, location):
        if location == 'home':
            twitter = Twitter(self._config)
            return twitter.timeline()
        elif location.startswith('@'):
            twitter = Twitter(self._config)
            return twitter.timeline(location[1:])
        else:
            raise ValueError('Only twitter://home and twitter://@username are'
                             'supported at this time')
