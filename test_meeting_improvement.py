#!/usr/bin/env python3
"""
Test script to verify meeting transcript processing improvements
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the modules directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_meeting_transcript_processing():
    """Test the improved meeting transcript processing"""
    
    try:
        from utils import extract_meeting_transcript_modules
        
        # Sample meeting transcript content
        meeting_content = """
        10:00 - John: Alright team, let's go over the bridge fabrication process today.
        
        10:01 - Sarah: Yes, we need to make sure everyone understands the new safety protocols.
        
        10:02 - John: Exactly. So first, when working with the steel beams, you must always wear your PPE.
        
        10:03 - Mike: What about the welding procedures? We had some issues last week.
        
        10:04 - Sarah: Good point. The welding must be done in the designated area with proper ventilation.
        
        10:05 - John: And don't forget the quality control checkpoints. Every weld needs to be inspected.
        
        10:06 - Mike: How often should we check the equipment?
        
        10:07 - Sarah: Daily inspections are mandatory. Check for any signs of wear or damage.
        
        10:08 - John: And document everything in the logbook. This is crucial for safety compliance.
        
        10:09 - Mike: What about the new flowchart process?
        
        10:10 - Sarah: Yes, we need to update the process mapping. Each step should be clearly documented.
        
        10:11 - John: The flowchart will help new employees understand the workflow better.
        
        10:12 - Mike: Should we include the emergency procedures in the flowchart?
        
        10:13 - Sarah: Absolutely. Emergency shutdown procedures must be prominently displayed.
        
        10:14 - John: And make sure everyone knows the evacuation routes and assembly points.
        
        10:15 - Mike: What about the material handling procedures?
        
        10:16 - Sarah: All materials must be properly secured during transport and storage.
        
        10:17 - John: And use the correct lifting equipment. No manual lifting of heavy materials.
        
        10:18 - Mike: Got it. Any other procedures we should review?
        
        10:19 - Sarah: Yes, the quality assurance process needs to be followed step by step.
        
        10:20 - John: And remember, safety is everyone's responsibility. Report any concerns immediately.
        """
        
        # Sample training context
        context = {
            'primary_goals': 'Bridge fabrication safety and quality procedures',
            'training_type': 'Safety Training',
            'target_audience': 'Manufacturing Team',
            'industry': 'Construction',
            'company_size': 'Medium'
        }
        
        print("🔍 Testing improved meeting transcript processing...")
        print(f"📋 Context: {context}")
        print(f"📄 Meeting content length: {len(meeting_content)} characters")
        
        # Process the meeting transcript
        modules = extract_meeting_transcript_modules(
            "Teams Meeting Transcript.txt",
            meeting_content,
            context,
            context['primary_goals']
        )
        
        print(f"\n✅ **Results:**")
        print(f"📊 Total modules extracted: {len(modules)}")
        
        for i, module in enumerate(modules, 1):
            print(f"\n📋 **Module {i}:**")
            print(f"   Title: {module.get('title', 'No title')}")
            print(f"   Description: {module.get('description', 'No description')}")
            print(f"   Content length: {len(module.get('content', ''))} characters")
            print(f"   Source: {module.get('source', 'No source')}")
            print(f"   Content types: {len(module.get('content_types', []))} types")
            print(f"   Key points: {module.get('key_points', [])}")
            
            # Show a preview of the content
            content = module.get('content', '')
            if content:
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"   Content preview: {preview}")
        
        return modules
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"📝 Full error: {traceback.format_exc()}")
        return []

if __name__ == "__main__":
    test_meeting_transcript_processing() 