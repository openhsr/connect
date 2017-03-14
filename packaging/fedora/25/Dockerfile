FROM fedora:25

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

# Python
RUN dnf install -y python3{,-devel,-pip,-setuptools,-setuptools_scm}

# Packaging
RUN dnf install -y fedora-packager fedora-review gnupg rpm-sign

# User (this is dependent on the packaging)
RUN groupadd -g ${DOCKER_GID} user && \
	useradd --home /build -u ${DOCKER_UID} -g ${DOCKER_GID} -G mock -M user && \
	mkdir -p /source/{dist,build,openhsr_connect.egg-info} /repo /build/.gnupg && \
	chmod 700 /build/.gnupg && \
	chown -R user:user /build /repo /source

# Add relevant files for build
ADD packaging/${DISTRIBUTION}/${VERSION}/gpg.conf /build/.gnupg/gpg.conf
ADD packaging/${DISTRIBUTION}/${VERSION}/build.bash /opt/build.bash

# Add relevant files for creating packages
ADD ./ /src/
RUN chown -R user:user /src/

USER user
CMD [ "/opt/build.bash" ]
