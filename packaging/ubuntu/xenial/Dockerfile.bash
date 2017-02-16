#!/bin/bash
set -e
# Required env variables:
# - DOCKER_UID: UID of your desktop user
# - DOCKER_GID: GID of your desktop user

# User
groupadd -g ${DOCKER_GID} user
useradd --home /build -u ${DOCKER_UID} -g ${DOCKER_GID} -M user
mkdir -p /source/{dist,build,openhsr_connect.egg-info} /repo /build/.gnupg
chmod 700 /build/.gnupg
chown -R ${DOCKER_UID}:${DOCKER_GID} /build /repo /source

# Packages
apt-get update

# Python
apt-get install -y python3 python3-pip python3-pkg-resources

# Packaging
apt-get install -y dpkg-dev dpkg-sig reprepro
