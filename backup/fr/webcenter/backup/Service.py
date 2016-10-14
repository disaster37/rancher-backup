from fr.webcenter.backup.Client import Client
from pprint import pprint


class Service(object):

    def __init__(self):

        self._client = Client.getClient()


    def getServices(self):

        listServices = self._client.list('service')

        # We keep only enable services and services that have not 'backup.disable' label set to true
        targetListServices = []
        for service in listServices:
            if service["state"] == "active" and ("backup.disable" not in service['launchConfig']['labels'] or service['launchConfig']['labels']['backup.disable'] == "false"):

                # We add the stack associated to it
                service['stack'] = self._client._get(service['links']['environment'])

                # We add the instances
                service['instances'] = self._client._get(service['links']['instances'])
                for instance in service['instances']:
                    instance['host'] = self._client._get(instance['links']['hosts'])[0]

                targetListServices.append(service)


        return targetListServices