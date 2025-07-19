#!/usr/bin/env python3
"""
Fast AI Agents for Pathway Generation using Google Gemini
Optimized for speed while maintaining quality
"""

import json
import re
import random
import time
import concurrent.futures
import threading
from modules.config import model
from modules.utils import debug_print

# Global content tracking to prevent duplication across pathways
GENERATED_CONTENT_CACHE = set()

def is_content_unique(content_hash):
    """Check if content hash is unique across all generated pathways"""
    return content_hash not in GENERATED_CONTENT_CACHE

def add_content_to_cache(content_hash):
    """Add content hash to cache to prevent future duplication"""
    GENERATED_CONTENT_CACHE.add(content_hash)

def create_goal_specific_content_fingerprint(content, primary_goals, content_type):
    """
    Create a fingerprint for content that considers goals and content type
    to prevent goal-specific duplications
    """
    import hashlib
    
    # Normalize content for comparison
    normalized_content = content.lower().strip()
    normalized_goals = primary_goals.lower().strip()
    
    # Create fingerprint combining content, goals, and type
    fingerprint_data = f"{normalized_content}|{normalized_goals}|{content_type}"
    content_hash = hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    return content_hash

def validate_content_uniqueness_for_goals(content, primary_goals, content_type):
    """
    Validate that content is unique for the specific goals and content type
    """
    fingerprint = create_goal_specific_content_fingerprint(content, primary_goals, content_type)
    
    if is_content_unique(fingerprint):
        add_content_to_cache(fingerprint)
        return True
    else:
        return False

