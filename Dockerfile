FROM jpetazzo/dind:latest
MAINTAINER Sebastien LANGOUREAUX <linuxworkgroup@hotmail.com>

ENV BACKUP_DIR /backup

# Add libs & tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends python-all python-yaml python-pip duplicity lftp ncftp python-paramiko python-gobject-2 python-boto && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Add rancher api
RUN pip install rancher_metadata

# Install go-cron
RUN curl -sL https://github.com/michaloo/go-cron/releases/download/v0.0.2/go-cron.tar.gz \
    | tar -x -C /usr/local/bin

# Add backup script
COPY assets/* /app/

# CLEAN Image
RUN rm -rf /tmp/* /var/tmp/*

VOLUME ["${BACKUP_DIR}"]

#ENTRYPOINT ["duplicity"]
