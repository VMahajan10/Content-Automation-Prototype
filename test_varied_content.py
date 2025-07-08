#!/usr/bin/env python3
"""
Test script for varied content extraction
Demonstrates how the system now creates diverse descriptions and content
based on actual content rather than generic templates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import extract_modules_from_file_content_fallback
from modules.config import *

def test_varied_content_extraction():
    """Test the improved varied content extraction"""
    
    print("🎯 **Testing Varied Content Extraction**")
    print("=" * 60)
    
    # Sample training context
    training_context = {
        'primary_goals': 'understand factory workflow and safety procedures',
        'success_metrics': 'feedback surveys and safety compliance',
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'construction'
    }
    
    print(f"🎯 **Training Goals:** {training_context['primary_goals']}")
    print(f"📋 **Training Type:** {training_context['training_type']}")
    print(f"👥 **Target Audience:** {training_context['target_audience']}")
    print()
    
    # Sample content with different types of information
    sample_content = """
    Safety procedures for handling steel materials are critical. First, inspect the material for any damage or defects before handling.
    Then use the proper lifting equipment and PPE - hard hat, safety glasses, steel-toed boots.
    The workflow starts with receiving the steel shipment and verifying it against the bill of lading.
    Then stage the materials in the designated area and begin the fabrication process.
    Quality control happens at multiple checkpoints - during material inspection, after cutting, and before final assembly.
    Documentation is important. You need to record all measurements, inspections, and any issues that arise.
    Equipment maintenance procedures must be followed regularly. Calibrate measuring tools before each use.
    Material handling requires proper techniques. Use appropriate lifting equipment and follow safety protocols.
    Communication with team members is essential. Coordinate handoffs and report any issues immediately.
    Process optimization involves analyzing workflow efficiency and identifying improvement opportunities.
    """
    
    print("📄 **Sample Content (with varied training information):**")
    print(sample_content)
    print()
    
    # Test the varied content extraction
    print("🔍 **Extracting Varied Training Information...**")
    modules = extract_modules_from_file_content_fallback(
        "varied_training.txt", 
        sample_content, 
        training_context
    )
    
    print(f"\n✅ **Results: {len(modules)} varied modules extracted**")
    print("=" * 60)
    
    for i, module in enumerate(modules, 1):
        print(f"\n📚 **Module {i}:**")
        print(f"📝 **Title:** {module['title']}")
        print(f"📋 **Description:** {module['description']}")
        print(f"📄 **Content Preview:** {module['content'][:150]}...")
        print(f"🎯 **Key Points:** {module.get('key_points', [])}")
        print("-" * 40)

def test_different_content_types():
    """Test with different types of content to show variety"""
    
    print("\n🎯 **Testing Different Content Types**")
    print("=" * 60)
    
    # Test 1: Safety-focused content
    safety_context = {
        'primary_goals': 'learn safety procedures and emergency response',
        'success_metrics': 'safety compliance and incident reduction',
        'training_type': 'Safety Training',
        'target_audience': 'operators',
        'industry': 'manufacturing'
    }
    
    safety_content = """
    Safety procedures for equipment operation are essential. Always wear PPE including hard hat, safety glasses, and steel-toed boots.
    Before starting any equipment, perform a pre-operation inspection to check for damage or malfunctions.
    Emergency procedures must be followed immediately if any safety issues are detected.
    All incidents must be reported and documented according to company policy.
    """
    
    print(f"🎯 **Safety Training Content:**")
    safety_modules = extract_modules_from_file_content_fallback(
        "safety_content.txt", 
        safety_content, 
        safety_context
    )
    
    print(f"✅ **Safety Modules:** {len(safety_modules)} extracted")
    for i, module in enumerate(safety_modules, 1):
        print(f"   {i}. {module['title']}")
        print(f"      Description: {module['description'][:80]}...")
    
    # Test 2: Quality-focused content
    quality_context = {
        'primary_goals': 'understand quality control and inspection procedures',
        'success_metrics': 'quality metrics and defect reduction',
        'training_type': 'Quality Training',
        'target_audience': 'inspectors',
        'industry': 'manufacturing'
    }
    
    quality_content = """
    Quality control procedures require careful attention to detail. Inspect all materials for defects before processing.
    Use calibrated measuring equipment and follow standard inspection procedures.
    Document all inspection results and report any non-conforming materials.
    Quality standards must be maintained throughout the entire production process.
    """
    
    print(f"\n🎯 **Quality Training Content:**")
    quality_modules = extract_modules_from_file_content_fallback(
        "quality_content.txt", 
        quality_content, 
        quality_context
    )
    
    print(f"✅ **Quality Modules:** {len(quality_modules)} extracted")
    for i, module in enumerate(quality_modules, 1):
        print(f"   {i}. {module['title']}")
        print(f"      Description: {module['description'][:80]}...")
    
    # Test 3: Process-focused content
    process_context = {
        'primary_goals': 'learn process procedures and workflow optimization',
        'success_metrics': 'process efficiency and productivity',
        'training_type': 'Process Training',
        'target_audience': 'workers',
        'industry': 'general'
    }
    
    process_content = """
    Process workflow procedures must be followed step-by-step. Coordinate with team members on process handoffs.
    Document any process deviations or issues that arise during production.
    Identify opportunities for process improvement and workflow optimization.
    Maintain proper documentation and record keeping for all process activities.
    """
    
    print(f"\n🎯 **Process Training Content:**")
    process_modules = extract_modules_from_file_content_fallback(
        "process_content.txt", 
        process_content, 
        process_context
    )
    
    print(f"✅ **Process Modules:** {len(process_modules)} extracted")
    for i, module in enumerate(process_modules, 1):
        print(f"   {i}. {module['title']}")
        print(f"      Description: {module['description'][:80]}...")

def test_content_variety_analysis():
    """Analyze the variety in generated content"""
    
    print("\n🎯 **Content Variety Analysis**")
    print("=" * 60)
    
    # Test with the same content multiple times to see variety
    training_context = {
        'primary_goals': 'understand factory workflow and safety procedures',
        'success_metrics': 'feedback surveys and safety compliance',
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'construction'
    }
    
    test_content = """
    Safety procedures for handling steel materials are critical. First, inspect the material for any damage or defects before handling.
    Then use the proper lifting equipment and PPE - hard hat, safety glasses, steel-toed boots.
    The workflow starts with receiving the steel shipment and verifying it against the bill of lading.
    Then stage the materials in the designated area and begin the fabrication process.
    Quality control happens at multiple checkpoints - during material inspection, after cutting, and before final assembly.
    Documentation is important. You need to record all measurements, inspections, and any issues that arise.
    """
    
    print("🔄 **Testing Content Variety (same content, multiple extractions):**")
    
    all_descriptions = []
    all_titles = []
    
    for run in range(3):
        print(f"\n📋 **Run {run + 1}:**")
        modules = extract_modules_from_file_content_fallback(
            f"test_run_{run}.txt", 
            test_content, 
            training_context
        )
        
        for i, module in enumerate(modules, 1):
            print(f"   Module {i}: {module['title']}")
            print(f"   Description: {module['description'][:60]}...")
            all_descriptions.append(module['description'])
            all_titles.append(module['title'])
    
    # Analyze variety
    unique_descriptions = len(set(all_descriptions))
    unique_titles = len(set(all_titles))
    total_modules = len(all_descriptions)
    
    print(f"\n📊 **Variety Analysis:**")
    print(f"   Total modules generated: {total_modules}")
    print(f"   Unique titles: {unique_titles}/{total_modules} ({unique_titles/total_modules*100:.1f}%)")
    print(f"   Unique descriptions: {unique_descriptions}/{total_modules} ({unique_descriptions/total_modules*100:.1f}%)")
    
    if unique_descriptions > total_modules * 0.7:
        print("✅ **Good variety achieved!**")
    else:
        print("⚠️ **Could use more variety**")

if __name__ == "__main__":
    print("🚀 **Varied Content Extraction Test**")
    print("This test demonstrates how the system now creates diverse")
    print("descriptions and content based on actual content analysis.")
    print()
    
    # Run tests
    test_varied_content_extraction()
    test_different_content_types()
    test_content_variety_analysis()
    
    print("\n✅ **Test Complete!**")
    print("The system now creates varied descriptions and content")
    print("based on actual content analysis rather than generic templates.") 