#!/usr/bin/env bash
set -e
cd `dirname $0`/../

# Distill current version number
description(){
	git describe --tags --long | cut --delimiter '-' --fields $1
}

TAG=`description 1`
DISTANCE=`description 2`
HASH=`description 3`
DATE=`date +'%Y%m%d'`

if [ $DISTANCE == 0 ]; then
	# Production release
	echo ${TAG}
else
	# Development release
	echo ${TAG}.${DATE}git${HASH}
fi
