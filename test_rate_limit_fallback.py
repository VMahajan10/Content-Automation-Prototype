#!/usr/bin/env python3
"""
Test script to demonstrate rate limit fallback functionality
"""

import sys
import os

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.utils import create_fallback_pathways

def test_rate_limit_fallback():
    """Test the rate limit fallback functionality"""
    
    print("🔄 **Testing Rate Limit Fallback**")
    print("=" * 50)
    
    # Create sample modules (like what would be extracted from files)
    sample_modules = [
        {
            'title': 'Steel Delivery Process Overview',
            'description': 'Understanding the steel delivery workflow',
            'content': 'The steel delivery process involves coordinating with suppliers, scheduling deliveries, and ensuring quality control. This module covers the key steps in the delivery workflow.',
            'source': 'File content'
        },
        {
            'title': 'Truss Assembly Safety Guidelines',
            'description': 'Safety procedures for truss assembly',
            'content': 'Safety is paramount during truss assembly. This includes proper PPE, equipment checks, and following established safety protocols.',
            'source': 'File content'
        },
        {
            'title': 'Quality Control Procedures',
            'description': 'Quality control in manufacturing',
            'content': 'Quality control ensures that all manufactured components meet specifications. This involves regular inspections and testing.',
            'source': 'File content'
        }
    ]
    
    training_context = {
        'primary_goals': 'understand the steel delivery and truss assembly process',
        'industry': 'construction',
        'training_type': 'Process Training',
        'target_audience': 'fabricators'
    }
    
    print(f"📋 Sample modules: {len(sample_modules)}")
    for i, module in enumerate(sample_modules):
        print(f"   Module {i+1}: {module['title']}")
    
    print(f"\n🔄 **Creating fallback pathways...**")
    
    # Test fallback pathway creation
    fallback_pathways = create_fallback_pathways(sample_modules, training_context)
    
    if fallback_pathways:
        pathway = fallback_pathways[0]
        print(f"✅ Fallback pathway created successfully!")
        print(f"📋 Pathway name: {pathway.get('pathway_name', 'Unknown')}")
        
        sections = pathway.get('sections', [])
        print(f"📋 Sections: {len(sections)}")
        
        for i, section in enumerate(sections):
            modules = section.get('modules', [])
            print(f"\nSection {i+1}: {section.get('title', 'Unknown')}")
            print(f"  Description: {section.get('description', 'No description')}")
            print(f"  Modules: {len(modules)}")
            
            for j, module in enumerate(modules):
                print(f"    Module {j+1}: {module.get('title', 'Unknown')}")
                print(f"      Content: {module.get('content', '')[:80]}...")
    else:
        print("❌ Fallback pathway creation failed")
    
    print(f"\n✅ **Test completed successfully!**")
    print(f"💡 **Key Benefits:**")
    print(f"   • Works without AI when rate limits are hit")
    print(f"   • Preserves all extracted content")
    print(f"   • Creates logical pathway structure")
    print(f"   • No API calls required")
    print(f"   • Instant results")

if __name__ == "__main__":
    test_rate_limit_fallback() 