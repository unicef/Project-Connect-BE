#!/bin/sh

set -e

# Perform all actions as $POSTGRES_USER
export PGUSER="$POSTGRES_USER"

psql "$POSTGRES_DB" < /postgres_data/devDB
