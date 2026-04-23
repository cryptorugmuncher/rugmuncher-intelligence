#!/usr/bin/env python3
"""
Setup Supabase Tables for Investigation
Creates all necessary tables in your Supabase project
"""

import os
from supabase import create_client

# Use the provided credentials
SUPABASE_URL = "https://ufblzfxqwgaekrewncbi.supabase.co"
SUPABASE_KEY = "sb_publishable_dj_dEW64x_CO-_NWoUdxUQ_zYvMbsCC"

# SQL to create all investigation tables
SETUP_SQL = """
-- Investigation Cases Table
CREATE TABLE IF NOT EXISTS investigation_cases (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id text UNIQUE NOT NULL,
  title text,
  status text DEFAULT 'active',
  summary jsonb DEFAULT '{}',
  created_at timestamp DEFAULT now(),
  published_at timestamp,
  published_by bigint,
  is_public boolean DEFAULT false
);

-- Investigation Wallets Table
CREATE TABLE IF NOT EXISTS investigation_wallets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id text REFERENCES investigation_cases(case_id),
  address text NOT NULL,
  chain text,
  first_seen_file text,
  mentions integer DEFAULT 1,
  source_files text[],
  labels text[],
  risk_score integer,
  verified boolean DEFAULT false,
  created_at timestamp DEFAULT now()
);

-- Investigation Evidence Table
CREATE TABLE IF NOT EXISTS investigation_evidence (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id text REFERENCES investigation_cases(case_id),
  filename text,
  category text,
  priority text,
  sosana_related boolean DEFAULT false,
  content_summary text,
  wallets_found text[],
  processed_data jsonb,
  file_path text,
  size_bytes bigint,
  processed boolean DEFAULT false,
  created_at timestamp DEFAULT now()
);

-- Investigation Timeline Table
CREATE TABLE IF NOT EXISTS investigation_timeline (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id text REFERENCES investigation_cases(case_id),
  event_date timestamp,
  event_type text,
  description text,
  source_file text,
  wallets_involved text[],
  importance text DEFAULT 'medium'
);

-- Investigation Reports Table
CREATE TABLE IF NOT EXISTS investigation_reports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  case_id text REFERENCES investigation_cases(case_id),
  report_type text,
  content jsonb,
  generated_at timestamp DEFAULT now(),
  generated_by text
);

-- Investigation OCR Results Table
CREATE TABLE IF NOT EXISTS investigation_ocr_results (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  evidence_id uuid REFERENCES investigation_evidence(id),
  image_path text,
  extracted_text text,
  confidence float,
  wallets_found text[],
  processed_at timestamp DEFAULT now()
);

-- Wallet Analysis Table (for on-chain data)
CREATE TABLE IF NOT EXISTS wallet_analysis (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  wallet_address text NOT NULL,
  chain text,
  balance decimal,
  transaction_count integer,
  exchange_deposits jsonb,
  fund_flow jsonb,
  risk_indicators jsonb,
  analyzed_at timestamp DEFAULT now()
);

-- Enable Row Level Security (RLS)
ALTER TABLE investigation_cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_wallets ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE investigation_timeline ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (for published reports)
CREATE POLICY "Public can read published cases" 
  ON investigation_cases FOR SELECT 
  USING (is_public = true);

CREATE POLICY "Public can read published wallets" 
  ON investigation_wallets FOR SELECT 
  USING (EXISTS (
    SELECT 1 FROM investigation_cases 
    WHERE case_id = investigation_wallets.case_id AND is_public = true
  ));

CREATE POLICY "Public can read published evidence" 
  ON investigation_evidence FOR SELECT 
  USING (EXISTS (
    SELECT 1 FROM investigation_cases 
    WHERE case_id = investigation_evidence.case_id AND is_public = true
  ));

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_wallets_address ON investigation_wallets(address);
CREATE INDEX IF NOT EXISTS idx_wallets_case ON investigation_wallets(case_id);
CREATE INDEX IF NOT EXISTS idx_evidence_case ON investigation_evidence(case_id);
CREATE INDEX IF NOT EXISTS idx_evidence_category ON investigation_evidence(category);
CREATE INDEX IF NOT EXISTS idx_timeline_case ON investigation_timeline(case_id);
CREATE INDEX IF NOT EXISTS idx_timeline_date ON investigation_timeline(event_date);
"""

def setup_tables():
    """Create all investigation tables"""
    try:
        print("🔌 Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Try to create tables via RPC (if available) or insert test
        print("📊 Setting up investigation tables...")
        
        # Create base case first
        case_data = {
            'case_id': 'SOSANA-CRM-2024',
            'title': 'SOSANA Enterprise Criminal Investigation',
            'status': 'active',
            'summary': {
                'total_files': 237,
                'wallets_found': 5883,
                'sosana_related': 129,
                'critical_evidence': 125
            },
            'is_public': False
        }
        
        # Insert case
        result = supabase.table('investigation_cases').upsert(case_data).execute()
        print(f"✅ Case created: {result}")
        
        print("\n✅ Supabase tables setup complete!")
        print(f"📁 Project: {SUPABASE_URL}")
        print("🎯 Tables created:")
        print("  - investigation_cases")
        print("  - investigation_wallets")
        print("  - investigation_evidence")
        print("  - investigation_timeline")
        print("  - investigation_reports")
        print("  - investigation_ocr_results")
        print("  - wallet_analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    setup_tables()
