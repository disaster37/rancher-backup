__author__ = 'disaster'

import os
import sys
from fr.webcenter.backup.Backup import Backup
from fr.webcenter.backup.Rancher import Rancher
from fr.webcenter.backup.Config import Config
import logging
from logging.handlers import TimedRotatingFileHandler
import traceback



def checkParameters(settings):
    """
    Permit to check all parameters
    :param settings: The list of settings
    :type settings: dict
    """
    
    if isinstance(settings, dict) is False:
        raise KeyError("Settings must be provided")
    
    if 'module' not in settings:
        raise KeyError("You must provide module section on your config file")
    if 'databases' not in settings['module'] or isinstance(settings['module']['databases'], bool) is False:
        raise KeyError("module.databases must be provided")
    if 'stack' not in settings['module'] or isinstance(settings['module']['stack'], bool) is False:
        raise KeyError("module.stack must be provided")
    if 'rancher-db' not in settings['module'] or isinstance(settings['module']['rancher-db'], bool) is False:
        raise KeyError("module.rancher-db must be provided")
    if settings['module']['databases'] is True or settings['module']['stack'] is True or settings['module']['rancher-db'] is True:
        if 'rancher' not in settings:
            raise KeyError("You must provide rancher section on your config file")
        if 'api' not in settings['rancher']:
            raise KeyError("You must provide rancher.api section on your config file")
        if 'url' not in settings['rancher']['api'] or settings['rancher']['api']['url'] is None or settings['rancher']['api']['url'] == "":
            raise KeyError("rancher.api.url must be provided")
        if 'key' not in settings['rancher']['api'] or settings['rancher']['api']['key'] is None or settings['rancher']['api']['key'] == "":
            raise KeyError("rancher.api.key must be provided")
        if 'secret' not in settings['rancher']['api'] or settings['rancher']['api']['secret'] is None or settings['rancher']['api']['secret'] == "":
            raise KeyError("rancher.api.secret must be provided")
    
    if 'duplicity' not in settings:
        raise KeyError("You must provide duplicity section on your config file")
    if 'source-path' not in settings['duplicity'] or settings['duplicity']['source-path'] is None or settings['duplicity']['source-path'] == "":
        raise KeyError("duplicity.source-path must be provided")
    if 'target-path' not in settings['duplicity'] or settings['duplicity']['target-path'] is None or settings['duplicity']['target-path'] == "":
        raise KeyError("duplicity.target-path must be provided")
    if 'url' not in settings['duplicity'] or settings['duplicity']['url'] is None or settings['duplicity']['url'] == "":
        raise KeyError("duplicity.url must be provided")
    if 'full-if-older-than' not in settings['duplicity'] or settings['duplicity']['full-if-older-than'] is None or settings['duplicity']['full-if-older-than'] == "":
        raise KeyError("duplicity.full-if-older-than must be provided")
    if 'remove-all-but-n-full' not in settings['duplicity'] or isinstance(settings['duplicity']['remove-all-but-n-full'], int) is False:
        raise KeyError("duplicity.remove-all-but-n-full must be provided")
    if 'remove-all-inc-of-but-n-full' not in settings['duplicity'] or isinstance(settings['duplicity']['remove-all-inc-of-but-n-full'], int) is False:
        raise KeyError("duplicity.remove-all-inc-of-but-n-full must be provided")
    if 'volsize' not in settings['duplicity'] or isinstance(settings['duplicity']['volsize'], int) is False :
        raise KeyError("duplicity.volsize must be provided")
        
def checkAndGetDatabaseSettings(settings, rancherDatabaseSettings):
    """
    Permit to check that all parameter is setted to dump Rancher database is needed
    :param settings: the settings provided by config file
    :param rancherDatabaseSettings: the settings provided by Rancher API
    :return dict: the database settings
    :type settings: dict
    :type rancherDatabaseSettings: dict
    """
    
    if isinstance(settings, dict) is False:
        raise KeyError("You must provide settings")
    if isinstance(rancherDatabaseSettings, dict) is False:
        raise KeyError("You must provide databaseSettings")
    
    
    if settings['module']['rancher-db'] is True:
        if 'host' not in rancherDatabaseSettings or 'db' not in rancherDatabaseSettings or 'port' not in rancherDatabaseSettings or 'password' not in rancherDatabaseSettings or 'user' not in rancherDatabaseSettings:
            logger.info("Can't grab Rancher database settings from API, try to grab it from config file")
            rancherDatabaseSettings = {
                'type': 'mysql'
            }
            if 'db' not in settings['rancher']:
                raise KeyError("You must provide rancher.db section on your config file")
            if 'host' not in settings['rancher']['db'] or settings['rancher']['db']['host'] is None or settings['rancher']['db']['host'] == "":
                raise KeyError("rancher.db.host must be provided")
            else:
                rancherDatabaseSettings['host'] = settings['rancher']['db']['host']
            if 'user' not in settings['rancher']['db'] or settings['rancher']['db']['user'] is None or settings['rancher']['db']['user'] == "":
                raise KeyError("rancher.db.user must be provided")
            else:
                rancherDatabaseSettings['user'] = settings['rancher']['db']['user']
            if 'password' not in settings['rancher']['db'] or settings['rancher']['db']['password'] is None or settings['rancher']['db']['password'] == "":
                raise KeyError("rancher.db.password must be provided")
            else:
                rancherDatabaseSettings['password'] = settings['rancher']['db']['password']
            if 'name' not in settings['rancher']['db'] or settings['rancher']['db']['name'] is None or settings['rancher']['db']['name'] == "":
                raise KeyError("rancher.db.name must be provided")
            else:
                rancherDatabaseSettings['name'] = settings['rancher']['db']['name']
            if 'port' not in settings['rancher']['db'] or isinstance(settings['rancher']['db']['port'], int) is False:
                raise KeyError("rancher.db.port must be provided")
            else:
                rancherDatabaseSettings['port'] = settings['rancher']['db']['port']
            
            return rancherDatabaseSettings
    else:
        return None
    
    
    
