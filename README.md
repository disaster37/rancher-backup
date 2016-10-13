# rancher-backup

It's a general purpose to solve backup matter on Rancher.
To goal, it's to have ability to use docker command to perform dump (when needed) before to start external backup with duplicity.

To do the job in easiest way, we use the rancher metadata API.

## Database compatibility
- `MySQL`: just link your container with prefix name `mysql-` (for example mysql-mydatabase)
- `PostgreSQL`: just link your container with prefix name `postgres-` (for example postgres-mydatabase)
- `MongoDB`: just link your container with prefix name `mongo-` (for example mongo-mydatabase)

Note : you can link many container as needed

## Backup options
The following options permit to set the backup policy :
- `CRON_SCHEDULE`: When you should start backup (incremental if full is not needed). For example, to start backup each day set `0 0 0 * * *`
- `TARGET_BACKEND`: This is the target URL to externalize the backup. For example, to use FTP as external backup set `ftp://login@my-ftp.com` and add environment variable `FTP_PASSWORD`. For Amazon S3, set `s3://host[:port]/bucket_name[/prefix]`. Read the ducplicity man for [all supported backend](http://duplicity.nongnu.org/duplicity.1.html#sect7). There are no default value.
- `TARGET_PATH`: The path were store backup on local and remote. The default value is `/backup/postgres`.
- `BK_FULL_FREQ`: The frequency when you should make a full backup. For example, if you should make a full backup each 7 days, set `7D`. The default value is `7D`.
- `BK_KEEP_FULL`: How many full backup you should to keep. For example, to keep 3 full backup set `3`. The default value is `3`.
- `BK_KEEP_FULL_CHAIN`: The number of intermediate incremental backup you should keep with the full backup. For example, if you should keep only the incremental backend after the last full backup set `1`. The default value is set to `1`.
- `VOLUME_SIZE`: The volume size to store the backup (in MB). The default value is `25`.

## How to extend this

You need to dump another database before to save it (note yet supported) ? Just clone this repository and edit the file `assets/setting.yml`

Then, add your new entry with the new database engine:

```yaml
mysql:
  regex: "mysql-"
  image: "mysql:latest"
  command: "mysqldump -h ${db_host} -u ${db_user} ${db_name} > ${target_dir}/${%service_name_env%_ENV_MYSQL_DATABASE}.dump"
  environment:
    - MYSQL_PWD:${%service_name_env%_ENV_MYSQL_PASSWORD}
    - db_user:${%service_name_env%_ENV_MYSQL_USER}
    - db_host:%service_name%
    - db_name:${%service_name_env%_ENV_MYSQL_DATABASE}
    - target_dir:${BACKUP_DIR}/%service_path%
```

Few explanation:
- `regex`: It's the prefix to use when you link container image
- `image`: It's the docker image to use to run the dump (generaly the latest tag)
- `command`: It's the command to launch on container to perform the dump
- `environment`: It's the list of environment variables you need to perform the dump

There are few macro you can use in command and in environment section:
- `%service_name%`: the name use to link the docker container (it's also the dns to join the host)
- `%service_name_env%`: It's the base of each environment variable linked
- `%service_path%`: It's the name of stack/service

> You need to add `target_dir` on environment section. It's use to mount volume on container used to perform the dump.
