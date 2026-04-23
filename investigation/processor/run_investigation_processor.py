"""
Run Investigation Processor
Master script to process all dumped files into investigation case
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main processing pipeline"""
    
    logger.info("=" * 60)
    logger.info("RMI INVESTIGATION PROCESSOR - STARTING")
    logger.info("=" * 60)
    
    # Step 1: Categorize all files
    logger.info("\n📁 STEP 1: Categorizing dumped files...")
    from file_categorizer import get_categorizer
    
    categorizer = get_categorizer()
    report = categorizer.export_report()
    
    logger.info(f"✅ Categorized {report['total_files']} files")
    logger.info(f"   - Critical evidence: {report['summary']['critical_evidence']}")
    logger.info(f"   - High priority: {report['summary']['high_priority']}")
    logger.info(f"   - SOSANA related: {report['summary']['sosana_related_files']}")
    logger.info(f"   - Unique wallets: {report['summary']['unique_wallets_found']}")
    
    # Step 2: Process evidence
    logger.info("\n🔍 STEP 2: Processing evidence...")
    from evidence_processor import get_processor
    
    processor = get_processor()
    
    # Process each category
    all_files = []
    for category, files in categorizer.categorized.items():
        all_files.extend(files)
    
    processed_count = 0
    for file_info in all_files[:100]:  # Process first 100 for speed
        result = processor.process_file(file_info)
        if result:
            processed_count += 1
    
    logger.info(f"✅ Processed {processed_count} files into structured evidence")
    logger.info(f"   - Unique wallets in DB: {len(processor.wallets_database)}")
    logger.info(f"   - Timeline events: {len(processor.timeline_events)}")
    
    # Step 3: Build investigation case
    logger.info("\n🏗️  STEP 3: Building investigation case...")
    from case_builder import CaseBuilder
    
    case_builder = CaseBuilder(case_id="SOSANA-CRM-2024")
    case_data = case_builder.build_from_processed_evidence(
        processor.processed_evidence,
        processor.wallets_database
    )
    
    # Export case file
    case_path = case_builder.export_case_file()
    logger.info(f"✅ Case built and exported to {case_path}")
    
    # Export command center data
    cc_data = case_builder.export_command_center_data()
    logger.info(f"✅ Command center data prepared")
    
    # Step 4: Export to Supabase (if configured)
    logger.info("\n💾 STEP 4: Exporting to Supabase...")
    try:
        from supabase import create_client
        import os
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if supabase_url and supabase_key:
            supabase = create_client(supabase_url, supabase_key)
            processor.export_to_supabase(supabase)
            logger.info("✅ Exported to Supabase")
        else:
            logger.info("⚠️  Supabase not configured, skipping database export")
    except Exception as e:
        logger.warning(f"Supabase export failed: {e}")
    
    # Final report
    logger.info("\n" + "=" * 60)
    logger.info("PROCESSING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"\n📊 SUMMARY:")
    logger.info(f"   Files analyzed: {report['total_files']}")
    logger.info(f"   Evidence processed: {processed_count}")
    logger.info(f"   Wallets cataloged: {len(processor.wallets_database)}")
    logger.info(f"   Case file: {case_path}")
    logger.info(f"\n🚀 Next steps:")
    logger.info("   1. Review case file")
    logger.info("   2. Verify wallet connections")
    logger.info("   3. Trace fund flows")
    logger.info("   4. Generate reports for law enforcement")
    
    # Print key wallets for immediate attention
    if processor.wallets_database:
        logger.info(f"\n💰 TOP WALLETS BY MENTIONS:")
        sorted_wallets = sorted(
            processor.wallets_database.items(),
            key=lambda x: x[1]['mentions'],
            reverse=True
        )[:10]
        
        for addr, data in sorted_wallets:
            logger.info(f"   {addr[:20]}... - {data['mentions']} mentions")
    
    return case_data

if __name__ == "__main__":
    try:
        case = main()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
