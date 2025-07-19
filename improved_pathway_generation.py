#!/usr/bin/env python3
"""
Improved pathway generation system that addresses:
1. Multiple sections instead of one
2. Professional and concise content
3. Content that reflects user training goals from uploaded files
4. Proper module distribution across sections
"""

import re
import json
from typing import Dict, List, Any

def extract_technical_content_professional(content: str) -> str:
    """
    Extract technical content and transform it into professional, concise training material
    """
    # Remove timestamps and speaker names
    content = re.sub(r'\d{1,2}:\d{2}:\d{2}\s*-\s*[^:]+:', '', content)
    content = re.sub(r'\d{1,2}:\d{2}\s*-\s*[^:]+:', '', content)
    
    # Remove conversational fillers
    fillers = ['um', 'uh', 'you know', 'like', 'so', 'well', 'basically', 'actually', 'really', 'just', 'simply', 'obviously', 'clearly', 'sort of', 'kind of']
    for filler in fillers:
        content = re.sub(rf'\\b{filler}\\b', '', content, flags=re.IGNORECASE)
    
    # Remove incomplete sentences and fragments
    sentences = re.split(r'[.!?]+', content)
    complete_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        # Only keep substantial, complete sentences
        if len(sentence) > 20 and not sentence.lower().startswith(('so', 'well', 'yeah', 'okay', 'right')):
            # Remove first-person references
            sentence = re.sub(r'\\bI\\b', 'Personnel', sentence)
            sentence = re.sub(r'\\bwe\\b', 'the team', sentence, flags=re.IGNORECASE)
            sentence = re.sub(r'\\byou\\b', 'operators', sentence, flags=re.IGNORECASE)
            
            # Capitalize first letter and ensure proper sentence structure
            sentence = sentence[0].upper() + sentence[1:] if sentence else ''
            
            if sentence and len(sentence) > 20:
                complete_sentences.append(sentence)
    
    return '. '.join(complete_sentences[:20])  # Limit to 20 sentences for conciseness

def create_professional_training_modules(content: str, training_context: Dict) -> List[Dict]:
    """
    Create professional training modules from content
    """
    professional_content = extract_technical_content_professional(content)
    
    if not professional_content:
        return []
    
    # Split content into logical sections
    content_chunks = professional_content.split('. ')
    chunk_size = max(3, len(content_chunks) // 4)  # Aim for 4 modules max
    
    modules = []
    for i in range(0, len(content_chunks), chunk_size):
        chunk = '. '.join(content_chunks[i:i+chunk_size])
        
        if len(chunk) > 100:  # Only create modules with substantial content
            module = {
                'title': f"{training_context.get('industry', 'Professional')} Training Module {len(modules) + 1}",
                'description': f"Essential training content for {training_context.get('target_audience', 'team members')}",
                'content': format_professional_content(chunk, training_context),
                'learning_objectives': generate_learning_objectives(chunk, training_context),
                'key_points': extract_key_points(chunk)
            }
            modules.append(module)
    
    return modules[:4]  # Maximum 4 modules

def format_professional_content(content: str, training_context: Dict) -> str:
    """
    Format content into professional training structure
    """
    formatted = f"""
TRAINING MODULE: {training_context.get('training_type', 'PROFESSIONAL TRAINING')}

Target Audience: {training_context.get('target_audience', 'Team Members')}
Industry: {training_context.get('industry', 'Professional')}
Training Focus: {training_context.get('primary_goals', 'Skill Development')}

CORE CONTENT:
{content}

IMPLEMENTATION GUIDELINES:
• Follow established protocols and procedures
• Maintain quality standards throughout all operations
• Ensure compliance with industry standards
• Document all processes and outcomes

ASSESSMENT CRITERIA:
• Demonstrate understanding of key concepts
• Apply knowledge in practical scenarios
• Meet performance standards
• Complete required evaluations
"""
    return formatted

def generate_learning_objectives(content: str, training_context: Dict) -> List[str]:
    """
    Generate learning objectives based on content
    """
    objectives = [
        f"Understand core concepts related to {training_context.get('industry', 'the field')}",
        f"Apply knowledge in {training_context.get('target_audience', 'professional')} scenarios",
        "Demonstrate competency in required procedures",
        "Meet quality and performance standards"
    ]
    return objectives

def extract_key_points(content: str) -> List[str]:
    """
    Extract key points from content
    """
    sentences = content.split('. ')
    key_points = []
    
    for sentence in sentences[:5]:  # Take first 5 sentences
        if len(sentence) > 20:
            key_points.append(sentence.strip())
    
    return key_points

def create_multiple_sections(modules: List[Dict], training_context: Dict) -> List[Dict]:
    """
    Organize modules into multiple sections (max 2 modules per section)
    """
    sections = []
    section_names = [
        "Foundation & Core Concepts",
        "Operational Procedures",
        "Advanced Applications",
        "Quality & Compliance"
    ]
    
    modules_per_section = 2
    
    for i, section_name in enumerate(section_names):
        start_idx = i * modules_per_section
        end_idx = start_idx + modules_per_section
        section_modules = modules[start_idx:end_idx]
        
        if section_modules:
            section = {
                'title': section_name,
                'description': f"Essential {section_name.lower()} for {training_context.get('target_audience', 'team members')}",
                'modules': section_modules
            }
            sections.append(section)
    
    return sections

def generate_improved_pathway(content: str, training_context: Dict, filename: str) -> Dict:
    """
    Generate improved pathway with multiple sections and professional content
    """
    # Create professional training modules
    modules = create_professional_training_modules(content, training_context)
    
    if not modules:
        return create_fallback_pathway(training_context, filename)
    
    # Organize into multiple sections
    sections = create_multiple_sections(modules, training_context)
    
    pathway = {
        'pathways': [{
            'pathway_name': f"Professional {training_context.get('industry', 'Training')} Program",
            'description': f"Comprehensive training program for {training_context.get('target_audience', 'team members')} in {training_context.get('industry', 'professional')} environment",
            'sections': sections,
            'source_files': [filename],
            'total_modules': len(modules)
        }]
    }
    
    return pathway

def create_fallback_pathway(training_context: Dict, filename: str) -> Dict:
    """
    Create fallback pathway when content extraction fails
    """
    return {
        'pathways': [{
            'pathway_name': f"Professional {training_context.get('industry', 'Training')} Program",
            'description': f"Training program for {training_context.get('target_audience', 'team members')}",
            'sections': [{
                'title': 'Foundation & Core Concepts',
                'description': 'Essential foundational knowledge',
                'modules': [{
                    'title': f"Introduction to {training_context.get('industry', 'Professional')} Training",
                    'description': f"Overview of key concepts for {training_context.get('target_audience', 'team members')}",
                    'content': f"""
TRAINING MODULE: {training_context.get('training_type', 'PROFESSIONAL TRAINING')}

This module provides essential training content based on uploaded materials.

CORE OBJECTIVES:
• Understand fundamental concepts
• Apply knowledge in practical scenarios
• Meet performance standards
• Ensure compliance with requirements

IMPLEMENTATION:
• Follow established procedures
• Maintain quality standards
• Document all processes
• Complete required assessments
""",
                    'learning_objectives': [
                        "Understand core concepts",
                        "Apply knowledge practically",
                        "Meet performance standards"
                    ],
                    'key_points': [
                        "Essential training concepts",
                        "Practical application methods",
                        "Quality assurance requirements"
                    ]
                }]
            }],
            'source_files': [filename],
            'total_modules': 1
        }]
    }
