#!/bin/bash
set -e
FEDORA_VERSION=25
SPECDIR="/src/packaging/fedora/${FEDORA_VERSION}/"

###############################################################################
# Build connect
###############################################################################
pushd /src > /dev/null
  sed -i -e 's/version[\t ]*=[\t ]*"[0-9]*\.[0-9]*\.[0-9]*"/version="'${CONNECT_VERSION}'"/gi' setup.py
  python3 ./setup.py sdist --dist-dir=$SPECDIR
popd > /dev/null

pushd $SPECDIR >/dev/null
  rpmdev-bumpspec -u openhsr -n "$CONNECT_VERSION" openhsr-connect.spec

  fedpkg --release f${FEDORA_VERSION} local
popd > /dev/null

mkdir -p /repo/${FEDORA_VERSION}/{i386,x86_64,SRPMS}

###############################################################################
# Build pysmb
###############################################################################
PYSMB_VERSION=1.1.19
pushd ${SPECDIR}pysmb/ > /dev/null
  curl -o pysmb-${PYSMB_VERSION}.tar.gz https://pypi.python.org/packages/f9/e7/1fd7faaa946cc6b43ce85bb7a177b75a4718d9c5e291201fec00112b497c/pysmb-1.1.19.tar.gz
  rpmdev-bumpspec -u openhsr -n "$PYSMB_VERSION" pysmb.spec
  fedpkg --release f${FEDORA_VERSION} local
popd > /dev/null

JSONSCHEMA_VERSION=2.6.0
pushd ${SPECDIR}jsonschema > /dev/null
  curl -o jsonschema-${JSONSCHEMA_VERSION}.tar.gz https://pypi.python.org/packages/58/b9/171dbb07e18c6346090a37f03c7e74410a1a56123f847efed59af260a298/jsonschema-${JSONSCHEMA_VERSION}.tar.gz
  rpmdev-bumpspec -u openhsr -n "$JSONSCHEMA_VERSION" jsonschema.spec
  fedpkg --release f${FEDORA_VERSION} local
popd > /dev/null

###############################################################################
# Package signing
###############################################################################
cat <<'__EOF__' > /build/.rpmmacros
%_signature gpg
%_gpg_path /build/.gnupg
%_gpg_name 0x5AE4B07A1957D46D
__EOF__

gpg --import <(echo -e "${GPG_KEY}")

find $SPECDIR -name '*.rpm' -exec rpm --addsign {} \;

###############################################################################
# Repositories
###############################################################################
# copy files to the repositories:
find $SPECDIR -name '*.src.rpm' -exec cp {} /repo/${FEDORA_VERSION}/SRPMS \;

for arch in i386 x86_64
  do find $SPECDIR -name '*.noarch.rpm' -exec cp {} /repo/${FEDORA_VERSION}/${arch} \;
done

for arch in SRPMS i386 x86_64; do
    pushd /repo/${FEDORA_VERSION}/${arch} >/dev/null
      createrepo_c --update .
      rm -rf .repodata
    popd >/dev/null 2>&1
done
