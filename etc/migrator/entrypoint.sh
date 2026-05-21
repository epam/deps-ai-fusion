#!/usr/bin/env bash

if [ -z "$DATABASE_HOST" ] || [ -z "$DATABASE_PORT" ] || [ -z "$DATABASE_DB" ] || [ -z "$DATABASE_USER" ] || [ -z "$DATABASE_PASSWORD" ]; then
    echo "Please, specify DB credentials DATABASE_HOST DATABASE_PORT DATABASE_DB DATABASE_USER DATABASE_PASSWORD"
    exit 1;
fi

MAX_RETRIES=10
RETRY_DELAY=5
RETRY_COUNT=0

until PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "postgres" <<- EOSQL
    create database "$DATABASE_DB";
    grant all privileges on database "$DATABASE_DB" to "$DATABASE_USER";
EOSQL
do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ "$RETRY_COUNT" -ge "$MAX_RETRIES" ]; then
        echo "Failed to connect to the database after $MAX_RETRIES attempts. Exiting."
        exit 1
    fi
    echo "Database is not ready yet. Retrying in $RETRY_DELAY seconds... (Attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep $RETRY_DELAY
done

LIQUIBASE_URL="jdbc:postgresql://$DATABASE_HOST:$DATABASE_PORT/$DATABASE_DB"

exec ./wait-for.sh $DATABASE_HOST:$DATABASE_PORT -- echo "N" | /liquibase/liquibase \
    --driver="org.postgresql.Driver" \
    --changeLogFile="$MASTER_CHANGELOG" \
    --logLevel="warning" \
    --url="$LIQUIBASE_URL" \
    --username="$DATABASE_USER" \
    --password="$DATABASE_PASSWORD" \
    "$@"

