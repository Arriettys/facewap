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
        self.parser.set_defaults(func=script.execute_script)

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
        for option in self.argument_list + self.optional_arguments:
            args = option["opts"]
            kwargs = {key: option[key] for key in option.keys() if key != "opts"}
            self.parser.add_argument(*args, **kwargs)

class ScriptExecutor(object):
    """
    En.Loads the relevant script modules and executes the script. 
    This class is initialised in each of the argparsers for the relevant
    command, then execute script is called within their set_default function.
    Cn.加载相关的脚本模块并执行脚本。此类初始化每个命令相关的参数解析器
    然后在它们默认的函数中调用执行脚本
    """
    def __init__(self, command, subparsers=None):
        self.command = command.lower()
        self.subparsers = subparsers

    def test_for_gui(self):
        """
        En.If running the gui, check the prerequisites
        Cn.加入运行GUI，检查先决条件
        """
        if self.command != "gui":
            return
        self.test_tkinter()
        self.check_display()

    def import_script(self):
        """
        En.Only import a script's modules when running that script.
        Cn.仅在运行脚本时导入脚本的模块
        """
        self.test_for_gui()
        cmd = sys.argv[0]
        src = "tools" if cmd == "tools.py" else "scripts"
        mod = ".".join((src, self.command.lower()))
        module = import_module(mod)
        script = getattr(module, self.command.title())
        return script

    @staticmethod
    def test_tkinter():
        """
        En.If the user is running the GUI, test whether the tkinter 
        app is available on their machine. If not exit gracefully. 

        This avoids having to import every tk function within the
        GUI in a wrapper and potentially spamming traceback errors 
        to console
        Cn.如果用户运行GUI，测试tkinter应用程序在他们的机器上是否
        可用。如果不能正常退出，这避免了在包装器中导入GUI中的每个
        tk函数，并可能将跟踪错误发送到控制台。
        """
        try:
            import tkinter
        except ImportError:
            print (
                    "It looks like TkInter isn't installed for your OS, so " 
                    "the GUI has been disabled. To enable the GUI please "
                    "install the TkInter application.\n\n"
                    "You can try:\n"
                    "  Windows/macOS:      Install ActiveTcl Community "
                    "Edition from "
                    "www.activestate.com\n" 
                    "  Ubuntu/Mint/Debian: sudo apt install python3-tk\n"
                    "  Arch:               sudo pacman -S tk\n" 
                    "  CentOS/Redhat:      sudo yum install tkinter\n"
                    "  Fedora:             sudo dnf install python3-tkinter\n"
                    )
            exit(1)

    @staticmethod
    def check_display():
        """
        En.Check whether there is a display to output the GUI. 
        If running on Windows then assume not running in headless mode
        Cn.检查是否有显示器输出图形用户界面。如果在Windows上运行，
        则假定不在无头模式下运行
        """
        if not os.environ.get("DISPLAY", None) and os.name != "nt":
            print ("No display detected.GUI mode has been disabled.")
            if platform.system() == "Darwin":
                print (
                        "macOS users need to install XQuartz. " 
                        "See https://support.apple.com/en-gb/HT201341")
                exit(1)
    def execute_script(self, arguments):
        """
        En.Run the script for called command
        Cn.运行被调用的命令脚本
        """
        script = self.import_script()
        process = script(arguments)
        process.process()


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
        argument_list = list()
        argument_list.append({
                             "opts": ("-i", "--input-dir"), 
                             "action": DirFullPaths, 
                             "dest": "input_dir",
                             "default": "input", 
                             "help": "Input directory. A directory "
                                     "containing the files you wish to " 
                                     "process. Defaults to 'input'"
                            })
        argument_list.append({
                             "opts": ("-o", "--output-dir"),
                             "action": DirFullPaths,
                             "dest": "output_dir", 
                             "default": "output",
                             "help": "Output directory. This is where the " 
                                    "converted files will be stored. "
                                    "Defaults to 'output'"
                             })
        argument_list.append({
                             "opts": ("--alignments", ),
                             "action": FileFullPaths,
                             "filetypes": alignments_filetypes,
                             "type": str,
                             "dest": "alignments_path",
                             "help": "Optional path to an alignments file."
                            })
        argument_list.append({
                             "opts": ("--serializer", ),
                             "type": str.lower,
                             "dest": "serializer",
                             "default": "json",
                             "choices": ("json", "pickle", "yaml"),
                             "help": "Serializer for alignments file. If "
                                    "yaml is chosen and not available, then " 
                                    "json will be used as the default " 
                                    "fallback."
                            })
        argument_list.append({
                            "opts": ("-D", "--detector"),
                            "type": str,
                            # 区分大小写，因为它用于加载插件
                            "choices": ("hog", "cnn", "all"),
                            "default": "hog", 
                            "help": "Detector to use. 'cnn' detects many "
                                    "more angles but will be much more "
                                    "resource intensive and may fail on "
                                    "large files"
                            })
        argument_list.append({
                            "opts": ("-l", "--ref_threshold"),
                            "type": float,
                            "dest": "ref_threshold",
                            "default": 0.6,
                            "help": "Threshold for positive face recognition"
                            })
        argument_list.append({
                            "opts": ("-n", "--nfilter"), 
                            "type": str, 
                            "dest": "nfilter",
                            "nargs": "+",
                            "default": None,
                            "help": "Reference image for the persons you do "
                                    "not want to process. Should be a front "
                                    "portrait. Multiple images can be added "
                                    "space separated"
                            })
        argument_list.append({
                            "opts": ("-v", "--verbose"),
                            "action": "store_true",
                            "dest": "verbose", 
                            "default": False,
                            "help": "Show verbose output"
                            })
        return argument_list

