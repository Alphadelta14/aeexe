
from collections import deque
import re

import six.moves

from alterego.config import config_register

config_register('max-last[int]', 2)


class Markov(object):
    def __init__(self, config):
        self.state = config.state_driver()
        self.maxlast = config['max-last']

    def parse(self, text):
        """Read some text and create new Markov mappings
        """
        words = re.split(r'\W+', text)
        queue = deque(maxlen=self.maxlast)
        for next_word in words:
            last = []
            for recent in queue:
                last.append(recent)
                key = ' '.join(last)
                self.state.append(key, next_word)
            queue.append(next_word)

    def say(self, message_length=100):
        queue = deque(maxlen=self.maxlast)
        message = self.state.random()
        queue.append(message)
        while len(message) < message_length:
            keys = []
            last = []
            for recent in queue:
                last.append(recent)
                keys.append(' '.join(recent))
            word = self.state.random(*keys)
            message += ' '+word
            queue.append(word)
        return message
