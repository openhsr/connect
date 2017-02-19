#!/bin/bash
FEDORA_VERSION=25
SPECDIR="/src/packaging/fedora/${FEDORA_VERSION}/"

###############################################################################
# Build connect
###############################################################################
pushd /src > /dev/null
  python3 ./setup.py sdist --dist-dir=$SPECDIR
popd > /dev/null

pushd $SPECDIR >/dev/null
  rpmdev-bumpspec -u openhsr -n "$VERSION" openhsr-connect.spec
  fedpkg --release f${FEDORA_VERSION} local
popd > /dev/null

mkdir -p /repo/{i386,x86_64,SRPMS}

###############################################################################
# Build pysmb
###############################################################################
PYSMB_VERSION=1.1.19
pushd ${SPECDIR}pysmb/ > /dev/null
  curl -o pysmb-${PYSMB_VERSION}.tar.gz https://pypi.python.org/packages/f9/e7/1fd7faaa946cc6b43ce85bb7a177b75a4718d9c5e291201fec00112b497c/pysmb-1.1.19.tar.gz
  rpmdev-bumpspec -u openhsr -n "$PYSMB_VERSION" pysmb.spec
  fedpkg --release f${FEDORA_VERSION} local
popd > /dev/null

###############################################################################
# Package signing
###############################################################################
cat <<'__EOF__' > /build/.rpmmacros
%_signature gpg
%_gpg_path /build/.gnupg
%_gpg_name 0x04969FB29CABC357
__EOF__

gpg --import <<__EOF__
${GPG_KEY}
__EOF__

find $SPECDIR -name '*.rpm' -exec rpm --addsign {} \;

###############################################################################
# Repositories
###############################################################################
# copy files to the repositories:
find $SPECDIR -name '*.src.rpm' -exec cp {} /repo/SRPMS \;

for arch in i386 x86_64
  do find $SPECDIR -name '*.noarch.rpm' -exec cp {} /repo/${arch} \;
done

for arch in SRPMS i386 x86_64; do
    pushd /repo/${arch} >/dev/null
      createrepo_c .
    popd >/dev/null 2>&1
done
