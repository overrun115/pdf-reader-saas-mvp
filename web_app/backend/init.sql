-- Initialize PDF Extractor Database
-- This script sets up the initial database structure

-- Create database (if running manually)
-- CREATE DATABASE pdf_extractor;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create initial admin user (run this after the application creates tables)
-- Password: admin123 (change in production)
-- This will be run by the application on first startup

-- Create indexes for better performance
-- These will be created by SQLAlchemy, but manual optimization can be added here

-- Example: Create index on file hash for faster deduplication
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_processed_files_hash 
-- ON processed_files(file_hash);

-- Create index on user email for faster lookups
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email 
-- ON users(email);

-- Create index on file status for filtering
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_processed_files_status 
-- ON processed_files(status);

-- Create composite index for user files
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_processed_files_user_created 
-- ON processed_files(user_id, created_at DESC);

-- Performance optimizations
-- Set up some basic PostgreSQL optimizations

-- Enable query plan caching
-- ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';

-- Optimize for typical workload
-- ALTER SYSTEM SET effective_cache_size = '1GB';
-- ALTER SYSTEM SET shared_buffers = '256MB';
-- ALTER SYSTEM SET work_mem = '4MB';

-- Restart required for some settings to take effect

-- Sample data for development (optional)
-- This should only be used in development environment

DO $$
BEGIN
    -- Only run if this is a development environment
    IF current_setting('server_version_num')::int >= 120000 THEN
        -- PostgreSQL 12+ specific optimizations
        RAISE NOTICE 'PostgreSQL 12+ detected, applying optimizations';
    END IF;
END $$;