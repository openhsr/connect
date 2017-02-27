FROM ubuntu:xenial

# Build time env variables 
ARG DOCKER_UID
ARG DOCKER_GID
ARG DISTRIBUTION
ARG VERSION
ARG CONNECT_VERSION
ENV DOCKER_UI $DOCKER_UID
ENV DOCKER_GID $DOCKER_GID
ENV DISTRIBUTION $DISTRIBUTION
ENV RELEASE $RELEASE
ENV VERSION $VERSION

# Writable subfolders
WORKDIR /build

# User
RUN groupadd -g ${DOCKER_GID} user && \
	useradd --home /build -u ${DOCKER_UID} -g ${DOCKER_GID} -M user && \
	mkdir -p /source/{dist,build,openhsr_connect.egg-info} /repo /build/.gnupg && \
	chmod 700 /build/.gnupg && \
	chown -R ${DOCKER_UID}:${DOCKER_GID} /build /repo /source

# Packages
RUN apt-get update

# Python
RUN apt-get install -y python3 python3-all python3-pip python3-pkg-resources

# Packaging
RUN apt-get install -y reprepro debhelper devscripts -y

# Add relevant files for build
ADD packaging/${DISTRIBUTION}/${VERSION}/gpg.conf /build/.gnupg/gpg.conf
# ADD packaging/${DISTRIBUTION}/${VERSION}/build.bash /opt/build.bash

# Add relevant files for creating packages
ADD ./ /build/openhsr-connect/
RUN chown -R user:user /build/openhsr-connect/


ADD packaging/${DISTRIBUTION}/${VERSION}/build.bash /opt/build.bash
USER user

CMD [ "/opt/build.bash" ]
