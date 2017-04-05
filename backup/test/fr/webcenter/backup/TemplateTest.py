import unittest
from fr.webcenter.backup.Config import Config
from fr.webcenter.backup.Backup import Backup

__author__ = 'disaster'


class TemplateTest(unittest.TestCase):

    def setUp(self):

        configService = Config("../../../../config")


    def testTemplateMysql(self):

        backupService = Backup()

        # When user, password and database are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mysql:latest',
                    'environment': {
                        'MYSQL_USER': 'user',
                        'MYSQL_DATABASE': 'test',
                        'MYSQL_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test2',
                'commands': [
                    "sh -c 'mysqldump -h 10.1.0.2 -u user test > /backup/stack-test/test2/test.dump'",
                ],
                'environments': ['MYSQL_PWD:pass'],
                'image': 'mysql:latest'
            }
        ]

        result = backupService.searchDump('/backup', listServices)
        self.assertEqual(targetResult, result)

        # When user, password are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mysql:latest',
                    'environment': {
                        'MYSQL_USER': 'user',
                        'MYSQL_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test2',
                'commands': [
                    "sh -c 'mysqldump -h 10.1.0.2 -u user --all-databases > /backup/stack-test/test2/all-databases.dump'",
                ],
                'environments': ['MYSQL_PWD:pass'],
                'image': 'mysql:latest'
            }
        ]

        result = backupService.searchDump('/backup', listServices)
        self.assertEqual(targetResult, result)

        # When root password and database are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mysql:latest',
                    'environment': {
                        'MYSQL_DATABASE': 'test',
                        'MYSQL_ROOT_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test2',
                'commands': [
                    "sh -c 'mysqldump -h 10.1.0.2 -u root test > /backup/stack-test/test2/test.dump'",
                ],
                'environments': ['MYSQL_PWD:pass'],
                'image': 'mysql:latest'
            }
        ]

        result = backupService.searchDump('/backup', listServices)
        self.assertEqual(targetResult, result)

        # When root password is setted
        listServices = [
            {
                'type': 'service',
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mysql:latest',
                    'environment': {
                        'MYSQL_ROOT_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test2',
                'commands': [
                    "sh -c 'mysqldump -h 10.1.0.2 -u root --all-databases > /backup/stack-test/test2/all-databases.dump'",
                ],
                'environments': ['MYSQL_PWD:pass'],
                'image': 'mysql:latest'
            }
        ]

        result = backupService.searchDump('/backup', listServices)
        self.assertEqual(targetResult, result)

        # When user, password, root password and database are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mysql:latest',
                    'environment': {
                        'MYSQL_USER': 'user',
                        'MYSQL_DATABASE': 'test',
                        'MYSQL_PASSWORD': 'pass',
                        'MYSQL_ROOT_PASSWORD': 'root_pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test2',
                'commands': [
                    "sh -c 'mysqldump -h 10.1.0.2 -u user test > /backup/stack-test/test2/test.dump'",
                ],
                'environments': ['MYSQL_PWD:pass'],
                'image': 'mysql:latest'
            }
        ]

        result = backupService.searchDump('/backup', listServices)
        self.assertEqual(targetResult, result)

    def testTemplateMariadb(self):
        backupService = Backup()

        # When user, password and database are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mariadb:latest',
                    'environment': {
                        'MYSQL_USER': 'user',
                        'MYSQL_DATABASE': 'test',
                        'MYSQL_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test2',
                'commands': [
                    "sh -c 'mysqldump -h 10.1.0.2 -u user test > /backup/stack-test/test2/test.dump'",
                ],
                'environments': ['MYSQL_PWD:pass'],
                'image': 'mariadb:latest'
            }
        ]

        result = backupService.searchDump('/backup', listServices)
        self.assertEqual(targetResult, result)

        # When user, password are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mariadb:latest',
                    'environment': {
                        'MYSQL_USER': 'user',
                        'MYSQL_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test2',
                'commands': [
                    "sh -c 'mysqldump -h 10.1.0.2 -u user --all-databases > /backup/stack-test/test2/all-databases.dump'",
                ],
                'environments': ['MYSQL_PWD:pass'],
                'image': 'mariadb:latest'
            }
        ]

        result = backupService.searchDump('/backup', listServices)
        self.assertEqual(targetResult, result)

        # When root password and database are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mariadb:latest',
                    'environment': {
                        'MYSQL_DATABASE': 'test',
                        'MYSQL_ROOT_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test2',
                'commands': [
                    "sh -c 'mysqldump -h 10.1.0.2 -u root test > /backup/stack-test/test2/test.dump'",
                ],
                'environments': ['MYSQL_PWD:pass'],
                'image': 'mariadb:latest'
            }
        ]

        result = backupService.searchDump('/backup', listServices)
        self.assertEqual(targetResult, result)

        # When root password is setted
        listServices = [
            {
                'type': 'service',
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mariadb:latest',
                    'environment': {
                        'MYSQL_ROOT_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test2',
                'commands': [
                    "sh -c 'mysqldump -h 10.1.0.2 -u root --all-databases > /backup/stack-test/test2/all-databases.dump'",
                ],
                'environments': ['MYSQL_PWD:pass'],
                'image': 'mariadb:latest'
            }
        ]

        result = backupService.searchDump('/backup', listServices)
        self.assertEqual(targetResult, result)

        # When user, password, root password and database are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test2',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/mariadb:latest',
                    'environment': {
                        'MYSQL_USER': 'user',
                        'MYSQL_DATABASE': 'test',
                        'MYSQL_PASSWORD': 'pass',
                        'MYSQL_ROOT_PASSWORD': 'root_pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/backup/stack-test/test2',
                'commands': [
                    "sh -c 'mysqldump -h 10.1.0.2 -u user test > /backup/stack-test/test2/test.dump'",
                ],
                'environments': ['MYSQL_PWD:pass'],
                'image': 'mariadb:latest'
            }
        ]

        result = backupService.searchDump('/backup', listServices)
        self.assertEqual(targetResult, result)



    def testTemplatePostgresql(self):
        backupService = Backup()

        # When user, password and database are setted
        listServices = [
            {
                'type': 'service',
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': [
                    'pg_dump -h 10.0.0.2 -U user -d test -f /tmp/backup/stack-test/test/test.dump'
                ],
                'environments': ['PGPASSWORD:pass'],
                'image': 'postgres:latest'
            }
        ]

        result = backupService.searchDump('/tmp/backup', listServices)
        self.assertEqual(targetResult, result)

        # When user, password are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/postgres:latest',
                    'environment': {
                        'POSTGRES_USER': 'user',
                        'POSTGRES_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': [
                    'pg_dump -h 10.0.0.2 -U user -d user -f /tmp/backup/stack-test/test/user.dump'
                ],
                'environments': ['PGPASSWORD:pass'],
                'image': 'postgres:latest'
            }
        ]

        result = backupService.searchDump('/tmp/backup', listServices)
        self.assertEqual(targetResult, result)

        # When password and database are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/postgres:latest',
                    'environment': {
                        'POSTGRES_DB': 'test',
                        'POSTGRES_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': [
                    'pg_dump -h 10.0.0.2 -U postgres -d test -f /tmp/backup/stack-test/test/test.dump'
                ],
                'environments': ['PGPASSWORD:pass'],
                'image': 'postgres:latest'
            }
        ]

        result = backupService.searchDump('/tmp/backup', listServices)
        self.assertEqual(targetResult, result)

        # When password are setted
        listServices = [
            {
                'type': 'service',
                'name': 'test',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'test/postgres:latest',
                    'environment': {
                        'POSTGRES_PASSWORD': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': [
                    'pg_dumpall -h 10.0.0.2 -U postgres --clean -f /tmp/backup/stack-test/test/all-databases.dump'
                ],
                'environments': ['PGPASSWORD:pass'],
                'image': 'postgres:latest'
            }
        ]

        result = backupService.searchDump('/tmp/backup', listServices)
        self.assertEqual(targetResult, result)

    def testTemplateMongodb(self):
        backupService = Backup()

        # When no user and password
        listServices = [
            {
                'type': 'service',
                'name': 'test',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'mongo:latest',
                    'environment': {
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': [
                    'mongodump --host 10.0.0.2 --out /tmp/backup/stack-test/test'
                ],
                'environments': [],
                'image': 'mongo:latest'
            }
        ]

        result = backupService.searchDump('/tmp/backup', listServices)
        self.assertEqual(targetResult, result)
        
        
        # When user and password
        listServices = [
            {
                'type': 'service',
                'name': 'test',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'mongo:latest',
                    'environment': {
                        'MONGO_USER': 'user',
                        'MONGO_PASS': 'pass'
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': [
                    'mongodump --host 10.0.0.2 -u user -p pass --out /tmp/backup/stack-test/test'
                ],
                'environments': [],
                'image': 'mongo:latest'
            }
        ]

        result = backupService.searchDump('/tmp/backup', listServices)
        self.assertEqual(targetResult, result)

    def testTemplateElasticsearch(self):
        backupService = Backup()

        listServices = [
            {
                'type': 'service',
                'name': 'test',
                'state': 'active',
                'launchConfig': {
                    'imageUuid': 'elasticsearch:latest',
                    'environment': {
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

        targetResult = [
            {
                'service': listServices[0],
                'target_dir': '/tmp/backup/stack-test/test',
                'commands': [
                    "-c 'rm -rf /tmp/backup/stack-test/test/*.json'",
                    "-c 'elasticdump --input=http://10.0.0.2:9200/ --output=/tmp/backup/stack-test/test/dump_mapping.json --type=mapping'",
                    "-c 'elasticdump --input=http://10.0.0.2:9200/ --output=/tmp/backup/stack-test/test/dump_data.json --type=data'",
                ],
                'environments': [],
                'entrypoint': "/bin/sh",
                'image': 'taskrabbit/elasticsearch-dump:latest'
            }
        ]

        result = backupService.searchDump('/tmp/backup', listServices)
        self.assertEqual(targetResult, result)



if __name__ == '__main__':
    unittest.main()