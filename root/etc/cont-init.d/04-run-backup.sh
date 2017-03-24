#!/usr/bin/with-contenv bash

s6-setuidgid ${USER} python "${APP_HOME}/backup.py"