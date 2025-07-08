#!/usr/bin/env python3
"""
Test script to verify improved module extraction and pathway creation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import gemini_generate_complete_pathway, get_parallel_config

def test_improved_extraction():
    """Test improved module extraction and pathway creation"""
    
    print("🧪 Testing Improved Module Extraction & Pathway Creation")
    print("=" * 70)
    
    # Sample training context (similar to user's)
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'construction',
        'primary_goals': 'understand factory workflow',
        'success_metrics': 'feedback surveys'
    }
    
    # Sample meeting transcript content (similar to user's file)
    extracted_file_contents = {
        'meeting_transcript.txt': """
        Meeting Discussion on Factory Workflow and Jig Assembly
        
        Bruce: So let's talk about the steel delivery process. When steel arrives at the factory, 
        it needs to be properly inspected and logged into our system. The receiving team should 
        check for any damage and verify the specifications match our order.
        
        Sarah: Right, and then we move it to the staging area where it gets organized by project. 
        Each piece should be tagged with the project number and priority level. This helps the 
        fabrication team know what to work on first.
        
        Mike: And during fabrication, we need to follow the safety protocols. Everyone should 
        wear proper PPE, and we have specific procedures for handling different types of steel. 
        The quality control checkpoints are crucial - we can't skip those.
        
        Bruce: Exactly. After fabrication, the assemblies go through final inspection before 
        being prepared for shipment. We need to ensure everything meets the specifications 
        and is properly packaged for transport.
        
        Sarah: What about the jig setup? That's a critical part of the process.
        
        Bruce: Yes, the jig is essential for consistent assembly. We need to make sure it's 
        properly calibrated and positioned before starting any fabrication work. The jig 
        ensures all components are aligned correctly.
        
        Mike: And we need to check the truss assembly process. The zigzag pattern is important 
        for structural integrity. We can't have any gaps or misalignments in the welding.
        
        Bruce: Right, the truss needs to be welded properly. We've welded the two halves together, 
        but we need to ensure the zigzag pattern is maintained throughout the assembly.
        
        Sarah: What about quality control? How do we verify the assembly meets specifications?
        
        Mike: We use calibrated measuring tools to check dimensional accuracy. We also do 
        visual inspections for weld quality and surface finish. Any defects need to be 
        documented and reported immediately.
        
        Bruce: And we need to maintain proper documentation. Every step of the process needs 
        to be recorded for quality assurance and future reference.
        
        Sarah: What about safety procedures? Are we following all the required protocols?
        
        Mike: Yes, we have comprehensive safety procedures in place. All workers must wear 
        appropriate PPE including safety glasses, steel-toed boots, and flame-resistant clothing. 
        Hard hats are required in all fabrication areas.
        
        Bruce: And we need to follow proper lifting techniques. Never attempt to lift heavy 
        materials manually. Always use appropriate lifting equipment such as cranes, forklifts, 
        or hoists.
        
        Sarah: What about emergency procedures? Do all workers know what to do in case of injury?
        
        Mike: Yes, everyone should know the location of emergency exits, first aid stations, 
        and fire extinguishers. In case of injury, immediately notify your supervisor and 
        seek medical attention if needed.
        
        Bruce: Good. Now let's talk about the workflow optimization. We need to streamline 
        the process to improve efficiency while maintaining quality standards.
        
        Sarah: I think we should implement better tracking systems. We need to know exactly 
        where each component is in the process at any given time.
        
        Mike: And we should establish clear handoff procedures between different workstations. 
        Each team needs to know exactly what the previous team completed and what they need 
        to do next.
        
        Bruce: Excellent points. Let's document these procedures and make sure everyone 
        is trained on the new workflow.
        """,
        
        'safety_procedures.txt': """
        Safety Procedures for Fabrication Operations
        
        Personal Protective Equipment Requirements
        All personnel must wear appropriate PPE based on their specific tasks. Safety 
        glasses with side shields are mandatory for all operations. Steel-toed boots 
        must meet ASTM standards. Flame-resistant clothing is required for welding 
        operations. Respiratory protection may be needed in areas with poor ventilation.
        
        Material Handling and Lifting Procedures
        Never attempt to lift heavy materials manually. Always use appropriate lifting 
        equipment such as cranes, forklifts, or hoists. Inspect lifting equipment before 
        each use. Ensure proper rigging and secure loads before lifting. Maintain clear 
        communication with crane operators and ground personnel during lifting operations.
        
        Equipment Operation and Maintenance
        Only trained and authorized personnel may operate heavy equipment. Conduct 
        pre-operation inspections of all equipment. Follow manufacturer guidelines for 
        maintenance schedules. Report any equipment malfunctions immediately. Keep all 
        safety guards and devices in place during operation.
        
        Emergency Response Procedures
        Know the location of emergency exits, first aid stations, and fire extinguishers. 
        In case of injury, immediately notify your supervisor and seek medical attention 
        if needed. For fires, use the appropriate extinguisher and evacuate if necessary. 
        Know the emergency contact numbers and evacuation procedures for your work area.
        
        Quality Control and Inspection
        Implement quality control checkpoints at each stage of the fabrication process. 
        Inspect welds for proper penetration and appearance. Verify dimensional accuracy 
        using calibrated measuring tools. Document all inspection results in the quality 
        control log. Any non-conforming items must be immediately reported to the supervisor.
        """
    }
    
    # Sample file inventory
    file_inventory = {
        'process_docs': 'Factory workflow procedures and safety protocols',
        'training_materials': 'Meeting transcripts and safety documentation'
    }
    
    print(f"📋 Training Context: {training_context}")
    print(f"📁 Files to process: {list(extracted_file_contents.keys())}")
    print(f"📝 File inventory: {file_inventory}")
    
    # Test with bypass filtering to include all content
    print("\n🔄 Testing with bypass filtering (include all content)...")
    
    try:
        result = gemini_generate_complete_pathway(
            training_context, 
            extracted_file_contents, 
            file_inventory, 
            bypass_filtering=True
        )
        
        if result and 'pathways' in result:
            pathways = result['pathways']
            print(f"✅ Successfully created {len(pathways)} pathways")
            
            total_modules = 0
            for i, pathway in enumerate(pathways):
                sections = pathway.get('sections', [])
                pathway_modules = sum(len(section.get('modules', [])) for section in sections)
                total_modules += pathway_modules
                
                print(f"\n📚 Pathway {i+1}: {pathway.get('pathway_name', 'Unknown')}")
                print(f"   Sections: {len(sections)}")
                print(f"   Total Modules: {pathway_modules}")
                
                for j, section in enumerate(sections):
                    modules = section.get('modules', [])
                    print(f"     Section {j+1}: {section.get('title', 'Unknown')} - {len(modules)} modules")
                    
                    for k, module in enumerate(modules):
                        print(f"       Module {k+1}: {module.get('title', 'No title')}")
                        print(f"         Description: {module.get('description', 'No description')}")
                        print(f"         Content length: {len(module.get('content', ''))} characters")
                        print(f"         Source: {module.get('source', 'Unknown')}")
                        
                        # Show first 100 characters of content
                        content_preview = module.get('content', '')[:100]
                        if content_preview:
                            print(f"         Content preview: {content_preview}...")
                        print()
            
            print(f"📊 **Summary:**")
            print(f"   Total Pathways: {len(pathways)}")
            print(f"   Total Modules: {total_modules}")
            print(f"   Average Modules per Pathway: {total_modules/len(pathways):.1f}")
            
        else:
            print("❌ No pathways created")
            
    except Exception as e:
        print(f"❌ Error creating pathways: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_extraction() 