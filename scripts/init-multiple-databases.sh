#!/bin/bash
set -e
set -u

# Create additional databases for N8n integration
function create_user_and_database() {
    local database=$1
    local user=$2
    local password=$3
    echo "Creating user '$user' and database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        CREATE USER $user WITH PASSWORD '$password';
        CREATE DATABASE $database;
        GRANT ALL PRIVILEGES ON DATABASE $database TO $user;
        GRANT CONNECT ON DATABASE $database TO $user;
        GRANT USAGE ON SCHEMA public TO $user;
        GRANT CREATE ON SCHEMA public TO $user;
        ALTER DATABASE $database OWNER TO $user;
EOSQL
}

if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    
    # Create N8n database and user
    create_user_and_database "n8n_db" "n8n_user" "n8n_password"
    
    echo "Multiple databases created successfully"
else
    echo "No additional databases to create"
fi