__author__ = 'disaster'

import unittest
import mock
from fr.webcenter.backup.Config import Config

def fakeSetting(path=None):

    Config._setting =  {
        'mysql': {
            'image': 'fake/image',
            'command': 'facke command'
        }
    }

class ConfigTest(unittest.TestCase):

    @mock.patch.object(Config, '__init__', side_effect=fakeSetting)
    def testGetConfig(self, run_mock):
        configService = Config("/fake/path")
        settings = configService.getConfig()

        targetSettings = {
            'mysql': {
                'image': 'fake/image',
                'command': 'facke command'
            }
        }

        self.assertEqual(settings, targetSettings)

        configService = Config()
        settings = configService.getConfig()
        self.assertEqual(settings, targetSettings)