class ExtractArgs(ExtractConvertArgs):
    """
    En.Class to parse the command line arguments for extraction.
    Inherits base options from ExtractConvertArgs where arguments
    that are used for both extract and convert should be placed
    Cn.用于提取的命令行参数解析器类。从ExtractConvertargs继承
    的基选项，其中应放置用于提取和转换的参数
    """
    @staticmethod
    def get_optional_arguments():
        """
        En.Put the arguments in a list so that they are 
        accessible from both argparse and gui
        Cn.将参数放在一个列表中，以便argparse和gui都可以访问
        """
        argument_list = []
        argument_list.append({
                            "opts": ("-r", "--rotate-images"),
                            "type": str,
                            "dest": "rotate_images",
                            "default": None,
                            "help": "If a face isn't found, rotate the " 
                                    "images to try to find a face. Can find " 
                                    "more faces at the cost of extraction "
                                    "speed. Pass in a single number to use "
                                    "increments of that size up to 360, or "
                                    "pass in a list of numbers to enumerate "
                                    "exactly what angles to check"
                            })
        argument_list.append({
                            "opts": ("-bt", "--blur-threshold"),
                            "type": int,
                            "dest": "blur_thresh",
                            "default": None,
                            "help": "Automatically discard images blurrier " 
                                    "than the specified threshold. " 
                                    "Discarded images are moved into a " 
                                    "\"blurry\" sub-folder. Lower values "
                                    "allow more blur"
                            })
        argument_list.append({									
                            "opts": ("-j", "--processes"),
                            "type": int,
                            "default": 1,
                            "help": "Number of CPU processes to use. "
                                    "WARNING: ONLY USE THIS IF YOU ARE NOT "
                                    "EXTRACTING ON A GPU. Anything above 1 "
                                    "process on a GPU will run out of "
                                    "memory and will crash"
                            })
        argument_list.append({		    			
                            "opts": ("-s", "--skip-existing"),
                            "action": "store_true",
                            "dest": "skip_existing",
                            "default": False,
                            "help": "Skips frames that have already been extracted"
                            })
        argument_list.append({
                            "opts": ("-dl", "--debug-landmarks"),
                            "action": "store_true",
                            "dest": "debug_landmarks",
                            "default": False,
                            "help": "Draw landmarks on the ouput faces for debug"
                            })
        argument_list.append({
                            "opts": ("-ae", "--align-eyes"),
                            "action": "store_true",
                            "dest": "align_eyes",
                            "default": False,
                            "help": "Perform extra alignment to ensure "
                                    "left/right eyes are  at the same "
                                    "height"
                            })
        return argument_list

