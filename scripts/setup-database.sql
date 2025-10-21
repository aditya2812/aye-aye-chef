-- Aye Aye Database Schema
-- Run this after the Aurora cluster is created

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- USERS table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,                 -- Cognito sub
    email TEXT UNIQUE NOT NULL,
    diets TEXT[] DEFAULT '{}',
    cuisines TEXT[] DEFAULT '{}',
    allergens TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- SCANS table
CREATE TABLE IF NOT EXISTS scans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    s3_key TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('processing','ready','confirmed','completed')) DEFAULT 'processing',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scans_user_status ON scans(user_id, status);
CREATE INDEX IF NOT EXISTS idx_scans_created ON scans(created_at DESC);

-- Add foreign key constraint (can be added later if needed)
-- ALTER TABLE scans ADD CONSTRAINT fk_scans_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- SCAN_ITEMS table
CREATE TABLE IF NOT EXISTS scan_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scan_id UUID NOT NULL REFERENCES scans(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    fdc_id TEXT,
    confidence REAL,
    grams_est REAL,
    grams REAL,
    confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT scan_items_confirmed_requires_grams CHECK (confirmed = FALSE OR grams IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_scan_items_scan ON scan_items(scan_id);
CREATE INDEX IF NOT EXISTS idx_scan_items_scan_confirmed ON scan_items(scan_id, confirmed);

-- RECIPES table
CREATE TABLE IF NOT EXISTS recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scan_id UUID REFERENCES scans(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    json_payload JSONB NOT NULL,
    nutrition JSONB NOT NULL,           -- {totals_per_recipe, per_serving}
    facts_snapshot JSONB,               -- [{"fdc_id":"05064","per_100g":{...}}, ...]
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_recipes_user ON recipes(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recipes_created ON recipes(created_at DESC);

-- MEALS table (optional)
CREATE TABLE IF NOT EXISTS meals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    servings INTEGER NOT NULL CHECK (servings >= 1),
    logged_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_meals_user_time ON meals(user_id, logged_at DESC);

-- AGENT_RUNS table (optional telemetry)
CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    intent TEXT,
    tool_calls JSONB,
    cost JSONB,
    outcome TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_time ON agent_runs(created_at DESC);