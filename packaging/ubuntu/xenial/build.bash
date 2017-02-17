#!/bin/bash

# Import GPG signing key
gpg --import <<__EOF__
${GPG_KEY}
__EOF__

# Build .deb and sign it... 
cd /build/openhsr-connect/

# Set current version...
sed -i 's/CONNECT_VERSION/'$CONNECT_VERSION'/g' packaging/${DISTRIBUTION}/${VERSION}/debian/changelog

cp -R packaging/${DISTRIBUTION}/${VERSION}/debian/ debian/
debuild --no-tgz-check

# Re-Generate pool
rm -Rf /repo/*
mkdir -p /repo/conf

cat <<'__EOF__' > /repo/conf/distributions
Origin: pool.openhsr.ch
Label: openHSR Ubuntu Xenial Pool
Suite: xenial
Codename: xenial
Version: 16.04
Architectures: i386 amd64 source
Components: main
Description: openHSR Ubuntu Xenial Pool
SignWith: Yes
__EOF__

reprepro -Vb /repo/ export
reprepro -Vb /repo/ includedeb xenial /build/openhsr-connect_${CONNECT_VERSION}_all.deb



