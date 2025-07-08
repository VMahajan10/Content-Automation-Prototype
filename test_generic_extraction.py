#!/usr/bin/env python3
"""
Test script to verify generic module extraction works with any industry
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import gemini_generate_complete_pathway

def test_different_industries():
    """Test with different industries"""
    
    print("🧪 Testing Generic Module Extraction Across Industries")
    print("=" * 60)
    
    # Test cases for different industries
    test_cases = [
        {
            'name': 'Healthcare',
            'context': {
                'training_type': 'Compliance Training',
                'target_audience': 'nurses',
                'industry': 'healthcare',
                'primary_goals': 'understand HIPAA compliance and patient safety protocols',
                'success_metrics': 'compliance audits and patient satisfaction scores'
            },
            'content': {
                'healthcare_procedures.txt': """
                HIPAA Compliance and Patient Safety Training
                
                Dr. Smith: Let's review the HIPAA compliance procedures. When handling patient 
                information, we must ensure all data is properly secured and access is limited 
                to authorized personnel only.
                
                Nurse Johnson: Right, and we need to verify patient identity before discussing 
                any medical information. We should always ask for two forms of identification.
                
                Dr. Smith: Exactly. And during patient care, we must follow the safety protocols. 
                Everyone should wash their hands before and after patient contact.
                """
            }
        },
        {
            'name': 'Technology',
            'context': {
                'training_type': 'Technical Training',
                'target_audience': 'developers',
                'industry': 'technology',
                'primary_goals': 'learn agile development methodologies and code quality standards',
                'success_metrics': 'code review scores and sprint velocity improvements'
            },
            'content': {
                'agile_methodology.txt': """
                Agile Development and Code Quality Training
                
                Team Lead: Let's discuss our agile development process. We follow Scrum methodology 
                with two-week sprints. Each sprint begins with planning where we estimate story points.
                
                Developer: Right, and during the sprint, we have daily standups to discuss progress, 
                blockers, and next steps. We need to update our task status in Jira regularly.
                
                Team Lead: Exactly. And for code quality, we have specific standards. All code must 
                pass automated tests before merging.
                """
            }
        },
        {
            'name': 'Finance',
            'context': {
                'training_type': 'Compliance Training',
                'target_audience': 'financial advisors',
                'industry': 'finance',
                'primary_goals': 'understand regulatory compliance and client communication protocols',
                'success_metrics': 'compliance audit results and client satisfaction ratings'
            },
            'content': {
                'compliance_procedures.txt': """
                Financial Compliance and Client Communication Training
                
                Compliance Officer: Let's review the regulatory requirements. We must follow 
                FINRA guidelines and SEC regulations. All client communications must be documented.
                
                Financial Advisor: Right, and we need to verify client identity and suitability 
                before making any investment recommendations.
                
                Compliance Officer: Exactly. And during client meetings, we must follow the 
                disclosure requirements.
                """
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🏭 Testing {test_case['name']} Industry")
        print("-" * 40)
        
        training_context = test_case['context']
        extracted_file_contents = test_case['content']
        file_inventory = {
            'process_docs': f'{test_case["name"]} procedures and protocols',
            'training_materials': f'{test_case["name"]} training documentation'
        }
        
        print(f"📋 Training Context: {training_context}")
        print(f"📁 Files to process: {list(extracted_file_contents.keys())}")
        
        try:
            result = gemini_generate_complete_pathway(
                training_context, 
                extracted_file_contents, 
                file_inventory, 
                bypass_filtering=True
            )
            
            if result and 'pathways' in result:
                pathways = result['pathways']
                total_modules = sum(len(section.get('modules', [])) for pathway in pathways for section in pathway.get('sections', []))
                
                print(f"✅ {test_case['name']}: {len(pathways)} pathways, {total_modules} modules")
                
                for i, pathway in enumerate(pathways):
                    pathway_name = pathway.get('pathway_name', 'Unknown')
                    sections = pathway.get('sections', [])
                    pathway_modules = sum(len(section.get('modules', [])) for section in sections)
                    print(f"   Pathway {i+1}: {pathway_name} ({pathway_modules} modules)")
                    
            else:
                print(f"❌ {test_case['name']}: No pathways created")
                
        except Exception as e:
            print(f"❌ {test_case['name']}: Error - {str(e)}")
    
    print("\n✅ Generic extraction testing completed!")

if __name__ == "__main__":
    test_different_industries() 