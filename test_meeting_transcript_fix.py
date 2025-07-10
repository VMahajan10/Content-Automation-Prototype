#!/usr/bin/env python3
"""
Test script to verify meeting transcript handling improvements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import extract_ai_goal_aligned_modules, debug_print
from modules.config import model

def test_meeting_transcript_handling():
    """Test the improved meeting transcript handling"""
    
    # Sample meeting transcript content
    meeting_content = """
    Teams Meeting Transcript
    0:00 - John: Yeah, so we need to discuss the new onboarding process for the bridge fabrication team.
    0:05 - Sarah: Right, I think we should focus on safety procedures first.
    0:10 - John: Absolutely. The new employees need to understand PPE requirements and proper equipment handling.
    0:15 - Sarah: And we should include quality control procedures too.
    0:20 - John: Yeah, that's important. We need to make sure they know how to inspect welds and check measurements.
    0:25 - Sarah: What about the documentation process?
    0:30 - John: Good point. They need to learn how to fill out the inspection forms and record their work.
    0:35 - Sarah: And we should cover the emergency procedures too.
    0:40 - John: Definitely. Safety first, always.
    """
    
    # Sample training context
    context = {
        'training_type': 'Onboarding',
        'target_audience': 'New Employees',
        'industry': 'Manufacturing',
        'primary_goals': 'Bridge fabrication safety and quality procedures'
    }
    
    print("🧪 Testing meeting transcript handling...")
    print(f"📄 Content length: {len(meeting_content)} characters")
    print(f"🎯 Training goals: {context['primary_goals']}")
    
    # Test the improved function
    modules = extract_ai_goal_aligned_modules(
        "Teams Meeting Transcript.txt",
        meeting_content,
        context,
        context['primary_goals']
    )
    
    print(f"\n📋 Results:")
    print(f"✅ Extracted {len(modules)} modules")
    
    for i, module in enumerate(modules, 1):
        print(f"\n📄 Module {i}:")
        print(f"   Title: {module.get('title', 'N/A')}")
        print(f"   Description: {module.get('description', 'N/A')}")
        print(f"   Content length: {len(module.get('content', ''))} characters")
        print(f"   Key points: {module.get('key_points', [])}")
    
    return len(modules) > 0

if __name__ == "__main__":
    success = test_meeting_transcript_handling()
    if success:
        print("\n✅ Meeting transcript handling test PASSED")
    else:
        print("\n❌ Meeting transcript handling test FAILED") 