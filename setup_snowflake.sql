-- Snowflake Setup Script for EVE
-- Run this in Snowflake Worksheets after connecting

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS EVE_DB;

-- Step 2: Create Schema
CREATE SCHEMA IF NOT EXISTS EVE_DB.EVE_SCHEMA;

-- Step 3: Create Warehouse (for compute)
CREATE WAREHOUSE IF NOT EXISTS EVE_WH
  WITH WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE
  INITIALLY_SUSPENDED = TRUE;

-- Step 4: Grant Permissions
GRANT ALL ON DATABASE EVE_DB TO ROLE ACCOUNTADMIN;
GRANT ALL ON SCHEMA EVE_DB.EVE_SCHEMA TO ROLE ACCOUNTADMIN;
GRANT USAGE ON WAREHOUSE EVE_WH TO ROLE ACCOUNTADMIN;

-- Step 5: Use the resources
USE DATABASE EVE_DB;
USE SCHEMA EVE_DB.EVE_SCHEMA;
USE WAREHOUSE EVE_WH;

-- Step 6: Create the conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(36) DEFAULT UUID_STRING(),
    user_id VARCHAR(255),
    transcript TEXT,
    summary TEXT,
    tasks TEXT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (id)
);

-- Verify setup
SELECT 'Database created: ' || CURRENT_DATABASE() as status;
SELECT 'Schema created: ' || CURRENT_SCHEMA() as status;
SELECT 'Warehouse: EVE_WH' as status;

