#!/usr/bin/env python3
"""
Test script for comprehensive content extraction
Verifies that modules contain actual training information and more pathways/sections are created
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.config import *
from modules.utils import extract_modules_from_file_content_fallback, group_modules_into_multiple_pathways

def test_comprehensive_extraction():
    """Test the comprehensive content extraction with sample data"""
    
    print("🧪 Testing Comprehensive Content Extraction")
    print("=" * 60)
    
    # Sample training context
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'primary_goals': 'understand factory workflow and safety procedures',
        'success_metrics': 'feedback surveys and safety compliance',
        'industry': 'construction'
    }
    
    # Sample content with more training-relevant information
    sample_content = """
    Meeting started at 10:00 AM
    
    Bruce: Good morning everyone. Today we're going to discuss the new fabrication workflow process.
    
    Sarah: Yes, we need to make sure all fabricators understand the new procedures.
    
    Bruce: Exactly. The new workflow starts with material receiving and inspection. Each piece needs to be checked for quality before it goes to the staging area. This includes checking for defects, verifying dimensions, and ensuring proper material specifications.
    
    Sarah: Right, and then the material moves through the fabrication stations in sequence. Station 1 handles cutting operations with specific safety protocols. All operators must wear proper PPE including hard hats, safety glasses, and steel-toed boots. The cutting equipment must be inspected before each use.
    
    Bruce: Important safety note - all fabricators must wear proper PPE at each station. Hard hats, safety glasses, and steel-toed boots are mandatory. Additionally, hearing protection is required when operating loud equipment, and respiratory protection may be needed depending on the materials being processed.
    
    Sarah: And we need to document everything. Each step in the process requires proper documentation and quality checkpoints. This includes recording material specifications, cutting parameters, quality measurements, and any deviations from standard procedures.
    
    Bruce: Yes, quality control is critical. We have checkpoints at each station to ensure the work meets our standards. The quality control process includes visual inspection, dimensional verification, and testing for material properties. Any non-conforming items must be immediately identified and segregated.
    
    Sarah: What about the handoff procedures between stations?
    
    Bruce: Good question. Each station must complete a handoff checklist before the work moves to the next station. This includes quality verification and safety checks. The handoff checklist includes verifying that all quality requirements have been met, safety equipment is properly stored, and the work area is clean and organized.
    
    Sarah: And we need to report any issues immediately. If there's a problem with materials or equipment, stop work and notify the supervisor. The reporting process includes documenting the issue, identifying the root cause, and implementing corrective actions to prevent recurrence.
    
    Bruce: Exactly. Safety first, always. Now let's talk about the finishing process. The finishing station handles final quality inspection, packaging, and preparation for shipment. All finished products must undergo final inspection to ensure they meet customer specifications and quality standards.
    
    Sarah: The finishing station handles final quality inspection, packaging, and preparation for shipment. The final inspection process includes checking for surface finish quality, verifying all dimensions are within tolerance, and ensuring proper labeling and packaging requirements are met.
    
    Bruce: Right. Each completed item gets a final inspection before it's packaged and labeled for shipping. The packaging process includes proper protection of finished items, accurate labeling with product information and handling instructions, and preparation of shipping documentation.
    
    Sarah: And we need to maintain accurate records of everything that goes through the process. Documentation requirements include recording all process parameters, quality measurements, inspection results, and any corrective actions taken. These records are essential for quality assurance and regulatory compliance.
    
    Bruce: Absolutely. Documentation is key for quality control and compliance. The documentation system includes electronic records for all process steps, quality measurements, and inspection results. These records must be maintained for the required retention period and be readily accessible for audits and inspections.
    
    Sarah: Any questions about the new workflow?
    
    Bruce: If anyone has questions, please ask your supervisor or come to me directly. We also have a comprehensive training manual that covers all these procedures in detail, and regular refresher training sessions will be scheduled to ensure everyone stays current with the latest procedures.
    
    Meeting ended at 11:00 AM
    """
    
    print(f"📋 Training Context:")
    print(f"   Type: {training_context['training_type']}")
    print(f"   Audience: {training_context['target_audience']}")
    print(f"   Goals: {training_context['primary_goals']}")
    print(f"   Industry: {training_context['industry']}")
    print()
    
    print(f"📄 Sample Content Length: {len(sample_content)} characters")
    print(f"📄 Content Preview: {sample_content[:300]}...")
    print()
    
    # Test the comprehensive extraction
    print("🔍 Testing Comprehensive Content Extraction...")
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
        content_preview = module['content'][:400] + "..." if len(module['content']) > 400 else module['content']
        print(f"   Content Preview:")
        print(f"   {content_preview}")
        print("-" * 80)
        print()
    
    # Test pathway generation
    if modules:
        print("🛤️ Testing Pathway Generation...")
        pathways = group_modules_into_multiple_pathways(modules, training_context)
        
        print(f"\n✅ Pathway Generation Results:")
        print(f"   Total pathways created: {len(pathways)}")
        
        for i, pathway in enumerate(pathways, 1):
            print(f"\n   Pathway {i}: {pathway['pathway_name']}")
            print(f"   Sections: {len(pathway['sections'])}")
            
            for j, section in enumerate(pathway['sections'], 1):
                modules_in_section = len(section['modules'])
                print(f"     Section {j}: {section['title']} - {modules_in_section} modules")
                print(f"       Description: {section['description']}")
        
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
    comprehensive_modules = [m for m in modules if len(m['content']) > 800]
    substantial_modules = [m for m in modules if len(m['content']) > 500]
    print(f"   Comprehensive modules (>800 chars): {len(comprehensive_modules)}")
    print(f"   Substantial modules (>500 chars): {len(substantial_modules)}")
    
    # Check if content contains actual training information
    training_info_modules = [m for m in modules if any(word in m['content'].lower() for word in ['procedure', 'process', 'safety', 'quality', 'inspection', 'equipment', 'training'])]
    print(f"   Modules with training information: {len(training_info_modules)}")
    
    # Check pathway structure
    if modules and 'pathways' in locals():
        total_sections = sum(len(p['sections']) for p in pathways)
        total_modules_in_pathways = sum(len(s['modules']) for p in pathways for s in p['sections'])
        print(f"   Total sections across pathways: {total_sections}")
        print(f"   Total modules in pathways: {total_modules_in_pathways}")
    
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
            
        if avg_content_length >= 600:
            print("   ✅ Comprehensive content")
        else:
            print("   ⚠️ Content could be more comprehensive")
            
        if len(training_info_modules) >= len(modules) * 0.7:
            print("   ✅ Most modules contain actual training information")
        else:
            print("   ⚠️ Some modules may lack training information")
            
        if modules and 'pathways' in locals() and len(pathways) >= 2:
            print("   ✅ Multiple pathways created")
        else:
            print("   ⚠️ Could create more pathways")
            
        if modules and 'pathways' in locals() and total_sections >= 4:
            print("   ✅ Good number of sections across pathways")
        else:
            print("   ⚠️ Could create more sections")
    else:
        print("❌ No modules extracted - extraction may need adjustment")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_comprehensive_extraction() 