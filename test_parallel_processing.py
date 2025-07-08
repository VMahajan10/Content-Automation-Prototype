#!/usr/bin/env python3
"""
Test script for parallel processing capabilities
Demonstrates how multiple AI agents work together to speed up analysis
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit for testing
class MockStreamlit:
    def write(self, text):
        print(f"DEBUG: {text}")
    
    def warning(self, text):
        print(f"WARNING: {text}")

# Replace streamlit with mock
import modules.utils
modules.utils.st = MockStreamlit()

from modules.utils import extract_modules_from_file_content_fallback, get_parallel_config

def test_parallel_processing():
    """Test the parallel processing capabilities"""
    
    # Sample training context
    training_context = {
        'primary_goals': 'Teach employees project management and team collaboration skills',
        'success_metrics': 'Improved project delivery times and team productivity',
        'training_type': 'Project Management',
        'target_audience': 'Project Managers and Team Leads',
        'industry': 'Technology'
    }
    
    # Sample content with many sections to test parallel processing
    sample_content = """
    Project Planning Fundamentals
    
    Every successful project starts with thorough planning. Define clear objectives, identify stakeholders, and establish realistic timelines. Break down the project into manageable phases and assign responsibilities.
    
    Team Communication Strategies
    
    Effective communication is the backbone of successful project management. Establish regular check-ins, use appropriate communication channels, and ensure all team members are informed of progress and changes.
    
    Risk Management Techniques
    
    Identify potential risks early in the project lifecycle. Assess the impact and probability of each risk, develop mitigation strategies, and create contingency plans for high-priority risks.
    
    Resource Allocation Best Practices
    
    Optimize resource allocation by understanding team member strengths and availability. Balance workload across the team and ensure critical tasks have adequate resources and backup plans.
    
    Stakeholder Management
    
    Build strong relationships with all project stakeholders. Understand their needs and expectations, communicate regularly, and address concerns promptly to maintain project support.
    
    Quality Assurance Processes
    
    Implement quality checks throughout the project lifecycle. Define quality standards, conduct regular reviews, and ensure deliverables meet established criteria before final delivery.
    
    Budget Management
    
    Monitor project costs carefully and track expenses against the budget. Identify cost-saving opportunities and address budget overruns early to maintain financial control.
    
    Timeline Management
    
    Use project management tools to track progress and identify potential delays. Adjust schedules as needed and communicate timeline changes to all stakeholders promptly.
    
    Conflict Resolution
    
    Address team conflicts quickly and professionally. Focus on the issue rather than personalities, facilitate open discussion, and work toward mutually acceptable solutions.
    
    Performance Monitoring
    
    Track key performance indicators throughout the project. Monitor progress, identify trends, and make data-driven decisions to improve project outcomes.
    """
    
    print("🚀 Testing Parallel Processing Capabilities")
    print("=" * 60)
    print(f"Training Goals: {training_context['primary_goals']}")
    print(f"Success Metrics: {training_context['success_metrics']}")
    print(f"Training Type: {training_context['training_type']}")
    print(f"Target Audience: {training_context['target_audience']}")
    print(f"Industry: {training_context['industry']}")
    print()
    
    # Show parallel configuration
    config = get_parallel_config()
    print(f"⚙️ **Parallel Configuration:**")
    print(f"   Max File Workers: {config['max_file_workers']}")
    print(f"   Max Section Workers: {config['max_section_workers']}")
    print(f"   Max Topic Workers: {config['max_topic_workers']}")
    print(f"   Timeout: {config['timeout_seconds']} seconds")
    print()
    
    # Test parallel extraction
    start_time = time.time()
    print("🔄 Starting parallel semantic analysis...")
    
    modules = extract_modules_from_file_content_fallback("sample_content.txt", sample_content, training_context)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"✅ Parallel processing completed in {processing_time:.2f} seconds")
    print(f"✅ Extracted {len(modules)} semantically relevant modules")
    print()
    
    # Display the extracted modules
    for i, module in enumerate(modules, 1):
        print(f"📚 Module {i}: {module['title']}")
        print(f"   Description: {module['description']}")
        print(f"   Relevance Score: {module.get('relevance_score', 'N/A')}")
        print(f"   Semantic Match: {module.get('key_points', [])}")
        if module.get('full_reason'):
            print(f"   Analysis: {module['full_reason']}")
        print(f"   Content Preview: {module['content'][:100]}...")
        print()
    
    # Performance summary
    print("📊 **Performance Summary:**")
    print(f"   Total Processing Time: {processing_time:.2f} seconds")
    print(f"   Modules Extracted: {len(modules)}")
    print(f"   Average Time per Module: {processing_time/len(modules):.2f} seconds")
    print(f"   Parallel Efficiency: {'High' if processing_time < 30 else 'Medium' if processing_time < 60 else 'Low'}")

if __name__ == "__main__":
    test_parallel_processing() 