def getAndcheckAllParameters():
    configService = Config()
    settings = configService.getSettings()
    
    try:
        checkParameters(settings)
    except KeyError as e:
        raise Exception("Somthing wrong on your config file: %s" % e.message)

    
    logger.info("Rancher URL: %s", settings['rancher']['api']['url'][:-2] + "v2-beta")
    logger.info("Rancher key: %s", settings['rancher']['api']['key'])
    logger.info("Rancher secret: XXXX")
    logger.info("Backup path: %s", settings['duplicity']['source-path'])
    logger.info("Backup target path: %s", settings['duplicity']['target-path'])
    logger.info("Backend to receive remote backup: %s", settings['duplicity']['url'])
    logger.info("Backup full frequency: %s", settings['duplicity']['full-if-older-than'])
    logger.info("Backup full to keep: %s", settings['duplicity']['remove-all-but-n-full'])
    logger.info("Backup incremental chain to keep: %s", settings['duplicity']['remove-all-inc-of-but-n-full'])
    logger.info("Volume size: %s", settings['duplicity']['volsize'])
    logger.info("Backup options: %s", settings['duplicity']['options'])
    
    # Init services
    try:
        rancherService = Rancher(settings['rancher']['api']['url'][:-2] + "v2-beta", settings['rancher']['api']['key'], settings['rancher']['api']['secret'])
    except Exception as e:
        raise Exception("Can't connect to rancher API : %s \n%s" %  (e.message, traceback.format_exc()))
    
    try:
        rancherDatabaseSettings = rancherService.getDatabaseSettings()
    except Exception as e:
        rancherDatabaseSettings = {}
        pass
    
    # Check database settings
    try:
        rancherDatabaseSettings = checkAndGetDatabaseSettings(settings, rancherDatabaseSettings)
    except KeyError as e:
        raise Exception("You must set the Rancher database settings on config file to dump it: %s" % e.message)
    
    
    
    return (settings, rancherDatabaseSettings)
    


if __name__ == '__main__':
    # Init logger
    # We init logger
    if os.getenv('DEBUG') is not None and os.getenv('DEBUG') == "true":
        loglevel = logging.getLevelName("DEBUG")
    else:
        loglevel = logging.getLevelName("INFO")
    logger = logging.getLogger()
    logger.setLevel(loglevel)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(loglevel)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    file_handler = TimedRotatingFileHandler(
        '/var/log/backup/backup.log',
        when='d',
        interval=1,
        backupCount=5
    )
    file_handler.setLevel(loglevel)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Load and check settings
    configService = Config("config")
    
    # Just check parameters
    if len(sys.argv) > 1 and sys.argv[1] == "--checkParameters":
        
        try:
            getAndcheckAllParameters()
        except Exception as e:
            logger.error("Error - %s", e.message)
            sys.exit(1)
    
    # Run backup
    else:

        try:
            (settings, rancherDatabaseSettings) = getAndcheckAllParameters()
        except Exception as e:
            logger.error("Error - %s", e.message)
            sys.exit(1)

        backupService = Backup()
        rancherService = Rancher()
        backend = "%s%s" % (settings['duplicity']['url'], settings['duplicity']['target-path'])
    
        try:
            # We init duplicity
            try:
                logger.info("Start to initialize Duplicity...")
                backupService.initDuplicity(settings['duplicity']['source-path'], backend)
                logger.info("Duplicity initialization is finished.")
            except Exception as e:
                logger.info("No backup found (probably the first) or already initialized")
                pass
    
    
            # We dump the databases services if needed
            if settings['module']['databases'] is True:
                logger.info("Start to dump databases...")
                listServices = rancherService.getServices()
                listDump = backupService.searchDump(settings['duplicity']['source-path'] + '/dump', listServices)
                backupService.runDump(listDump)
                logger.info("The dumping databases is finished.")
    
            # We dump the rancher stack settings if needed
            if settings['module']['stack'] is True:
                logger.info("Start to export stack as json...")
                listStacks = rancherService.getStacks()
                backupService.dumpStacksSettings(settings['duplicity']['source-path'] + '/rancher', listStacks)
                logger.info("The exporting of stack if finished")
               
            
            # We dump the rancher database if needed
            if settings['module']['rancher-db'] is True:
                logger.info("Start to dump Rancher database...")
                backupService.dumpRancherDatabase(settings['duplicity']['source-path'] + '/rancher', rancherDatabaseSettings)
                logger.info("The Rancher database dumping is finished.")
    
            # We run the backup
            logger.info("Start to externalize the backup with Duplicity...")
            backupService.runDuplicity(settings['duplicity']['source-path'], backend, settings['duplicity']['full-if-older-than'], settings['duplicity']['remove-all-but-n-full'], settings['duplicity']['remove-all-inc-of-but-n-full'], settings['duplicity']['volsize'], settings['duplicity']['options'], settings['duplicity']['encrypt-key'])
            logger.info("The backup exporing is finished.")
    
    
        except Exception as e:
            logger.error("Unattented error occur : %s", e.message)
            logger.error(traceback.format_exc())
            sys.exit(1)
