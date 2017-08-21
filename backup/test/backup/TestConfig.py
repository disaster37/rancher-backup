__author__ = 'disaster'

import unittest
import mock
from fr.webcenter.backup.Config import Config




def fakeSetting(path):
    
    settings = {
            'rancher.host': "test",
            'rancher.port': 1234
    }
    
    indexes = { 
                'mysql': {
                    'image': 'fake/image',
                    'command': 'facke command'
                }
    }
    
    templates = {
            path + '/templates/mysql.yml': "my mysql fake sample",
            'postgresql.yml': "my postgresql fake sample"
    }
    
    return (settings, indexes, templates)

class TestConfig(unittest.TestCase):
    
    def tearDown(self):
        Config._drop()
    
    @mock.patch.object(Config, '_load', side_effect=fakeSetting)
    def testGetSettings(self, run_mock):
        Config._drop()
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

    @mock.patch.object(Config, '_load', side_effect=fakeSetting)
    def testGetIndex(self, run_mock):
        Config._drop()
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

    @mock.patch.object(Config, '_load', side_effect=fakeSetting)
    def testGetTemplate(self, run_mock):
        Config._drop()
        configService = Config("/fake/path")
        template = configService.getTemplate("mysql.yml")

        targetTemplate = "my mysql fake sample"


        self.assertEqual(template, targetTemplate)

        configService = Config()
        template = configService.getTemplate("mysql.yml")
        self.assertEqual(template, targetTemplate)



if __name__ == '__main__':
    unittest.main()