
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
        words = re.split(r'''[^a-zA-Z0-9_'-]+''', text)
        queue = deque(maxlen=self.maxlast)
        for next_word in words:
            if not next_word:
                continue
            if next_word in queue:
                continue
            if len(next_word) < 3:
                queue.append(next_word)
                continue
            last = []
            for recent in queue:
                last.insert(0, recent)
                key = ' '.join(last)
                self.state.append(key.lower(), next_word)
            queue.append(next_word)

    def say(self, message_length=100):
        queue = deque([self.state.random() for idx_ in six.moves.range(self.maxlast)],
                      maxlen=self.maxlast)
        message = ' '.join(queue)
        while len(message) < message_length:
            keys = []
            last = list(reversed(queue))
            for idx in six.moves.range(len(last)):
                keys.append(' '.join(last[:idx+1]))
            word = self.state.random(*keys)
            message += ' '+word
            word = word.lower()
            if word in last:
                continue
            elif word:
                queue.append(word)
            else:
                try:
                    queue.popleft()
                except IndexError:
                    pass
        return message
