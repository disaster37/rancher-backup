__author__ = 'disaster'

import re
import logging
import os
from fr.webcenter.backup.Command import Command
from fr.webcenter.backup.Singleton import Singleton
from fr.webcenter.backup.Config import Config
from jinja2 import Environment
import yaml


logger = logging
class Backup(object):
    """
    This class permit to drive dump and backup on remote target
    """

    __metaclass__ = Singleton

    def searchDump(self, backupPath, listServices):
        """
        This class search service where to perform a dump before to backup them and grab all setting to perform backup
        :param backupPath: The path where to store the dump
        :param listServices: The list of all services provider by Rancher API
        :type backupPath: str
        :type listServices: list
        :return dict The list of service where to perform dump and docker command line associated to them.
        """

        if backupPath is None or backupPath == "":
            raise KeyError("backupPath must be provided")
        if isinstance(listServices, list) is False:
            raise KeyError("listServices must be a list")


        logger.debug("backupPath: %s", backupPath)
        logger.debug("listServices: %s", listServices)

        configService = Config()
        index = configService.getIndex()

        listDump = []

        for service in listServices:
            for name, setting in index.iteritems():
                # First search on label and then search on image name
                if ('labels' in service['launchConfig'] and 'backup.type' in service['launchConfig']['labels'] and re.search(setting['regex'], service['launchConfig']['labels']['backup.type'])) or re.search(setting['regex'], service['launchConfig']['imageUuid']):
                    
                    try:

                        logger.info("Found '%s/%s' to do dumping" % (service['stack']['name'], service['name']))
                        template = configService.getTemplate(setting['template'])
    
                        env = Environment()
                        template = env.from_string(template)
                        context = {}
    
                        # Get environment variables
                        if 'environment' in service['launchConfig']:
                            context["env"] = service['launchConfig']['environment']
                        else:
                            context["env"] = {}
    
                        # Get IP
                        for instance in service['instances']:
                            if instance['state'] == "running":
                                context["ip"] = instance['primaryIpAddress']
                                logger.debug("Found IP %s", context["ip"])
                                break
    
                        # Get Taget backup
                        context["target_dir"] = backupPath + "/" + service['stack']['name'] + "/" + service['name']
    
                        setting = yaml.load(template.render(context))
    
                        setting["service"] = service
                        setting["target_dir"] = context["target_dir"]
                        if "environments" not in setting or not setting["environments"]:
                            setting["environments"] = []
                        if "image" not in setting:
                            setting["image"] = service['launchConfig']['imageUuid']
    
                        listDump.append(setting)
                        break
                    
                    except Excexption as e:
                        logger.error("Error appear when extract infos from Rancher API about '%s/%s', skip : %s" % (service['stack']['name'], service['name'], e.message))
                        # Don't beack backup if somethink wrong
                        pass

        logger.debug(listDump)

        return listDump


    def runDump(self, listDump):
        """
        Permit to perform dump on each services with Docker command
        :param listDump: The list of service where to perform the dump
        :type listDump: list
        """

        if isinstance(listDump, list) is False:
            raise KeyError("listDump must be a list")

        logger.debug("listDump: %s", listDump)

        commandService = Command()


        for dump in listDump:
            
            try:
                logger.info("Dumping %s/%s in %s" % (dump['service']['stack']['name'], dump['service']['name'], dump['target_dir']))
                environments = ""
                for env in dump['environments']:
                    environments += " -e '%s'" % env.replace(':', '=', 1)
    
    
                if 'entrypoint' in dump:
                    entrypoint = "--entrypoint='%s'" % dump['entrypoint']
                else:
                    entrypoint = ''
    
                # Check if folder to receive dump exist, else create it
                if os.path.isdir(dump['target_dir']) is False:
                    os.makedirs(dump['target_dir'])
                    logger.debug("Create directory '%s'", dump['target_dir'])
                else:
                    logger.debug("Directory '%s' already exist", dump['target_dir'])
    
                commandService.runCmd("docker pull %s" % dump['image'])
    
                for command in dump['commands']:
                    dockerCmd = "docker run --rm %s -v %s:%s %s %s %s" % (entrypoint, dump['target_dir'], dump['target_dir'], environments, dump['image'], command)
                    commandService.runCmd(dockerCmd)
                logger.info("Dump %s/%s is finished" % (dump['service']['stack']['name'], dump['service']['name']))
            
            except Exception as e:
                logger.error("Error appear when dump '%s/%s', skip : %s" % (dump['service']['stack']['name'], dump['service']['name'], e.message))
                # Don't beack backup if somethink wrong
                pass


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



    def runDuplicity(self, backupPath, backend, fullBackupFrequency, fullBackupKeep, incrementalBackupChainKeep, volumeSize, options=None, encryptKey=None):
        """
        Permit to backup the dump on remote target
        :param backupPath: the path where dump is stored
        :param backend: the full URL of remote target where to store backup
        :param fullBackupFrequency: when run full backup
        :param fullBackupKeep: how many full backup to keep
        :param incrementalBackupChainKeep: how many incremental backup chain to keep
        :param volumeSize: how many size for each volume
        :param options: set some duplicity options
        :param encryptKey: The GPG key if you should crypt backup
        :type backupPath: str
        :type backend: str
        :type fullBackupFrequency: str
        :type incrementalBackupChainKeep: str
        :type volumeSize: str
        :type options: str
        :type encryptKey: str
        """

        if backupPath is None or backupPath == "":
            raise KeyError("backupPath must be provided")
        if backend is None or backend == "":
            raise KeyError("backend must be provided")
        if fullBackupFrequency is None or fullBackupFrequency == "":
            raise KeyError("fullBackupFrequency  must be provided")
        if isinstance(fullBackupKeep, int) is False:
            raise KeyError("fullBackupKeep must be provided")
        if isinstance(incrementalBackupChainKeep, int) is False:
            raise KeyError("incrementalBackupChainKeep must be provided")
        if isinstance(volumeSize, int) is False:
            raise KeyError("volumeSize must be provided")
        if options is None:
            options = ""
        if options is not None and isinstance(options, basestring) is False:
            raise KeyError("options must be a None or string")
        if encryptKey is not None and isinstance(encryptKey, basestring) is False:
            raise KeyError("encryptKey must be a None or string")

        logger.debug("backupPath: %s", backupPath)
        logger.debug("backend: %s", backend)
        logger.debug("fullBackupFrequency: %s", fullBackupFrequency)
        logger.debug("fullBackupKeep: %s", fullBackupKeep)
        logger.debug("incrementalBackupChainKeep: %s", incrementalBackupChainKeep)
        logger.debug("volumeSize: %s", volumeSize)
        logger.debug("options: %s", options)
        logger.debug("encryptKey: %s", encryptKey)
        
        if encryptKey is None or encryptKey == "":
            crypt = "--no-encryption"
        else:
            crypt = "--encrypt-key %s" % encryptKey
        

        commandService = Command()

        logger.info("Start backup")
        result = commandService.runCmd("duplicity %s --volsize %s %s --allow-source-mismatch --full-if-older-than %s %s %s" % (options, volumeSize, crypt, fullBackupFrequency, backupPath, backend))
        logger.info(result)

        logger.info("Clean old full backup is needed")
        result = commandService.runCmd("duplicity remove-all-but-n-full %s --force --allow-source-mismatch %s %s" % (fullBackupKeep, crypt, backend))
        logger.info(result)

        logger.info("Clean old incremental backup if needed")
        result = commandService.runCmd("duplicity remove-all-inc-of-but-n-full %s --force --allow-source-mismatch %s %s" % (incrementalBackupChainKeep, crypt,  backend))
        logger.info(result)

        logger.info("Cleanup backup")
        result = commandService.runCmd("duplicity  cleanup --force %s %s" % (crypt, backend))
        logger.info(result)


    def dumpStacksSettings(self,backupPath, listEnvironments):
        """
        Permit to write the stack setting in docker-compose file and rancher-compose file.
        :param backupPath: the backup path where store the stack setting extraction
        :param listEnvironments: the list of stack
        :type backupPath: str
        :type listEnvironments: list
        """

        if backupPath is None or backupPath == "":
            raise KeyError("backupPath must be provided")
        if isinstance(listEnvironments, list) is False:
            raise KeyError("listEnvironments must be provided")

        for environment in listEnvironments:
            
            try:

                targetDir = "%s/%s" % (backupPath, environment['name'])
                logger.info("Save the Rancher setting for stack %s in %s", environment['name'], targetDir)
    
                if os.path.isdir(targetDir) is False:
                    os.makedirs(targetDir)
                    logger.debug("Create directory '%s'", targetDir)
                else:
                    logger.debug("Directory '%s' already exist", targetDir)
    
                # Save docker-compose
                fp = open(targetDir + '/docker-compose.yml', 'w')
                fp.write(environment['settings']['dockerComposeConfig'])
                fp.close()
    
                # Save rancher-compose
                fp = open(targetDir + '/rancher-compose.yml', 'w')
                fp.write(environment['settings']['rancherComposeConfig'])
                fp.close()
                
            except Exception as e:
                logger.error("Error appear when save setting for stack '%s', skip : %s" % (environment['name'], e.message))
                pass


    def dumpRancherDatabase(self, backupPath, listDatabaseSettings):
        """
        Permit to dump Rancher database
        :param backupPath: the backup path where store the database dump
        :param listDatabaseSettings: the database parameters to connect on it
        :type backupPath: basestring
        :type listDatabaseSettings: dict
        """

        if backupPath is None or backupPath == "":
            raise KeyError("backupPath must be provided")
        if isinstance(listDatabaseSettings, dict) is False:
            raise KeyError("listDatabaseSettings must be provided")

        if "type" not in listDatabaseSettings:
            raise KeyError("You must provide the database type")
        if "host" not in listDatabaseSettings:
            raise KeyError("You must provide the database host")
        if "port" not in listDatabaseSettings:
            raise KeyError("You must provide the database port")
        if "user" not in listDatabaseSettings:
            raise KeyError("You must provide the database user")
        if "password" not in listDatabaseSettings:
            raise KeyError("You must provide the database password")
        if "name" not in listDatabaseSettings:
            raise KeyError("You must provide the database name")

        commandService = Command()
        target_dir = "%s/database" % (backupPath)
        image = "mysql:latest"
        logger.info("Dumping the Rancher database '%s' in '%s'", listDatabaseSettings['name'], target_dir)

        if os.path.isdir(target_dir) is False:
            os.makedirs(target_dir)
            logger.debug("Create directory '%s'", target_dir)
        else:
            logger.debug("Directory '%s' already exist", target_dir)

        commandService.runCmd("docker pull %s" % image)
        command = "sh -c 'mysqldump -h %s -P %s -u %s %s > %s/%s.dump'" % (listDatabaseSettings['host'], listDatabaseSettings['port'], listDatabaseSettings['user'], listDatabaseSettings['name'], target_dir, listDatabaseSettings['name'])
        dockerCmd = "docker run --rm -v %s:%s -e 'MYSQL_PWD=%s' %s %s" % (target_dir, target_dir, listDatabaseSettings['password'], image, command)
        commandService.runCmd(dockerCmd)
        logger.info("Dump Rancher database is finished")








