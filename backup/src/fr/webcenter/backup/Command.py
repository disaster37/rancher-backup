__author__ = 'disaster'

import subprocess
import logging
from fr.webcenter.backup.Singleton import Singleton


logger = logging.getLogger(__name__)
class Command(object):
    """
    Class permit to lauch shell command and control the return code.
    """

    __metaclass__ = Singleton

    def runCmd(self, cmd):
        """
        Permit to run system command and get the result
        :type cmd: str
        :param cmd: the command to excute
        :return str: the answere when run the command
        """

        if cmd is None or cmd == "":
            raise KeyError("You must set cmd")

        logger.debug('Command to exec : %s', cmd)


        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        logger.debug("Results : %s", out)

        if err:
            raise Exception("Error when run cmd " + cmd + " : " + err)
        elif p.returncode != 0:
            raise Exception("Error when run cmd " + cmd + " : " + out)

        out = out.decode('utf-8')

        return out