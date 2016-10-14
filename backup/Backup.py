from fr.webcenter.backup.Backup import Backup
from fr.webcenter.backup.Config import Config
from fr.webcenter.backup.Service import Service
from fr.webcenter.backup.Client import Client
import os

if __name__ == '__main__':

    # Init client
    Client()
    Config("config/*.yml")
    backupPath = os.getenv('BACKUP_DIR', "/backup")

    service = Service()
    listServices = service.getServices()
    listSettings = Config.getConfig()

    # We search the container that I can dump before save it
    backup = Backup()
    listDump = backup.searchDump(listServices, listSettings)
    backup.runDump(listDump)

