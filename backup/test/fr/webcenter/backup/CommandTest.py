__author__ = 'disaster'

import unittest
import mock

import subprocess

from fr.webcenter.backup.Command import Command


class CommandTest(unittest.TestCase):

    @mock.patch.object(subprocess, 'Popen', autospec=True)
    def testRunCmd(self, mock_popen):

        commandService = Command()

        # When no error
        mock_popen.return_value.returncode = 0
        mock_popen.return_value.communicate.return_value = ("output", None)
        result = commandService.runCmd("fake cmd")
        self.assertEqual("output", result)

        # With error
        mock_popen.return_value.returncode = 0
        mock_popen.return_value.communicate.return_value = ("output", "Error")
        self.assertEqual("output", result)

        # With bad return code
        mock_popen.return_value.returncode = 1
        mock_popen.return_value.communicate.return_value = ("output", None)
        self.assertRaises(Exception, commandService.runCmd, "fake cmd")
        
if __name__ == '__main__':
    unittest.main()