#!/usr/bin/python
import os
import re
import sys
import time
from rancher_metadata import MetadataAPI

__author__ = 'Sebastien LANGOUREAUX'

BACKUP_DIR = '/backup'


class ServiceRun():

  def __get_list_mysql(self):

      # Check on link container that start by mysql
      metadata_manager = MetadataAPI()
      list_services = metadata_manager.get_service_links()
      list_mysql = []
      for service in list_services:
          if re.search('^mysql', service):
              database = {}
              database['host'] = service
              database['name'] = os.getenv(service.upper() + '_ENV_MYSQL_DATABASE', os.getenv(service.upper() + '_ENV_MYSQL_USER'))
              database['user'] = os.getenv(service.upper() + '_ENV_MYSQL_USER', 'root')
              database['password'] = os.getenv(service.upper() + '_ENV_MYSQL_PASSWORD', os.getenv(service.upper() + '_ENV_MYSQL_ROOT_PASSWORD'))
              list_mysql.append(database)
              print("Found Mysql host : " + service)

      return list_mysql

  def _get_list_postgresql(self):

      # Check on link container that start by mysql
      metadata_manager = MetadataAPI()
      list_services = metadata_manager.get_service_links()
      list_postgresql = []
      for service in list_services:
          service_name = list_services[service]
          service_name_env = service_name.upper().replace('-', '_')
          if re.search('^postgres', service_name):
              database = {}
              database['host'] = service_name
              database['db'] = os.getenv(service_name_env + '_ENV_POSTGRES_DB', os.getenv(service_name_env + '_ENV_POSTGRES_USER'))
              database['user'] = os.getenv(service_name_env + '_ENV_POSTGRES_USER', 'postgres')
              database['password'] = os.getenv(service_name_env + '_ENV_POSTGRES_PASSWORD')
              database['name'] = service

              list_postgresql.append(database)
              print("Found Postgresql host : " + service + "(" + service_name + ")")

      return list_postgresql

  def backup_postgres(self):
      global BACKUP_DIR

      list_postgresql = self._get_list_postgresql()

      for database in list_postgresql:

          cmd = 'pg_dump -h ' + database['host']

          if database['user'] is not None and database['password'] is not None:
              cmd += ' -U ' + database['user']
              cmd = 'PGPASSWORD="' + database['password'] + '" ' + cmd

          cmd += ' -d ' + database['db']

          path = BACKUP_DIR + '/postgresql/' + database['name']

          os.system('mkdir -p ' + path)
          print(cmd + ' -f ' + path + '/' + database['host'] + '_' + database['db'] + '.sql')
          os.system(cmd + ' -f ' + path + '/' + database['host'] + '_' + database['db'] + '.sql')
          print("We just dump " + database['name'] + " on host " + database['host'])





if __name__ == '__main__':
    # Start


    service = ServiceRun()
    service.backup_postgres()
