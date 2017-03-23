__author__ = 'disaster'

import os
import sys
from fr.webcenter.backup.Backup import Backup
from fr.webcenter.backup.Rancher import Rancher
from fr.webcenter.backup.Config import Config
import logging
from logging.handlers import TimedRotatingFileHandler
import traceback




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
    settings = configService.getSettings()
    if 'module' not in settings:
        logger.error("You must provide module section on your config file")
        sys.exit(1)
    if 'databases' not in settings['module'] or isinstance(settings['module']['databases'], bool) is False:
        logger.error("module.databases must be provided")
        sys.exit(1)
    if 'stack' not in settings['module'] or isinstance(settings['module']['stack'], bool) is False:
        logger.error("module.stack must be provided")
        sys.exit(1)
    if 'rancher-db' not in settings['module'] or isinstance(settings['module']['rancher-db'], bool) is False:
        logger.error("module.rancher-db must be provided")
        sys.exit(1)
    if settings['module']['databases'] is True or settings['module']['stack'] is True or settings['module']['rancher-db'] is True:
        if 'rancher' not in settings:
            logger.error("You must provide rancher section on your config file")
            sys.exit(1)
        if 'api' not in settings['rancher']:
            logger.error("You must provide rancher.api section on your config file")
            sys.exit(1)
        if 'url' not in settings['rancher']['api'] or settings['rancher']['api']['url'] is None or settings['rancher']['api']['url'] == "":
            logger.error("rancher.api.url must be provided")
            sys.exit(1)
        if 'key' not in settings['rancher']['api'] or settings['rancher']['api']['key'] is None or settings['rancher']['api']['key'] == "":
            logger.error("rancher.api.key must be provided")
            sys.exit(1)
        if 'secret' not in settings['rancher']['api'] or settings['rancher']['api']['secret'] is None or settings['rancher']['api']['secret'] == "":
            logger.error("rancher.api.secret must be provided")
            sys.exit(1)
    
    if 'duplicity' not in settings:
        logger.error("You must provide duplicity section on your config file")
        sys.exit(1)
    if 'source-path' not in settings['duplicity'] or settings['duplicity']['source-path'] is None or settings['duplicity']['source-path'] == "":
        logger.error("duplicity.source-path must be provided")
        sys.exit(1)
    if 'target-path' not in settings['duplicity'] or settings['duplicity']['target-path'] is None or settings['duplicity']['target-path'] == "":
        logger.error("duplicity.target-path must be provided")
        sys.exit(1)
    if 'url' not in settings['duplicity'] or settings['duplicity']['url'] is None or settings['duplicity']['url'] == "":
        logger.error("duplicity.url must be provided")
        sys.exit(1)
    if 'full-if-older-than' not in settings['duplicity'] or settings['duplicity']['full-if-older-than'] is None or settings['duplicity']['full-if-older-than'] == "":
        logger.error("duplicity.full-if-older-than must be provided")
        sys.exit(1)
    if 'remove-all-but-n-full' not in settings['duplicity'] or isinstance(settings['duplicity']['remove-all-but-n-full'], int) is False:
        logger.error("duplicity.remove-all-but-n-full must be provided")
        sys.exit(1)
    if 'remove-all-inc-of-but-n-full' not in settings['duplicity'] or isinstance(settings['duplicity']['remove-all-inc-of-but-n-full'], int) is False:
        logger.error("duplicity.remove-all-inc-of-but-n-full must be provided")
        sys.exit(1)
    if 'volsize' not in settings['duplicity'] or isinstance(settings['duplicity']['volsize'], int) is False :
        logger.error("duplicity.volsize must be provided")
        sys.exit(1)



    logger.info("Rancher URL: %s", settings['rancher']['api']['url'])
    logger.info("Rancher key: %s", settings['rancher']['api']['key'])
    logger.info("Rancher secret: XXXX")
    logger.info("Backup path: %s", settings['duplicity']['source-path'])
    logger.info("Backup target path: %s", settings['duplicity']['target-path'])
    logger.info("Backend to receive remote backup: %s", settings['duplicity']['url'])
    logger.info("Backup full frequency: %s", settings['duplicity']['full-if-older-than'])
    logger.info("Backup full to keep: %s", settings['duplicity']['remove-all-but-n-full'])
    logger.info("Backup incremental chain to keep: %s", BK_KEEP_FULL_CHAIN)
    logger.info("Volume size: %s", settings['duplicity']['volsize'])

    # Init services
    try:
        rancherService = Rancher(settings['rancher']['api']['url'], settings['rancher']['api']['key'], settings['rancher']['api']['secret'])
    except Exception as e:
        logger.error("Can't connect to rancher API : %s", e.message)
        logger.error(traceback.format_exc())
        sys.exit(1)

    # Check if all parameter to backup rancher database if needed
    if settings['module']['rancher-db'] is True:
        rancherDatabaseSettings = rancherService.getDatabaseSettings()
        if 'host' not in rancherDatabaseSettings or 'db' not in rancherDatabaseSettings or 'port' not in rancherDatabaseSettings or 'password' not in rancherDatabaseSettings or 'user' not in rancherDatabaseSettings:
            logger.info("Can't grab Rancher database settings from API, try to grab it from config file")
            rancherDatabaseSettings = {
                'type': 'mysql'
            }
            if 'db' not in settings['rancher']:
                logger.error("You must provide rancher.db section on your config file")
                sys.exit(1)
            if 'host' not in settings['rancher']['db'] or settings['rancher']['db']['host'] is None or settings['rancher']['db']['host'] == "":
                logger.error("rancher.db.host must be provided")
                sys.exit(1)
            else:
                rancherDatabaseSettings['host'] = settings['rancher']['db']['host']
            if 'user' not in settings['rancher']['db'] or settings['rancher']['db']['user'] is None or settings['rancher']['db']['user'] == "":
                logger.error("rancher.db.user must be provided")
                sys.exit(1)
            else:
                rancherDatabaseSettings['user'] = settings['rancher']['db']['user']
            if 'password' not in settings['rancher']['db'] or settings['rancher']['db']['password'] is None or settings['rancher']['db']['password'] == "":
                logger.error("rancher.db.password must be provided")
                sys.exit(1)
            else:
                rancherDatabaseSettings['password'] = settings['rancher']['db']['password']
            if 'name' not in settings['rancher']['db'] or settings['rancher']['db']['name'] is None or settings['rancher']['db']['name'] == "":
                logger.error("rancher.db.name must be provided")
                sys.exit(1)
            else:
                rancherDatabaseSettings['name'] = settings['rancher']['db']['name']
            if 'port' not in settings['rancher']['db'] or isinstance(settings['rancher']['db']['port'], int) is False:
                logger.error("rancher.db.port must be provided")
                sys.exit(1)
            else:
                rancherDatabaseSettings['port'] = settings['rancher']['db']['port']

    backupService = Backup()
    backend = "%s%s" % (settings['duplicity']['url'], settings['duplicity']['target-path'])

    try:

        # We init duplicity
        try:
            backupService.initDuplicity(settings['duplicity']['source-path'], backend)
        except Exception as e:
            logger.info("No backup found (probably the first) or already initialized")
            pass


        # We dump the databases services if needed
        if settings['module']['databases'] is True:
            listServices = rancherService.getServices()
            listDump = backupService.searchDump(settings['duplicity']['source-path'], listServices)
            backupService.runDump(listDump)

        # We dump the rancher stack settings if needed
        if settings['module']['stack'] is True:
            listStacks = rancherService.getStacks()
            backupService.dumpStacksSettings(settings['duplicity']['source-path'] + '/rancher', listStacks)
           
        
        # We dump the rancher database if needed
        if settings['module']['rancher-db'] is True:
            backupService.dumpRancherDatabase(settings['duplicity']['source-path'] + '/rancher', rancherDatabaseSettings)

        # We run the backup
        backupService.runDuplicity(settings['duplicity']['source-path'], backend, settings['duplicity']['full-if-older-than'], settings['duplicity']['remove-all-but-n-full'], settings['duplicity']['remove-all-inc-of-but-n-full'], settings['duplicity']['volsize'], settings['duplicity']['options'])


    except Exception as e:
        logger.error("Unattented error occur : %s", e.message)
        logger.error(traceback.format_exc())
        sys.exit(1)
