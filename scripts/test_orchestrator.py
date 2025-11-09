#!/usr/bin/env python3
"""
CLI script to test the full orchestrator workflow.

Usage: python scripts/test_orchestrator.py "research topic"
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from loguru import logger
from mediscout.orchestrator import ResearchOrchestrator
from mediscout.config import get_settings


def main():
    """Test the complete research orchestrator workflow."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_orchestrator.py 'research topic'")
        print("Example: python scripts/test_orchestrator.py 'metformin efficacy for diabetes'")
        sys.exit(1)
    
    research_topic = sys.argv[1]
    
    # Check configuration
    settings = get_settings()
    
    print("\n" + "="*80)
    print("MEDISCOUT ORCHESTRATOR TEST")
    print("="*80)
    
    print("\n📋 Configuration Check:")
    print(f"  OpenRouter API Key: {'✓ Configured' if settings.has_openrouter_key else '✗ Missing'}")
    print(f"  LangSmith Tracing: {'✓ Enabled' if settings.langsmith_enabled else '✗ Disabled'}")
    print(f"  LLM Model: {settings.openrouter_model}")
    print(f"  PubMed Email: {settings.pubmed_email}")
    
    if not settings.has_openrouter_key:
        print("\n❌ OpenRouter API key not found!")
        print("   Set OPENROUTER_API_KEY in your .env file")
        sys.exit(1)
    
    print(f"\n🔬 Research Topic: '{research_topic}'")
    print("\n⚙️  Initializing orchestrator...")
    
    try:
        orchestrator = ResearchOrchestrator()
        print("✓ Orchestrator initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize orchestrator: {e}")
        logger.exception("Initialization failed")
        sys.exit(1)
    
    print("\n🚀 Running research workflow...")
    print("="*80)
    
    try:
        result = orchestrator.run_research(research_topic)
        
        print("\n" + "="*80)
        print("WORKFLOW RESULTS")
        print("="*80)
        
        # Display workflow stages
        print(f"\n📊 Final Stage: {result.get('current_stage', 'unknown')}")
        print(f"⏱️  Processing Time: {result.get('processing_time_seconds', 0):.2f}s")
        
        # Query validation
        if result.get('query_validation'):
            qv = result['query_validation']
            print(f"\n🔍 Query Validation:")
            print(f"   Valid: {qv.is_valid}")
            print(f"   Refined: {qv.refined_query}")
            if qv.medical_terms:
                print(f"   Medical Terms: {', '.join(qv.medical_terms)}")
        
        # Retrieval results
        if result.get('retrieval_result'):
            rr = result['retrieval_result']
            print(f"\n📚 Retrieval:")
            print(f"   Total Documents: {rr.total_count}")
            print(f"   User Documents: {len(rr.user_documents)}")
            print(f"   PubMed Documents: {len(rr.pubmed_documents)}")
            print(f"   Sources Used: {', '.join(rr.sources_used)}")
            print(f"   Retrieval Time: {rr.retrieval_time_seconds:.2f}s")
        
        # Analysis results
        if result.get('analysis_results'):
            analyses = result['analysis_results']
            print(f"\n🔬 Analysis:")
            print(f"   Documents Analyzed: {len(analyses)}")
            
            avg_reliability = sum(a.reliability_score for a in analyses) / len(analyses) if analyses else 0
            print(f"   Avg Reliability: {avg_reliability:.2f}")
            
            total_findings = sum(len(a.key_findings) for a in analyses)
            print(f"   Total Key Findings: {total_findings}")
            
            contradictions = [a for a in analyses if a.contradictions]
            if contradictions:
                print(f"   Documents with Contradictions: {len(contradictions)}")
        
        # Report
        if result.get('final_report_markdown'):
            report = result['final_report_markdown']
            print(f"\n📄 Report Generated:")
            print(f"   Length: {len(report)} characters")
            print(f"   Sections: {report.count('##')} headers")
            
            # Save report
            output_file = Path("test_report.md")
            output_file.write_text(report)
            print(f"   Saved to: {output_file.absolute()}")
            
            # Print first part of report
            print(f"\n📖 Report Preview (first 500 chars):")
            print("-" * 80)
            print(report[:500])
            print("-" * 80)
        
        # Errors
        if result.get('error_message'):
            print(f"\n⚠️  Errors: {result['error_message']}")
        
        print("\n✅ Test completed successfully!")
        print("\nFull report saved to: test_report.md")
        
        # Return success
        return 0
    
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        logger.exception("Workflow execution failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

