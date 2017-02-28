#!/usr/bin/env bash

# Abort if a command fails!
set -e
echo "Starting deployment configuration..."
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [ ! -n "$HOST" ];then
    echo "missing option \"HOST\", aborting"
    exit 1
fi
if [ ! -n "$USER" ];then
    echo  "missing option \"USER\", aborting"
    exit 1
fi
if [ ! -n "$PASSWORD" ];then
    echo  "missing option \"PASSWORD\", aborting"
    exit 1
fi

if [ ! -n "$DIR_REMOTE" ];then
    echo  "missing option \"DIR_REMOTE\", aborting"
    exit 1
fi

# Go into the DIR_LOCAL, the root to upload data from
cd "${DIR}/${DIR_LOCAL}"


echo "Uploading..."
lftp -e "
open $HOST
set ssl:verify-certificate no
set ssl:check-hostname off
set cmd:fail-exit true
user $USER $PASSWORD
cd $DIR_REMOTE
mirror --reverse --delete --ignore-time --verbose --parallel . .
bye
"

# Complete!
echo "Done!"
exit 0