class ConvertArgs(ExtractConvertArgs):
    """
    En.Class to parse the command line arguments for conversion.
    Inherits base options from ExtractConvertArgs where arguments
    that are used for both extract and convert should be placed
    Cn.用于提取的命令行参数解析器类。从ExtractConvertargs
    继承基选项，其中应放置用于提取和转换的参数
    """
    @staticmethod
    def get_optional_arguments():
        """
        En.Put the arguments in a list so that they are accessible
        from both argparse and gui
        Cn.将参数放在一个列表中，以便argparse和gui都可以访问
        """
        argument_list = []
        argument_list.append({
                            "opts": ("-m", "--model-dir"),
                            "action": DirFullPaths,
                            "dest": "model_dir",
                            "default": "models",
                            "help": "Model directory. A directory " 
                                    "containing the trained model you wish " 
                                    "to process. Defaults to 'models'"
                            })
        argument_list.append({
                            "opts": ("-a", "--input-aligned-dir"),
                            "action": DirFullPaths, 
                            "dest": "input_aligned_dir",
                            "default": None,
                            "help": "Input \"aligned directory\". A "
                                    "directory that should contain the "
                                    "aligned faces extracted from the input "
                                    "files. If you delete faces from this "
                                    "folder, they'll be skipped during " 
                                    "conversion. If no aligned dir is "
                                    "specified, all faces will be converted"
                            })
        argument_list.append({
                            "opts": ("-t", "--trainer"), 
                            "type": str,
                            # 区分大小写，因为它用于加载插件
                            "choices": PluginLoader.get_available_models(),
                            "default": PluginLoader.get_default_model(), 
                            "help": "Select the trainer that was used to create the model"
                            })
        argument_list.append({
                            "opts": ("-c", "--converter"), 
                            "type": str,
                            # 区分大小写，因为它用于加载插件
                            "choices": ("Masked", "Adjust"), 
                            "default": "Masked",
                            "help": "Converter to use"
                            })
        argument_list.append({
                            "opts": ("-b", "--blur-size"),
                            "type": int,
                            "default": 2,
                            "help": "Blur size. (Masked converter only)"
                            })
        argument_list.append({
                            "opts": ("-e", "--erosion-kernel-size"),
                            "dest": "erosion_kernel_size",
                            "type": int,
                            "default": None,
                            "help": "Erosion kernel size. Positive values "
                                    "apply erosion which reduces the edge "
                                    "of the swapped face. Negative values "
                                    "apply dilation which allows the "
                                    "swapped face to cover more space. "
                                    "(Masked converter only)"
                            })
        argument_list.append({
                            "opts": ("-M", "--mask-type"),
                            # 小写这个，因为以后它只是一个字符串
                            "type": str.lower,
                            "dest": "mask_type",
                            "choices": ["rect", "facehull", "facehullandrect"],
                            "default": "facehullandrect",
                            "help": "Mask to use to replace faces. (Masked converter only)" 
                            })
        argument_list.append({
                            "opts": ("-sh", "--sharpen"),
                            "type": str.lower,
                            "dest": "sharpen_image",
                            "choices": ["bsharpen", "gsharpen"],
                            "default": None,
                            "help": "Use Sharpen Image. bsharpen for Box " 
                                    "Blur, gsharpen for Gaussian Blur "
                                    "(Masked converter only)"
                            })
        argument_list.append({
                            "opts": ("-g", "--gpus"),
                            "type": int, 
                            "default": 1,
                            "help": "Number of GPUs to use for conversion"
                            })
        argument_list.append({
                            "opts": ("-fr", "--frame-ranges"),
                            "nargs": "+",
                            "type": str,
                            "help": "frame ranges to apply transfer to e.g. "
                                    "For frames 10 to 50 and 90 to 100 use "
                                    "--frame-ranges 10-50 90-100. Files "
                                    "must have the frame-number as the last "
                                    "number in the name!"
                            })
        argument_list.append({
                            "opts": ("-d", "--discard-frames"),
                            "action": "store_true",
                            "dest": "discard_frames",
                            "default": False,
                            "help": "When used with --frame-ranges discards "
                                    "frames that are not processed instead "
                                    "of writing them out unchanged"
                            })
        argument_list.append({
                            "opts": ("-s", "--swap-model"),
                            "action": "store_true",
                            "dest": "swap_model",
                            "default": False, 
                            "help": "Swap the model. Instead of A -> B, swap B -> A"
                            }) 
        argument_list.append({
                            "opts": ("-S", "--seamless"),
                            "action": "store_true",
                            "dest": "seamless_clone",
                            "default": False, 
                            "help": "Use cv2's seamless clone. (Masked converter only)"
                            })
        argument_list.append({
                            "opts": ("-mh", "--match-histogram"),
                            "action": "store_true",
                            "dest": "match_histogram", 
                            "default": False, 
                            "help": "Use histogram matching. (Masked converter only)"
                            })
        argument_list.append({
                            "opts": ("-sm", "--smooth-mask"),
                            "action": "store_true", 
                            "dest": "smooth_mask",
                            "default": True,
                            "help": "Smooth mask (Adjust converter only)"
                            })
        argument_list.append({
                            "opts": ("-aca", "--avg-color-adjust"),
                            "action": "store_true", 
                            "dest": "avg_color_adjust",
                            "default": True,
                            "help": "Average color adjust. (Adjust converter only)"
                            })
        return argument_list

