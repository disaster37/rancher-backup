__author__ = 'disaster'

import yaml
import glob
import logging
from fr.webcenter.backup.Singleton import Singleton
from jinja2 import Environment


logger = logging
class Config(object):

    __metaclass__ = Singleton

    def __init__(self, path=None):
        """
        Permit to load all settings
        :param path: the base path where settings is stored
        :type path: basestring
        """



        # Load index settings
        contendIndex = ""
        for file in glob.glob(path + '/index/*.yml'):
            contendIndex += open(file, 'r').read() + "\n"

        logger.debug("Index settings : %s", contendIndex)
        Config._index = yaml.load(contendIndex)

        # Load templates
        contendTemplates = {}
        for file in glob.glob(path + '/templates/*'):
            contendTemplates[file] = open(file, 'r').read()
        Config._templates = contendTemplates

        Config._path = path




    def getIndex(self):
        """
        Permit to get the index
        :return dict: the index
        """
        if isinstance(self._index, dict) is False:
            raise Exception("You must init Config first")

        logger.debug("return : %s", self._index)
        return self._index

    def getTemplate(self, templateFile):
        """
        Permit to get the template by name
        :param templateFile: The template filename that needed
        :type templateFile: basestring
        :return basestring: the template
        """
        if self._templates is None:
            raise Exception("You must init Config first")

        if templateFile is None or templateFile == "":
            raise KeyError("You must provide templateFile")

        templateFile = "%s/templates/%s" % (self._path, templateFile)

        if templateFile in self._templates:
            logger.debug("return: %s", self._templates[templateFile])
            return self._templates[templateFile]
        else:
            raise Exception("Template %s not found", templateFile)


