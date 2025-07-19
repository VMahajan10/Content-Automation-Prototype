#!/usr/bin/env python3
"""
Simple test for the RAG pathway generation algorithm
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import gemini_generate_complete_pathway, debug_print, flush_debug_logs_to_streamlit

def test_simple_rag():
    """Test the RAG algorithm with simple, non-meeting content"""
    
    # Simple training context
    context = {
        'training_type': 'Safety Training',
        'target_audience': 'employees',
        'industry': 'manufacturing',
        'primary_goals': 'Improve workplace safety and reduce accidents'
    }
    
    # Simple file contents (no meeting transcripts)
    extracted_file_contents = {
        'Safety Procedures.txt': """
        Workplace Safety Procedures
        
        Personal Protective Equipment (PPE)
        All employees must wear appropriate PPE for their work area. This includes hard hats, safety glasses, steel-toed boots, and hearing protection where required. PPE must be inspected before each use and replaced if damaged.
        
        Emergency Procedures
        In case of emergency, immediately stop work and evacuate to the designated assembly point. Follow the evacuation route posted in your work area. Do not use elevators during evacuation. Report to your supervisor for headcount.
        
        Equipment Safety
        Before operating any equipment, ensure all safety guards are in place. Never bypass safety devices or remove protective covers. Report any equipment malfunctions immediately to maintenance.
        
        Chemical Safety
        Always read safety data sheets before handling chemicals. Use appropriate ventilation and wear required protective equipment. Store chemicals in designated areas and never mix incompatible substances.
        """,
        
        'Quality Control Guidelines.txt': """
        Quality Control Procedures
        
        Inspection Process
        All products must undergo visual inspection before packaging. Check for defects, damage, or irregularities. Use calibrated measuring tools for dimensional inspections. Document all findings in the quality control log.
        
        Testing Requirements
        Functional testing must be performed on all products before shipment. Follow the testing checklist for each product type. Record test results and any deviations from specifications. Products failing tests must be quarantined for review.
        
        Documentation Standards
        Maintain accurate records of all quality control activities. Include date, time, inspector name, and detailed findings. Use standardized forms and procedures for consistency. Archive records according to company retention policies.
        """,
        
        'Manufacturing Standards.txt': """
        Manufacturing Process Standards
        
        Assembly Procedures
        Follow the standard operating procedures for each assembly step. Use the correct tools and equipment for each task. Verify each step is completed before proceeding to the next. Maintain clean and organized work areas.
        
        Material Handling
        Store materials in designated locations with proper labeling. Use appropriate lifting techniques and equipment for heavy items. Inspect materials for damage before use. Return unused materials to storage areas.
        
        Process Control
        Monitor process parameters continuously during production. Record measurements at specified intervals. Adjust settings as needed to maintain quality standards. Report any process deviations immediately.
        """
    }
    
    # Sample inventory
    inventory = {
        'total_files': len(extracted_file_contents),
        'file_types': ['txt'],
        'total_content_length': sum(len(content) for content in extracted_file_contents.values())
    }
    
    print("🚀 Testing Simple RAG Pathway Generation")
    print("=" * 50)
    
    try:
        # Generate pathways using the RAG algorithm
        result = gemini_generate_complete_pathway(
            context=context,
            extracted_file_contents=extracted_file_contents,
            inventory=inventory,
            enhanced_content=True
        )
        
        # Display results
        print("\n✅ Pathway Generation Successful!")
        print(f"📊 Generated {len(result['pathways'])} pathways")
        
        for i, pathway in enumerate(result['pathways'], 1):
            print(f"\n🎯 Pathway {i}: {pathway['pathway_name']}")
            print(f"📚 Sections: {len(pathway['sections'])}")
            
            total_modules = sum(len(section['modules']) for section in pathway['sections'])
            print(f"📝 Total Modules: {total_modules}")
            
            for j, section in enumerate(pathway['sections'], 1):
                print(f"\n  📖 Section {j}: {section['title']}")
                print(f"     Modules: {len(section['modules'])}")
                
                for k, module in enumerate(section['modules'], 1):
                    print(f"\n     📋 Module {k}: {module['title']}")
                    print(f"        Source: {module['source']}")
                    print(f"        Description: {module['description'][:100]}...")
                    print(f"        Content Types: {len(module.get('content_types', []))}")
                    print(f"        Key Points: {len(module.get('key_points', []))}")
                    print(f"        Relevance Score: {module.get('relevance_score', 0)}")
                    
                    # Check content quality
                    content = module.get('content', '')
                    if content:
                        print(f"        Content Length: {len(content)} characters")
                        if 'conversational' in content.lower() or 'um' in content.lower() or 'uh' in content.lower():
                            print(f"        ⚠️  Content may still be conversational")
                        else:
                            print(f"        ✅ Content appears professional")
        
        # Flush debug logs
        flush_debug_logs_to_streamlit()
        
        return result
        
    except Exception as e:
        print(f"❌ Error during pathway generation: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_simple_rag()
    if result:
        print("\n🎉 Simple RAG Pathway Generation Test Completed Successfully!")
    else:
        print("\n💥 Simple RAG Pathway Generation Test Failed!") 