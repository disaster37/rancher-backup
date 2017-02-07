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

    BACKUP_PATH = '/backup'
    TARGET_PATH = os.getenv('TARGET_PATH', "/backup")
    BK_FULL_FREQ = os.getenv('BK_FULL_FREQ', "7D")
    BK_KEEP_FULL = os.getenv('BK_KEEP_FULL', "3")
    BK_KEEP_FULL_CHAIN = os.getenv('BK_KEEP_FULL_CHAIN', "1")
    VOLUME_SIZE = os.getenv('VOLUME_SIZE', "25")
    DISABLE_DUMP = os.getenv('DISABLE_DUMP', "false")
    DISABLE_DUMP_RANCHER = os.getenv('DISABLE_DUMP_RANCHER', "false")

    if os.getenv("CATTLE_URL") is None or os.getenv("CATTLE_URL") == "":
        logger.error("CATTLE_URL must be provided")
        sys.exit(1)
    if os.getenv("CATTLE_ACCESS_KEY") is None or os.getenv("CATTLE_ACCESS_KEY") == "":
        logger.error("CATTLE_ACCESS_KEY must be provided")
        sys.exit(1)
    if os.getenv("CATTLE_SECRET_KEY") is None or os.getenv("CATTLE_SECRET_KEY") == "":
        logger.error("CATTLE_SECRET_KEY must be provided")
        sys.exit(1)
    if BACKUP_PATH is None or BACKUP_PATH == "":
        logger.error("BACKUP_PATH must be provided")
        sys.exit(1)
    if TARGET_PATH is None or TARGET_PATH == "":
        logger.error("TARGET_PATH must be provided")
        sys.exit(1)
    if os.getenv('BACKEND') is None or os.getenv('BACKEND') == "":
        logger.error("BACKEND must be provided")
        sys.exit(1)
    if BK_FULL_FREQ is None or BK_FULL_FREQ == "":
        logger.error("BK_FULL_FREQ must be provided")
        sys.exit(1)
    if BK_KEEP_FULL is None or BK_KEEP_FULL == "":
        logger.error("BK_KEEP_FULL must be provided")
        sys.exit(1)
    if BK_KEEP_FULL_CHAIN is None or BK_KEEP_FULL_CHAIN == "":
        logger.error("BK_KEEP_FULL_CHAIN must be provided")
        sys.exit(1)
    if VOLUME_SIZE is None or VOLUME_SIZE == "":
        logger.error("VOLUME_SIZE must be provided")
        sys.exit(1)
    if DISABLE_DUMP is None or DISABLE_DUMP == "":
        logger.error("DISABLE_DUMP must be provided")
        sys.exit(1)
    if DISABLE_DUMP_RANCHER is None or DISABLE_DUMP_RANCHER == "":
        logger.error("DISABLE_DUMP_RANCHER must be provided")
        sys.exit(1)







    logger.info("Rancher URL: %s", os.getenv("RANCHER_API_URL"))
    logger.info("Rancher key: %s", os.getenv("RANCHER_API_KEY"))
    logger.info("Rancher secret: XXXX")
    logger.info("Backup path: %s", BACKUP_PATH)
    logger.info("Backup target path: %s", TARGET_PATH)
    logger.info("Backend to receive remote backup: %s", os.getenv('BACKEND'))
    logger.info("Backup full frequency: %s", BK_FULL_FREQ)
    logger.info("Backup full to keep: %s", BK_KEEP_FULL)
    logger.info("Backup incremental chain to keep: %s", BK_KEEP_FULL_CHAIN)
    logger.info("Volume size: %s", VOLUME_SIZE)

    # Init services
    try:
        rancherService = Rancher(os.getenv("RANCHER_API_URL"), os.getenv("RANCHER_API_KEY"), os.getenv("RANCHER_API_SECRET"))
    except Exception as e:
        logger.error("Can't connect to rancher API : %s", e.message)
        logger.error(traceback.format_exc())
        sys.exit(1)

    try:
        configService = Config("config/*.yml")
    except Exception as e:
        logger.error("Can't load settings or syntax errors : %s", e.message)
        logger.error(traceback.format_exc())
        sys.exit(1)

    backupService = Backup()
    backend = os.getenv('BACKEND') + TARGET_PATH

    try:

        # Load settings
        listSettings = configService.getConfig()


        # We init duplicity
        try:
            backupService.initDuplicity(BACKUP_PATH, backend)
        except Exception as e:
            logger.info("No backup found (probably the first) or already initialized")
            pass


        # We dump the container if needed
        # Get all services (potential dump)
        if DISABLE_DUMP != "true":
            listServices = rancherService.getServices()
            listDump = backupService.searchDump(BACKUP_PATH, listServices, listSettings)
            backupService.runDump(listDump)

        # We dump the rancher settings
        if DISABLE_DUMP_RANCHER != "true":
            listStacks = rancherService.getStacks()
            backupService.dumpStacksSettings(BACKUP_PATH + '/rancher', listStacks)

        # We run the backup
        backupService.runDuplicity(BACKUP_PATH, backend, BK_FULL_FREQ, BK_KEEP_FULL, BK_KEEP_FULL_CHAIN, VOLUME_SIZE)


    except Exception as e:
        logger.error("Unattented error occur : %s", e.message)
        logger.error(traceback.format_exc())
        sys.exit(1)
