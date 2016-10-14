import yaml
import glob

class Config(object):

    def __init__(self, path):
        contend = ""
        for file in glob.glob(path):
            contend += open(file, 'r').read()

        Config._setting = yaml.load(contend)

    @staticmethod
    def getConfig():
        if Config._setting is None:
            raise Exception("You must init Config first")

        return Config._setting