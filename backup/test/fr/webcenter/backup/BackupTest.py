__author__ = 'disaster'

import unittest
import mock
import os
import io
from mock import mock_open
import fr.webcenter.backup.Backup
import __builtin__
from fr.webcenter.backup.Backup import Backup
from fr.webcenter.backup.Command import Command


def fakeInitDuplicity(cmd):
    return cmd

class BackupTest(unittest.TestCase):

    def test_replaceMacro(self):
        backupService = Backup()

        # We a list
        result = backupService._replaceMacro("%ip%", "10.0.0.1", "ip: %ip%")
        self.assertEqual("ip: 10.0.0.1", result)

        # With a list
        result = backupService._replaceMacro("%ip%", "10.0.0.1", ["ip: %ip%", "ddd: dfdf", "test: %ip% sdsd"])
        self.assertEqual(["ip: 10.0.0.1", "ddd: dfdf", "test: 10.0.0.1 sdsd"], result)

    @mock.patch.object(Command, 'runCmd', autospec=True)
    def testInitDuplicity(self, mock_runCmd):
        backupService = Backup()
        backupService.initDuplicity('/backup', 'ftp://user:pass@my-server.com/backup/dump')
        mock_runCmd.assert_any_call(mock.ANY, 'duplicity --no-encryption ftp://user:pass@my-server.com/backup/dump /backup')

    @mock.patch.object(Command, 'runCmd', autospec=True)
    def testRunDuplicity(self, mock_runCmd):
        backupService = Backup()
        backupService.runDuplicity('/backup', 'ftp://user:pass@my-server.com/backup/dump', '1D', '7', '1', '1000')
        mock_runCmd.assert_any_call(mock.ANY, 'duplicity --volsize 1000 --no-encryption --allow-source-mismatch --full-if-older-than 1D /backup ftp://user:pass@my-server.com/backup/dump')
        mock_runCmd.assert_any_call(mock.ANY, 'duplicity remove-all-but-n-full 7 --force --allow-source-mismatch --no-encryption ftp://user:pass@my-server.com/backup/dump')
        mock_runCmd.assert_any_call(mock.ANY, 'duplicity remove-all-inc-of-but-n-full 1 --force --allow-source-mismatch --no-encryption ftp://user:pass@my-server.com/backup/dump')
        mock_runCmd.assert_any_call(mock.ANY, 'duplicity  cleanup --force --no-encryption ftp://user:pass@my-server.com/backup/dump')


    def testSearchDump(self):
        backupService = Backup()

        listServices = [
            {
                'name': 'test',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/postgres:latest',
                    'environment': {
                        'POSTGRES_USER': 'user',
                        'POSTGRES_DB':'test',
                        'POSTGRES_PASSWORD':'pass'
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
            },
            {
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mysql:latest',
                    'environment': {
                        'MYSQL_USER': 'user',
                        'MYSQL_DB': 'test',
                        'MYSQL_PASSWORD': 'pass'
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
                        'primaryIpAddress': '10.1.0.1',
                        'host': {
                            'name': 'host-1'
                        },
                        'links': {
                            'hosts': 'https://fake/hosts'
                        }
                    },
                    {
                        'state': 'running',
                        'primaryIpAddress': '10.1.0.2',
                        'host': {
                            'name': 'host-1'
                        },
                        'links': {
                            'hosts': 'https://fake/hosts'
                        }
                    },
                    {
                        'state': 'running',
                        'primaryIpAddress': '10.1.0.3',
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

        # With environment on settings
        listConfig = {
            'postgres': {
                'regex': "postgres",
                'image': 'postgres:latest',
                'commands': [
                    'pg_dump -h %ip% -U %env_POSTGRES_USER% -d %env_POSTGRES_DB% -f %target_dir%/%env_POSTGRES_DB%.dump',
                    'fake_cmd2 -h %ip% -U %env_POSTGRES_USER%'
                ],
                'entrypoint': "sh -c",
                'environment': ['PGPASSWORD:%env_POSTGRES_PASSWORD%']
            },
            'mysql': {
                'regex': "mysql",
                'image': 'mysql:latest',
                'commands': [
                    'mysqldump -h %ip% -U %env_MYSQL_USER% -d %env_MYSQL_DB% -f %target_dir%/%env_MYSQL_DB%.dump',
                    'fake_cmd2 -h %ip% -U %env_MYSQL_USER%'
                ],
                'environment': ['MYSQLPASSWORD:%env_MYSQL_PASSWORD%']
            }
        }
        result = backupService.searchDump('/tmp/backup',listServices, listConfig)

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': [
                    'pg_dump -h 10.0.0.2 -U user -d test -f /tmp/backup/stack-test/test/test.dump',
                    'fake_cmd2 -h 10.0.0.2 -U user'
                ],
                'entrypoint': "sh -c",
                'environments': ['PGPASSWORD:pass'],
                'image': 'postgres:latest'
            },
            {
                'service': listServices[1],
                'target_dir': '/tmp/backup/stack-test/test2',
                'commands': [
                    'mysqldump -h 10.1.0.2 -U user -d test -f /tmp/backup/stack-test/test2/test.dump',
                    'fake_cmd2 -h 10.1.0.2 -U user'
                ],
                'environments': ['MYSQLPASSWORD:pass'],
                'image': 'mysql:latest'
            }
        ]

        self.assertEqual(targetResult, result)

        # Without environment on setting
        listConfig = {
            'postgres': {
                'regex': "postgres",
                'image': 'postgres:latest',
                'commands': ['pg_dump -h %ip% -U %env_POSTGRES_USER% -d %env_POSTGRES_DB% -f %target_dir%/%env_POSTGRES_DB%.dump'],
            }
        }
        result = backupService.searchDump('/tmp/backup', listServices, listConfig)

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': ['pg_dump -h 10.0.0.2 -U user -d test -f /tmp/backup/stack-test/test/test.dump'],
                'environments': [],
                'image': 'postgres:latest'
            }
        ]

        # Without image on setting
        listConfig = {
            'postgres': {
                'regex': "postgres",
                'commands': ['pg_dump -h %ip% -U %env_POSTGRES_USER% -d %env_POSTGRES_DB% -f %target_dir%/%env_POSTGRES_DB%.dump'],
            }
        }
        result = backupService.searchDump('/tmp/backup', listServices, listConfig)

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': ['pg_dump -h 10.0.0.2 -U user -d test -f /tmp/backup/stack-test/test/test.dump'],
                'environments': [],
                'image': 'test/postgres:latest'
            }
        ]

        self.assertEqual(targetResult, result)

    @mock.patch.object(Command, 'runCmd', autospec=True)
    def testRunDump(self, mock_runCmd):

        backupService = Backup()

        listServices = [
            {
                'name': 'test',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/postgres:latest',
                    'environment': {
                        'POSTGRES_USER': 'user',
                        'POSTGRES_DB': 'test',
                        'POSTGRES_PASSWORD': 'pass'
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
            },
            {
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mysql:latest',
                    'environment': {
                        'MYSQL_USER': 'user',
                        'MYSQL_DB': 'test',
                        'MYSQL_PASSWORD': 'pass'
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
                        'primaryIpAddress': '10.1.0.1',
                        'host': {
                            'name': 'host-1'
                        },
                        'links': {
                            'hosts': 'https://fake/hosts'
                        }
                    },
                    {
                        'state': 'running',
                        'primaryIpAddress': '10.1.0.2',
                        'host': {
                            'name': 'host-1'
                        },
                        'links': {
                            'hosts': 'https://fake/hosts'
                        }
                    },
                    {
                        'state': 'running',
                        'primaryIpAddress': '10.1.0.3',
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

        listDump = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': ['pg_dump -h 10.0.0.2 -U user -d test -f /tmp/backup/stack-test/test/test.dump'],
                'entrypoint': "sh -c",
                'environments': ['PGPASSWORD:pass'],
                'image': 'postgres:latest'
            },
            {
                'service': listServices[1],
                'target_dir': '/tmp/backup/stack-test/test2',
                'commands': [
                    'mysqldump -h 10.1.0.2 -U user -d test -f /tmp/backup/stack-test/test2/test.dump',
                    'fake_cmd2 -h 10.1.0.2 -U user'
                ],
                'environments': ['MYSQLPASSWORD:pass'],
                'image': 'mysql:latest'
            }
        ]

        backupService.runDump(listDump)
        #print("Nb call %s" % mock_runCmd.call_args_list)
        mock_runCmd.assert_any_call(mock.ANY, 'docker pull postgres:latest')
        mock_runCmd.assert_any_call(mock.ANY, "docker run --rm --entrypoint='sh -c' -v /tmp/backup/stack-test/test:/tmp/backup/stack-test/test  -e 'PGPASSWORD=pass' postgres:latest pg_dump -h 10.0.0.2 -U user -d test -f /tmp/backup/stack-test/test/test.dump")
        mock_runCmd.assert_any_call(mock.ANY, 'docker pull mysql:latest')
        mock_runCmd.assert_any_call(mock.ANY, "docker run --rm  -v /tmp/backup/stack-test/test2:/tmp/backup/stack-test/test2  -e 'MYSQLPASSWORD=pass' mysql:latest mysqldump -h 10.1.0.2 -U user -d test -f /tmp/backup/stack-test/test2/test.dump")


    @mock.patch('__builtin__.open', new_callable=mock.mock_open(), create=True)
    @mock.patch.object(os, 'makedirs', autospec=True)
    def testdumpStacksSettings(self, mock_makedirs, mock_file):
        backupService = Backup()

        listStack = [
            {
                "id": "1e44",
                "type": "environment",
                "links": {
                    "self": "/v1/projects/1a203/environments/1e44",
                    "account": "/v1/projects/1a203/environments/1e44/account",
                    "services": "/v1/projects/1a203/environments/1e44/services",
                    "composeConfig": "/v1/projects/1a203/environments/1e44/composeconfig",
                },
                "actions": {
                    "upgrade": "/v1/projects/1a203/environments/1e44/?action=upgrade",
                    "update": "/v1/projects/1a203/environments/1e44/?action=update",
                    "remove": "/v1/projects/1a203/environments/1e44/?action=remove",
                    "addoutputs": "/v1/projects/1a203/environments/1e44/?action=addoutputs",
                    "activateservices": "/v1/projects/1a203/environments/1e44/?action=activateservices",
                    "deactivateservices": "/v1/projects/1a203/environments/1e44/?action=deactivateservices",
                    "exportconfig": "/v1/projects/1a203/environments/1e44/?action=exportconfig",
                },
                "name": "Default",
                "state": "active",
                "accountId": "1a203",
                "created": "2016-09-14T07:41:09Z",
                "createdTS": 1473838869000,
                "description": None,
                "dockerCompose": None,
                "environment": None,
                "externalId": None,
                "healthState": "healthy",
                "kind": "environment",
                "outputs": None,
                "previousEnvironment": None,
                "previousExternalId": None,
                "rancherCompose": None,
                "removed": None,
                "startOnCreate": None,
                "transitioning": "no",
                "transitioningMessage": None,
                "transitioningProgress": None,
                "uuid": "e2c02a5f-5585-4ee7-8bdb-3672e874de10",
                'settings': {
                    "id": None,
                    "type": "composeConfig",
                    "links": {},
                    "actions": {},
                    "dockerComposeConfig": "test:\r\n  environment:\r\n    BACKEND: ftp://test\r\n    FTP_PASSWORD: test\r\n    CRON_SCHEDULE: 0 0 * * *\r\n    BK_FULL_FREQ: 1D\r\n    BK_KEEP_FULL: '7'\r\n    BK_KEEP_FULL_CHAIN: '1'\r\n    VOLUME_SIZE: '1000'\r\n    RANCHER_API_URL: https://test/v1/projects/1a203\r\n    RANCHER_API_KEY: test\r\n    RANCHER_API_SECRET: test\r\n    DEBUG: 'false'\r\n  labels:\r\n    io.rancher.container.pull_image: always\r\n    backup.disable: 'true'\r\n  tty: true\r\n  image: webcenter/rancher-backup:develop\r\n  privileged: true\r\n  stdin_open: true\r\nmariadb:\r\n  environment:\r\n    MYSQL_ROOT_PASSWORD: root-pass\r\n    MYSQL_DATABASE: teampass\r\n    MYSQL_PASSWORD: user-pass\r\n    MYSQL_USER: teampass\r\n  labels:\r\n    io.rancher.container.pull_image: always\r\n  tty: true\r\n  image: mariadb\r\n  stdin_open: true\r\npostgres:\r\n  environment:\r\n    PGDATA: /var/lib/postgresql/data/pgdata\r\n    POSTGRES_DB: alfresco\r\n    POSTGRES_USER: user\r\n    POSTGRES_PASSWORD: pass\r\n  labels:\r\n    io.rancher.container.pull_image: always\r\n  tty: true\r\n  image: postgres:9.4\r\n  volumes:\r\n  - /data/postgres:/var/lib/postgresql/data/pgdata\r\n  stdin_open: true\r\nmysql:\r\n  environment:\r\n    MYSQL_ROOT_PASSWORD: root-pass\r\n    MYSQL_DATABASE: teampass\r\n    MYSQL_PASSWORD: user-pass\r\n    MYSQL_USER: teampass\r\n  labels:\r\n    io.rancher.container.pull_image: always\r\n  tty: true\r\n  image: mysql/mysql-server:5.5\r\n  stdin_open: true\r\n",
                    "rancherComposeConfig": "test:\r\n  scale: 1\r\nmariadb:\r\n  scale: 1\r\npostgres:\r\n  scale: 1\r\nmysql:\r\n  scale: 1\r\n",
                }

            },
            {
                "id": "1e45",
                "type": "environment",
                "links": {
                    "self": "/v1/projects/1a203/environments/1e45",
                    "account": "/v1/projects/1a203/environments/1e45/account",
                    "services": "/v1/projects/1a203/environments/1e45/services",
                    "composeConfig": "/v1/projects/1a203/environments/1e45/composeconfig",
                },
                "actions": {
                    "upgrade": "/v1/projects/1a203/environments/1e45/?action=upgrade",
                    "update": "/v1/projects/1a203/environments/1e45/?action=update",
                    "remove": "/v1/projects/1a203/environments/1e45/?action=remove",
                    "addoutputs": "/v1/projects/1a203/environments/1e45/?action=addoutputs",
                    "activateservices": "/v1/projects/1a203/environments/1e45/?action=activateservices",
                    "deactivateservices": "/v1/projects/1a203/environments/1e45/?action=deactivateservices",
                    "exportconfig": "/v1/projects/1a203/environments/1e45/?action=exportconfig",
                },
                "name": "seedbox",
                "state": "active",
                "accountId": "1a203",
                "created": "2016-09-14T07:43:01Z",
                "createdTS": 1473838981000,
                "description": None,
                "dockerCompose": "plex:\n  ports:\n  - 32400:32400/tcp\n  environment:\n    PLEX_USERNAME: user\n    PLEX_PASSWORD: pass\n    PLEX_DISABLE_SECURITY: '0'\n    SKIP_CHOWN_CONFIG: 'false'\n    PLEX_ALLOWED_NETWORKS: 10.0.0.0/8\n  labels:\n    io.rancher.container.pull_image: always\n  tty: true\n  hostname: home\n  image: timhaak/plex\n  volumes:\n  - /mnt/nas:/data\n  - /data/seedbox/plex:/config\n  stdin_open: true",
                "environment": None,
                "externalId": "",
                "healthState": "healthy",
                "kind": "environment",
                "outputs": None,
                "previousEnvironment": None,
                "previousExternalId": None,
                "rancherCompose": "plex:\n  scale: 1",
                "removed": None,
                "startOnCreate": True,
                "transitioning": "no",
                "transitioningMessage": None,
                "transitioningProgress": None,
                "uuid": "1a5c08a4-c851-4651-b516-e950982d617b",
                'settings': {
                    "id": None,
                    "type": "composeConfig",
                    "links": {},
                    "actions": {},
                    "dockerComposeConfig": "plex:\r\n  ports:\r\n  - 32400:32400/tcp\r\n  environment:\r\n    PLEX_ALLOWED_NETWORKS: 10.0.0.0/8\r\n    PLEX_DISABLE_SECURITY: '0'\r\n    PLEX_PASSWORD: test\r\n    PLEX_USERNAME: test\r\n    SKIP_CHOWN_CONFIG: 'false'\r\n  labels:\r\n    io.rancher.container.pull_image: always\r\n  tty: true\r\n  hostname: home\r\n  image: timhaak/plex\r\n  volumes:\r\n  - /mnt/nas:/data\r\n  - /data/seedbox/plex:/config\r\n  stdin_open: true\r\n",
                    "rancherComposeConfig": "plex:\r\n  scale: 1\r\n",
                }
            },
            {
                "id": "1e48",
                "type": "environment",
                "links": {
                    "self": "/v1/projects/1a203/environments/1e48",
                    "account": "/v1/projects/1a203/environments/1e48/account",
                    "services": "/v1/projects/1a203/environments/1e48/services",
                    "composeConfig": "/v1/projects/1a203/environments/1e48/composeconfig",
                },
                "actions": {
                    "upgrade": "/v1/projects/1a203/environments/1e48/?action=upgrade",
                    "update": "/v1/projects/1a203/environments/1e48/?action=update",
                    "remove": "/v1/projects/1a203/environments/1e48/?action=remove",
                    "addoutputs": "/v1/projects/1a203/environments/1e48/?action=addoutputs",
                    "activateservices": "/v1/projects/1a203/environments/1e48/?action=activateservices",
                    "deactivateservices": "/v1/projects/1a203/environments/1e48/?action=deactivateservices",
                    "exportconfig": "/v1/projects/1a203/environments/1e48/?action=exportconfig",
                },
                "name": "test",
                "state": "active",
                "accountId": "1a203",
                "created": "2016-10-21T09:21:46Z",
                "createdTS": 1477041706000,
                "description": None,
                "dockerCompose": None,
                "environment": None,
                "externalId": "",
                "healthState": "healthy",
                "kind": "environment",
                "outputs": None,
                "previousEnvironment": None,
                "previousExternalId": None,
                "rancherCompose": None,
                "removed": None,
                "startOnCreate": True,
                "transitioning": "no",
                "transitioningMessage": None,
                "transitioningProgress": None,
                "uuid": "0fec46ea-99d5-494d-b430-eac97beb419f",
                "settings": {
                    "id": None,
                    "type": "composeConfig",
                    "links": {},
                    "actions": {},
                    "dockerComposeConfig": "elasticsearch:\r\n  labels:\r\n    io.rancher.container.pull_image: always\r\n  tty: true\r\n  image: elasticsearch\r\n  stdin_open: true\r\nmongo:\r\n  labels:\r\n    io.rancher.container.pull_image: always\r\n  tty: true\r\n  command:\r\n  - mongod\r\n  - --smallfiles\r\n  - --oplogSize\r\n  - '128'\r\n  image: mongo\r\n  stdin_open: true\r\n",
                    "rancherComposeConfig": "elasticsearch:\r\n  scale: 1\r\nmongo:\r\n  scale: 1\r\n",
                }

            },
            {
                "id": "1e49",
                "type": "environment",
                "links": {
                    "self": "/v1/projects/1a203/environments/1e49",
                    "account": "/v1/projects/1a203/environments/1e49/account",
                    "services": "/v1/projects/1a203/environments/1e49/services",
                    "composeConfig": "/v1/projects/1a203/environments/1e49/composeconfig",
                },
                "actions": {
                    "upgrade": "/v1/projects/1a203/environments/1e49/?action=upgrade",
                    "update": "/v1/projects/1a203/environments/1e49/?action=update",
                    "remove": "/v1/projects/1a203/environments/1e49/?action=remove",
                    "addoutputs": "/v1/projects/1a203/environments/1e49/?action=addoutputs",
                    "activateservices": "/v1/projects/1a203/environments/1e49/?action=activateservices",
                    "deactivateservices": "/v1/projects/1a203/environments/1e49/?action=deactivateservices",
                    "exportconfig": "/v1/projects/1a203/environments/1e49/?action=exportconfig",
                },
                "name": "lb",
                "state": "active",
                "accountId": "1a203",
                "created": "2016-10-24T09:55:44Z",
                "createdTS": 1477302944000,
                "description": None,
                "dockerCompose": None,
                "environment": None,
                "externalId": "",
                "healthState": "healthy",
                "kind": "environment",
                "outputs": None,
                "previousEnvironment": None,
                "previousExternalId": None,
                "rancherCompose": None,
                "removed": None,
                "startOnCreate": True,
                "transitioning": "no",
                "transitioningMessage": None,
                "transitioningProgress": None,
                "uuid": "7ac2a47f-b084-4002-a2fb-919a1e738bda",
                "settings": {
                    "id": None,
                    "type": "composeConfig",
                    "links": {},
                    "actions": {},
                    "dockerComposeConfig": "{}\r\n",
                    "rancherComposeConfig": "{}\r\n",
                }
            },
        ]

        backupService.dumpStacksSettings('/backup', listStack)

        #print("Call makedirs: %s", mock_makedirs.call_args_list)
        #print("Call open: %s", mock_file.call_args_list)

        mock_makedirs.assert_any_call('/backup/Default')
        mock_makedirs.assert_any_call('/backup/seedbox')
        mock_makedirs.assert_any_call('/backup/test')
        mock_makedirs.assert_any_call('/backup/lb')

        mock_file.assert_any_call('/backup/Default/docker-compose.yml', 'w')
        mock_file.assert_any_call('/backup/Default/rancher-compose.yml', 'w')
        mock_file.assert_any_call('/backup/seedbox/docker-compose.yml', 'w')
        mock_file.assert_any_call('/backup/seedbox/rancher-compose.yml', 'w')
        mock_file.assert_any_call('/backup/test/docker-compose.yml', 'w')
        mock_file.assert_any_call('/backup/test/rancher-compose.yml', 'w')
        mock_file.assert_any_call('/backup/lb/docker-compose.yml', 'w')
        mock_file.assert_any_call('/backup/lb/rancher-compose.yml', 'w')





if __name__ == '__main__':
    unittest.main()
