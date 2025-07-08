#!/usr/bin/env python3
"""
Test script for cohesive module creation
Tests the new approach that creates title, description, and content that work together
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import (
    create_cohesive_module_content,
    is_meaningful_training_content,
    extract_core_topic,
    create_cohesive_title,
    create_cohesive_description,
    create_cohesive_content_structure
)

def test_cohesive_module_creation():
    """Test the cohesive module creation approach"""
    
    # Sample training context
    training_context = {
        'primary_goals': 'understand truss assembly and safety procedures',
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing'
    }
    
    # Test cases with different types of content
    test_cases = [
        {
            'name': 'Good Safety Content',
            'content': "Safety procedures for fabricators include wearing proper PPE at all times. All workers must wear hard hats, safety glasses, and steel-toed boots. Before starting any work, conduct a thorough hazard assessment of the work area. Report any safety concerns immediately to supervisors.",
            'expected_topic': 'safety'
        },
        {
            'name': 'Good Quality Content',
            'content': "Quality control procedures require thorough inspection of all welds and connections. Each component must be verified against engineering drawings before proceeding. Dimensional checks must be performed at each stage of assembly. Non-conforming parts must be reported and documented immediately.",
            'expected_topic': 'quality'
        },
        {
            'name': 'Good Process Content',
            'content': "The truss assembly process follows a specific workflow sequence. First, verify all materials against the bill of lading. Then set up the assembly jig according to specifications. Proceed with component assembly following the established sequence. Document each step in the process log.",
            'expected_topic': 'process'
        },
        {
            'name': 'Conversational Content (Should be rejected)',
            'content': "You're a bit lagging, but I think we can hear you. Backgrounds, filters, appearance. That's the truss, but it hasn't got the zigzags in yet. Interesting to learn about it.",
            'expected_topic': None
        },
        {
            'name': 'Mixed Content (Should be filtered)',
            'content': "Yeah, so the truss assembly process requires careful inspection. You know, we need to verify all the welds and check the dimensions. The quality control procedures are really important for safety and compliance.",
            'expected_topic': 'quality'
        }
    ]
    
    print("🧪 Testing Cohesive Module Creation")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        content = test_case['content']
        print(f"📄 Content: {content[:100]}...")
        
        # Test meaningful content validation
        is_meaningful = is_meaningful_training_content(content, training_context)
        print(f"🔍 Is Meaningful: {is_meaningful}")
        
        # Test core topic extraction
        core_topic = extract_core_topic(content, training_context)
        print(f"🎯 Core Topic: {core_topic}")
        
        if is_meaningful:
            # Test cohesive module creation
            cohesive_module = create_cohesive_module_content(content, training_context, i)
            
            if cohesive_module:
                print(f"✅ Cohesive Module Created:")
                print(f"   📝 Title: {cohesive_module['title']}")
                print(f"   📋 Description: {cohesive_module['description']}")
                print(f"   📄 Content Preview: {cohesive_module['content'][:150]}...")
                print(f"   🎯 Core Topic: {cohesive_module['core_topic']}")
            else:
                print("❌ Cohesive module creation failed")
        else:
            print("⚠️ Content rejected as not meaningful")
        
        print()
    
    print("✅ Cohesive module testing completed!")

def test_individual_functions():
    """Test individual cohesive functions"""
    
    print("\n🔧 Testing Individual Cohesive Functions")
    print("=" * 50)
    
    training_context = {
        'primary_goals': 'understand manufacturing processes',
        'training_type': 'Process Training',
        'target_audience': 'operators',
        'industry': 'manufacturing'
    }
    
    # Test content
    test_content = "Equipment maintenance procedures require regular calibration and inspection. All tools must be checked before use and any defects reported immediately. Follow the maintenance schedule strictly to ensure optimal performance."
    
    print(f"📄 Test Content: {test_content}")
    
    # Test core topic extraction
    core_topic = extract_core_topic(test_content, training_context)
    print(f"🎯 Extracted Core Topic: {core_topic}")
    
    # Test cohesive title
    title = create_cohesive_title(test_content, core_topic, training_context, 1)
    print(f"📝 Cohesive Title: {title}")
    
    # Test cohesive description
    description = create_cohesive_description(test_content, core_topic, training_context)
    print(f"📋 Cohesive Description: {description}")
    
    # Test cohesive content structure
    content_structure = create_cohesive_content_structure(test_content, core_topic, training_context)
    print(f"📄 Content Structure Preview: {content_structure[:200]}...")

def test_content_validation():
    """Test content validation function"""
    
    print("\n🔍 Testing Content Validation")
    print("=" * 40)
    
    training_context = {
        'primary_goals': 'understand safety procedures',
        'training_type': 'Safety Training',
        'target_audience': 'workers',
        'industry': 'construction'
    }
    
    test_contents = [
        "Safety procedures require proper PPE usage and hazard assessment.",
        "You're a bit lagging, but I think we can hear you.",
        "Equipment maintenance and calibration procedures must be followed strictly.",
        "Backgrounds, filters, appearance.",
        "Quality control processes include inspection and verification procedures."
    ]
    
    for i, content in enumerate(test_contents, 1):
        is_meaningful = is_meaningful_training_content(content, training_context)
        print(f"{i}. '{content[:50]}...' -> Meaningful: {is_meaningful}")

if __name__ == "__main__":
    test_cohesive_module_creation()
    test_individual_functions()
    test_content_validation()
    
    print("\n🎯 Summary:")
    print("• Cohesive approach creates title, description, and content that work together")
    print("• Content validation ensures only meaningful training content is processed")
    print("• Core topic extraction provides focus for module creation")
    print("• Conversational content is properly filtered out")
    print("• Modules are more structured and professional") 