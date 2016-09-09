
from collections import deque
import re

import six.moves

from alterego.config import config_register

config_register('max-last', 2)


class Parser(object):
    def __init__(self, config):
        self.state = config.state_driver()
        self.maxlast = config['max-last']

    def parse(self, text):
        """Read some text and create new Markov mappings
        """
        words = re.split(r'\W+', text)
        last = deque(maxlen=self.maxlast)
        for next_word in words:
            for idx in six.moves.range(len(last)):
                key = ' '.join(last[idx:])
                self.state.append(key, next_word)
            last.append(next_word)
