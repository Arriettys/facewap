#!/usr/bin/env python
#-*- coding:UTF-8 -*-
"""Command Line Arguments"""

import argparse
import os
import platform
import sys
from importlib import import_module
from plugins.PluginLoader import PluginLoader

class FullHelpArgumentParser(argparse.ArgumentParser):
    """
    En.Identical to the build-in argument parser,but on error it 
    print full help message instand of just usage information
    Cn.通过继承创建一个和argparse的ArgumentParser(参数解析器类)
    一样的参数解析器，但在error时它能打印完整的帮助信息，而不仅
    仅是使用信息。
    """
    def error(self,message):
        # sys.srderr 即错误输出
        self.print_help(sys.stderr)
        args = {"prog":self.prog,"message":message}
        self.exit(2,"%(prog)s: error: %(message)s\n" % args)
