#!/usr/bin/env python3
"""
Test script for the optimized fast pathway generation algorithm
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import gemini_generate_complete_pathway, debug_print, flush_debug_logs_to_streamlit

def test_fast_pathway_generation():
    """Test the optimized fast pathway generation algorithm"""
    
    # Training context
    context = {
        'training_type': 'Manufacturing Training',
        'target_audience': 'factory workers',
        'industry': 'manufacturing',
        'primary_goals': 'Improve manufacturing efficiency, quality control, and safety procedures'
    }
    
    # Sample file contents
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
        'file_types': ['txt'],
        'total_content_length': sum(len(content) for content in extracted_file_contents.values())
    }
    
    print("🚀 Testing Fast Pathway Generation Algorithm")
    print("=" * 50)
    print("Target: 2-3 minutes processing time")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Generate pathways using the fast algorithm
        result = gemini_generate_complete_pathway(
            context=context,
            extracted_file_contents=extracted_file_contents,
            inventory=inventory,
            enhanced_content=False  # Use fast mode
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Display results
        print(f"\n✅ Pathway Generation Completed!")
        print(f"⏱️ Processing Time: {processing_time:.1f} seconds ({processing_time/60:.1f} minutes)")
        
        if processing_time <= 180:  # 3 minutes
            print("🎯 Target achieved: Processing completed within 3 minutes!")
        else:
            print("⚠️ Processing took longer than 3 minutes")
        
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
                    print(f"        Description: {module['description'][:80]}...")
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
        
        return result, processing_time
        
    except Exception as e:
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"❌ Error during pathway generation: {e}")
        print(f"⏱️ Processing Time: {processing_time:.1f} seconds")
        import traceback
        traceback.print_exc()
        return None, processing_time

if __name__ == "__main__":
    result, processing_time = test_fast_pathway_generation()
    if result:
        print(f"\n🎉 Fast Pathway Generation Test Completed Successfully!")
        print(f"⏱️ Total Time: {processing_time:.1f} seconds ({processing_time/60:.1f} minutes)")
        if processing_time <= 180:
            print("✅ Performance target achieved!")
        else:
            print("⚠️ Performance target not met - may need further optimization")
    else:
        print(f"\n💥 Fast Pathway Generation Test Failed!")
        print(f"⏱️ Time before failure: {processing_time:.1f} seconds") 