class TrainArgs(FaceSwapArgs):
    """
    En.Class to parse the command line arguments for training
    Cn.训练过程的命令行参数解析类
    """
    @staticmethod
    def get_argument_list():
        """
        En.Put the arguments in a list so that they are accessible 
        from both argparse and gui
        Cn.将参数放在列表中以便argparse和gui访问
        """
        argument_list = list()
        argument_list.append({
                            "opts": ("-A", "--input-A"),
                            "action": DirFullPaths,
                            "dest": "input_A", 
                            "default": "input_A", 
                            "help": "Input directory. A directory "
                                    "containing training images for face A. "
                                    "Defaults to 'input'"
                            })
        argument_list.append({
                            "opts": ("-B", "--input-B"),
                            "action": DirFullPaths,
                            "dest": "input_B",
                            "default": "input_B",
                            "help": "Input directory. A directory "
                                    "containing training images for face B. "
                                    "Defaults to 'input'"
                            })
        argument_list.append({
                            "opts": ("-m", "--model-dir"),
                            "action": DirFullPaths,
                            "dest": "model_dir",
                            "default": "models",
                            "help": "Model directory. This is where the "
                                    "training data will be stored. "
                                    "Defaults to 'model'"
                            })
        argument_list.append({
                            "opts": ("-s", "--save-interval"),
                            "type": int,
                            "dest": "save_interval",
                            "default": 100,
                            "help": "Sets the number of iterations before "
                                    "saving the model"
                            })
        argument_list.append({
                            "opts": ("-t", "--trainer"),
                            "type": str,
                            "choices": PluginLoader.get_available_models(),
                            "default": PluginLoader.get_default_model(),
                            "help": "Select which trainer to use, Use "
                                    "LowMem for cards with less than 2GB of "
                                    "VRAM"
                            })
        argument_list.append({
                            "opts": ("-bs", "--batch-size"),
                            "type": int,
                            "default": 64,
                            "help": "Batch size, as a power of 2 (64, 128, 256, etc)"
                            })
        argument_list.append({
                            "opts": ("-ep", "--epochs"),
                            "type": int,
                            "default": 1000000,
                            "help": "Length of training in epochs"
                            })
        argument_list.append({
                            "opts": ("-g", "--gpus"),
                            "type": int,
                            "default": 1,
                            "help": "Number of GPUs to use for training"
                            })
        argument_list.append({
                            "opts": ("-p", "--preview"), 
                            "action": "store_true",
                            "dest": "preview",
                            "default": False,
                            "help": "Show preview output. If not specified, "
                                    "write progress to file"
                            })
        argument_list.append({
                            "opts": ("-w", "--write-image"),
                            "action": "store_true",
                            "dest": "write_image",
                            "default": False,
                            "help": "Writes the training result to a file "
                                    "even on preview mode"
                            })
        argument_list.append({
                            "opts": ("-pl", "--use-perceptual-loss"),
                            "action": "store_true",
                            "dest": "perceptual_loss",
                            "default": False,
                            "help": "Use perceptual loss while training"
                            })
        argument_list.append({
                            "opts": ("-ag", "--allow-growth"),
                            "action": "store_true",
                            "dest": "allow_growth", 
                            "default": False, 
                            "help": "Sets allow_growth option of Tensorflow "
                                    "to spare memory on some configs"
                            })
        argument_list.append({
                            "opts": ("-v", "--verbose"),
                            "action": "store_true",
                            "dest": "verbose", 
                            "default": False,
                            "help": "Show verbose output"
                            })
        # 这是一个隐藏的参数，用于指示正在使用GUI
        # 因此应相应地重定向预览窗口
        argument_list.append({
                            "opts": ("-gui", "--gui"),
                            "action": "store_true",
                            "dest": "redirect_gui",
                            "default": False,
                            "help": argparse.SUPPRESS
                            })
        return argument_list

