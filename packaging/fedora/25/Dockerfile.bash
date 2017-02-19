#!/bin/bash
set -e
# Required env variables:
# - DOCKER_UID: UID of your desktop user
# - DOCKER_GID: GID of your desktop user
FEDORA_VERSION=25

# Python
dnf install -y python3{,-devel,-pip,-setuptools,-setuptools_scm}

# Packaging
dnf install -y fedora-packager fedora-review gnupg rpm-sign

# User
groupadd -g ${DOCKER_GID} user
useradd --home /build -u ${DOCKER_UID} -g ${DOCKER_GID} -G mock -M user
mkdir -p /source/{dist,build,openhsr_connect.egg-info} /repo /build/.gnupg
chmod 700 /build/.gnupg
chown -R user:user /build /repo /source
