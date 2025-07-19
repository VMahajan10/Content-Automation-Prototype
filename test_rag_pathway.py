#!/usr/bin/env python3
"""
Test script for the new RAG-powered pathway generation algorithm
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import gemini_generate_complete_pathway, debug_print, flush_debug_logs_to_streamlit

def test_rag_pathway_generation():
    """Test the new RAG algorithm with sample content"""
    
    # Sample training context
    context = {
        'training_type': 'Manufacturing Training',
        'target_audience': 'factory workers',
        'industry': 'manufacturing',
        'primary_goals': 'Improve manufacturing efficiency, quality control, and safety procedures'
    }
    
    # Sample file contents (including meeting transcript)
    extracted_file_contents = {
        'Meet Meeting Transcript (1).txt': """
        0:00 - MaiLinh Ho: I wanted to work through the construction flow chart with you, just to understand how does that work now that we have pretty much the overview of manufacturing and I'm diving deeper into that with Bruce. Actually, today we were able to walk through the factory and really get deeper into what each component, how it's made and everything like that. So yeah, wanted to understand the construction side, but before we go into that, is there anything else you wanted to talk about or you had thoughts on in the meantime?
        
        0:15 - Bruce: Well, I think the key thing we need to focus on is the quality control process. We've been seeing some issues with the final product inspection, and I want to make sure everyone understands the proper procedures.
        
        0:30 - MaiLinh Ho: Absolutely, that's crucial. Can you walk me through the current quality control workflow?
        
        0:45 - Bruce: Sure. First, we have the initial inspection at the assembly line. Each component needs to be checked for defects before it moves to the next station. Then we have the final assembly inspection where we test the complete product functionality. Finally, we do a packaging inspection to ensure everything is properly labeled and protected.
        
        1:00 - MaiLinh Ho: That sounds comprehensive. What about safety protocols? I noticed some workers weren't wearing proper PPE in certain areas.
        
        1:15 - Bruce: You're absolutely right. Safety is our top priority. We need to enforce strict PPE requirements in all manufacturing areas. Hard hats, safety glasses, and steel-toed boots are mandatory. We also need to review the emergency evacuation procedures and make sure all safety equipment is properly maintained.
        
        1:30 - MaiLinh Ho: Good point. And what about the new equipment we're getting next month? How should we prepare for that?
        
        1:45 - Bruce: Excellent question. We need to develop training programs for the new equipment operators. The new machines are more automated, so we'll need to train workers on the new control systems and safety features. We should also update our standard operating procedures to reflect the new equipment capabilities.
        """,
        
        'Manufacturing Procedures.pdf': """
        Manufacturing Process Overview
        
        The manufacturing process consists of several key stages that must be followed precisely to ensure product quality and safety.
        
        Stage 1: Raw Material Inspection
        All incoming raw materials must be inspected for quality and compliance with specifications. Materials that don't meet standards should be rejected and returned to suppliers.
        
        Stage 2: Assembly Process
        The assembly process follows a specific sequence that optimizes efficiency while maintaining quality. Each step must be completed before moving to the next.
        
        Stage 3: Quality Control
        Quality control is integrated throughout the manufacturing process, with multiple checkpoints to ensure product integrity.
        
        Stage 4: Final Testing
        All products undergo comprehensive testing before packaging and shipping to customers.
        
        Safety Guidelines
        - Always wear appropriate PPE for your work area
        - Follow lockout/tagout procedures when working with machinery
        - Report any safety concerns immediately
        - Participate in regular safety training sessions
        """,
        
        'Quality Control Manual.txt': """
        Quality Control Procedures Manual
        
        This manual outlines the essential quality control procedures that must be followed in all manufacturing operations.
        
        Inspection Procedures
        1. Visual Inspection: Check for visible defects, damage, or irregularities
        2. Dimensional Inspection: Verify all measurements meet specifications
        3. Functional Testing: Test all product functions and features
        4. Documentation Review: Ensure all required documentation is complete
        
        Quality Standards
        - All products must meet or exceed industry standards
        - Defect rates must be kept below 2%
        - Customer satisfaction scores must remain above 95%
        
        Corrective Actions
        When quality issues are identified, immediate corrective actions must be taken:
        1. Stop production if necessary
        2. Identify the root cause of the issue
        3. Implement corrective measures
        4. Verify the effectiveness of corrections
        5. Resume production only after quality is confirmed
        """
    }
    
    # Sample inventory
    inventory = {
        'total_files': len(extracted_file_contents),
        'file_types': ['txt', 'pdf'],
        'total_content_length': sum(len(content) for content in extracted_file_contents.values())
    }
    
    print("🚀 Testing RAG Pathway Generation Algorithm")
    print("=" * 50)
    
    try:
        # Generate pathways using the new RAG algorithm
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
    result = test_rag_pathway_generation()
    if result:
        print("\n🎉 RAG Pathway Generation Test Completed Successfully!")
    else:
        print("\n💥 RAG Pathway Generation Test Failed!") 