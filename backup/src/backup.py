import os
import sys
from fr.webcenter.backup.Backup import Backup
from fr.webcenter.backup.Rancher import Rancher
from fr.webcenter.backup.Config import Config
import logging
import traceback




if __name__ == '__main__':

    # Init logger
    # We init logger
    if os.getenv('DEBUG') is not None and os.getenv('DEBUG') == "true":
        loglevel = logging.getLevelName("DEBUG")
    else:
        loglevel = logging.getLevelName("INFO")
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(loglevel)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    BACKUP_PATH = os.getenv('BACKUP_PATH', "/backup")
    TARGET_PATH = os.getenv('TARGET_PATH', "/backup")
    BK_FULL_FREQ = os.getenv('BK_FULL_FREQ', "7D")
    BK_KEEP_FULL = os.getenv('BK_KEEP_FULL', "3")
    BK_KEEP_FULL_CHAIN = os.getenv('BK_KEEP_FULL_CHAIN', "1")
    VOLUME_SIZE = os.getenv('VOLUME_SIZE', "25")

    if os.getenv("RANCHER_API_URL") is None or os.getenv("RANCHER_API_URL") == "":
        logger.error("RANCHER_API_URL must be provided")
        sys.exit(1)
    if os.getenv("RANCHER_API_KEY") is None or os.getenv("RANCHER_API_KEY") == "":
        logger.error("RANCHER_API_KEY must be provided")
        sys.exit(1)
    if os.getenv("RANCHER_API_SECRET") is None or os.getenv("RANCHER_API_SECRET") == "":
        logger.error("RANCHER_API_SECRET must be provided")
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

        # Get all services (potential dump)
        listServices = rancherService.getServices()

        # We init duplicity
        try:
            backupService.initDuplicity(BACKUP_PATH, backend)
        except Exception as e:
            logger.info("No backup found (probably the first)")
            pass


        # We dump the container if needed
        backupService = Backup()
        listDump = backupService.searchDump(BACKUP_PATH, listServices, listSettings)
        backupService.runDump(listDump)

        # We run the backup
        backupService.runDuplicity(BACKUP_PATH, backend, BK_FULL_FREQ, BK_KEEP_FULL, BK_KEEP_FULL_CHAIN, VOLUME_SIZE)


    except Exception as e:
        logger.error("Unattented error occur : %s", e.message)
        logger.error(traceback.format_exc())
        sys.exit(1)
