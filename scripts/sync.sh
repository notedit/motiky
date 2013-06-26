#!/usr/bin/env sh
rsync -ravz --exclude=.hg  wwwuser@host:/data/backups /data/backups
