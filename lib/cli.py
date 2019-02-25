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

class FaceSwapArgs(object):
    """
    En.Faceswap argument parser function that are universal to all commends.
    Should be that the parent function of all subsequent argparses
    Cn.Faceswap 通常情况下所有命令的参数解析器函数，且是所有后来
    的子类解析器的父类。
    """
    def __init__(self, subparser, command, description="default", subparsers=None):
        self.argument_list = self.get_argument_list()
        self.optional_arguments = self.get_optional_arguments()
        if not subparser:
            return
        self.parser = self.create_parser(subparser, command, description)
        self.add_arguments()
        script = ScriptExecutor(command, subparsers)
        self.parser.set_default(func=script.execute_script)

    @staticmethod
    def get_argument_list():
        """
        En.Put the arguments in a list so that they are accessible from
        both argparser and gui override for command specific arguments
        Cn.将参数放在列表中以便于参数解析器和GUI对于特定命令进行访问
        """
        argument_list = []
        return argument_list
    
    @staticmethod
    def get_optional_arguments():
        """
        En.Put the arguments in a list so that they are accessinle from
        both argparser and gui.This is used for when there are sub-children
        (e.g. convert and extract) Override this for custom arguments
        Cn.将参数放在列表中以便于参数解析器和GUI进行访问。当存在子级
        (e.g convert and extract)此选项用于自定义参数重写。
        """
        argument_list = []
        return argument_list

    @staticmethod
    def create_parser(subparser, command, description):
        """
        En.Create the parser for the selected command
        Cn.为所选命令创建解析器
        """
        parser = subparser.add_parser(
            command,
            help=description,
            description=description,
            epilog="Questions and feedback: \
            https://github.com/deepfakes/faceswap-playground")
        return parser

    def add_arguments(self):
        """
        En.Parse the arguments passed in from argparse
        Cn.解析从argparse传入的参数
        """
        for option in self.argument_list + self.option_arguments:
            args = option["opts"]
            kwargs = {key: option[key] for key in option.keys() if key != "opts"}
            self.parser.add_argument(*args, **kwargs)
        
class ExtractConvertArgs(FaceSwapArgs):
    """
    En.This class is used as a parent class to capture arguments that
    will be used in both the extract and convert process.
    Argument that can be used in both of there processes should be 
    placed here, but no further processing should be done. This class
    just captures arguments
    Cn.此类作为父类捕获在提取和转换进程中使用的参数。
    可以将这两个进程中使用的参数放置此处，但不做进一步处理
    该类只捕获参数。
    """
    @staticmethod
    def get_argument_list():
        """
        En.Put the arguments in a list so that they are accessible from both
        argparse and gui
        Cn.将参数放在列表中以便argparse和gui进行访问
        """
        alignments_filetypes = [["Serializers", ["json", "p", "yaml"]],
                                ["JSON", ["json"]],
                                ["Pickle", ["p"]],
                                ["YAML",["yaml"]]]
        alignments_filetypes = FileFullPaths.prep_filetypes(alignments_filetypes)

class FullPaths(argparse.Action):
    """
    En.Expand user- and relative-paths
    Cn.展开用户和相对路劲
    """
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, os.path.abspath(os.path.expanduser(values)))

class DirFullPaths(FullPaths):
    """
    En.Class that gui uses to determine if you need to open a directory
    Cn.gui用于确定是否打开目录的类
    """
    pass

class FileFullPaths(FullPaths):
    """
    En.Class that gui uses to determine if you need to open a file.
    Filetypes added as an argparse argument must be an iterable, i.e. a
    list of lists, tuple of tuples, list of tuples etc... formatted like so:
        [("File Type", ["*.ext", "*.extension"])]
    A more realistic example:
        [("Video File", ["*.mkv", "mp4", "webm"])]
    If the file extensions are not prepended with '*.', use the
    prep_filetypes() method to format them in the arguments_list.
    Cn.gui用于确定是否打开目录的类
    作为argparse参数添加的文件类型必须是ITerable，即
    列表列表、元组列表、元组列表等…格式如下：
    [（“文件类型”，[“*.ext”，“*.extension”]）]
    一个更现实的例子：
    [（“视频文件”，[“*.mkv”，“mp4”，“webm”]）]
    如果文件扩展名前面没有“*”，请使用
    准备\u filetypes（）方法在参数列表中格式化它们。
    """
    def __init__(self, option_strings, dest, nargs=None, filetypes=None, **kwargs):
        super(FileFullPaths, self).__init__(option_strings, dest, **kwargs)
        if nargs is not None:
            raise ValueError("nargs not allowed")
        self.filetypes = filetypes


