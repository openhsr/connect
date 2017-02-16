FROM ubuntu:xenial

# Build time env variables 
ARG DOCKER_UID
ARG DOCKER_GID
ARG DISTRIBUTION
ARG VERSION
ENV DOCKER_UI $DOCKER_UID
ENV DOCKER_GID $DOCKER_GID
ENV DISTRIBUTION $DISTRIBUTION
ENV RELEASE $RELEASE

# Writable subfolders
WORKDIR /build

# Add relevant files for build
ADD packaging/$DISTRIBUTION/$VERSION/gpg.conf /build/.gnupg/gpg.conf
# ADD packaging/$DISTRIBUTION/$VERSION/build.bash /opt/build.bash

# Provisioning script
ADD packaging/$DISTRIBUTION/$VERSION/Dockerfile.bash /opt/
RUN /bin/bash /opt/Dockerfile.bash 

# TODO: add above
ADD packaging/$DISTRIBUTION/$VERSION/build.bash /opt/build.bash

# Add relevant files for creating packages
ADD ./ /src/
RUN chown -R ${DOCKER_UID}:${DOCKER_GID} /src/


CMD [ "/opt/build.bash" ]
