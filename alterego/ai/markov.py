
from collections import deque
import re

import six.moves

from alterego.ai.preprocess import preprocess
from alterego.config import config_register

config_register('max-last[int]', 2)


class Markov(object):
    def __init__(self, config):
        self.state = config.state_driver()
        self.maxlast = config['max-last']

    def parse(self, text):
        """Read some text and create new Markov mappings
        """
        # words = re.split(r'''[^a-zA-Z0-9_'-]+''', text)
        text = preprocess(text)
        lines = text.splitlines()
        for line in lines:
            words = re.split(r'\s', line)
            queue = deque(['']*self.maxlast, maxlen=self.maxlast)
            for next_word in words+['']:
                if queue and queue[-1] == next_word:
                    continue
                lqueue = list(queue)
                while lqueue:
                    key = ' '.join(lqueue)
                    lqueue.pop(0)
                    self.state.append(key, next_word)
                queue.append(next_word)

    def say(self, message_length=100):
        message = ''
        queue = deque(['']*self.maxlast, maxlen=self.maxlast)
        while len(message) < message_length:
            keys = []
            lqueue = list(queue)
            while lqueue:
                key = ' '.join(lqueue)
                keys.append(' '.join(lqueue))
                lqueue.pop(0)
            word = self.state.random(*keys)
            if not message:
                message = word
            elif word != '':
                message += ' '+word
            if word:
                queue.append(word)
            else:
                try:
                    queue.popleft()
                except IndexError:
                    pass
        match = re.match(r'(.*[.?!])[^.?!]*?$', message)
        if match:
            message = match.group(1)
        message = message.lstrip('-')
        return message
