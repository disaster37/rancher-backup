__author__ = 'disaster'

import unittest
import mock
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
            }
        ]

        listConfig = {
            'postgres': {
                'regex': "postgres",
                'image': 'postgres:latest',
                'command': 'pg_dump -h %ip% -U %env_POSTGRES_USER% -d %env_POSTGRES_DB% -f %target_dir%/%env_POSTGRES_DB%.dump',
                'environment': ['PGPASSWORD:%env_POSTGRES_PASSWORD%']
            }
        }
        result = backupService.searchDump('/backup',listServices, listConfig)

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test',
                'command': 'pg_dump -h 10.0.0.2 -U user -d test -f /backup/stack-test/test/test.dump',
                'environments': ['PGPASSWORD:pass'],
                'image': 'postgres:latest'
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
            }
        ]

        listDump = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test',
                'command': 'pg_dump -h 10.0.0.2 -U user -d test -f /backup/stack-test/test/test.dump',
                'environments': ['PGPASSWORD:pass'],
                'image': 'postgres:latest'
            }
        ]

        backupService.runDump(listDump)
        print("Nb call %s" % mock_runCmd.call_args_list)
        mock_runCmd.assert_any_call(mock.ANY, 'docker pull postgres:latest')
        mock_runCmd.assert_any_call(mock.ANY, "docker run --rm -v /backup/stack-test/test:/backup/stack-test/test  -e 'PGPASSWORD=pass' postgres:latest pg_dump -h 10.0.0.2 -U user -d test -f /backup/stack-test/test/test.dump")