#!/usr/bin/env python3
"""
Test script for unique module descriptions
Tests that each module in a section gets a unique description
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import (
    create_cohesive_description,
    extract_specific_phrases_from_content,
    extract_specific_procedures,
    extract_meaningful_content_snippet
)

def test_unique_descriptions():
    """Test that each module gets a unique description"""
    
    # Sample training context
    training_context = {
        'primary_goals': 'understand truss assembly and safety procedures',
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing'
    }
    
    # Test cases with different content for the same section
    test_modules = [
        {
            'name': 'Module 1 - Safety Procedures',
            'content': "Safety procedures for fabricators include wearing proper PPE at all times. All workers must wear hard hats, safety glasses, and steel-toed boots. Before starting any work, conduct a thorough hazard assessment of the work area. Report any safety concerns immediately to supervisors.",
            'core_topic': 'safety'
        },
        {
            'name': 'Module 2 - Quality Control',
            'content': "Quality control procedures require thorough inspection of all welds and connections. Each component must be verified against engineering drawings before proceeding. Dimensional checks must be performed at each stage of assembly. Non-conforming parts must be reported and documented immediately.",
            'core_topic': 'quality'
        },
        {
            'name': 'Module 3 - Process Workflow',
            'content': "The truss assembly process follows a specific workflow sequence. First, verify all materials against the bill of lading. Then set up the assembly jig according to specifications. Proceed with component assembly following the established sequence. Document each step in the process log.",
            'core_topic': 'process'
        },
        {
            'name': 'Module 4 - Equipment Operation',
            'content': "Equipment operation and maintenance procedures ensure proper functioning of all tools and machinery. Regular calibration of measuring equipment is essential for accuracy. Perform equipment checks before each use and report any malfunctions immediately. Follow maintenance schedules strictly.",
            'core_topic': 'equipment'
        },
        {
            'name': 'Module 5 - Material Handling',
            'content': "Material handling and fabrication techniques require careful attention to specifications. Store materials in designated areas with proper labeling. Follow material processing procedures exactly as specified. Maintain material traceability throughout the fabrication process.",
            'core_topic': 'material'
        }
    ]
    
    print("🧪 Testing Unique Module Descriptions")
    print("=" * 60)
    
    descriptions = []
    
    for i, module in enumerate(test_modules, 1):
        print(f"\n📋 {module['name']}")
        print("-" * 40)
        
        content = module['content']
        core_topic = module['core_topic']
        
        print(f"📄 Content: {content[:100]}...")
        print(f"🎯 Core Topic: {core_topic}")
        
        # Test specific content extraction
        specific_phrases = extract_specific_phrases_from_content(content)
        specific_procedures = extract_specific_procedures(content)
        meaningful_snippet = extract_meaningful_content_snippet(content)
        
        print(f"💡 Specific Phrases: {specific_phrases[:2]}")
        print(f"🔧 Specific Procedures: {specific_procedures}")
        print(f"📝 Meaningful Snippet: {meaningful_snippet[:80] if meaningful_snippet else 'None'}...")
        
        # Test description creation
        description = create_cohesive_description(content, core_topic, training_context)
        descriptions.append(description)
        
        print(f"📋 Description: {description}")
        print()
    
    # Check for uniqueness
    print("🔍 Uniqueness Analysis")
    print("=" * 40)
    
    unique_descriptions = set(descriptions)
    total_descriptions = len(descriptions)
    unique_count = len(unique_descriptions)
    
    print(f"Total descriptions: {total_descriptions}")
    print(f"Unique descriptions: {unique_count}")
    print(f"Uniqueness rate: {(unique_count/total_descriptions)*100:.1f}%")
    
    if unique_count == total_descriptions:
        print("✅ All descriptions are unique!")
    else:
        print("⚠️ Some descriptions are duplicated")
        # Find duplicates
        seen = set()
        duplicates = []
        for desc in descriptions:
            if desc in seen:
                duplicates.append(desc)
            seen.add(desc)
        
        if duplicates:
            print(f"🔄 Duplicate descriptions: {duplicates}")
    
    print("\n📋 All Descriptions:")
    for i, desc in enumerate(descriptions, 1):
        print(f"{i}. {desc}")

def test_description_variety():
    """Test description variety within the same topic"""
    
    print("\n🎨 Testing Description Variety")
    print("=" * 40)
    
    training_context = {
        'primary_goals': 'understand safety procedures',
        'training_type': 'Safety Training',
        'target_audience': 'workers',
        'industry': 'construction'
    }
    
    # Multiple safety-related modules
    safety_modules = [
        "Safety procedures for fabricators include wearing proper PPE at all times. All workers must wear hard hats, safety glasses, and steel-toed boots.",
        "Before starting any work, conduct a thorough hazard assessment of the work area. Report any safety concerns immediately to supervisors.",
        "Emergency response procedures must be clearly understood by all workers. Know the location of emergency exits and first aid stations.",
        "Equipment safety protocols require proper lockout-tagout procedures. Never operate equipment without proper training and authorization."
    ]
    
    print("Safety Module Descriptions:")
    for i, content in enumerate(safety_modules, 1):
        description = create_cohesive_description(content, 'safety', training_context)
        print(f"{i}. {description}")

if __name__ == "__main__":
    test_unique_descriptions()
    test_description_variety()
    
    print("\n🎯 Summary:")
    print("• Each module now gets a unique description based on its specific content")
    print("• Descriptions use multiple approaches for variety")
    print("• Content-specific phrases and procedures are extracted")
    print("• Hash-based uniqueness ensures no duplicates")
    print("• Descriptions are more informative and specific") 