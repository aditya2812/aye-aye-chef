#!/usr/bin/env node

const { RDSData } = require('@aws-sdk/client-rds-data');
const fs = require('fs');

const rdsData = new RDSData({ region: 'us-west-2' });

const DB_CLUSTER_ARN = 'arn:aws:rds:us-west-2:709716141648:cluster:ayeayestack-ayeayedatabase0b30717a-rpdqhqj2xiae';
const DB_SECRET_ARN = 'arn:aws:secretsmanager:us-west-2:709716141648:secret:AyeAyeStackAyeAyeDatabaseSe-YDNHzu7WU4lh-Y3OiO3';

async function executeSQL(sql) {
  try {
    const result = await rdsData.executeStatement({
      resourceArn: DB_CLUSTER_ARN,
      secretArn: DB_SECRET_ARN,
      database: 'ayeaye',
      sql: sql
    });
    return result;
  } catch (error) {
    console.error(`Error executing SQL: ${sql.substring(0, 50)}...`);
    console.error(error.message);
    throw error;
  }
}

async function setupDatabase() {
  console.log('🗄️  Setting up Aye Aye database schema...\n');

  const statements = [
    'CREATE EXTENSION IF NOT EXISTS "pgcrypto"',
    
    `CREATE TABLE IF NOT EXISTS users (
      id UUID PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      diets TEXT[] DEFAULT '{}',
      cuisines TEXT[] DEFAULT '{}',
      allergens TEXT[] DEFAULT '{}',
      created_at TIMESTAMPTZ DEFAULT now()
    )`,
    
    `CREATE TABLE IF NOT EXISTS scans (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID NOT NULL,
      s3_key TEXT NOT NULL,
      status TEXT NOT NULL CHECK (status IN ('processing','ready','confirmed','completed')) DEFAULT 'processing',
      created_at TIMESTAMPTZ DEFAULT now()
    )`,
    
    'CREATE INDEX IF NOT EXISTS idx_scans_user_status ON scans(user_id, status)',
    'CREATE INDEX IF NOT EXISTS idx_scans_created ON scans(created_at DESC)',
    
    `CREATE TABLE IF NOT EXISTS scan_items (
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
    )`,
    
    'CREATE INDEX IF NOT EXISTS idx_scan_items_scan ON scan_items(scan_id)',
    'CREATE INDEX IF NOT EXISTS idx_scan_items_scan_confirmed ON scan_items(scan_id, confirmed)',
    
    `CREATE TABLE IF NOT EXISTS recipes (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      scan_id UUID REFERENCES scans(id) ON DELETE SET NULL,
      title TEXT NOT NULL,
      json_payload JSONB NOT NULL,
      nutrition JSONB NOT NULL,
      facts_snapshot JSONB,
      created_at TIMESTAMPTZ DEFAULT now()
    )`,
    
    'CREATE INDEX IF NOT EXISTS idx_recipes_user ON recipes(user_id, created_at DESC)',
    'CREATE INDEX IF NOT EXISTS idx_recipes_created ON recipes(created_at DESC)',
    
    `CREATE TABLE IF NOT EXISTS meals (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
      servings INTEGER NOT NULL CHECK (servings >= 1),
      logged_at TIMESTAMPTZ DEFAULT now()
    )`,
    
    'CREATE INDEX IF NOT EXISTS idx_meals_user_time ON meals(user_id, logged_at DESC)',
    
    `CREATE TABLE IF NOT EXISTS agent_runs (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID REFERENCES users(id) ON DELETE SET NULL,
      intent TEXT,
      tool_calls JSONB,
      cost JSONB,
      outcome TEXT,
      created_at TIMESTAMPTZ DEFAULT now()
    )`,
    
    'CREATE INDEX IF NOT EXISTS idx_agent_runs_time ON agent_runs(created_at DESC)'
  ];

  for (let i = 0; i < statements.length; i++) {
    const sql = statements[i];
    console.log(`${i + 1}/${statements.length}: ${sql.substring(0, 60)}...`);
    
    try {
      await executeSQL(sql);
      console.log('   ✅ Success\n');
    } catch (error) {
      console.log('   ❌ Failed\n');
      if (!error.message.includes('already exists')) {
        throw error;
      }
    }
  }

  console.log('✅ Database schema setup complete!');
  console.log('\n📋 Tables created:');
  console.log('   - users (user profiles and preferences)');
  console.log('   - scans (image scan records)');
  console.log('   - scan_items (detected ingredients)');
  console.log('   - recipes (generated recipes)');
  console.log('   - meals (optional meal logging)');
  console.log('   - agent_runs (optional telemetry)');
}

setupDatabase().catch(console.error);