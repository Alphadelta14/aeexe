#!/usr/bin/env python
"""AlterEgo Command Line Interface module

This exposes the main() entrypoint of the program
"""

import argparse
import sys

from alterego.ai.markov import Markov
from alterego.config import Configuration
from alterego.learn import AELearn
from alterego.outgoing.twitter import Twitter


def parse_args(argv=None):
    root = argparse.ArgumentParser()
    root.add_argument('--config', '-c', default='config.ini')
    root.add_argument('command', choices=('help', 'learn', 'say', 'tweet', 'generate'), default='help')
    root.add_argument('args', nargs='*')

    return root.parse_args(argv)


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
    elif args.command == 'tweet':
        Twitter(config).tweet(Markov(config).say())
    elif args.command == 'say':
        print(Markov(config).say())
    return 0


if __name__ == '__main__':
    sys.exit(main())
