__author__ = 'disaster'

import re
import logging
from fr.webcenter.backup.Command import Command
from fr.webcenter.backup.Singleton import Singleton

logger = logging
class Backup(object):
    """
    This class permit to drive dump and backup on remote target
    """

    __metaclass__ = Singleton

    def searchDump(self, backupPath, listServices, listSettings):
        """
        This class search service where to perform a dump before to backup them
        :param backupPath: The path where to store the dump
        :param listServices: The list of all services provider by Rancher API
        :param listSettings: The list of settings to identify the service where perform dump and command line to do that.
        :type backupPath: str
        :type listServices: list
        :type listSettings: dict
        :return dict The list of service where to perform dump and docker command line associated to them.
        """

        if backupPath is None or backupPath == "":
            raise KeyError("backupPath must be provided")
        if isinstance(listServices, list) is False:
            raise KeyError("listServices must be a dict")
        if isinstance(listSettings, dict) is False:
            raise KeyError("listSettings must be a dict")

        logger.debug("backupPath: %s", backupPath)
        logger.debug("listServices: %s", listServices)
        logger.debug("listSettings: %s", listSettings)

        listDump = []

        for service in listServices:
            for name, setting in listSettings.iteritems():
                if re.search(setting['regex'], service['launchConfig']['imageUuid']):

                    logger.info("Found '%s/%s' to do dumping" % (service['stack']['name'], service['name']))

                    #Replace macro ip
                    command = setting['command']
                    if 'environment' in setting:
                        environments = setting['environment']
                    else:
                        environments = []
                    ip = None
                    for instance in service['instances']:
                        if instance['state'] == "running":
                            ip = instance['primaryIpAddress']
                            logger.debug("Found IP %s", ip)
                            break
                    command = self._replaceMacro('%ip%', ip, command)
                    environments = self._replaceMacro("%ip", ip, environments)

                    # Replace target_dir macro
                    target_dir = backupPath + "/" + service['stack']['name'] + "/" + service['name']
                    command = self._replaceMacro('%target_dir%', target_dir, command)
                    environments = self._replaceMacro("%target_dir", target_dir, environments)

                    # Replace environment macro
                    for envKey, envValue in service['launchConfig']['environment'].iteritems():
                        command = self._replaceMacro("%env_" + envKey + "%", envValue, command)
                        environments = self._replaceMacro("%env_" + envKey + "%", envValue, environments)

                    dump = {}
                    dump['service'] = service
                    dump['target_dir'] = target_dir
                    dump['command'] = command
                    dump["environments"] = environments
                    if "image" in setting:
                        dump['image'] = setting['image']
                    else:
                        dump['image'] = service['launchConfig']['imageUuid']




                    listDump.append(dump)
                    break

        logger.debug(listDump)

        return listDump


    def runDump(self, listDump):
        """
        Permit to perform dump on each services
        :param listDump: The list of service where to perform the dump
        :type listDump: list
        """

        if isinstance(listDump, list) is False:
            raise KeyError("listDump must be a dict")

        logger.debug("listDump: %s", listDump)

        commandService = Command()


        for dump in listDump:
            logger.info("Dumping %s/%s in %s" % (dump['service']['stack']['name'], dump['service']['name'], dump['target_dir']))
            environments = ""
            for env in dump['environments']:
                environments += " -e '%s'" % env.replace(':', '=')
            dockerCmd = "docker run --rm -v %s:%s %s %s %s" % (dump['target_dir'], dump['target_dir'], environments, dump['image'], dump['command'])
            commandService.runCmd("docker pull %s" % dump['image'])

            commandService.runCmd(dockerCmd)
            logger.info("Dump %s/%s is finished" % (dump['service']['stack']['name'], dump['service']['name']))



    def initDuplicity(self, backupPath, backend):
        """
        Permit to init Duplicity with the target
        :param backupPath: the path where dump is stored
        :param backend: the full URL of remote target where to store backup
        :type backupPath: str
        :type backend: str
        """

        if backupPath is None or backupPath == "":
            raise KeyError("backupPath must be provided")
        if backend is None or backend == "":
            raise KeyError("backend must be provided")

        logger.debug("backupPath: %s", backupPath)
        logger.debug("backend: %s", backend)

        commandService = Command()

        result = commandService.runCmd("duplicity --no-encryption %s %s" % (backend, backupPath))
        logger.info(result)



    def runDuplicity(self, backupPath, backend, fullBackupFrequency, fullBackupKeep, incrementalBackupChainKeep, volumeSize):
        """
        Permit to backup the dump on remote target
        :param backupPath: the path where dump is stored
        :param backend: the full URL of remote target where to store backup
        :param fullBackupFrequency: when run full backup
        :param fullBackupKeep: how many full backup to keep
        :param incrementalBackupChainKeep: how many incremental backup chain to keep
        :param volumeSize: how many size for each volume
        :type backupPath: str
        :type backend: str
        :type fullBackupFrequency: str
        :type incrementalBackupChainKeep: str
        :type volumeSize: str
        """

        if backupPath is None or backupPath == "":
            raise KeyError("backupPath must be provided")
        if backend is None or backend == "":
            raise KeyError("backend must be provided")
        if fullBackupFrequency is None or fullBackupFrequency == "":
            raise KeyError("fullBackupFrequency  must be provided")
        if fullBackupKeep is None or fullBackupKeep == "":
            raise KeyError("fullBackupKeep must be provided")
        if incrementalBackupChainKeep is None or incrementalBackupChainKeep == "":
            raise KeyError("incrementalBackupChainKeep must be provided")
        if volumeSize is None or volumeSize == "":
            raise KeyError("volumeSize must be provided")

        logger.debug("backupPath: %s", backupPath)
        logger.debug("backend: %s", backend)
        logger.debug("fullBackupFrequency: %s", fullBackupFrequency)
        logger.debug("fullBackupKeep: %s", fullBackupKeep)
        logger.debug("incrementalBackupChainKeep: %s", incrementalBackupChainKeep)
        logger.debug("volumeSize: %s", volumeSize)

        commandService = Command()

        logger.info("Start backup")
        result = commandService.runCmd("duplicity --volsize %s --no-encryption --allow-source-mismatch --full-if-older-than %s %s %s" % (volumeSize, fullBackupFrequency, backupPath, backend))
        logger.info(result)

        logger.info("Clean old full backup is needed")
        result = commandService.runCmd("duplicity remove-all-but-n-full %s --force --allow-source-mismatch --no-encryption %s" % (fullBackupKeep, backend))
        logger.info(result)

        logger.info("Clean old incremental backup if needed")
        result = commandService.runCmd("duplicity remove-all-inc-of-but-n-full %s --force --allow-source-mismatch --no-encryption %s" % (incrementalBackupChainKeep, backend))
        logger.info(result)

        logger.info("Cleanup backup")
        result = commandService.runCmd("duplicity  cleanup --force --no-encryption %s" % (backend))
        logger.info(result)


    def _replaceMacro(self, macro, value, data):
        """
        Permit to replace macro by value on data.
        :param macro: the macro to replace
        :param value: the value to replace macro
        :param data: search macro on it
        :type macro: str
        :type value: str
        :type data: str or list
        :return str or list the data with value
        """

        if macro is None or macro == "":
            raise KeyError("Macro must be provided")
        if value is None:
            raise KeyError("Value must be provided")
        if data is None:
            raise KeyError("Data must be provided")

        logger.debug("macro: %s", macro)
        logger.debug("value: %s", value)
        logger.debug("data: %s", data)

        if isinstance(data, basestring):
            data = data.replace(macro, value)

        elif isinstance(data, list):
            for index in range(len(data)):
                data[index] = data[index].replace(macro, value)
        else:
            raise KeyError("Data must be str or list")

        return data
