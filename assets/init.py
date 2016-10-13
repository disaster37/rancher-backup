#!/usr/bin/python
import os
import re
import sys
import time
import yaml
import string
from rancher_metadata import MetadataAPI

__author__ = 'Disaster <linuxworkgroup@hotmail.com>'


BACKUP_DIR = os.getenv('BACKUP_DIR')

class ServiceRun():


    def run(self):
        """
        Loop over each linked container et tryp to dump it if needed
        """

        list_services = self._get_link_services()
        settings = self._get_settings()
        self._run_backup_container(list_services, settings)


    def backup_duplicity(self, backend, target_path, full_backup_frequency, nb_full_backup_keep,
                         nb_increment_backup_chain_keep, volume_size, is_init=False):
        """
        Manage duplicity for remote backup
        """
        global BACKUP_DIR
        if backend is None or backend == "":
            raise KeyError("You must set the target backend")
        if target_path is None or target_path == "":
            raise KeyError("You must set the target path")
        if full_backup_frequency is None or full_backup_frequency == "":
            raise KeyError("You must set the full backup frequency")
        if nb_full_backup_keep is None or nb_full_backup_keep == "":
            raise KeyError("You must set how many full backup you should to keep")
        if nb_increment_backup_chain_keep is None or nb_increment_backup_chain_keep == "":
            raise KeyError("You must set how many incremental chain with full backup you should to keep")
        if volume_size is None or volume_size == "":
            raise KeyError("You must set the volume size")

        backend = "%s%s" % (backend, target_path)
        cmd = "duplicity"

        # First, we restore the last backup
        if is_init is True:
            print("Starting init the backup folder")
            os.system("%s --no-encryption %s %s" % (cmd, backend, BACKUP_DIR))


        else:
            # We backup on FTP
            print("Starting backup")
            os.system("%s --volsize %s --no-encryption --allow-source-mismatch --full-if-older-than %s %s %s" % (
            cmd, volume_size, full_backup_frequency, BACKUP_DIR, backend))

            # We clean old backup
            print("Starting cleanup")
            os.system("%s remove-all-but-n-full %s --force --allow-source-mismatch --no-encryption %s" % (
            cmd, nb_full_backup_keep, backend))
            os.system("%s remove-all-inc-of-but-n-full %s --force --allow-source-mismatch --no-encryption %s" % (
            cmd, nb_increment_backup_chain_keep, backend))
            os.system("%s cleanup --force --no-encryption %s" % (cmd, backend))


    def _get_link_services(self):
        """
        Permit to get all info needed to backup all linked services
        """

        metadata_manager = MetadataAPI()
        list_services = metadata_manager.get_service_links()
        list_containers = []
        for service in list_services:
            container = {}
            container['service_name'] = list_services[service]
            container['service_name_env'] = list_services[service].upper().replace('-', '_')
            container['service_path'] = service
            list_containers.append(container)


        return list_containers


    def _get_settings(self):
        """
        Permit to load setting from setting.yml file
        """
        return yaml.load(open('setting.yml'))

    def _get_env(self, setting):
        """
        Permit to get all environment varaiable to dump container
        """

        list_env = {}

        for env in setting["environment"]:
            regex_env = re.search('^([^:]+):(.*)$', env)
            if regex_env:
                list_env[regex_env.group(1)] = regex_env.group(2)

        return list_env

    def _replace_macro(self, command, service):
        """
        Replace macro by value on string
        """

        return command.replace('%service_name_env%', service['service_name_env']).replace('%service_name%', service['service_name']).replace('%service_path%', service['service_path']).replace('%backup_dir%', os.getenv('BACKUP_DIR'))


    def _run_backup_container(self, list_services, settings):
        """
        Permit to run docker container to try to backup linked services
        """

        for service in list_services:
            for key, value in settings.items():
                if re.search(value['regex'], service['service_name']):
                    list_env = self._get_env(value)

                    command = "docker run --rm"
                    for env, env_value in list_env.items():
                        command += " -e '%s=%s'" % (env, env_value)
                    command  += " -v '%s:%s' %s /bin/bash -c '%s'" % (list_env['target_dir'], list_env['target_dir'], value['image'], value['command'])
                    command = self._replace_macro(command, service)
                    command = os.path.expandvars(command)

                    os.system("docker pull %s" % value['image'])
                    print("Start dump for %s \n" % service["service_path"])
                    os.system(command)
                    print("End dump for %s \n" % service["service_path"])



if __name__ == '__main__':
    # Start


    service = ServiceRun()
    service.backup_duplicity(os.getenv('TARGET_BACKEND'), os.getenv('TARGET_PATH', "/backup"),
                             os.getenv('BK_FULL_FREQ', "7D"), os.getenv('BK_KEEP_FULL', "3"),
                             os.getenv('BK_KEEP_FULL_CHAIN', "1"), os.getenv('VOLUME_SIZE', "25"), True)
    service.run()
    service.backup_duplicity(os.getenv('TARGET_BACKEND'), os.getenv('TARGET_PATH', "/backup"),
                             os.getenv('BK_FULL_FREQ', "7D"), os.getenv('BK_KEEP_FULL', "3"),
                             os.getenv('BK_KEEP_FULL_CHAIN', "1"), os.getenv('VOLUME_SIZE', "25"))
