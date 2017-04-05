__author__ = 'disaster'

import unittest
import mock
from fr.webcenter.backup.Config import Config

def fakeSetting(path=None):
    
    if path is not None:
    
        Config._settings = {
            'rancher.host': "test",
            'rancher.port': 1234
        }

        Config._index =  {
            'mysql': {
                'image': 'fake/image',
                'command': 'facke command'
            }
        }

        Config._templates = {
            path + '/templates/mysql.yml': "my mysql fake sample",
            'postgresql.yml': "my postgresql fake sample"
        }

        Config._path = path

class ConfigTest(unittest.TestCase):
    
    @mock.patch.object(Config, '__init__', side_effect=fakeSetting)
    def testGetSettings(self, run_mock):
        configService = Config("/fake/path")
        settings = configService.getSettings()

        targetSettings = {
            'rancher.host': "test",
            'rancher.port': 1234
        }

        self.assertEqual(settings, targetSettings)

        configService = Config()
        settings = configService.getSettings()
        self.assertEqual(settings, targetSettings)

    @mock.patch.object(Config, '__init__', side_effect=fakeSetting)
    def testGetIndex(self, run_mock):
        configService = Config("/fake/path")
        index = configService.getIndex()

        targetIndex = {
            'mysql': {
                'image': 'fake/image',
                'command': 'facke command'
            }
        }

        self.assertEqual(index, targetIndex)

        configService = Config()
        index = configService.getIndex()
        self.assertEqual(index, targetIndex)

    @mock.patch.object(Config, '__init__', side_effect=fakeSetting)
    def testGetTemplate(self, run_mock):
        configService = Config("/fake/path")
        template = configService.getTemplate("mysql.yml")

        targetTemplate = "my mysql fake sample"


        self.assertEqual(template, targetTemplate)

        configService = Config()
        template = configService.getTemplate("mysql.yml")
        self.assertEqual(template, targetTemplate)



if __name__ == '__main__':
    unittest.main()