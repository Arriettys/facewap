#!/usr/bin/env python
#-*- coding:UTF-8 -*-

import sys
import lib.cli as cli

if sys.version_info[0] < 3:
    raise Exception("This program requires at least python3.6")
if sys.version_info[0] == 3 and sys.version_info[1] < 6:
    raise Exception("This program requires at least python3.6")

if __name__ == "__main__":
    PARSER = cli.FullHelpArgumentParser()
    SUBPARSER = PARSER.add_subparsers()
    EXTRACT = cli.ExtractArgs(SUBPARSER,"extract","Extract the face from pictures")
    TRAIN = cli
