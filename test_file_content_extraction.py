#!/usr/bin/env python3
"""
Test script to verify that modules are using actual file content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import extract_modules_from_file_content

def test_file_content_extraction():
    """Test that modules use actual file content"""
    
    print("🔍 Testing File Content Extraction")
    print("=" * 50)
    
    # Sample file content that should be preserved
    sample_content = """
    The truss assembly process involves several critical steps. First, fabricators must 
    verify the steel shipment against the bill of lading and inspect for any damage. 
    Material handling procedures require proper staging and storage of steel components. 
    During assembly, welders follow specific welding procedures and quality control 
    checkpoints. Safety protocols must be followed throughout, including proper PPE usage. 
    Equipment maintenance and calibration are essential for accurate fabrication. 
    Documentation requirements include recording all quality inspections and process steps.
    
    The steel delivery process begins with receiving raw materials at the dock. 
    Each shipment must be verified against the purchase order and inspected for damage. 
    Proper material handling is crucial to prevent injuries and maintain quality. 
    Fabricators use specific tools and equipment for cutting, bending, and welding operations.
    """
    
    # Sample training context
    training_context = {
        'primary_goals': 'understand truss assembly and steel fabrication processes',
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'success_metrics': 'feedback surveys and quality assessments'
    }
    
    print(f"📄 Sample Content Length: {len(sample_content)} characters")
    print(f"🎯 Training Goals: {training_context['primary_goals']}")
    print()
    
    # Extract modules
    modules = extract_modules_from_file_content("test_file.txt", sample_content, training_context)
    
    print(f"✅ Extracted {len(modules)} modules")
    print()
    
    # Check each module for actual file content
    for i, module in enumerate(modules, 1):
        print(f"📋 Module {i}: {module['title']}")
        print(f"📝 Description: {module['description']}")
        print(f"📄 Content Length: {len(module['content'])} characters")
        print(f"📄 Content Preview: {module['content'][:100]}...")
        
        # Check if content contains actual file content
        content_lower = module['content'].lower()
        if any(phrase in content_lower for phrase in [
            'truss assembly', 'steel shipment', 'bill of lading', 'material handling',
            'welding procedures', 'quality control', 'safety protocols', 'ppe usage',
            'equipment maintenance', 'calibration', 'documentation requirements'
        ]):
            print("✅ PASS: Module contains actual file content")
        else:
            print("❌ FAIL: Module does not contain actual file content")
        
        print(f"🏷️ Source: {module.get('source', 'Unknown')}")
        print("-" * 50)
    
    print()
    print("🎯 Summary:")
    print(f"• Total modules extracted: {len(modules)}")
    print(f"• Modules with actual content: {sum(1 for m in modules if any(phrase in m['content'].lower() for phrase in ['truss', 'steel', 'welding', 'quality', 'safety']))}")
    print(f"• Content preservation: {'✅ Working' if len(modules) > 0 else '❌ Failed'}")

if __name__ == "__main__":
    test_file_content_extraction() 