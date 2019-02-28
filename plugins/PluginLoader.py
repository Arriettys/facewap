import os

class PluginLoader():
    @staticmethod
    def get_extractor(name):
        return PluginLoader._import("Extract", "Extract_{0}".format(name))

    @staticmethod
    def _import(attr, name):
        print ("Loading {} from {} plugin...".format(attr, name))
        # __import__ 动态加载模块
        # locals(): 局部名字空间的拷贝
        # globals(): 实际的全局名字空间
        module = __import__(name, globals(), locals(), [], 1)
        return getattr(module, attr)

    @staticmethod
    def get_converter(name):
        return PluginLoader._import("Convert", "Convert_{0}".format(name))

    @staticmethod
    def get_model(name):
        return PluginLoader._import("Model", "Model_{0}".format(name))

    @staticmethod
    def get_trainer(name):
        return PluginLoader._import("Trainer", "Model_{0}".format(name))

    @staticmethod
    def get_available_models():
        models = ()
        # os.path.dirname(__file__)的作用是 返回脚本的路径，即文件路径中所在的目录（不包含文件名）
        for dir in next(os.walk(os.path.dirname(__file__)))[1]:
            if dir[0:6].lower() == "model_":
                models += (dir[6:],)
        return models

    @staticmethod
    def get_default_model():
        models = PluginLoader.get_available_models()
        return "Original" if "Original" in models else models[0]
