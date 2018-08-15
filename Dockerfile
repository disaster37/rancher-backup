FROM alpine:3.5
MAINTAINER Sebastien LANGOUREAUX <linuxworkgroup@hotmail.com>

# Application settings
ENV CONFD_PREFIX_KEY="/backup" \
    CONFD_BACKEND="env" \
    CONFD_INTERVAL="60" \
    CONFD_NODES="" \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    APP_HOME="/opt/backup" \
    APP_DATA="/backup" \
    USER=backup \
    LANG=C.UTF-8 \
    CONTAINER_NAME="rancher-backup" \
    CONTAINER_AUHTOR="Sebastien LANGOUREAUX <linuxworkgroup@hotmail.com>" \
    CONTAINER_SUPPORT="https://github.com/disaster37/rancher-backup/issues" \
    APP_WEB="https://github.com/disaster37/rancher-backup"


# Add libs & tools
COPY backup/requirements.txt /${APP_HOME}/
RUN apk update && \
    apk add python2 py-pip bash tar curl docker duplicity lftp ncftp py-paramiko py-gobject py-boto py-lockfile ca-certificates librsync py-cryptography py-cffi rsync  &&\
    apk add --no-cache --virtual .build-deps gcc python2-dev linux-headers musl-dev &&\
    pip install --upgrade pip &&\
    pip install azure.storage==0.20.0 pyrax dropbox mediafire urllib3 gdata requests requests_oauthlib python-swiftclient python-keystoneclient  &&\
    pip install -r "${APP_HOME}/requirements.txt" &&\
    apk del .build-deps &&\
    rm /var/cache/apk/*


# Install go-cron
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz \
    | tar -x -C /usr/local/bin

# Install confd
ENV CONFD_VERSION="0.14.0" \
    CONFD_HOME="/opt/confd"
RUN mkdir -p "${CONFD_HOME}/etc/conf.d" "${CONFD_HOME}/etc/templates" "${CONFD_HOME}/log" "${CONFD_HOME}/bin" &&\
    curl -Lo "${CONFD_HOME}/bin/confd" "https://github.com/kelseyhightower/confd/releases/download/v${CONFD_VERSION}/confd-${CONFD_VERSION}-linux-amd64" &&\
    chmod +x "${CONFD_HOME}/bin/confd"

# Install s6-overlay
RUN curl -sL https://github.com/just-containers/s6-overlay/releases/download/v1.19.1.1/s6-overlay-amd64.tar.gz \
    | tar -zx -C /


# Copy files
COPY root /
COPY backup/src/ /${APP_HOME}/
COPY backup/config /${APP_HOME}/config
RUN mkdir -p /var/log/backup ${APP_DATA} &&\
    adduser -D -h ${APP_HOME} -G docker -s /bin/sh ${USER} &&\
    chown -R ${USER} ${APP_HOME} &&\
    chown -R ${USER} ${APP_DATA} &&\
    chown -R ${USER} /var/log/backup

# CLEAN Image
RUN rm -rf /tmp/* /var/tmp/*

VOLUME ["${APP_DATA}"]
WORKDIR "${APP_HOME}"
CMD ["/init"]
