#!/usr/bin/with-contenv bash

cat << EOF > ${CONFD_HOME}/etc/conf.d/rancher-backup.yml.toml
[template]
prefix = "${CONFD_PREFIX_KEY}"
src = "rancher-backup.yml.tmpl"
dest = "${APP_HOME}/config/rancher-backup.yml"
uid = 1001
gid = 1001
mode = "0644"
keys = [
  "/duplicity",
  "/rancher",
  "/module",
  "/cron"
]
EOF

cat << EOF > ${CONFD_HOME}/etc/conf.d/env.sh.toml
[template]
prefix = "${CONFD_PREFIX_KEY}"
src = "env.sh.tmpl"
dest = "${APP_HOME}/config/env.sh"
uid = 1001
gid = 1001
mode = "0644"
keys = [
  "/duplicity",
]
EOF


cat << EOF > ${CONFD_HOME}/etc/conf.d/cron.toml
[template]
prefix = "${CONFD_PREFIX_KEY}"
src = "cron.tmpl"
dest = "/etc/services.d/cron/run"
mode = "0644"
keys = [
  "/cron",
]
EOF
