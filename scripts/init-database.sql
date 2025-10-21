-- Simple database initialization for Aye Aye
-- This creates the minimal tables needed for the app to work

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- USERS table (simplified)
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,                 -- Cognito sub as string
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- SCANS table (simplified)
CREATE TABLE IF NOT EXISTS scans (
    id TEXT PRIMARY KEY,                 -- UUID as string
    user_id TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'processing',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- SCAN_ITEMS table (simplified)
CREATE TABLE IF NOT EXISTS scan_items (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    scan_id TEXT NOT NULL,
    label TEXT NOT NULL,
    fdc_id TEXT,
    confidence REAL,
    grams_est REAL,
    confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_scans_user_status ON scans(user_id, status);
CREATE INDEX IF NOT EXISTS idx_scan_items_scan ON scan_items(scan_id);

-- Insert a test user to avoid foreign key issues
INSERT INTO users (id, email) VALUES ('test-user-123', 'test@example.com') ON CONFLICT (id) DO NOTHING;