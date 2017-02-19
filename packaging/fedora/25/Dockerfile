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

# Add relevant files for build
ADD packaging/${DISTRIBUTION}/${VERSION}/gpg.conf /build/.gnupg/gpg.conf
#ADD packaging/${DISTRIBUTION}/${VERSION}/build.bash /opt/build.bash

# Provisioning script
ADD packaging/${DISTRIBUTION}/${VERSION}/Dockerfile.bash /opt/
RUN /bin/bash /opt/Dockerfile.bash 

# Add relevant files for creating packages
ADD ./ /src/
RUN chown -R user:user /src/
ADD packaging/${DISTRIBUTION}/${VERSION}/build.bash /opt/build.bash

USER user
CMD [ "/opt/build.bash" ]
