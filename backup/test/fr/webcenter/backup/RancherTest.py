__author__ = 'disaster'

import unittest
import mock
from cattle import Client
from fr.webcenter.backup.Rancher import Rancher

def fakeCallApiList(section):

    if section == "service":

        service = {}
        service['name'] = "test"
        service["state"] = "active"
        service['launchConfig'] = {}
        service['launchConfig']['imageUuid'] = "test/postgres:latest"
        service['launchConfig']['environment'] = {
            'POSTGRES_USER': 'user',
            'POSTGRES_DB': 'test',
            'PGPASSWORD': 'pass'
        }
        service['links'] = {}
        service['links']['environment'] = 'https://fake/environment'
        service['links']['instances'] = 'https://fake/instances'

        return [service]

    else:
        return None

def fakeCallApiGet(url):
    if url == "https://fake/environment":
        environment = {}
        environment['name'] = 'stack-test'
        return environment

    if url == "https://fake/hosts":
        host = {}
        host['name'] = "host-1"
        host2 = {}
        host2['name'] = "host-2"

        return [host, host2]

    if url == 'https://fake/instances':
        instance = {}
        instance['state'] = "disabled"
        instance['primaryIpAddress'] = '10.0.0.1'
        instance['links'] = {
            'hosts': 'https://fake/hosts'
        }

        instance2 = {}
        instance2['state'] = "running"
        instance2['primaryIpAddress'] = '10.0.0.2'
        instance2['links'] = {
            'hosts': 'https://fake/hosts'
        }

        instance3 = {}
        instance3['state'] = "running"
        instance3['primaryIpAddress'] = '10.0.0.3'
        instance3['links'] = {
            'hosts': 'https://fake/hosts'
        }

        return [instance, instance2, instance3]

def fakeClient(url, access_key, secret_key):
    return  None


class RancherTest(unittest.TestCase):


    @mock.patch.object(Client, 'list', side_effect=fakeCallApiList)
    @mock.patch.object(Client, '_get', side_effect=fakeCallApiGet)
    @mock.patch.object(Client, '__init__', side_effect=fakeClient)
    def testGetServices(self, mock_run, mock_run2, mock_run4):

        rancherService = Rancher("https://url", "key", "secret")
        listServices = rancherService.getServices()

        targetListServices = [
            {
                'name': 'test',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/postgres:latest',
                    'environment': {
                        'POSTGRES_USER': 'user',
                        'POSTGRES_DB': 'test',
                        'PGPASSWORD': 'pass'
                    }
                },
                'links': {
                    'environment': 'https://fake/environment',
                    'instances': 'https://fake/instances',
                },
                'stack': {
                    'name': 'stack-test'
                },
                'instances': [
                    {
                        'state': 'disabled',
                        'primaryIpAddress': '10.0.0.1',
                        'host': {
                            'name': 'host-1'
                        },
                        'links': {
                            'hosts': 'https://fake/hosts'
                        }
                    },
                    {
                        'state': 'running',
                        'primaryIpAddress': '10.0.0.2',
                        'host': {
                            'name': 'host-1'
                        },
                        'links': {
                            'hosts': 'https://fake/hosts'
                        }
                    },
                    {
                        'state': 'running',
                        'primaryIpAddress': '10.0.0.3',
                        'host': {
                            'name': 'host-1'
                        },
                        'links': {
                            'hosts': 'https://fake/hosts'
                        }
                    }

                ],
            }
        ]

        self.assertEquals(listServices, targetListServices)

        rancherService = Rancher()
        listServices = rancherService.getServices()
        self.assertEquals(listServices, targetListServices)