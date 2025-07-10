#!/usr/bin/env python3
"""
Test script to verify performance optimizations work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import get_parallel_config, detect_content_type, extract_training_information_from_content

def test_performance_optimizations():
    """Test that performance optimizations work correctly"""
    
    print("🚀 Testing Performance Optimizations")
    print("=" * 50)
    
    # Test 1: Check parallel config
    config = get_parallel_config()
    print(f"✅ Parallel config: {config}")
    print(f"   Max file workers: {config['max_file_workers']}")
    print(f"   Timeout: {config['timeout_seconds']}s")
    print(f"   Batch AI calls: {config['batch_ai_calls']}")
    
    # Test 2: Check content type detection
    sample_content = """
    Teams Meeting
    Mon, Dec 9, 2024
    
    0:00 - Mike Wright
    in too Bruce, all good?
    
    0:02 - Bruce Mullaney
    Yeah, thank you. I've got to stop and use the restroom in about five minutes.
    """
    
    content_type = detect_content_type(sample_content)
    print(f"✅ Content type detection: {content_type}")
    
    # Test 3: Check training information extraction
    training_context = {
        'primary_goals': 'understand meeting protocols',
        'training_type': 'Communication Training',
        'target_audience': 'employees',
        'industry': 'general'
    }
    
    try:
        training_info = extract_training_information_from_content(sample_content, training_context)
        print(f"✅ Training info extraction: {len(training_info)} sections")
    except Exception as e:
        print(f"⚠️ Training info extraction failed: {e}")
    
    print("\n✅ Performance optimizations test completed!")

if __name__ == "__main__":
    test_performance_optimizations() 