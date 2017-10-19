# rancher-backup

It's a general purpose to solve backup matter on Rancher.
The goal, it's to have ability to use docker command to perform dump (when needed) before to start external backup with duplicity.

To do the job in easiest way, we use the power of Rancher API to discover the service witch must be dumped before to start the backup.
We use some settings files on `/opt/backup/config` to explain how discover the service witch must be dumped and how to do that.
Next, all the contains of `BACKUP_duplicity_source-path` (default is /backup) is backuped on remote backend with duplicity. So you can map your data volume on this container to backup it in the same time.

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

> We use [Confd](https://github.com/yunify/confd) to configure backup options.

Confd settings:
- **CONFD_PREFIX_KEY**: The prefix key use by Confd. Default is `/backup`
- **CONFD_BACKEND**: The backend used by Confd. Default is `env`
- **CONFD_NODES**: The nodes to use to access on backend. Defaukt is empty. 

The following options permit to set the backup policy :
- **BACKUP_CRON_schedule**: when you should start backup. For example, to start backup each day set `0 0 0 * * *`. Default is `0 0 0 * * *`
- **BACKUP_MODULE_database**: Allow to auto discover service and perform dump (when Know) before start backup with Duplicity. Default is `true`.
- **BACKUP_MODULE_stack**: Allow to perform export of each stack before start backup with Duplicity. Default is `true`.
- **BACKUP_MODULE_rancher-db**: Allow to perform a dump of Rancher database befaire start backup with Duplicity. Default is `true`.
- **BACKUP_DUPLICITY_source-path**: The path to backup with Duplicity. Default is `/backup`.
- **BACKUP_DUPLICITY_target-path**: The path were store backup on remote backend. The default value is `/`.
- **BACKUP_DUPLICITY_url**: this is the target URL to externalize the backup. For example, to use FTP as external backup set `ftp://login@my-ftp.com` and add environment variable `FTP_PASSWORD`. For Amazon S3, set `s3://host[:port]/bucket_name[/prefix]`. Read the ducplicity man for [all supported backend](http://duplicity.nongnu.org/duplicity.1.html#sect7). There are no default value.
- **BACKUP_DUPLICITY_options**: List of options added when start backup with Duplicity. Is usefull to add SSH options. There are no default value.
- **BACKUP_DUPLICITY_full-if-older-than**: The frequency when you should make a full backup. For example, if you should make a full backup each 7 days, set `7D`. The default value is `7D`.
- **BACKUP_DUPLICITY_remove-all-but-n-full**: How many full backup you should to keep. For example, to keep 3 full backup set `3`. The default value is `3`.
- **BACKUP_DUPLICITY_remove-all-inc-of-but-n-full**: The number of intermediate incremental backup you should keep with the full backup. For example, if you should keep only the incremental backend after the last full backup set `1`. The default value is set to `1`.
- **BACKUP_DUPLICITY_volsize**: The volume size to store the backup (in MB). The default value is `200`.
- **BACKUP_DUPLICITY_encrypt-key**: The GPG key ID to crypt / decrypt backup. You need to set `PASSPHRASE` environment to allow crypt/decrypt without user interaction. You need to mount your GPG keys on `/opt/backup/.gnupg`.
- **BACKUP_RANCHER_db_host**: The rancher database IP/DNS (needed if you should perform Rancher database dump). No default value.
- **BACKUP_RANCHER_db_port**: The rancher database port (needed if you should perform Rancher database dump). Default is `3306`.
- **BACKUP_RANCHER_db_user**: The rancher database user (needed if you should perform Rancher database dump). Default is `rancher`.
- **BACKUP_RANCHER_db_password**: The rancher database password (needed if you should perform Rancher database dump). No default value.
- **BACKUP_RANCHER_db_name**: The rancher database name (needed if you should perform Rancher database dump). Default is `rancher`.

To set the Rancher API connection prefer to add special label that generate access on the flow:
- `io.rancher.container.create_agent=true`
- `io.rancher.container.agent.role=environment`

Or you can define them manually :
- **BACKUP_RANCHER_api_url**: the API URL with your project ID
- **BACKUP_RANCHER_api_key**: the API key
- **BACKUP_RANCHER_api_secret**: the API secret key

## How to extend this

You need to dump another service before to save it (note yet supported) ? Just clone this repository and 2 files per service:
- `backup/index/service.yml`: contain the regex to identifiy the new service
- `backup/template/service.yml`: caontain the instruction about how dump the new service. We use Jinja2 templating.

Then, add your new entry (sample with MySQL):

backup/index/mysql.yml
```yaml
mysql:
  regex: "mysql"
  template: "mysql.yml"
```

Few explanation:
- **regex**: It's the regex to discover service witch must be dumped. This regex is applied to image docker used in service.
- **template**: It's the template to use to perform MySQL dump.

backup/template/mysql.yml
```yaml
image: "mysql:latest"
commands:
  {% if env.MYSQL_USER and env.MYSQL_DATABASE %}
  {# When user, password and database setted #}
  - "sh -c 'mysqldump -h {{ ip }} -u {{ env.MYSQL_USER }} {{env.MYSQL_DATABASE}} > {{ target_dir }}/{{ env.MYSQL_DATABASE }}.dump'"

  {% elif env.MYSQL_USER and not env.MYSQL_DATABASE %}
  {# When user, password setted #}
  - "sh -c 'mysqldump -h {{ ip }} -u {{ env.MYSQL_USER }} --all-databases > {{ target_dir }}/all-databases.dump'"

  {% elif not env.MYSQL_USER and env.MYSQL_DATABASE %}
  {# When database setted #}
  - "sh -c 'mysqldump -h {{ ip }} -u root {{env.MYSQL_DATABASE}} > {{ target_dir }}/{{ env.MYSQL_DATABASE }}.dump'"

  {% elif not env.MYSQL_USER and not env.MYSQL_DATABASE %}
  {# When just root setted #}
  - "sh -c 'mysqldump -h {{ ip }} -u root --all-databases > {{ target_dir }}/all-databases.dump'"

  {% endif %}
environments:
  {% if env.MYSQL_PASSWORD %}
  - MYSQL_PWD:{{ env.MYSQL_PASSWORD }}
  {% elif env.MYSQL_ROOT_PASSWORD %}
  - MYSQL_PWD:{{ env.MYSQL_ROOT_PASSWORD }}
  {% endif %}
```

Few explanation:
- **template**: It's the template to use to perform MySQL dump.
- **image**: It's the docker image to use to run the dump (generaly the latest tag). If you not add image entry, it use the service docker image.
- **commands**: It's the list of commands to launch on container to perform the dump
- **environments**: It's the list of environment variables you need to perform the dump

We use [Jinja2 templating](http://jinja.pocoo.org/docs/2.9/templates/) and we add some variable that you can use in template:
- `{{ip}}`: the IP to join the container to perform a remote dump
- `{{env.SERVICE_ENV}}`: Take the value of service environment called `SERVICE_ENV`
- `{{target_dir}}`: It's the path where store the dump (`BACKUP_PATH/dump/STACK_NAME/SERVICE_NAME`)


# Contribute

Your PR are welcome, but please use develop branch and not master.