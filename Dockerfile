FROM jpetazzo/dind:latest
MAINTAINER Sebastien LANGOUREAUX <linuxworkgroup@hotmail.com>

# Application settings
ENV CONFD_PREFIX_KEY="/backup" \
    CONFD_BACKEND="env" \
    CONFD_INTERVAL="60" \
    CONFD_NODES="" \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    APP_HOME="/opt/backup" \
    APP_DATA="/backup" \
    USER=kibana \
    CONTAINER_NAME="rancher-backup" \
    CONTAINER_AUHTOR="Sebastien LANGOUREAUX <linuxworkgroup@hotmail.com>" \
    CONTAINER_SUPPORT="https://github.com/disaster37/rancher-backup/issues" \
    APP_WEB="https://github.com/disaster37/rancher-backup"


# Add libs & tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends python-all python-yaml python-pip duplicity lftp ncftp python-paramiko python-gobject-2 python-boto && \
    pip install Jinja2 &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add rancher api
RUN pip install rancher_metadata
RUN pip install Cattle

# Install go-cron
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz \
    | tar -x -C /usr/local/bin

# Install confd
ENV CONFD_VERSION="v0.13.1" \
    CONFD_HOME="/opt/confd"
ADD https://github.com/yunify/confd/releases/download/${CONFD_VERSION}/confd-linux-amd64.tar.gz ${CONFD_HOME}/bin/
RUN mkdir -p "${CONFD_HOME}/etc/conf.d" "${CONFD_HOME}/etc/templates" "${CONFD_HOME}/log" &&\
    tar -xvzf "${CONFD_HOME}/bin/confd-linux-amd64.tar.gz" -C "${CONFD_HOME}/bin/" &&\
    rm "${CONFD_HOME}/bin/confd-linux-amd64.tar.gz"

# Install s6-overlay
ADD https://github.com/just-containers/s6-overlay/releases/download/v1.19.1.1/s6-overlay-amd64.tar.gz /tmp/
RUN gunzip -c /tmp/s6-overlay-amd64.tar.gz | tar -xf - -C /

# Copy files
COPY root /
COPY backup/src/ /${APP_HOME}/
COPY backup/config /${APP_HOME}/config
RUN mkdir -p /var/log/backup

# CLEAN Image
RUN rm -rf /tmp/* /var/tmp/*

VOLUME ["${APP_HOME}"]
WORKDIR "${APP_HOME}"
CMD ["/init"]
