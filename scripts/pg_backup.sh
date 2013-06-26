#!/bin/bash
export PGPASSWORD='password'
pg_dump -Uuser -hlocalhost -a -f /data/backups/`date +%F`.sql database
