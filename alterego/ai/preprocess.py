
# -*- coding:utf-8 -*-

import unicodedata

import six

punctuation = {
    0x2013: '-',
    0x2014: '--',
    0x2015: '-',
    0x2016: '\n',  # '||',
    0x2017: '\'',  # '_',
    0x2018: '\'',
    0x2019: '\'',
    0x201A: ',',
    0x201B: '`',
    0x201C: '"',
    0x201D: '"',
    0x0333: '_',
}
punctuation = dict((key, six.u(value)) for (key, value) in six.iteritems(punctuation))


def preprocess(text):
    text = unicodedata.normalize('NFKD', text.decode('utf8'))
    text = text.translate(punctuation)
    text = text.encode('utf-8')
    return text
