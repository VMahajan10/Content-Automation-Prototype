#!/usr/bin/env python3
"""
Test script for improved content extraction
Verifies that modules are more relevant, comprehensive, and user-friendly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.config import *
from modules.utils import extract_modules_from_file_content_fallback

def test_improved_extraction():
    """Test the improved content extraction with sample data"""
    
    print("🧪 Testing Improved Content Extraction")
    print("=" * 50)
    
    # Sample training context
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'primary_goals': 'understand factory workflow',
        'success_metrics': 'feedback surveys',
        'industry': 'construction'
    }
    
    # Sample content (simulating a meeting transcript with some relevant content)
    sample_content = """
    Meeting started at 10:00 AM
    
    Bruce: Good morning everyone. Today we're going to discuss the new fabrication workflow process.
    
    Sarah: Yes, we need to make sure all fabricators understand the new procedures.
    
    Bruce: Exactly. The new workflow starts with material receiving and inspection. Each piece needs to be checked for quality before it goes to the staging area.
    
    Sarah: Right, and then the material moves through the fabrication stations in sequence. Station 1 handles cutting, Station 2 does assembly, and Station 3 is finishing.
    
    Bruce: Important safety note - all fabricators must wear proper PPE at each station. Hard hats, safety glasses, and steel-toed boots are mandatory.
    
    Sarah: And we need to document everything. Each step in the process requires proper documentation and quality checkpoints.
    
    Bruce: Yes, quality control is critical. We have checkpoints at each station to ensure the work meets our standards.
    
    Sarah: What about the handoff procedures between stations?
    
    Bruce: Good question. Each station must complete a handoff checklist before the work moves to the next station. This includes quality verification and safety checks.
    
    Sarah: And we need to report any issues immediately. If there's a problem with materials or equipment, stop work and notify the supervisor.
    
    Bruce: Exactly. Safety first, always. Now let's talk about the finishing process...
    
    Sarah: The finishing station handles final quality inspection, packaging, and preparation for shipment.
    
    Bruce: Right. Each completed item gets a final inspection before it's packaged and labeled for shipping.
    
    Sarah: And we need to maintain accurate records of everything that goes through the process.
    
    Bruce: Absolutely. Documentation is key for quality control and compliance.
    
    Sarah: Any questions about the new workflow?
    
    Bruce: If anyone has questions, please ask your supervisor or come to me directly.
    
    Meeting ended at 11:00 AM
    """
    
    print(f"📋 Training Context:")
    print(f"   Type: {training_context['training_type']}")
    print(f"   Audience: {training_context['target_audience']}")
    print(f"   Goals: {training_context['primary_goals']}")
    print(f"   Industry: {training_context['industry']}")
    print()
    
    print(f"📄 Sample Content Length: {len(sample_content)} characters")
    print(f"📄 Content Preview: {sample_content[:200]}...")
    print()
    
    # Test the improved extraction
    print("🔍 Testing Improved Content Extraction...")
    modules = extract_modules_from_file_content_fallback(
        "test_transcript.txt", 
        sample_content, 
        training_context, 
        bypass_filtering=False
    )
    
    print(f"\n✅ Extraction Results:")
    print(f"   Total modules extracted: {len(modules)}")
    print()
    
    # Display each module
    for i, module in enumerate(modules, 1):
        print(f"📚 Module {i}: {module['title']}")
        print(f"   Relevance Score: {module['relevance_score']:.2f}")
        print(f"   Description: {module['description']}")
        print(f"   Content Length: {len(module['content'])} characters")
        print(f"   Key Points: {module.get('key_points', [])}")
        print(f"   Source: {module['source']}")
        print()
        
        # Show content preview
        content_preview = module['content'][:300] + "..." if len(module['content']) > 300 else module['content']
        print(f"   Content Preview:")
        print(f"   {content_preview}")
        print("-" * 80)
        print()
    
    # Analyze results
    print("📊 Analysis:")
    
    # Check relevance scores
    high_relevance = [m for m in modules if m['relevance_score'] >= 0.6]
    medium_relevance = [m for m in modules if 0.3 <= m['relevance_score'] < 0.6]
    low_relevance = [m for m in modules if m['relevance_score'] < 0.3]
    
    print(f"   High relevance modules (≥0.6): {len(high_relevance)}")
    print(f"   Medium relevance modules (0.3-0.6): {len(medium_relevance)}")
    print(f"   Low relevance modules (<0.3): {len(low_relevance)}")
    
    # Check content quality
    comprehensive_modules = [m for m in modules if len(m['content']) > 500]
    print(f"   Comprehensive modules (>500 chars): {len(comprehensive_modules)}")
    
    # Check if descriptions are user-friendly
    user_friendly_descriptions = [m for m in modules if len(m['description']) > 50 and 'training' in m['description'].lower()]
    print(f"   User-friendly descriptions: {len(user_friendly_descriptions)}")
    
    print()
    
    # Overall assessment
    if len(modules) > 0:
        avg_relevance = sum(m['relevance_score'] for m in modules) / len(modules)
        avg_content_length = sum(len(m['content']) for m in modules) / len(modules)
        
        print("🎯 Overall Assessment:")
        print(f"   Average relevance score: {avg_relevance:.2f}")
        print(f"   Average content length: {avg_content_length:.0f} characters")
        
        if avg_relevance >= 0.5:
            print("   ✅ Good relevance to training goals")
        else:
            print("   ⚠️ Relevance could be improved")
            
        if avg_content_length >= 300:
            print("   ✅ Comprehensive content")
        else:
            print("   ⚠️ Content could be more comprehensive")
            
        if len(user_friendly_descriptions) == len(modules):
            print("   ✅ All descriptions are user-friendly")
        else:
            print("   ⚠️ Some descriptions could be more user-friendly")
    else:
        print("❌ No modules extracted - extraction may need adjustment")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_improved_extraction() 