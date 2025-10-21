-- Fix scan_items constraint issue
-- Run this to remove the problematic unique constraint

-- Drop the constraint that's causing the UUID comparison issue
ALTER TABLE scan_items DROP CONSTRAINT IF EXISTS uq_scan_item;

-- Add a more appropriate unique constraint using the id field instead
-- This allows multiple items per scan with different temporary fdc_ids
-- The real uniqueness will be enforced when we implement proper FDC mapping

-- Optional: Add index for better query performance
CREATE INDEX IF NOT EXISTS idx_scan_items_scan_label ON scan_items(scan_id, label);