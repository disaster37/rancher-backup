__author__ = 'disaster'

import unittest
import mock
from cattle import Client
from fr.webcenter.backup.Rancher import Rancher

def fakeCallApiList(section):

    if section == "service":

        service = {}
        service['type'] = "service"
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
        service['links']['stack'] = 'https://fake/stack'
        service['links']['instances'] = 'https://fake/instances'

        return [service]

    elif section == "setting":
        listSettings = []
        setting = {}
        setting['id'] = "1as!account.by.key.credential.types"
        setting['type'] = "activeSetting"
        setting['name'] = "account.by.key.credential.types"
        setting['activeValue'] = "agentApiKey, apiKey, usernamePassword"
        listSettings.append(setting)

        setting = {}
        setting['id'] = "1as!cattle.db.cattle.database"
        setting['type'] = "activeSetting"
        setting['name'] = "cattle.db.cattle.database"
        setting['activeValue'] = "mysql"
        listSettings.append(setting)

        setting = {}
        setting['id'] = "1as!cattle.db.cattle.mysql.host"
        setting['type'] = "activeSetting"
        setting['name'] = "cattle.db.cattle.mysql.host"
        setting['activeValue'] = "db"
        listSettings.append(setting)

        setting = {}
        setting['id'] = "1as!cattle.db.cattle.mysql.name"
        setting['type'] = "activeSetting"
        setting['name'] = "cattle.db.cattle.mysql.name"
        setting['activeValue'] = "rancher"
        listSettings.append(setting)

        setting = {}
        setting['id'] = "1as!cattle.db.cattle.mysql.port"
        setting['type'] = "activeSetting"
        setting['name'] = "cattle.db.cattle.mysql.port"
        setting['activeValue'] = "3306"
        listSettings.append(setting)

        setting = {}
        setting['id'] = "1as!cattle.db.cattle.password"
        setting['type'] = "activeSetting"
        setting['name'] = "cattle.db.cattle.password"
        setting['activeValue'] = "password"
        listSettings.append(setting)

        setting = {}
        setting['id'] = "1as!cattle.db.cattle.username"
        setting['type'] = "activeSetting"
        setting['name'] = "cattle.db.cattle.username"
        setting['activeValue'] = "rancher"
        listSettings.append(setting)

        return listSettings

    else:
        return None

def fakeCallApiGet(url):
    if url == "https://fake/stack":
        stack = {}
        stack['name'] = 'stack-test'
        return stack

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
                'type': 'service',
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
                    'stack': 'https://fake/stack',
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

    @mock.patch.object(Client, '_get', autospec=True)
    @mock.patch.object(Client, 'list', autospec=True)
    @mock.patch.object(Client, '__init__', side_effect=fakeClient)
    def testGetStacks(self, mock_init, mock_list, mock_get):

        rancherService = Rancher("https://url", "key", "secret")
        rancherService.getStacks()
        mock_list.assert_any_call(mock.ANY,'stack')

    @mock.patch.object(Client, 'list', side_effect=fakeCallApiList)
    @mock.patch.object(Client, '__init__', side_effect=fakeClient)
    def testGetDatabaseSettings(self, mock_init, mock_list):
        rancherService = Rancher("https://url", "key", "secret")

        targetListSettings = {
            "type": "mysql",
            "host": "db",
            "db": "rancher",
            "user": "rancher",
            "password": "password",
            "port": "3306"
        }

        listSettings = rancherService.getDatabaseSettings()

        self.assertEquals(listSettings, targetListSettings)

if __name__ == '__main__':
    unittest.main()