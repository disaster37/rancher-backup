__author__ = 'disaster'

import cattle
import logging
from fr.webcenter.backup.Singleton import Singleton

logger = logging
class Rancher(object):
    """
    This class provide helper for Rancher API.
    """

    __metaclass__ = Singleton

    def __init__(self, url=None, key=None, secret=None):
        """
        Init the connexion on Rancher API
        :param url: the Rancher URL to access on API
        :param key: The rancher key to access on API
        :param secret: The Rancher secret to access on API
        :type url: str
        :type key: str
        :type secret: str
        """

        logger.debug("url: %s", url)
        logger.debug("key: %s", key)
        logger.debug("secret: xxxx")

        self._client = cattle.Client(url=url, access_key=key, secret_key=secret)


    def getServices(self):
        """
        Get all services and many information associatied to them (stacks, instances and hosts)
        :return list The list of services
        """

        listServices = self._client.list('service')

        # We keep only enable services and services that have not 'backup.disable' label set to true
        targetListServices = []
        for service in listServices:
            if service["type"] == "service" and "imageUuid" in service['launchConfig'] and  service["state"] == "active" and ("labels" not in service['launchConfig'] or ("backup.disable" not in service['launchConfig']['labels'] or service['launchConfig']['labels']['backup.disable'] == "false")):

                logger.debug("Found service %s", service["name"])

                # We add the stack associated to it
                if 'stack' in service['links']:
                    service['stack'] = self._client._get(service['links']['stack'])
                    logger.debug("Service %s is on stack %s", service["name"], service['stack']['name'])
                else:
                    logger.debug("No stack for service %s", service["name"])


                # We add the instances
                if 'instances' in service['links']:
                    service['instances'] = self._client._get(service['links']['instances'])
                    for instance in service['instances']:
                        hosts = self._client._get(instance['links']['hosts'])
                        if isinstance(hosts, list):
                            instance['host'] = hosts[0]
                        else:
                            instance['host'] = None
                            logger.debug("No host associated to instance %s", instance["name"])
                            

                    logger.debug("Service %s have %d intances", service["name"], len(service['instances']))
                else:
                    logger.debug("No instance for service %s", service["name"])


                targetListServices.append(service)


        return targetListServices


    def getStacks(self):
        """
        Permit to get all stack on Rancher environment
        :return list: the list of Rancher stack
        """

        listStacks = self._client.list('stack')
        targetListStacks = []
        for stack in listStacks:
            if stack['type'] == 'stack':
                logger.debug("Grab setting for stack %s", stack['name'])
                stack['settings'] = self._client.action(stack, 'exportconfig')
                targetListStacks.append(stack)
            else:
                logger.info("Skip Grab setting for stack %s because it's %s type", stack['name'], stack['type'])


        logger.debug("Return: %s", targetListStacks)

        return targetListStacks


    def getDatabaseSettings(self):
        """
        Permit to get the Rancher database settings to perform backup on it
        :return dict: the database settings to connect on it
        """

        listSettings = self._client.list('setting')
        listTargetSettings = {}

        for setting in listSettings:
            if setting["name"] == "cattle.db.cattle.database":
                listTargetSettings["type"] = setting["activeValue"]
            elif setting["name"] == "cattle.db.cattle.mysql.host":
                listTargetSettings["host"] = setting["activeValue"]
            elif setting["name"] == "cattle.db.cattle.mysql.name":
                listTargetSettings["db"] = setting["activeValue"]
            elif setting["name"] == "cattle.db.cattle.mysql.port":
                listTargetSettings["port"] = setting["activeValue"]
            elif setting["name"] == "cattle.db.cattle.password":
                listTargetSettings["password"] = setting["activeValue"]
            elif setting["name"] == "cattle.db.cattle.username":
                listTargetSettings["user"] = setting["activeValue"]

        return listTargetSettings





