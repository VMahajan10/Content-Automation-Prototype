#!/usr/bin/env python3
"""
Test file for content-aware chatbot functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_content_search():
    """Test the content search functionality"""
    
    # Mock editable pathways data
    editable_pathways = {
        'Safety Procedures': [
            {
                'title': 'PPE Requirements',
                'description': 'Personal protective equipment requirements',
                'content': 'All workers must wear hard hats, safety glasses, and steel-toed boots. High-visibility vests are mandatory in all work areas.'
            },
            {
                'title': 'Equipment Safety',
                'description': 'Equipment safety procedures',
                'content': 'Inspect all tools before use. Follow lockout/tagout procedures. Report damaged equipment immediately.'
            }
        ],
        'Quality Control': [
            {
                'title': 'Inspection Procedures',
                'description': 'Quality inspection methods',
                'content': 'Perform visual inspections before and after each operation. Check for defects and document findings.'
            }
        ]
    }
    
    print("🔍 Testing content search functionality...")
    
    # Test search for safety-related content
    from app import search_modules_by_content
    results = search_modules_by_content("safety", editable_pathways)
    
    print(f"Found {len(results)} results for 'safety':")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result['section']} - Module {result['module_number']}: {result['module_title']}")
        print(f"     Relevance score: {result['relevance_score']}")
    
    assert len(results) > 0, "Should find safety-related content"
    assert any('Safety Procedures' in result['section'] for result in results), "Should find content in Safety Procedures section"
    
    # Test search for equipment-related content
    results = search_modules_by_content("equipment", editable_pathways)
    print(f"\nFound {len(results)} results for 'equipment':")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result['section']} - Module {result['module_number']}: {result['module_title']}")
    
    assert len(results) > 0, "Should find equipment-related content"
    
    print("✅ Content search tests passed!")

def test_content_question_answering():
    """Test the content question answering functionality"""
    
    # Mock editable pathways data
    editable_pathways = {
        'Safety Procedures': [
            {
                'title': 'PPE Requirements',
                'description': 'Personal protective equipment requirements',
                'content': 'All workers must wear hard hats, safety glasses, and steel-toed boots. High-visibility vests are mandatory in all work areas.'
            }
        ]
    }
    
    print("\n🤖 Testing content question answering...")
    
    # Test question about PPE
    from app import answer_content_question
    question = "What PPE is required for workers?"
    answer = answer_content_question(question, editable_pathways)
    
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    
    # The answer should mention PPE requirements
    assert "PPE" in answer or "protective" in answer.lower() or "hard hat" in answer.lower(), "Answer should mention PPE requirements"
    
    print("✅ Content question answering tests passed!")

def test_module_content_summary():
    """Test the module content summary functionality"""
    
    print("\n📝 Testing module content summary...")
    
    module_data = {
        'title': 'Safety Procedures',
        'content': 'This module covers essential safety procedures including PPE requirements, emergency procedures, and hazard identification. Workers must follow all safety protocols to prevent accidents and injuries.'
    }
    
    from app import get_module_content_summary
    summary = get_module_content_summary(module_data)
    
    print(f"Module: {module_data['title']}")
    print(f"Summary: {summary}")
    
    assert len(summary) > 0, "Summary should not be empty"
    assert "safety" in summary.lower(), "Summary should mention safety"
    
    print("✅ Module content summary tests passed!")

def test_content_question_handling():
    """Test the content question handling functionality"""
    
    print("\n💬 Testing content question handling...")
    
    from app import handle_content_question_request
    
    # Test search request
    search_query = "find safety procedures"
    response = handle_content_question_request(search_query)
    print(f"Search query: {search_query}")
    print(f"Response: {response[:100]}...")
    
    assert "find" in response.lower() or "search" in response.lower(), "Should handle search requests"
    
    # Test content question
    content_question = "What are the safety requirements?"
    response = handle_content_question_request(content_question)
    print(f"Content question: {content_question}")
    print(f"Response: {response[:100]}...")
    
    # Test module content request
    module_request = "show content of module 1"
    response = handle_content_question_request(module_request)
    print(f"Module request: {module_request}")
    print(f"Response: {response[:100]}...")
    
    print("✅ Content question handling tests passed!")

def test_relevance_scoring():
    """Test the relevance scoring functionality"""
    
    print("\n📊 Testing relevance scoring...")
    
    from app import calculate_relevance_score
    
    # Test exact matches
    score = calculate_relevance_score("safety", "safety procedures", "safety", "safety description")
    print(f"Exact match score: {score}")
    assert score > 0, "Exact matches should have positive score"
    
    # Test partial matches
    score = calculate_relevance_score("ppe", "PPE requirements", "PPE", "personal protective equipment")
    print(f"Partial match score: {score}")
    assert score > 0, "Partial matches should have positive score"
    
    # Test no matches
    score = calculate_relevance_score("xyz", "safety procedures", "safety", "safety description")
    print(f"No match score: {score}")
    assert score == 0, "No matches should have zero score"
    
    print("✅ Relevance scoring tests passed!")

def main():
    """Run all content-aware chatbot tests"""
    print("🧠 Testing Content-Aware Chatbot Functionality")
    print("=" * 50)
    
    try:
        test_content_search()
        test_content_question_answering()
        test_module_content_summary()
        test_content_question_handling()
        test_relevance_scoring()
        
        print("\n🎉 All content-aware chatbot tests passed!")
        print("\n✅ Content-aware chatbot features implemented:")
        print("   • Search through module content")
        print("   • Answer questions about training content")
        print("   • Generate module content summaries")
        print("   • Calculate relevance scores")
        print("   • Handle various content question types")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 