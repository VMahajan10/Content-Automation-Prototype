#!/usr/bin/env python3
"""
Direct test for pathway generation without Streamlit
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_direct_pathway():
    """Direct test for pathway generation"""
    
    try:
        from utils import gemini_generate_complete_pathway
        
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
        
        print("🔍 Testing direct pathway generation...")
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
                    for k, module in enumerate(modules[:3], 1):  # Show first 3 modules
                        print(f"       Module {k}: {module.get('title', 'No title')}")
        else:
            print("❌ No pathways generated")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"📝 Full error: {traceback.format_exc()}")

if __name__ == "__main__":
    test_direct_pathway() 