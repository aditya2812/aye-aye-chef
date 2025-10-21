#!/usr/bin/env python3
"""
Quick script to run database migration
"""
import boto3
import os

def run_migration():
    rds_client = boto3.client('rds-data')
    
    # These should match your CDK outputs
    db_cluster_arn = "arn:aws:rds:us-west-2:709716141648:cluster:ayeayestack-ayeayedatabase0b30717a-rpdqhqj2xiae"
    db_secret_arn = "arn:aws:secretsmanager:us-west-2:709716141648:secret:AyeAyeStackAyeAyeDatabaseSe-YDNHzu7WU4lh-Y3OiO3"
    
    try:
        print("Running database migration...")
        
        # Drop the problematic constraint
        response = rds_client.execute_statement(
            resourceArn=db_cluster_arn,
            secretArn=db_secret_arn,
            database='ayeaye',
            sql="ALTER TABLE scan_items DROP CONSTRAINT IF EXISTS uq_scan_item;"
        )
        print("✅ Dropped uq_scan_item constraint")
        
        # Add performance index
        response = rds_client.execute_statement(
            resourceArn=db_cluster_arn,
            secretArn=db_secret_arn,
            database='ayeaye',
            sql="CREATE INDEX IF NOT EXISTS idx_scan_items_scan_label ON scan_items(scan_id, label);"
        )
        print("✅ Added performance index")
        
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_migration()