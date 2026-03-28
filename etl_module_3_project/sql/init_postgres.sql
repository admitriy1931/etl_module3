-- ============================================
-- Bootstrap: create ETL user, database, schemas
-- Runs as superuser (airflow) during container init
-- ============================================

CREATE USER etl_user WITH PASSWORD 'etl_password';
CREATE DATABASE etl_project OWNER etl_user;

\connect etl_project

CREATE SCHEMA IF NOT EXISTS staging AUTHORIZATION etl_user;
CREATE SCHEMA IF NOT EXISTS dwh     AUTHORIZATION etl_user;
CREATE SCHEMA IF NOT EXISTS mart    AUTHORIZATION etl_user;

GRANT ALL ON SCHEMA staging TO etl_user;
GRANT ALL ON SCHEMA dwh     TO etl_user;
GRANT ALL ON SCHEMA mart    TO etl_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT ALL ON TABLES TO etl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA dwh     GRANT ALL ON TABLES TO etl_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA mart    GRANT ALL ON TABLES TO etl_user;
