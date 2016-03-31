FROM quay.io/webcenter/rancher-base-image:latest
MAINTAINER Sebastien LANGOUREAUX <linuxworkgroup@hotmail.com>


# Add docker source
RUN echo 'deb http://get.docker.io/ubuntu docker main' > /etc/apt/sources.list.d/docker.list
RUN sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9

# Add duplicity to manage backup
RUN apt-get update && \
    apt-get install -y lxc-docker duplicity ncftp python-paramiko python-gobject-2 python-boto mysql-client postgresql-client





# CLEAN APT
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


#ENTRYPOINT ["duplicity"]
VOLUME ["/backup"]
#CMD ["npm", "start"]