class GuiArgs(FaceSwapArgs):
    @staticmethod
    def get_argument_list():
        """
        En.Put the arguments in a list so that they are accessible 
        from both argparse and gui
        Cn.将参数放在列表中以便argparse和gui访问
        """
        argument_list = []
        argument_list.append({
                            "opts": ("-d", "--debug"),
                            "action": "store_true",
                            "dest": "debug",
                            "default": False,
                            "help": "Output to Shell console instead of GUI console"
                            })
        return argument_list

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
    prep_filetypes（）方法在参数列表中格式化它们。
    """
    def __init__(self, option_strings, dest, nargs=None, filetypes=None, **kwargs):
        super(FileFullPaths, self).__init__(option_strings, dest, **kwargs)
        if nargs is not None:
            raise ValueError("nargs not allowed")
        self.filetypes = filetypes

    @staticmethod
    def prep_filetypes(filetypes):
        """
        En.Prepare the filetypes for required file
        Cn.为所需文件准备文件类型
        """
        all_files = ("All Files", "*.*")
        filetypes_l = list()
        for filetype in filetypes:
            filetypes_l.append(FileFullPaths._process_filetypes(filetype))
        filetypes_l.append(all_files)
        return tuple(filetypes_l)

    @staticmethod
    def _process_filetypes(filetypes):
        """
        Cn.用于检测文件类型格式是否正常
        若文件类型为列表或元组且文件类型格式则正确直接返回
        若文件类型不为列表或元组直接报错
        若文件类型格式不对，则补充完整返回
        """
        if filetypes is None:
            return None

        filetypes_name = filetypes[0]
        filetypes_l = filetypes[1]
        if isinstance(filetypes_l, (list,tuple)) and all("*." in i for i in filetypes_l):
            return filetypes #假定文件类型格式正确

        if not isinstance(filetypes_l, list) and not isinstance(filetypes_l, tuple):
            raise ValueError("The filetypes extensions list was"
                             "neither a list nor a tuple: "  
                            "{}".format(filetypes_l))
        filetypes_list = list()
        for filetype in filetypes_l:
            filetype = filetype.strip("*.") # 用于去除文件类型名中的"*."
            filetype = filetype.strip(";") 
            filetypes_list.append("*." + filetype)
        return filetypes_name, filetypes_list

    def _get_kwargs(self):
        names = [
                "option_strings",
                "dest",
                "nargs",
                "const",
                "default",
                "type",
                "choices",
                "help",
                "metavar",
                "filetypes",
                ]
        return [(name, getattr(self, name)) for name in names]

class ComboFullPaths(FileFullPaths):
    """
    En.Class that gui uses to determine if you need to open a 
    file or a directory based on which action you are choosing
    Cn.gui用于决定是否根据你的选择操作打开一个文件或目录
    """
    def __init__(self, option_strings, dest, nargs=None, filetypes=None, actions_open_type=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ComboFullPaths, self).__init__(open_strings, dest, filetypes=None, **kwargs)
        self.actions_open_type = actions_open_type
        self.filetypes = filetypes

    @staticmethod
    def prep_filetypes(filetypes):
        """
        En.Prepare the filetypes for required file
        Cn.为所需文件准备类型
        """
        all_files = ("All Files", "*.")
        filetypes_d = dict()
        for key, val in filetypes.items():
            filetypes_d[key] = ()
            if val is None:
                filetypes_d[key] = None
                continue
            filetypes_l = list()
            for filetype in val:
                filetypes_l.append(ComboFullPaths._process_filetypes(filetype))
            filetypes_d[key] = (tuple(filetypes_l), all_files)
        return filetypes_d

    def _get_kwargs(self):
        names = [
                "option_strings",
                "dest",
                "nargs",
                "const",
                "default",
                "type",
                "choices",
                "help",
                "metavar",
                "filetypes",
                "actions_open_type"
                ]
        return [(name, getattr(self, name)) for name in names]

        
        





