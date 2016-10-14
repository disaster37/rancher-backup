import re
import os
from pprint import pprint
class Backup(object):

    def searchDump(self, backupPath, listServices, listSettings):

        listDump = []

        for service in listServices:
            for name, setting in listSettings.iteritems():
                if re.search(setting['regex'], service['launchConfig']['imageUuid']):

                    print("Found '%s/%s' to do dumping" % (service['stack']['name'], service['name']))

                    #Replace macro ip
                    command = setting['command']
                    environments = setting['environment']
                    ip = None
                    for instance in service['instances']:
                        if instance['state'] == "running":
                            ip = instance['primaryIpAddress']
                    command = self._replace_macro('%ip%', ip, command)
                    environments = self._replace_macro("%ip", ip, environments)

                    # Replace target_dir macro
                    target_dir = backupPath + "/" + service['stack']['name'] + "/" + service['name']
                    command = self._replace_macro('%target_dir%', target_dir, command)
                    environments = self._replace_macro("%target_dir", target_dir, environments)

                    # Replace environment macro
                    for envKey, envValue in service['launchConfig']['environment'].iteritems():
                        command = self._replace_macro("%env_" + envKey + "%", envValue, command)
                        environments = self._replace_macro("%env_" + envKey + "%", envValue, environments)

                    dump = {}
                    dump['service'] = service
                    dump['target_dir'] = target_dir
                    dump['command'] = command
                    dump["environments"] = environments
                    if "image" in setting:
                        dump['image'] = setting['image']
                    else:
                        dump['image'] = service['launchConfig']['imageUuid']

                    listDump.append(dump)
                    break

        return listDump


    def runDump(self, listDump):

        for dump in listDump:
            print("Dumping %s/%s in %s" % (dump['service']['stack']['name'], dump['service']['name'], dump['target_dir']))
            environments = ""
            for env in dump['environments']:
                environments += " -e '%s'" % env.replace(':', '=')
            dockerCmd = "docker run --rm -v %s:%s %s %s %s" % (dump['target_dir'], dump['target_dir'], environments, dump['image'], dump['command'])
            os.system("docker pull %s" % dump['image'])
            #os.system(dockerCmd)
            print(dockerCmd)
            print("Dump %s/%s is finished" % (dump['service']['stack']['name'], dump['service']['name']))


    def initDuplicity(self, backupPath, backend):

        os.system("duplicity --no-encryption %s %s" % (backend, backupPath))

    backend, target_path, full_backup_frequency, nb_full_backup_keep,
    nb_increment_backup_chain_keep, volume_size

    def runDuplicity(self, backupPath, backend, fullBackupFrequency, fullBackupKeep, incrementalBackupChainKeep, volumeSize):

        print("Start full backup if needed")
        os.system("duplicity remove-all-but-n-full %s --force --allow-source-mismatch --no-encryption %s" % (fullBackupKeep, backend))
        print("Start incremental backup if needed")
        os.system("ducplicity remove-all-inc-of-but-n-full %s --force --allow-source-mismatch --no-encryption %s" % (incrementalBackupChainKeep, backend))
        print("Clean old backup")
        os.system("ducplicity  cleanup --force --no-encryption %s" % (backend))





    def _replace_macro(self,macro, value, data):

        if isinstance(data, basestring):
            data = data.replace(macro, value)

        elif isinstance(data, list):
            for index in range(len(data)):
                data[index] = data[index].replace(macro, value)



        return data
