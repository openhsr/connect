#!/bin/bash
set -e

# Import GPG signing key
gpg --import <(echo -e "${GPG_KEY}")

# get pysmb
PYSMB_VERSION=1.1.19
curl -o /build/pysmb-${PYSMB_VERSION}.tar.gz https://pypi.python.org/packages/f9/e7/1fd7faaa946cc6b43ce85bb7a177b75a4718d9c5e291201fec00112b497c/pysmb-1.1.19.tar.gz
tar -xzf /build/pysmb-${PYSMB_VERSION}.tar.gz -C /build/
cp -R /build/openhsr-connect/packaging/${DISTRIBUTION}/${VERSION}/pysmb_debian /build/pysmb-${PYSMB_VERSION}/debian/
cd /build/pysmb-${PYSMB_VERSION}/
sed -i 's/PYSMB_VERSION/'${PYSMB_VERSION}'/g' debian/changelog
debuild --no-tgz-check

# Build .deb and sign it... 
cd /build/openhsr-connect/

# Set current version...
sed -i -e 's/version[\t ]*=[\t ]*"[0-9]*\.[0-9]*\.[0-9]*"/version="'${CONNECT_VERSION}'"/gi' setup.py
sed -i 's/CONNECT_VERSION/'$CONNECT_VERSION'/g' packaging/${DISTRIBUTION}/${VERSION}/debian/changelog

cp -R packaging/${DISTRIBUTION}/${VERSION}/debian/ debian/
debuild --no-tgz-check

# Re-Generate pool
mkdir -p /repo/conf

cat /build/openhsr-connect/packaging/${DISTRIBUTION}/*/distributions > /repo/conf/distributions

reprepro -Vb /repo/ export
reprepro -Vb /repo/ includedeb ${VERSION} /build/openhsr-connect_${CONNECT_VERSION}_all.deb
reprepro -Vb /repo/ includedeb ${VERSION} /build/python3-pysmb_${PYSMB_VERSION}_all.deb
