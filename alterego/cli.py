#!/usr/bin/env python
"""AlterEgo Command Line Interface module

This exposes the main() entrypoint of the program
"""

from __future__ import print_function

import argparse
import sys

from alterego.ai.markov import Markov
from alterego.ai.spider import Spider
from alterego.config import Configuration
from alterego.learn import AELearn
from alterego.outgoing.twitter import Twitter


def parse_args(argv=None):
    root = argparse.ArgumentParser()
    root.add_argument('--config', '-c', default='config.ini')
    root.add_argument('--length', '-n', default=100, type=int)
    root.add_argument('command', choices=('help', 'learn', 'say', 'tweet', 'generate', 'scrape'),
                      default='help')
    # root.add_argument('args', nargs='*')

    args, rest = root.parse_known_args(argv)
    args.args = rest
    if args.command == 'help':
        root.print_help()
        sys.exit(0)
    return args


def main():
    """Main entrypoint for AlterEgo
    """
    args = parse_args()
    if args.command == 'generate':
        config = Configuration()
        config.save(args.config)
        return 0
    config = Configuration(filename=args.config)
    if args.command == 'learn':
        AELearn(config).learn(args.args)
    elif args.command == 'scrape':
        Spider(config).scrape(args.args)
    elif args.command == 'tweet':
        message = Markov(config).say(args.length)
        print(message)
        Twitter(config).tweet(message)
    elif args.command == 'say':
        print(Markov(config).say(args.length))
    return 0


if __name__ == '__main__':
    sys.exit(main())
