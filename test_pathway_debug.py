#!/usr/bin/env python3
"""
Debug script to test pathway generation
"""

import os
from dotenv import load_dotenv
from modules.utils import gemini_generate_complete_pathway, debug_print

# Load environment variables
load_dotenv()

def test_pathway_generation():
    """Test pathway generation with sample data"""
    
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
        3. Report any safety incidents immediately
        4. Keep work areas clean and organized
        5. Use proper lifting techniques
        """,
        'onboarding_checklist.txt': """
        New Employee Onboarding Checklist
        - Complete safety orientation
        - Review company policies
        - Set up workstation
        - Meet team members
        - Review job responsibilities
        """
    }
    
    # Sample inventory
    inventory = {
        'process_docs': 'Safety manuals, onboarding guides',
        'training_materials': 'Videos, presentations, checklists'
    }
    
    print("🔍 Testing pathway generation...")
    print(f"📋 Context: {context}")
    print(f"📄 Files: {list(extracted_file_contents.keys())}")
    
    try:
        result = gemini_generate_complete_pathway(context, extracted_file_contents, inventory)
        print(f"✅ Result: {result}")
        
        if result and 'pathways' in result:
            pathways = result['pathways']
            print(f"📊 Generated {len(pathways)} pathways:")
            for i, pathway in enumerate(pathways):
                print(f"   Pathway {i+1}: {pathway.get('pathway_name', 'Unknown')}")
                sections = pathway.get('sections', [])
                print(f"   Sections: {len(sections)}")
                for j, section in enumerate(sections):
                    modules = section.get('modules', [])
                    print(f"     Section {j+1}: {section.get('title', 'Unknown')} - {len(modules)} modules")
        else:
            print("❌ No pathways generated")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pathway_generation() 