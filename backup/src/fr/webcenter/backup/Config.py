__author__ = 'disaster'

import yaml
import glob
import logging
from fr.webcenter.backup.Singleton import Singleton


logger = logging.getLogger(__name__)
class Config(object):

    __metaclass__ = Singleton

    def __init__(self, path=None):
        contend = ""
        for file in glob.glob(path):
            contend += open(file, 'r').read()

        logger.debug("Settings : %s", contend)
        Config._setting = yaml.load(contend)


    def getConfig(self):
        if self._setting is None:
            raise Exception("You must init Config first")

        logger.debug("return : %s", )
        return self._setting