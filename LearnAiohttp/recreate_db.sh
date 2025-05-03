# export PGPASSWORD=secret
# psql --host 127.0.0.1 -p 5431 -U swapi -d postgres -c "drop database swapi"
# psql --host 127.0.0.1 -p 5431 -U swapi -d postgres -c "create database swapi"

#!/bin/bash

# --- PostgreSQL Database Configuration ---
export POSTGRES_USER="advertisement_user"
export POSTGRES_PASSWORD="strong_password123"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5431"
export POSTGRES_DB="advert_db"

# Удаление старой базы данных
PGPASSWORD=$POSTGRES_PASSWORD psql --host=$POSTGRES_HOST --port=$POSTGRES_PORT --username=$POSTGRES_USER --dbname=postgres -c "DROP DATABASE IF EXISTS $POSTGRES_DB;"

# Создание новой базы данных
PGPASSWORD=$POSTGRES_PASSWORD psql --host=$POSTGRES_HOST --port=$POSTGRES_PORT --username=$POSTGRES_USER --dbname=postgres -c "CREATE DATABASE $POSTGRES_DB;"
