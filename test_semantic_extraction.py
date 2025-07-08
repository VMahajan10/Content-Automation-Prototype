#!/usr/bin/env python3
"""
Test script for semantic topic analysis extraction
Demonstrates how content is analyzed semantically for relevance
"""

import sys
import os
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

from modules.utils import extract_modules_from_file_content_fallback

def test_semantic_extraction():
    """Test the semantic content extraction with sample data"""
    
    # Sample training context with specific goals
    training_context = {
        'primary_goals': 'Teach employees effective communication and problem-solving skills',
        'success_metrics': 'Improved team collaboration and faster issue resolution',
        'training_type': 'Professional Development',
        'target_audience': 'Team Leaders and Managers',
        'industry': 'Technology'
    }
    
    # Sample content with various topics
    sample_content = """
    Effective Communication Strategies
    
    Active listening is the foundation of good communication. When someone is speaking, focus entirely on what they're saying without planning your response. Ask clarifying questions to ensure understanding.
    
    Problem-Solving Framework
    
    When faced with a complex problem, start by clearly defining the issue. Break it down into smaller, manageable components. Gather relevant information and consider multiple perspectives before developing solutions.
    
    Team Collaboration Best Practices
    
    Successful teams establish clear roles and responsibilities. Regular check-ins and transparent communication channels help maintain alignment. Celebrate wins and learn from challenges together.
    
    Technical Documentation Standards
    
    All code changes must be documented with clear comments. Use consistent formatting and include examples where appropriate. Maintain version control and update documentation regularly.
    
    Customer Service Excellence
    
    Always put the customer first. Listen to their concerns with empathy and respond promptly. Follow up to ensure satisfaction and use feedback to improve processes.
    
    Project Management Fundamentals
    
    Define clear objectives and timelines for each project. Assign responsibilities and establish checkpoints for progress review. Communicate regularly with stakeholders and adjust plans as needed.
    
    Conflict Resolution Techniques
    
    Address conflicts early before they escalate. Focus on the issue, not the person. Find common ground and work toward mutually acceptable solutions. Document agreements and follow up.
    
    Leadership Development
    
    Good leaders inspire and motivate their teams. Lead by example and provide constructive feedback. Encourage growth and development while maintaining high standards.
    """
    
    print("🧠 Testing Semantic Topic Analysis Extraction")
    print("=" * 60)
    print(f"Training Goals: {training_context['primary_goals']}")
    print(f"Success Metrics: {training_context['success_metrics']}")
    print(f"Training Type: {training_context['training_type']}")
    print(f"Target Audience: {training_context['target_audience']}")
    print(f"Industry: {training_context['industry']}")
    print()
    
    # Extract modules using the semantic analysis function
    modules = extract_modules_from_file_content_fallback("sample_content.txt", sample_content, training_context)
    
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

if __name__ == "__main__":
    test_semantic_extraction() 