class FastPathwayAgent:
    """
    Single, fast AI agent that generates complete pathways in one optimized call
    """
    
    def __init__(self):
        self.model = model
        
    def generate_complete_pathways_fast(self, extracted_content, training_context, file_inventory):
        """
        Generate complete pathways in a single, optimized AI call
        """
        try:
            if not self.model:
                debug_print("⚠️ Gemini model not available, using fallback")
                return self._create_fast_fallback(extracted_content, training_context)
            
            # Prepare optimized prompt
            prompt = self._build_fast_comprehensive_prompt(extracted_content, training_context, file_inventory)
            
            debug_print("🚀 FastPathwayAgent: Generating complete pathways in single call...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                result = self._parse_complete_pathways(response.text)
                if result and result.get('pathways'):
                    debug_print(f"✅ FastPathwayAgent: Generated {len(result['pathways'])} complete pathways")
                    
                    # Import and apply validation to ensure minimum modules per section and sections per pathway
                    from modules.utils import validate_and_enhance_pathway_modules
                    result = validate_and_enhance_pathway_modules(result, min_modules_per_section=6, min_sections_per_pathway=4)
                    debug_print(f"✅ FastPathwayAgent: Validated and enhanced pathways")
                    
                    # Add content hashes to cache to prevent duplication in future generations
                    import hashlib
                    if result and 'pathways' in result:
                        for pathway in result['pathways']:
                            for section in pathway.get('sections', []):
                                for module in section.get('modules', []):
                                    content = module.get('content', '')
                                    content_hash = hashlib.md5(content.encode()).hexdigest()
                                    add_content_to_cache(content_hash)
                    
                    return result
                else:
                    debug_print("⚠️ Failed to parse AI response, using fallback")
                    return self._create_fast_fallback(extracted_content, training_context)
            else:
                debug_print("⚠️ No AI response, using fallback")
                return self._create_fast_fallback(extracted_content, training_context)
                
        except Exception as e:
            debug_print(f"⚠️ FastPathwayAgent error: {str(e)}")
            return self._create_fast_fallback(extracted_content, training_context)
    
    def _build_fast_comprehensive_prompt(self, extracted_content, training_context, file_inventory):
        """
        Build a single, comprehensive prompt for complete pathway generation with randomization
        """
        # Extract content relevant to training goals
        primary_goals = training_context.get('primary_goals', '')
        training_type = training_context.get('training_type', '')
        
        # Add unique randomization elements to prevent repetitive content
        from modules.utils import generate_unique_content_seed
        unique_seed = generate_unique_content_seed()
        
        variation_approaches = [
            "comprehensive and detailed",
            "practical and hands-on", 
            "step-by-step and methodical",
            "interactive and engaging",
            "case-study focused",
            "problem-solving oriented",
            "scenario-based learning",
            "competency-focused training",
            "industry-specific applications"
        ]
        
        # Use hash of unique seed to select approach for consistency with uniqueness
        import hashlib
        approach_index = int(hashlib.md5(unique_seed.encode()).hexdigest(), 16) % len(variation_approaches)
        selected_approach = variation_approaches[approach_index]
        
        content_summary = f"PRIMARY TRAINING GOALS: {primary_goals}\nTRAINING TYPE: {training_type}\n\n"
        content_summary += f"UNIQUE CONTENT ID: {unique_seed}\n"
        content_summary += f"VARIATION APPROACH: Create {selected_approach} content with unique perspectives\n"
        content_summary += f"CONTENT DIFFERENTIATION: Ensure this content is distinct from other pathways using seed {unique_seed}\n\n"
        
        for filename, content in list(extracted_content.items())[:5]:  # Increased to 5 files for more comprehensive content
            if content:
                # Clean and extract substantive content - use more content for better depth
                preview = content[:3000] if content else "No content"  # Increased content length for more context
                # Clean preview for better AI processing
                preview = re.sub(r'Teams Meeting.*?\d{4}', '', preview, flags=re.IGNORECASE)
                preview = re.sub(r'thank personnel|restroom|car accident|highway', '', preview, flags=re.IGNORECASE)
                preview = re.sub(r'Oh,.*?sense\.', '', preview, flags=re.IGNORECASE)
                preview = re.sub(r'\s+', ' ', preview)  # Clean multiple spaces
                
                # Extract specific content elements for modules
                content_summary += f"\n=== FILE: {filename} ===\n"
                content_summary += f"FULL CONTENT EXTRACT (USE THIS SPECIFIC INFORMATION):\n{preview}\n"
                
                # Add specific instructions for using this file content
                content_summary += f"MANDATORY FILE USAGE INSTRUCTIONS FOR {filename}:\n"
                content_summary += f"- Extract SPECIFIC procedures, steps, and information from this file content\n"
                content_summary += f"- Use ACTUAL data, processes, and requirements mentioned in the file\n"
                content_summary += f"- Create modules that teach users the SPECIFIC content from this file\n"
                content_summary += f"- Reference SPECIFIC details, examples, and procedures from this file\n"
                content_summary += f"- Generate content_blocks with ACTUAL information from this file\n"
                content_summary += f"- AVOID generic content - use the specific file information\n\n"
                
                content_summary += f"CRITICAL: Each module must include SPECIFIC information from {filename} that helps achieve: {primary_goals}\n"
                content_summary += f"FOCUS: Create detailed, actionable modules using ACTUAL file content for: {primary_goals}\n"
        
        prompt = f"""You are an expert Training Pathway Creator specializing in goal-driven, user-specific onboarding pathways. Generate 2-3 comprehensive training pathways that directly achieve the user's specified goals and requirements.

=== USER-SPECIFIED TRAINING GOALS (HIGHEST PRIORITY) ===
PRIMARY GOALS: {primary_goals}
SUCCESS METRICS: {training_context.get('success_metrics', 'User engagement and knowledge retention')}
TARGET AUDIENCE: {training_context.get('target_audience', 'New employees')}
INDUSTRY CONTEXT: {training_context.get('industry', 'General business')}
TRAINING TYPE: {training_context.get('training_type', 'Onboarding')}
URGENCY LEVEL: {training_context.get('urgency_level', 'Medium')}
TIMELINE: {training_context.get('timeline', 'Standard')}

=== CONTENT TO PROCESS ===
{content_summary}

=== CRITICAL REQUIREMENTS ===
TASK: Create 2-3 distinct pathways with 4-5 sections each, 4-6 modules per section.
GOAL ALIGNMENT: Every module must directly support achieving the user's PRIMARY TRAINING GOALS: {primary_goals}
PERSONALIZATION: All content must be customized to the user's specific requirements, NOT generic templates.
USER-CENTRIC: Focus on what the user specifically wants to achieve, not generic onboarding content.

VARIATION REQUIREMENT: Make this content {selected_approach} with unique perspectives, examples, and approaches. 
CONTENT UNIQUENESS: Use unique content ID {unique_seed} to ensure this pathway is completely distinct from any other pathways.
AVOID REPETITION: Do not reuse content patterns, examples, or structures from previous generations.

MODULE GENERATION REQUIREMENT: You MUST generate ALL modules for each section with decimal numbering:
- Section 1: Modules 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
- Section 2: Modules 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
- Section 3: Modules 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
- etc.

CRITICAL CONTENT TYPE REQUIREMENT: Each module MUST contain at least 3 distinct content types from this list:
- Text, List, Image, Flashcard, Video, File, Accordion, Divider, Tabs, Knowledge Check, Survey, Assignment

CONTENT TYPE DIVERSITY MANDATE:
- Use ALL available content types across modules, not just Text/List/Video
- Include interactive types: Survey, Knowledge Check, Accordion, Tabs
- Include media types: Video, Image, File
- Include structured types: Flashcard, Assignment, Divider
- Ensure each pathway uses at least 8 different content types total

CRITICAL MODULE GENERATION: Generate exactly 4-6 modules per section as specified. Each module must have 3+ different content types within it.
VALIDATION: Each module in your JSON output must include "content_types": ["type1", "type2", "type3"] array with 3+ distinct types.

CONTENT TYPE EXAMPLES FOR USER GOALS: {primary_goals}
- Survey: Assess user understanding of goals and progress
- Knowledge Check: Test comprehension of goal-related concepts  
- Accordion: Organize complex goal-related information
- Tabs: Present multiple aspects of goal achievement
- Flashcard: Reinforce key concepts for goal success
- Assignment: Practice activities that advance toward goals

GOAL-DRIVEN CONTENT REQUIREMENTS:
- Pathway names must directly reference the user's PRIMARY TRAINING GOALS: {primary_goals}
- Each module title must indicate how it supports achieving the user's specific goals
- Content must be 100% customized to user requirements, NO generic templates or meeting transcript content
- Every learning objective must directly advance the user's PRIMARY TRAINING GOALS
- Success metrics alignment: Show how each module contributes to {training_context.get('success_metrics', 'goal achievement')}

CONTENT STRUCTURE REQUIREMENTS:
- Each module must have content_type and content_data with detailed, actionable content
- Use diverse content types from ALL available block types, especially interactive ones
- Generate unique, varied content - no repetitive patterns or identical structures  
- Use decimal numbering for module titles (e.g., "Module 1.1:", "Module 1.2:", etc.)
- Professional, actionable content (no conversational language)

CONTENT FIELD SPECIFICATIONS:
- CRITICAL: "content" field = comprehensive summary explaining exactly how this module advances the PRIMARY TRAINING GOALS: {primary_goals} using SPECIFIC information from the uploaded files
- CRITICAL: "content_data" field = detailed, immediately usable content extracted from actual file content that users can apply to achieve their goals
- CRITICAL: "content_types" field = array with exactly 3+ distinct content types per module
- MANDATORY: Use SPECIFIC file content in every content_data field - NO generic content allowed
- FILE INTEGRATION: Extract actual procedures, data, and information from uploaded files for content_blocks
- Each module should be substantial (300-500 words in content field) and goal-focused with SPECIFIC file references
- Link every module clearly to user success metrics and goal achievement using ACTUAL file content
- CONTENT BLOCKS REQUIREMENT: Each content_block must contain SPECIFIC information extracted from the uploaded files

EXAMPLE MODULE STRUCTURE (customize for user's PRIMARY GOALS: {primary_goals}):
{{
  "title": "Module 1.1: Goal Achievement Foundation for {primary_goals}",
  "description": "Essential foundation module specifically designed to advance the user's primary training goals",
  "content": "This goal-focused module directly supports achieving the user's PRIMARY TRAINING GOALS: {primary_goals}. Every learning activity, assessment, and resource is customized to advance their specific objectives and success metrics: {training_context.get('success_metrics', 'goal achievement')}. The module provides targeted knowledge, practical skills, and measurable progress toward their stated goals. Content is 100% personalized to their industry context, audience needs, and success criteria - no generic templates or meeting transcript content. Students will gain specific competencies that directly contribute to achieving their primary training goals through interactive learning experiences, practical applications, and goal-oriented assessments.",
  "content_types": ["text", "survey", "knowledge_check"],
  "content_blocks": [
    {{
      "type": "text", 
      "title": "Goal-Focused Learning Introduction using File Content",
      "content_data": {{
        "text": "MANDATORY: Include SPECIFIC procedures, data, or information from the uploaded files that directly advance the PRIMARY TRAINING GOALS: {primary_goals}. Reference actual file content, not generic text.",
        "key_points": ["Specific procedure from uploaded file", "Actual data/metrics from file content", "File-based examples and applications", "Concrete steps extracted from files"]
      }}
    }},
    {{
      "type": "survey",
      "title": "File Content Understanding Assessment", 
      "content_data": {{
        "questions": ["Based on the uploaded file content, how confident are you with [specific procedure from file]?", "Which file-specific process needs more clarification for achieving your goals?", "How will you apply the specific information from the files to measure success?"],
        "question_type": "file_content_assessment",
        "purpose": "Assess understanding of SPECIFIC file content related to their training goals"
      }}
    }},
    {{
      "type": "knowledge_check",
      "title": "File Content Comprehension Check",
      "content_data": {{
        "questions": ["What specific procedure is outlined in the uploaded file for [relevant topic]?", "According to the file content, what are the key steps for [specific process]?", "How does the file content information help achieve your PRIMARY TRAINING GOALS?"],
        "answers": ["SPECIFIC procedure from actual file content", "ACTUAL steps/process from uploaded files", "Direct connection between file information and user's goals"],
        "question_type": "file_content_verification"
      }}
    }}
  ],
  "learning_objectives": ["Understand direct alignment between content and personal training goals", "Assess current progress toward goal achievement", "Identify specific knowledge gaps to address", "Establish clear success metrics"],
  "key_points": ["Personalized goal alignment", "Progress assessment", "Success measurement", "Custom learning pathway"]
}}

CRITICAL OUTPUT REQUIREMENTS:
- MUST follow the exact JSON structure below
- Each module MUST have "content_types" array with 3+ distinct types
- Each module MUST have "content_blocks" array with detailed content_data
- Pathway names MUST reference user's PRIMARY TRAINING GOALS: {primary_goals}
- All content MUST be goal-focused and personalized to user requirements

OUTPUT FORMAT (JSON only):
{{
  "pathways": [
    {{
      "pathway_name": "Goal-Focused Pathway for {primary_goals}",
      "description": "Customized pathway specifically designed to achieve the user's primary training goals",
      "goal_alignment": "This pathway directly supports achieving: {primary_goals}",
      "success_metrics": "{training_context.get('success_metrics', 'Goal achievement and knowledge application')}",
      "sections": [
        {{
          "title": "Section 1: Foundation for Goal Achievement",
          "description": "Essential foundation knowledge to advance toward the user's primary training goals", 
          "goal_connection": "Establishes baseline understanding needed to achieve: {primary_goals}",
          "modules": [
            {{
              "title": "Module 1.1: Goal-Aligned Introduction to [User's Specific Topic]",
              "description": "Customized introduction specifically targeting the user's primary training goals",
              "content": "Comprehensive explanation of how this module directly advances the user's PRIMARY TRAINING GOALS: {primary_goals}. Detailed content focused on practical knowledge and skills that support goal achievement. Content is 100% personalized to user requirements, industry context, and success metrics. No generic templates or meeting transcript content - everything is customized to advance the user's specific objectives.",
              "content_types": ["text", "survey", "knowledge_check"],
              "content_blocks": [
                {{
                  "type": "text",
                  "title": "Goal-Focused Learning Overview",
                  "content_data": {{
                    "text": "Detailed explanation of module content and its direct relationship to achieving user's primary training goals",
                    "key_points": ["Goal alignment", "Expected outcomes", "Success metrics", "Practical applications"]
                  }}
                }},
                {{
                  "type": "survey", 
                  "title": "Personal Goal Progress Assessment",
                  "content_data": {{
                    "questions": ["Current progress toward primary training goals", "Specific knowledge gaps", "Success measurement preferences"],
                    "question_type": "goal_assessment",
                    "purpose": "Assess user's starting point relative to their specific training goals"
                  }}
                }},
                {{
                  "type": "knowledge_check",
                  "title": "Goal Comprehension Check",
                  "content_data": {{
                    "questions": ["What are your primary training goals?", "How does this content support your goals?"],
                    "answers": ["User-specific responses based on their stated goals", "Direct connection to goal achievement"],
                    "question_type": "goal_verification"
                  }}
                }}
              ],
              "learning_objectives": ["Understand direct connection between content and personal goals", "Assess current progress", "Identify next steps for goal achievement"],
              "key_points": ["Personalized goal alignment", "Progress assessment", "Success planning", "Custom pathway development"],
              "goal_contribution": "Establishes foundation understanding essential for achieving: {primary_goals}"
            }}
            // GENERATE 3-5 MORE MODULES WITH DIVERSE CONTENT TYPES FOR EACH SECTION
            // ENSURE EACH MODULE HAS 3+ CONTENT TYPES AND SUPPORTS USER'S PRIMARY GOALS
          ]
        }}
        // GENERATE 3-4 MORE SECTIONS WITH 4-6 MODULES EACH
      ]
    }}
    // GENERATE 1-2 MORE PATHWAYS WITH DIFFERENT APPROACHES TO ACHIEVING USER'S GOALS
  ]
}}

CRITICAL FINAL REMINDERS:
1. Every pathway name must reference the user's PRIMARY TRAINING GOALS: {primary_goals}
2. Every module must have "content_types" array with 3+ distinct types
3. Every module must have "content_blocks" array with detailed, goal-focused content_data
4. Use ALL available content types across modules: Text, List, Image, Flashcard, Video, File, Accordion, Divider, Tabs, Knowledge Check, Survey, Assignment
5. Content must be 100% customized to user's goals - NO generic templates or meeting transcript content
6. Generate 4-6 modules per section, 4-5 sections per pathway
7. Focus entirely on achieving the user's specific PRIMARY TRAINING GOALS: {primary_goals}"""
        
        return prompt
    
    def _generate_additional_module(self, section, module_number):
        """
        Generate an additional module for a section that doesn't have enough modules
        """
        section_title = section.get('title', 'Training Section')
        
        # Different content types for variety
        content_types = ['text', 'video', 'knowledge_check', 'list', 'assignment']
        content_type = content_types[module_number % len(content_types)]
        
        # Generate module based on section content
        module = {
            'title': f"Module {module_number}: {section_title} - Advanced Topics",
            'description': f"Advanced concepts and practical applications for {section_title}",
            'content': f"This module covers advanced topics in {section_title}. Students will learn detailed procedures, best practices, and practical applications. The module includes hands-on exercises and real-world scenarios to reinforce learning. By the end, learners will have a comprehensive understanding of advanced concepts and be able to apply them effectively.",
            'content_type': content_type,
            'learning_objectives': [f"Master advanced {section_title} concepts", "Apply best practices", "Complete practical exercises"],
            'key_points': ["Advanced concepts", "Best practices", "Practical applications"]
        }
        
        # Add appropriate content_data based on content type
        if content_type == 'text':
            module['content_data'] = {
                'text': f"Detailed text content covering advanced {section_title} concepts and procedures.",
                'suggested_length': '2-3 paragraphs'
            }
        elif content_type == 'video':
            module['content_data'] = {
                'video_script': f"Scene 1: Introduction to advanced {section_title} concepts. Scene 2: Step-by-step demonstrations. Scene 3: Best practices and summary.",
                'video_duration': '5-7 minutes',
                'video_summary': f"Comprehensive video covering advanced {section_title} topics"
            }
        elif content_type == 'knowledge_check':
            module['content_data'] = {
                'questions': [f"What are the key advanced concepts in {section_title}?", f"How do you apply best practices in {section_title}?"],
                'answers': [f"Key advanced concepts include...", f"Best practices are applied by..."],
                'question_type': 'multiple choice'
            }
        elif content_type == 'list':
            module['content_data'] = {
                'list_items': [f"Advanced concept 1 in {section_title}", f"Advanced concept 2 in {section_title}", f"Advanced concept 3 in {section_title}"],
                'list_type': 'procedure'
            }
        elif content_type == 'assignment':
            module['content_data'] = {
                'assignment_task': f"Complete a practical exercise applying advanced {section_title} concepts",
                'deliverables': 'Submit completed exercise with documentation',
                'evaluation_criteria': 'Accuracy, completeness, and practical application'
            }
        
        return module
    
    def _parse_complete_pathways(self, response_text):
        """
        Parse complete pathway response efficiently
        """
        try:
            # Find JSON in response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                # Validate structure
                if 'pathways' in result and isinstance(result['pathways'], list):
                    # Clean up any remaining conversational content and ensure content types exist
                    for pathway in result['pathways']:
                        for section in pathway.get('sections', []):
                            modules = section.get('modules', [])
                            
                            # Check if we have enough modules per section
                            if len(modules) < 4:
                                debug_print(f"⚠️ Section '{section.get('title', 'Unknown')}' has only {len(modules)} modules. Generating additional modules...")
                                # Generate additional modules to reach minimum of 6
                                while len(modules) < 6:
                                    additional_module = self._generate_additional_module(section, len(modules) + 1)
                                    modules.append(additional_module)
                                section['modules'] = modules
                                debug_print(f"✅ Enhanced section '{section.get('title', 'Unknown')}' to {len(modules)} modules")
                            
                            for module in section.get('modules', []):
                                content = module.get('content', '')
                                # Quick clean of common issues
                                content = re.sub(r'Teams Meeting.*?\d{4}', '', content, flags=re.IGNORECASE)
                                content = re.sub(r'thank personnel|restroom|car accident', '', content, flags=re.IGNORECASE)
                                content = re.sub(r'Oh,.*?sense\.', '', content, flags=re.IGNORECASE)
                                content = re.sub(r'Personnel\'ll|operators don\'t mind', '', content, flags=re.IGNORECASE)
                                module['content'] = content.strip()
                                
                                # Ensure content_type exists (add if missing from AI response)
                                if 'content_type' not in module:
                                    module['content_type'] = 'text'
                                
                                # Ensure content_data exists (add if missing from AI response)
                                if 'content_data' not in module:
                                    content_type = module.get('content_type', 'text')
                                    if content_type == 'text':
                                        module['content_data'] = {
                                            'text': 'Detailed text content for users to implement based on training goals',
                                            'suggested_length': '2-3 paragraphs'
                                        }
                                    elif content_type == 'video':
                                        module['content_data'] = {
                                            'video_summary': 'What the video will demonstrate to achieve training goals',
                                            'video_script': 'Detailed scene-by-scene script for video production',
                                            'video_duration': '3-5 minutes'
                                        }
                                    elif content_type == 'list':
                                        module['content_data'] = {
                                            'list_items': ['Step 1: Specific action to achieve training goals', 'Step 2: Specific action to achieve training goals', 'Step 3: Specific action to achieve training goals'],
                                            'list_type': 'procedure',
                                            'instructions': 'How to use this list effectively'
                                        }
                                    elif content_type == 'knowledge_check':
                                        module['content_data'] = {
                                            'questions': ['What are the key requirements for training goals?', 'How should this be implemented?'],
                                            'answers': ['Detailed answer based on training goals', 'Detailed answer based on training goals'],
                                            'question_type': 'multiple choice'
                                        }
                                    elif content_type == 'assignment':
                                        module['content_data'] = {
                                            'assignment_task': 'Step-by-step instructions for practical application of training goals',
                                            'deliverables': 'What students must submit',
                                            'evaluation_criteria': 'How to assess completion'
                                        }
                                    elif content_type == 'flashcard':
                                        module['content_data'] = {
                                            'flashcard_front': 'Question about training goals',
                                            'flashcard_back': 'Answer related to training goals',
                                            'difficulty_level': 'beginner'
                                        }
                                    elif content_type == 'image':
                                        module['content_data'] = {
                                            'image_description': 'Detailed description of what visual will show for training goals',
                                            'image_purpose': 'Why this visual helps learning',
                                            'suggested_format': 'infographic'
                                        }
                                    else:
                                        module['content_data'] = {
                                            'detailed_content': 'Specific content for users to implement for training goals',
                                            'purpose': 'Why this format helps learning'
                                        }
                                
                                # Validate content structure and fix if needed
                                content = module.get('content', '')
                                content_type = module.get('content_type', 'text')
                                
                                # Validate content structure based on block type
                                content_type = module.get('content_type', 'text')
                                content = module.get('content', '')
                                
                                # Check if content contains descriptions instead of educational material
                                media_phrases = ['this video', 'video demonstrates', 'video shows', 'this image', 'image shows', 'watch this', 'view this', 'see the video', 'in this video', 'the video shows', 'this list contains', 'the flashcard shows', 'this assignment requires']
                                has_media_description = any(phrase in content.lower() for phrase in media_phrases)
                                
                                if has_media_description:
                                    debug_print(f"⚠️ Found media description in content field for {module.get('title', 'module')} ({content_type}), fixing structure")
                                    
                                    # Fix content structure based on block type
                                    module['content_data'] = module.get('content_data', {})
                                    title = module.get('title', 'this topic').lower()
                                    
                                    if content_type == 'video':
                                        module['content_data']['video_summary'] = content
                                        # Replace with file-based summary explaining what learners will learn
                                        module_title = module.get('title', 'this topic').replace('video', '').replace('Video', '').strip()
                                        module['content'] = f"This module provides an overview of {module_title.lower()} based on the uploaded training materials. Students will learn about key concepts, procedures, and best practices covered in the source documents. The module examines important topics and practical applications relevant to the workplace. By the end, learners will understand the essential principles and be able to apply this knowledge in their professional role."
                                    
                                    elif content_type == 'image':
                                        module['content_data']['image_description'] = content
                                        # Replace with file-based summary explaining what the image will teach
                                        module_title = module.get('title', 'this topic').replace('image', '').replace('Image', '').strip()
                                        module['content'] = f"This module provides an overview of {module_title.lower()} based on the uploaded visual materials. Students will learn about key concepts and procedures illustrated in the source documents. The module examines visual elements, their practical applications, and their relevance to workplace operations. By the end, learners will understand the visual information and be able to apply this knowledge in their professional tasks."
                                    
                                    elif content_type == 'list':
                                        module['content_data']['list_description'] = content
                                        # Replace with file-based summary explaining what the list covers
                                        module_title = module.get('title', 'this topic').replace('list', '').replace('List', '').strip()
                                        module['content'] = f"This module provides an overview of {module_title.lower()} based on the uploaded procedural materials. Students will learn about structured steps, requirements, and key elements covered in the source documents. The module examines systematic approaches and their practical applications in the workplace. By the end, learners will understand the organized information and be able to follow the procedures effectively."
                                    
                                    elif content_type == 'flashcard':
                                        module['content_data']['flashcard_summary'] = content
                                        # Replace with file-based summary about the key concepts being tested
                                        module_title = module.get('title', 'this topic').replace('flashcard', '').replace('Flashcard', '').strip()
                                        module['content'] = f"This module provides an overview of key terminology and concepts for {module_title.lower()} based on the uploaded reference materials. Students will learn about fundamental terms, definitions, and their practical applications covered in the source documents. The module examines essential vocabulary and concepts relevant to the workplace. By the end, learners will understand the key terminology and be able to use these concepts effectively in their professional role."
                                    
                                    elif content_type == 'knowledge_check':
                                        module['content_data']['assessment_summary'] = content
                                        # Replace with file-based summary reviewing the concepts being assessed
                                        module_title = module.get('title', 'this topic').replace('quiz', '').replace('Quiz', '').replace('assessment', '').replace('Assessment', '').strip()
                                        module['content'] = f"This module provides an overview of {module_title.lower()} concepts based on the uploaded training materials. Students will learn about essential knowledge and procedures covered in the source documents. The module examines critical concepts and their practical applications in the workplace. By the end, learners will understand the key principles and be able to demonstrate their knowledge through assessment."
                                    
                                    elif content_type == 'assignment':
                                        module['content_data']['assignment_summary'] = content
                                        # Replace with file-based summary about the practical application
                                        module_title = module.get('title', 'this topic').replace('assignment', '').replace('Assignment', '').strip()
                                        module['content'] = f"This module provides an overview of practical applications for {module_title.lower()} based on the uploaded training materials. Students will learn about hands-on skills and real-world scenarios covered in the source documents. The module examines practical exercises and their relevance to workplace tasks. By the end, learners will understand the practical applications and be able to complete related assignments successfully."
                                    
                                    else:
                                        # For other content types (text, file, accordion, tabs, survey, divider)
                                        module['content_data']['summary'] = content
                                        module_title = module.get('title', 'this topic')
                                        module['content'] = f"This module provides an overview of {module_title.lower()} based on the uploaded training materials. Students will learn about key concepts, procedures, and best practices covered in the source documents. The module examines important topics and their practical applications relevant to the workplace. By the end, learners will understand the essential principles and be able to apply this knowledge in their professional role."
                                
                                # Debug log what we got
                                debug_print(f"Module: {module.get('title', 'Unknown')} - Type: {content_type} - Content: {len(module.get('content', ''))}")
                    
                    debug_print(f"✅ Parsed {len(result['pathways'])} pathways with content types")
                    return result
            
            debug_print("⚠️ Could not parse JSON from AI response")
            return None
            
        except Exception as e:
            debug_print(f"⚠️ Error parsing pathways: {str(e)}")
            return None
    
    def _create_fast_fallback(self, extracted_content, training_context):
        """
        Quick fallback when AI is unavailable
        """
        industry = training_context.get('industry', 'Professional')
        audience = training_context.get('target_audience', 'Team Members')
        
        # Create based on file names and basic content
        pathways = []
        files = list(extracted_content.items())
        
        for i, (filename, content) in enumerate(files[:2]):  # Max 2 pathways for speed
            base_name = filename.replace('.pdf', '').replace('.docx', '').replace('_', ' ').title()
            
            pathway = {
                "pathway_name": f"{base_name} Training Program",
                "description": f"Professional training based on {filename} for {audience}",
                "sections": [
                    {
                        "title": f"Section 1: {base_name} Fundamentals",
                        "description": "Core concepts and procedures",
                        "modules": [
                            {
                                "title": f"Module 1.1: {base_name} Overview",
                                "description": "Introduction to key concepts and fundamentals",
                                "content": f"This module covers essential {base_name.lower()} concepts, procedures, and best practices relevant to {audience.lower()}. Understanding these fundamentals is crucial for success in your role and maintaining professional standards.",
                                "content_type": "text",
                                "content_data": {
                                    "text": f"Comprehensive overview of {base_name.lower()} fundamentals, including key concepts, procedures, and professional standards applicable to your role and industry."
                                },
                                "learning_objectives": ["Understand core concepts", "Apply best practices", "Follow professional standards"],
                                "key_points": ["Core fundamentals", "Professional standards", "Best practices"],
                                "engagement_level": "medium",
                                "estimated_time": "15 minutes"
                            },
                            {
                                "title": f"Module 1.2: {base_name} Procedures", 
                                "description": "Step-by-step implementation procedures",
                                "content": f"Practical procedures for implementing {base_name.lower()} in your daily work. Follow established workflows, maintain quality standards, and ensure proper documentation of all activities and outcomes.",
                                "content_type": "list",
                                "content_data": {
                                    "list_items": [
                                        "Step 1: Review requirements and prepare resources",
                                        "Step 2: Follow established procedures and protocols",
                                        "Step 3: Execute tasks according to guidelines",
                                        "Step 4: Perform quality checks and validation",
                                        "Step 5: Document activities and outcomes"
                                    ]
                                },
                                "learning_objectives": ["Execute procedures correctly", "Maintain quality standards", "Document activities"],
                                "key_points": ["Workflow procedures", "Quality standards", "Documentation"],
                                "engagement_level": "high",
                                "estimated_time": "20 minutes"
                            },
                            {
                                "title": f"Module 1.3: {base_name} Best Practices",
                                "description": "Industry best practices and professional standards",
                                "content": f"Learn industry-leading best practices for {base_name.lower()} implementation. Master professional standards, quality assurance methods, and continuous improvement techniques.",
                                "content_type": "text",
                                "content_data": {
                                    "text": f"Comprehensive guide to professional standards and industry best practices for {base_name.lower()}. Includes quality assurance methods, continuous improvement techniques, and professional development strategies."
                                },
                                "learning_objectives": ["Apply best practices", "Maintain professional standards", "Implement quality assurance"],
                                "key_points": ["Industry standards", "Quality assurance", "Continuous improvement"],
                                "engagement_level": "high",
                                "estimated_time": "18 minutes"
                            },
                            {
                                "title": f"Module 1.4: {base_name} Troubleshooting",
                                "description": "Problem-solving and issue resolution",
                                "content": f"Develop problem-solving skills for common {base_name.lower()} challenges. Learn systematic troubleshooting methods, root cause analysis, and effective resolution strategies.",
                                "content_type": "assignment",
                                "content_data": {
                                    "assignment_task": f"Practice troubleshooting common {base_name.lower()} issues using systematic problem-solving methods",
                                    "deliverables": "Submit documented troubleshooting process and resolution steps",
                                    "evaluation_criteria": "Systematic approach, root cause identification, effective resolution"
                                },
                                "learning_objectives": ["Solve problems systematically", "Identify root causes", "Implement effective solutions"],
                                "key_points": ["Problem-solving methods", "Root cause analysis", "Resolution strategies"],
                                "engagement_level": "very high",
                                "estimated_time": "25 minutes"
                            },
                            {
                                "title": f"Module 1.5: {base_name} Assessment",
                                "description": "Knowledge verification and competency evaluation",
                                "content": f"Evaluate your understanding of {base_name.lower()} concepts, procedures, and best practices. This assessment ensures you have mastered the essential knowledge required for your role.",
                                "content_type": "knowledge_check",
                                "content_data": {
                                    "questions": [
                                        f"What are the key requirements for {base_name.lower()} in your role?",
                                        f"How should {base_name.lower()} activities be properly documented?",
                                        f"What are the main troubleshooting steps for {base_name.lower()} issues?"
                                    ],
                                    "answers": [
                                        "Follow all established procedures and maintain professional standards appropriate to your role and industry",
                                        "Document activities clearly with appropriate detail, timestamps, and required approvals",
                                        "Systematic problem identification, root cause analysis, solution implementation, and verification"
                                    ]
                                },
                                "learning_objectives": ["Demonstrate understanding", "Apply knowledge effectively", "Meet competency standards"],
                                "key_points": ["Knowledge verification", "Competency validation", "Performance standards"],
                                "engagement_level": "high",
                                "estimated_time": "10 minutes"
                            }
                        ]
                    },
                    {
                        "title": f"Section 2: {base_name} Implementation",
                        "description": "Practical implementation and procedures",
                        "modules": [
                            {
                                "title": f"Module 2.1: {base_name} Planning",
                                "description": "Strategic planning and preparation",
                                "content": f"Learn systematic planning approaches for {base_name.lower()} implementation. Develop skills in resource allocation, timeline management, and stakeholder coordination.",
                                "content_type": "list",
                                "content_data": {
                                    "list_items": ["Strategic planning principles", "Resource allocation methods", "Timeline development", "Stakeholder coordination", "Risk assessment"]
                                },
                                "learning_objectives": ["Plan effectively", "Allocate resources", "Coordinate stakeholders"],
                                "estimated_time": "20 minutes"
                            }
                        ]
                    },
                    {
                        "title": f"Section 3: {base_name} Quality Management",
                        "description": "Quality assurance and continuous improvement",
                        "modules": [
                            {
                                "title": f"Module 3.1: {base_name} Quality Standards",
                                "description": "Quality standards and compliance requirements",
                                "content": f"Master quality standards and compliance requirements for {base_name.lower()}. Learn quality control methods, audit procedures, and improvement strategies.",
                                "content_type": "assignment",
                                "content_data": {
                                    "assignment_task": f"Develop a quality assurance plan for {base_name.lower()} operations",
                                    "deliverables": "Submit comprehensive quality plan with metrics",
                                    "evaluation_criteria": "Completeness, practicality, compliance alignment"
                                },
                                "learning_objectives": ["Apply quality standards", "Develop QA plans", "Ensure compliance"],
                                "estimated_time": "25 minutes"
                            }
                        ]
                    },
                    {
                        "title": f"Section 4: {base_name} Advanced Applications",
                        "description": "Advanced concepts and specialized applications",
                        "modules": [
                            {
                                "title": f"Module 4.1: {base_name} Innovation",
                                "description": "Innovation and future developments",
                                "content": f"Explore innovative approaches and future developments in {base_name.lower()}. Learn emerging trends, technology integration, and change management strategies.",
                                "content_type": "video",
                                "content_data": {
                                    "video_script": f"Comprehensive exploration of innovative {base_name.lower()} approaches, emerging technologies, and future trends",
                                    "video_duration": "15 minutes",
                                    "video_summary": f"Advanced concepts in {base_name.lower()} innovation"
                                },
                                "learning_objectives": ["Understand innovations", "Apply new technologies", "Manage change"],
                                "estimated_time": "30 minutes"
                            }
                        ]
                    }
                ]
            }
            pathways.append(pathway)
        
        return {"pathways": pathways}


class ContentTypeAgent:
    """
    Specialized agent for generating diverse content types for modules
    """
    
    def __init__(self):
        self.model = model
        
    def enhance_module_with_content_types(self, module, training_context, source_content):
        """
        Enhance a module with appropriate content type based on its purpose
        """
        try:
            if not self.model:
                return self._add_basic_content_type(module)
            
            # Generate content type and content data using AI
            prompt = self._build_content_type_prompt(module, training_context, source_content)
            
            debug_print(f"🎨 ContentTypeAgent: Generating content type for '{module.get('title', 'Unknown')}'...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                enhanced_module = self._parse_content_type_response(response.text, module)
                return enhanced_module
            else:
                return self._add_basic_content_type(module)
                
        except Exception as e:
            debug_print(f"⚠️ ContentTypeAgent error: {str(e)}")
            return self._add_basic_content_type(module)
    
    def _build_content_type_prompt(self, module, training_context, source_content):
        """
        Build prompt for content type generation
        """
        prompt = f"""You are an expert Instructional Designer. Create engaging content type and data for this training module.

MODULE INFO:
Title: {module.get('title', 'Training Module')}
Description: {module.get('description', 'Training content')}
Current Content: {module.get('content', 'Basic content')[:300]}

TRAINING CONTEXT:
Industry: {training_context.get('industry', 'General')}
Audience: {training_context.get('target_audience', 'Employees')}

SOURCE MATERIAL:
{source_content[:200] if source_content else 'General training content'}

TASK: Choose the BEST content type for this module and create appropriate content data.

CONTENT TYPES AVAILABLE:
- text: Professional written content (for foundational knowledge)
- video: Video concept (for demonstrations, processes) - provide 2-3 sentence summary
- list: Structured lists (for procedures, checklists)
- image: Visual content (for equipment, processes, safety)
- flashcard: Key concepts (for terminology, quick review)
- knowledge_check: Quiz questions (for assessment)
- assignment: Practical tasks (for hands-on learning)
- accordion: Expandable sections (for detailed procedures)
- tabs: Organized information (for multi-step processes)
- survey: Feedback forms (for evaluation)
- file: Document references (for policies, manuals)

OUTPUT (JSON only):
{{
  "content_type": "best_type_for_this_module",
  "content_data": {{
    "text": "Professional written content if text type",
    "video_summary": "2-3 sentence video concept description if video type",
    "list_items": ["Item 1", "Item 2", "Item 3"] if list type,
    "image_description": "Detailed description of visual content if image type",
    "flashcard_front": "Question or concept if flashcard type",
    "flashcard_back": "Answer or explanation if flashcard type",
    "questions": ["Question 1?", "Question 2?"] if knowledge_check type,
    "answers": ["Answer 1", "Answer 2"] if knowledge_check type,
    "assignment_task": "Detailed practical task description if assignment type",
    "file_reference": "Document name and description if file type",
    "accordion_sections": ["Section 1: Content", "Section 2: Content"] if accordion type,
    "tab_content": ["Tab 1: Content", "Tab 2: Content"] if tabs type,
    "survey_questions": ["Question 1", "Question 2"] if survey type
  }},
  "engagement_level": "high|medium|low",
  "estimated_time": "X minutes"
}}

Choose the most appropriate content type based on the module's learning objectives and create engaging, professional content."""
        
        return prompt
    
    def _parse_content_type_response(self, response_text, original_module):
        """
        Parse content type response and enhance module
        """
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                content_data = json.loads(json_str)
                
                # Enhance the original module
                enhanced_module = original_module.copy()
                enhanced_module['content_type'] = content_data.get('content_type', 'text')
                enhanced_module['content_data'] = content_data.get('content_data', {})
                enhanced_module['engagement_level'] = content_data.get('engagement_level', 'medium')
                enhanced_module['estimated_time'] = content_data.get('estimated_time', '15 minutes')
                
                debug_print(f"✅ Enhanced module with {enhanced_module['content_type']} content type")
                return enhanced_module
            else:
                return self._add_basic_content_type(original_module)
                
        except Exception as e:
            debug_print(f"⚠️ Error parsing content type response: {str(e)}")
            return self._add_basic_content_type(original_module)
    
    def _add_basic_content_type(self, module):
        """
        Add basic content type when AI is unavailable
        """
        enhanced_module = module.copy()
        
        # Determine basic content type based on module title/content
        title = module.get('title', '').lower()
        content = module.get('content', '').lower()
        
        if 'overview' in title or 'introduction' in title:
            content_type = 'text'
            content_data = {
                "text": module.get('content', 'Professional training content')
            }
        elif 'procedure' in title or 'steps' in title or 'process' in title:
            content_type = 'list'
            content_data = {
                "list_items": ["Step 1: Preparation", "Step 2: Execution", "Step 3: Completion"]
            }
        elif 'assessment' in title or 'check' in title or 'quiz' in title:
            content_type = 'knowledge_check'
            content_data = {
                "questions": ["What are the key safety requirements?", "How should procedures be documented?"],
                "answers": ["Follow all established safety protocols", "Document each step clearly and completely"]
            }
        elif 'assignment' in title or 'practice' in title or 'exercise' in title:
            content_type = 'assignment'
            content_data = {
                "assignment_task": "Complete the practical exercise following all established procedures and safety guidelines."
            }
        else:
            content_type = 'text'
            content_data = {
                "text": module.get('content', 'Professional training content')
            }
        
        enhanced_module['content_type'] = content_type
        enhanced_module['content_data'] = content_data
        enhanced_module['engagement_level'] = 'medium'
        enhanced_module['estimated_time'] = '15 minutes'
        
        return enhanced_module


class ParallelPathwayProcessor:
    """
    Processor that handles multiple content files in parallel for speed
    """
    
    def __init__(self):
        self.fast_agent = FastPathwayAgent()
        self.content_type_agent = ContentTypeAgent()
    
    def process_content_parallel(self, extracted_content, training_context, file_inventory):
        """
        Process content files in parallel when possible
        """
        try:
            if len(extracted_content) <= 2:
                # For small content, use single call
                result = self.fast_agent.generate_complete_pathways_fast(
                    extracted_content, training_context, file_inventory
                )
                
                if result and 'pathways' in result:
                    # Content types are already generated by the main AI prompt
                    # No need for additional enhancement - just return the result
                    debug_print(f"✅ Generated pathways with built-in content types")
                    return result
                
                return result
            
            # For larger content, process in chunks
            debug_print(f"🚀 Processing {len(extracted_content)} files in parallel chunks...")
            
            content_items = list(extracted_content.items())
            chunk_size = 2  # Process 2 files per chunk for optimal speed
            chunks = [dict(content_items[i:i+chunk_size]) for i in range(0, len(content_items), chunk_size)]
            
            all_pathways = []
            
            # Process chunks with threading for speed
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = []
                for chunk in chunks[:3]:  # Limit to 3 chunks for API limits
                    future = executor.submit(
                        self.fast_agent.generate_complete_pathways_fast,
                        chunk, training_context, file_inventory
                    )
                    futures.append(future)
                
                # Collect results with timeout
                for future in concurrent.futures.as_completed(futures, timeout=60):
                    try:
                        result = future.result()
                        if result and 'pathways' in result:
                            all_pathways.extend(result['pathways'])
                    except Exception as e:
                        debug_print(f"⚠️ Chunk processing failed: {str(e)}")
            
            if all_pathways:
                debug_print(f"✅ Parallel processing complete: {len(all_pathways)} pathways")
                
                # Content types are already included in the AI-generated pathways
                # No need for additional enhancement
                debug_print(f"✅ Parallel processing complete with content types")
                return {"pathways": all_pathways[:6]}
            else:
                debug_print("⚠️ Parallel processing failed, using fallback")
                fallback_result = self.fast_agent.generate_complete_pathways_fast(
                    extracted_content, training_context, file_inventory
                )
                # Return fallback result directly - content types included
                return fallback_result
                
        except Exception as e:
            debug_print(f"⚠️ Parallel processing error: {str(e)}")
            return self.fast_agent.generate_complete_pathways_fast(
                extracted_content, training_context, file_inventory
            )
    
    def _enhance_pathways_with_content_types(self, pathways, training_context, extracted_content):
        """
        Enhance all modules in pathways with appropriate content types
        """
        try:
            debug_print("🎨 Enhancing modules with diverse content types...")
            
            # Combine all content for context
            all_content = " ".join(extracted_content.values())
            
            enhanced_pathways = []
            
            for pathway in pathways:
                enhanced_sections = []
                
                for section in pathway.get('sections', []):
                    enhanced_modules = []
                    
                    for module in section.get('modules', []):
                        # Enhance module with content type
                        enhanced_module = self.content_type_agent.enhance_module_with_content_types(
                            module, training_context, all_content
                        )
                        enhanced_modules.append(enhanced_module)
                    
                    section_copy = section.copy()
                    section_copy['modules'] = enhanced_modules
                    enhanced_sections.append(section_copy)
                
                pathway_copy = pathway.copy()
                pathway_copy['sections'] = enhanced_sections
                enhanced_pathways.append(pathway_copy)
            
            debug_print(f"✅ Enhanced {len(enhanced_pathways)} pathways with content types")
            return enhanced_pathways
            
        except Exception as e:
            debug_print(f"⚠️ Content type enhancement failed: {str(e)}")
            return pathways  # Return original pathways if enhancement fails


class OptimizedPathwayOrchestrator:
    """
    Optimized orchestrator for fast, high-quality pathway generation
    """
    
    def __init__(self):
        self.processor = ParallelPathwayProcessor()
    
    def generate_optimized_pathways(self, extracted_content, training_context, file_inventory):
        """
        Generate pathways using optimized, fast AI processing
        """
        try:
            debug_print("🚀 Starting optimized AI pathway generation...")
            
            # Quick validation
            if not extracted_content:
                debug_print("❌ No content to process")
                return None
            
            # Pre-process content for speed
            cleaned_content = self._preprocess_content_fast(extracted_content)
            
            # Generate pathways using optimized processing
            result = self.processor.process_content_parallel(
                cleaned_content, training_context, file_inventory
            )
            
            if result and 'pathways' in result and result['pathways']:
                debug_print(f"✅ Optimized generation complete: {len(result['pathways'])} pathways")
                
                # Final quality check and cleanup
                self._final_quality_pass(result['pathways'])
                
                return result
            else:
                debug_print("❌ Optimized generation failed")
                return None
                
        except Exception as e:
            debug_print(f"❌ OptimizedPathwayOrchestrator error: {str(e)}")
            return None
    
    def _preprocess_content_fast(self, extracted_content):
        """
        Quick preprocessing to clean content before AI processing
        """
        cleaned = {}
        for filename, content in extracted_content.items():
            if content and len(content.strip()) > 50:
                # Quick clean of obvious issues
                clean_content = re.sub(r'Teams Meeting.*?\d{4}', '', content, flags=re.IGNORECASE)
                clean_content = re.sub(r'thank personnel.*?\.', '', clean_content, flags=re.IGNORECASE)
                clean_content = re.sub(r'restroom.*?minutes\.', '', clean_content, flags=re.IGNORECASE)
                clean_content = re.sub(r'car accident.*?highway\.', '', clean_content, flags=re.IGNORECASE)
                clean_content = re.sub(r'\s+', ' ', clean_content)  # Clean whitespace
                
                # Limit content length for speed (keep first 1000 chars of meaningful content)
                if len(clean_content) > 1000:
                    clean_content = clean_content[:1000] + "..."
                
                cleaned[filename] = clean_content.strip()
        
        return cleaned
    
    def _final_quality_pass(self, pathways):
        """
        Final quality check to ensure professional content
        """
        for pathway in pathways:
            # Ensure pathway names are professional
            name = pathway.get('pathway_name', '')
            if 'pathway' in name.lower() and 'training' not in name.lower():
                pathway['pathway_name'] = name.replace('Pathway', 'Training Program')
            
            # Clean sections and modules
            for section in pathway.get('sections', []):
                for module in section.get('modules', []):
                    content = module.get('content', '')
                    
                    # Final cleanup of any remaining conversational content
                    content = re.sub(r'\b(um|uh|well|so)\b', '', content, flags=re.IGNORECASE)
                    content = re.sub(r'Personnel hope.*?\.', '', content, flags=re.IGNORECASE)
                    content = re.sub(r'\s+', ' ', content)
                    
                    module['content'] = content.strip()
        
        debug_print("✅ Final quality pass complete")