#!/usr/bin/env bash
set -e
set -x
cd `dirname $0`/../

usage() {
	echo "Usage: ${0} VERSION" >&2
	echo "" >&2
	echo "VERSION must be a semver like e.g. 1.23.4" >&2
	exit 255
}

# Validate version scheme
if [ "$1" != "" ] && [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]  ; then
	export VERSION="${1}"
else
	usage
fi

# Check that everything is clean and go to master branch
if [ `git status --short | wc -l` != 0 ]; then
	echo "You have uncommited changes in the repository! Aborting." >&2
	exit 2
fi

git checkout master

read -r -p "Are you shure you would like to release version '${VERSION}' on master? [y/N]" release
if ! [[ "$release" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
	echo "Release aborted" >&2
	exit 1
fi

# Bump setup.py
sed -i -e 's/version[\t ]*=[\t ]*"[0-9]*\.[0-9]*\.[0-9]*"/version="'${VERSION}'"/gi' setup.py
git add setup.py
git commit -m "Release ${VERSION}"

# Create tag
git tag ${VERSION}

read -r -p "Should the master branch and tags be pushed NOW? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
then
	git push origin master
	git push --tags
else
	echo "Please push the tag and release commit by yourself."
fi
