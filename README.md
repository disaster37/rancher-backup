# rancher-backup

It's a general purpose to solve backup matter on Rancher.
The goal, it's to have ability to use docker command to perform dump (when needed) before to start external backup with duplicity.

To do the job in easiest way, we use the power of Rancher API to discover the service witch must be dumped before to start the backup.
We use some settings files on `/app/config` to explain how discover the service witch must be dumped and how to do that.
Next, all the contains of `BACKUP_PATH` (default is /backup) is backuped on remote backend with duplicity. So you can map your data volume on this container to backup it in the same time.

You are welcome to contribute on github to extend the supported service.

# Compatibilities

## Standard databases compatibilities

No extra need, use dump tools utilities to do remote dump.

- `MySQL`: the docker image must have `mysql` on name. Use `mysqldump` to perform the dump.
- `MariaDB`: the docker image must have `mariadb` on name. Use `mysqldump` to perform the dump.
- `PostgreSQL`: the docker image must have `postgres` on name. Use `pgdump` to perform the dump.
- `MongoDB`: the docker image must have `mongo` on name. Use `mongodump` to perform the dump.
- `Elasticsearch`: the docker image must have `elasticsearch` on name. Use `elasticdump` to perform the dump.

## Distributed NoSQL databases

Need to have shared volume (like glusterfs, S3, Ceph, etc.) between each database nodes and the backup service.
To to dump, we use tools utilities to ask each nodes perform a local dump (on shared volume) and we mount this shared volume on backup service to perform the remote backup.

For example, if you have 3 Cassandra nodes on 3 hosts, you must to have sharded storage on each hosts (`/mnt/cassandra`) witch is mounted on each nodes (`/dump`).
Then, you need to mount the shared storage on backup service (`/mnt/cassandra:/backup/cassandra`).
When we detect Cassandra service, we send command to Cassandra to ask it to perform a dump of each nodes on `/dump`, ans next we perform a backup with duplicity of `/backup` folder.



## Disable dump on specific service

If you should to not dump a particular service witch is supported, you can add label on service `backup.disable=true`

## Backup options
The following options permit to set the backup policy :
- `CRON_SCHEDULE`: when you should start backup (incremental if full is not needed). For example, to start backup each day set `0 0 0 * * *`
- `BACKEND`: this is the target URL to externalize the backup. For example, to use FTP as external backup set `ftp://login@my-ftp.com` and add environment variable `FTP_PASSWORD`. For Amazon S3, set `s3://host[:port]/bucket_name[/prefix]`. Read the ducplicity man for [all supported backend](http://duplicity.nongnu.org/duplicity.1.html#sect7). There are no default value.
- `TARGET_PATH`: The path were store backup on local and remote. The default value is `/backup`.
- `BK_FULL_FREQ`: The frequency when you should make a full backup. For example, if you should make a full backup each 7 days, set `7D`. The default value is `7D`.
- `BK_KEEP_FULL`: How many full backup you should to keep. For example, to keep 3 full backup set `3`. The default value is `3`.
- `BK_KEEP_FULL_CHAIN`: The number of intermediate incremental backup you should keep with the full backup. For example, if you should keep only the incremental backend after the last full backup set `1`. The default value is set to `1`.
- `VOLUME_SIZE`: The volume size to store the backup (in MB). The default value is `25`.
- `RANCHER_API_URL`: the API URL with your project ID
- `RANCHER_API_KEY`: the API key
- `RANCHER_API_SECRET`: the API secret key

## How to extend this

You need to dump another service before to save it (note yet supported) ? Just clone this repository and add the file in `backup/config/new-service.yml`

Then, add your new entry (sample with MySQL):

```yaml
mysql:
  regex: "mysql"
  image: "mysql:latest"
  commands:
    - "mysqldump -h %ip% -u %env_MYSQL_USER% %env_MYSQL_DATABASE% > %target_dir%/%env_MYSQL_DATABASE%.dump"
  environment:
    - MYSQL_PWD:%env_MYSQL_PASSWORD%
```

Few explanation:
- `regex`: It's the regex to discover service witch must be dumped. This regex is applied to image docker used in service.
- `image`: It's the docker image to use to run the dump (generaly the latest tag). If you not add image entry, it use the service docker image.
- `commands`: It's the list of commands to launch on container to perform the dump
- `environment`: It's the list of environment variables you need to perform the dump

There are few macro you can use in command and in environment section:
- `%ip%`: the IP to join the container to perform a remote dump
- `%env_SERVICE_ENV%`: Take the value of service environment called `SERVICE_ENV`
- `%target_dir%`: It's the path where store the dump (`BACKUP_PATH/STACK_NAME/SERVICE_NAME`)
