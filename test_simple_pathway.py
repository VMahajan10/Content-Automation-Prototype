#!/usr/bin/env python3
"""
Simple test for pathway generation
"""

import os
from dotenv import load_dotenv
from modules.utils import gemini_generate_complete_pathway, debug_print

# Load environment variables
load_dotenv()

def test_simple_pathway():
    """Simple test for pathway generation"""
    
    # Sample training context
    context = {
        'primary_goals': 'Employee onboarding and safety training',
        'training_type': 'Onboarding',
        'target_audience': 'New Employees',
        'industry': 'Manufacturing',
        'company_size': 'Medium'
    }
    
    # Sample file contents
    extracted_file_contents = {
        'safety_manual.txt': """
        Safety Procedures for Manufacturing
        1. Always wear PPE when entering the production floor
        2. Follow lockout/tagout procedures before maintenance
        3. Report all safety incidents immediately
        4. Keep work areas clean and organized
        5. Use proper lifting techniques
        """,
        'onboarding_checklist.txt': """
        New Employee Onboarding Checklist
        - Complete safety orientation
        - Review company policies
        - Set up workstation
        - Meet team members
        - Understand job responsibilities
        """
    }
    
    print("🔍 Testing simple pathway generation...")
    print(f"📋 Context: {context}")
    print(f"📄 Files: {list(extracted_file_contents.keys())}")
    
    # Test pathway generation
    result = gemini_generate_complete_pathway(context, extracted_file_contents, {})
    
    print(f"✅ Result: {result}")
    if result and 'pathways' in result:
        pathways = result['pathways']
        print(f"📊 Generated {len(pathways)} pathways:")
        for i, pathway in enumerate(pathways, 1):
            print(f"   Pathway {i}: {pathway.get('pathway_name', 'Unknown')}")
            sections = pathway.get('sections', [])
            print(f"   Sections: {len(sections)}")
            for j, section in enumerate(sections, 1):
                modules = section.get('modules', [])
                print(f"     Section {j}: {section.get('title', 'Unknown')} - {len(modules)} modules")
    else:
        print("❌ No pathways generated")

if __name__ == "__main__":
    test_simple_pathway() 