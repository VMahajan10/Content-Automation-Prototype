#!/usr/bin/env python3
"""
Fixed version of utils.py with correct indentation
"""

import json
import queue
import re
import concurrent.futures
import streamlit as st
import time
import threading
from modules.config import model

# Global debug log queue for background threads
debug_log_queue = queue.Queue()

# Thread-safe log buffer for background thread logs
debug_logs = []
debug_lock = threading.Lock()

def debug_print(message, is_error=False):
    """Thread-safe debug printing"""
    with debug_lock:
        debug_logs.append({
            'message': message,
            'is_error': is_error,
            'timestamp': time.time()
        })
        print(message)

def create_quick_pathway(context, extracted_file_contents, inventory):
    """Create a quick pathway without AI analysis for speed"""
    try:
        # Create a simple pathway structure
        pathway_name = f"{context.get('training_type', 'Training')} Pathway"
        
        # Group content by file
        modules_by_file = {}
        for filename, content in extracted_file_contents.items():
            if content and len(content.strip()) > 100:
                # Create simple modules from file content
                file_modules = create_simple_modules_from_content(filename, content, context)
                if file_modules:
                    modules_by_file[filename] = file_modules
        
        # Create sections based on file content
        sections = []
        for filename, modules in modules_by_file.items():
            section_title = f"Content from {filename}"
            sections.append({
                'title': section_title,
                'description': f'Training content extracted from {filename}',
                'modules': modules
            })
        
        # If no sections created, create a default one
        if not sections:
            sections.append({
                'title': 'General Training Content',
                'description': 'Training content from uploaded files',
                'modules': [{
                    'title': 'Training Overview',
                    'description': 'Overview of training content',
                    'content': 'Training content has been processed and is ready for review.',
                    'source': list(extracted_file_contents.keys()),
                    'content_types': []
                }]
            })
        
        return {
            'pathways': [{
                'pathway_name': pathway_name,
                'sections': sections
            }]
        }
        
    except Exception as e:
        return {
            'pathways': [{
                'pathway_name': 'Quick Training Pathway',
                'sections': [{
                    'title': 'Training Content',
                    'description': 'Content from uploaded files',
                    'modules': [{
                        'title': 'Training Overview',
                        'description': 'Overview of training content',
                        'content': 'Training content has been processed.',
                        'source': list(extracted_file_contents.keys()),
                        'content_types': []
                    }]
                }]
            }]
        }

def flush_debug_logs_to_streamlit():
    """Flush any debug logs from background threads to Streamlit"""
    try:
        while not debug_log_queue.empty():
            log_entry = debug_log_queue.get_nowait()
            st.write(f"🔍 Debug: {log_entry}")
    except Exception as e:
        pass  # Silently handle any queue errors

def create_simple_modules_from_content(filename, content, training_context):
    """
    Create simple modules from file content without complex AI processing
    """
    try:
        if not content or len(content.strip()) < 50:
            return []
        
        # Split content into chunks
        content_chunks = chunk_content_simple(content)
        
        modules = []
        for i, chunk in enumerate(content_chunks):
            if len(chunk.strip()) > 100:
                # Create simple module
                title = extract_simple_title(chunk, filename, i+1)
                description = f"Content from {filename} - Module {i+1}"
                
                module = {
                    'title': title,
                    'description': description,
                    'content': chunk.strip(),
                    'source': filename,
                    'key_points': extract_simple_key_points(chunk),
                    'relevance_score': 0.8,
                    'full_reason': f'Content from {filename}'
                }
                modules.append(module)
        
        return modules
        
    except Exception as e:
        print(f"⚠️ Simple module creation failed: {str(e)}")
        return []

def chunk_content_simple(content, max_chunk_size=2000):
    """
    Split content into simple chunks
    """
    try:
        # Split by sentences first
        sentences = re.split(r'[.!?]+', content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Only substantial sentences
                if len(current_chunk + sentence) < max_chunk_size:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [content[:max_chunk_size]]
        
    except Exception as e:
        return [content[:2000]]

def extract_simple_title(content, filename, module_num):
    """
    Extract a simple title from content
    """
    try:
        # Get first meaningful sentence
        sentences = re.split(r'[.!?]+', content)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 100:
                # Clean up the sentence
                title = re.sub(r'^\w+:\s*', '', sentence)  # Remove speaker prefixes
                title = title.strip()
                if len(title) > 10:
                    return f"Module {module_num}: {title[:50]}..."
        
        # Fallback
        return f"Module {module_num}: Content from {filename}"
        
    except Exception as e:
        return f"Module {module_num}: Content from {filename}"

def extract_simple_key_points(content):
    """
    Extract simple key points from content
    """
    try:
        sentences = content.split('. ')
        key_points = []
        
        for sentence in sentences[:3]:  # Take first 3 sentences
            if len(sentence) > 20:
                key_points.append(sentence.strip())
        
        return key_points
        
    except Exception as e:
        return []

def generate_content_types_with_ai_fast(content, training_context):
    """
    Generate content types quickly using AI if available, otherwise use basic detection
    """
    try:
        if not content or len(content.strip()) < 50:
            return ['general']
        
        # Use basic content type detection
        content_lower = content.lower()
        
        content_types = []
        
        # Check for different content types
        if any(word in content_lower for word in ['safety', 'ppe', 'protective', 'hazard']):
            content_types.append('safety')
        
        if any(word in content_lower for word in ['quality', 'inspection', 'control', 'standard']):
            content_types.append('quality')
        
        if any(word in content_lower for word in ['process', 'procedure', 'workflow', 'method']):
            content_types.append('process')
        
        if any(word in content_lower for word in ['equipment', 'tool', 'operation', 'maintenance']):
            content_types.append('equipment')
        
        if any(word in content_lower for word in ['communication', 'meeting', 'collaboration']):
            content_types.append('communication')
        
        if any(word in content_lower for word in ['documentation', 'record', 'report']):
            content_types.append('documentation')
        
        # If no specific types found, return general
        return content_types if content_types else ['general']
        
    except Exception as e:
        print(f"⚠️ Content type generation failed: {str(e)}")
        return ['general']

def generate_enhanced_content_types_with_gemini(content):
    """
    Generate 3 enhanced content types using Gemini AI with actual Veo3 video generation
    """
    try:
        if not model:
            # Fallback to basic content types if Gemini not available
            return [
                {
                    'type': 'text', 
                    'title': 'Training Manual',
                    'description': 'Comprehensive written guide',
                    'content_data': {
                        'text': 'Detailed training material covering key concepts and procedures',
                        'suggested_length': '2-3 paragraphs'
                    }
                },
                {
                    'type': 'video', 
                    'title': 'Veo3 Video Demonstration',
                    'description': 'AI-generated video using Veo3',
                    'content_data': {
                        'video_status': 'generating',
                        'video_url': None,
                        'video_duration': '3-5 minutes',
                        'video_summary': 'Visual demonstration of training concepts using Veo3'
                    }
                },
                {
                    'type': 'knowledge_check', 
                    'title': 'Comprehension Assessment',
                    'description': 'Interactive questions to test understanding',
                    'content_data': {
                        'questions': ['What are the key concepts covered?', 'How do you apply these procedures?'],
                        'answers': ['Key concepts include...', 'Procedures are applied by...'],
                        'question_type': 'multiple choice'
                    }
                }
            ]
        
        # Generate text and knowledge check content first
        text_and_quiz_prompt = f"""
        Based on the following training content, generate exactly 2 content types (text and knowledge_check) with DETAILED, ACTIONABLE content.

        Training Content: {content[:1500]}

        Create 2 content types:
        1. TEXT type: Include actual text content (2-3 paragraphs)
        2. KNOWLEDGE_CHECK type: Include actual questions and answers

        Respond in JSON format:
        [
            {{
                "type": "text",
                "title": "Detailed Training Guide",
                "description": "Comprehensive written material",
                "content_data": {{
                    "text": "Actual detailed paragraph content about the training topic, including specific procedures, key concepts, and actionable steps. This should be 2-3 paragraphs of substantive content.",
                    "key_points": ["Point 1", "Point 2", "Point 3"],
                    "suggested_length": "2-3 paragraphs"
                }}
            }},
            {{
                "type": "knowledge_check",
                "title": "Knowledge Assessment",
                "description": "Comprehensive understanding check",
                "content_data": {{
                    "questions": ["Specific question 1 based on content", "Specific question 2 based on content", "Specific question 3 based on content"],
                    "answers": ["Detailed answer 1", "Detailed answer 2", "Detailed answer 3"],
                    "question_type": "multiple choice",
                    "difficulty_level": "intermediate"
                }}
            }}
        ]

        Generate detailed, actionable content based on this training material:
        """
        
        response = model.generate_content(text_and_quiz_prompt)
        
        # Parse the JSON response for text and knowledge check
        import json
        try:
            content_types = json.loads(response.text.strip())
            
            # Generate actual Veo3 video
            video_content_type = generate_veo3_video_content(content)
            
            # Combine all content types
            all_content_types = content_types + [video_content_type]
            
            # Ensure we have exactly 3 content types with proper structure
            if len(all_content_types) >= 3:
                validated_types = []
                for ct in all_content_types[:3]:
                    # Ensure each content type has the required fields
                    if 'content_data' not in ct or not ct['content_data']:
                        ct['content_data'] = generate_default_content_data(ct.get('type', 'text'))
                    validated_types.append(ct)
                return validated_types
            else:
                # If fewer than 3, pad with defaults
                while len(all_content_types) < 3:
                    all_content_types.append(generate_default_content_type())
                return all_content_types[:3]
                
        except json.JSONDecodeError:
            # If JSON parsing fails, extract content types from text response
            return parse_detailed_content_types_from_text(response.text, content)
            
    except Exception as e:
        print(f"⚠️ Gemini content type generation failed: {str(e)}")
        # Return fallback content types with actual content
        return generate_fallback_content_types(content)

def generate_veo3_video_content(content):
    """
    Generate actual Veo3 video content type with real video generation
    """
    try:
        from modules.veo3_integration import generate_veo3_video
        
        # Create a video prompt based on the content
        video_prompt = f"""
        Create a professional training video that demonstrates the key concepts from this content:
        
        {content[:800]}
        
        Show:
        - Clear visual demonstration of the main concepts
        - Step-by-step procedures
        - Professional presentation style
        - Key takeaways and best practices
        
        Style: Professional training video with clear narration and visual demonstrations
        """
        
        # Generate the actual video with Veo3
        video_result = generate_veo3_video(
            prompt=video_prompt,
            duration="3-5 minutes",
            style="professional_training"
        )
        
        return {
            'type': 'video',
            'title': 'Veo3 Training Video',
            'description': 'AI-generated video demonstration using Veo3',
            'content_data': {
                'video_status': 'completed' if video_result.get('success') else 'generating',
                'video_url': video_result.get('video_url'),
                'video_data': video_result.get('video_data'),
                'thumbnail_url': video_result.get('thumbnail_url'),
                'video_duration': video_result.get('duration', '3-5 minutes'),
                'video_summary': 'Professional training video generated with Veo3 AI',
                'generated_with': 'Veo3',
                'generation_id': video_result.get('generation_id'),
                'prompt_used': video_prompt[:200] + "..." if len(video_prompt) > 200 else video_prompt
            }
        }
        
    except Exception as e:
        print(f"⚠️ Veo3 video generation failed: {str(e)}")
        return {
            'type': 'video',
            'title': 'Veo3 Training Video',
            'description': 'AI-generated video demonstration using Veo3',
            'content_data': {
                'video_status': 'failed',
                'video_url': None,
                'video_duration': '3-5 minutes',
                'video_summary': 'Video generation failed - will retry automatically',
                'generated_with': 'Veo3',
                'error_message': str(e)
            }
        }

def parse_content_types_from_text(text):
    """
    Parse content types from text response when JSON parsing fails
    """
    try:
        # Try to extract content types from the response
        content_types = []
        
        # Look for common patterns
        if 'video' in text.lower():
            content_types.append({
                'type': 'video',
                'title': 'Video Tutorial',
                'description': 'Visual demonstration using Veo3'
            })
        
        if any(word in text.lower() for word in ['quiz', 'question', 'test', 'assessment']):
            content_types.append({
                'type': 'knowledge_check',
                'title': 'Knowledge Assessment',
                'description': 'Interactive questions to test understanding'
            })
        
        if any(word in text.lower() for word in ['text', 'manual', 'guide', 'document']):
            content_types.append({
                'type': 'text',
                'title': 'Training Manual',
                'description': 'Comprehensive written guide'
            })
        
        # Ensure we have 3 content types
        while len(content_types) < 3:
            content_types.append({
                'type': 'text',
                'title': 'Training Content',
                'description': 'Additional training material'
            })
        
        return content_types[:3]
        
    except Exception as e:
        return [
            {'type': 'text', 'title': 'Module Content', 'description': 'Training material'},
            {'type': 'video', 'title': 'Video Explanation', 'description': 'Visual demonstration using Veo3'},
            {'type': 'knowledge_check', 'title': 'Knowledge Check', 'description': 'Assessment questions'}
        ]

def generate_default_content_data(content_type):
    """Generate default content data for a content type"""
    defaults = {
        'text': {
            'text': 'Comprehensive training material covering key concepts and procedures',
            'key_points': ['Key concept 1', 'Key concept 2', 'Key concept 3'],
            'suggested_length': '2-3 paragraphs'
        },
        'video': {
            'video_script': 'Scene 1: Introduction to key concepts. Scene 2: Step-by-step demonstration. Scene 3: Best practices summary.',
            'video_duration': '3-5 minutes',
            'video_summary': 'Visual demonstration of training concepts using Veo3',
            'scenes': ['Opening introduction', 'Step-by-step process', 'Key points summary']
        },
        'knowledge_check': {
            'questions': ['What are the key concepts covered?', 'How do you apply these procedures?', 'What are the best practices?'],
            'answers': ['Key concepts include...', 'Procedures are applied by...', 'Best practices involve...'],
            'question_type': 'multiple choice',
            'difficulty_level': 'intermediate'
        }
    }
    return defaults.get(content_type, {'content': 'Training material'})

def generate_default_content_type():
    """Generate a default content type"""
    return {
        'type': 'text',
        'title': 'Training Content',
        'description': 'Additional training material',
        'content_data': generate_default_content_data('text')
    }

def parse_detailed_content_types_from_text(text, original_content):
    """Parse detailed content types from text response with actual content generation"""
    try:
        content_types = []
        
        # Extract key concepts and procedures from original content
        import re
        sentences = re.split(r'[.!?]+', original_content)
        key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:10]
        
        # Generate substantial text content
        text_content = f"""This comprehensive training module provides detailed coverage of essential concepts and procedures. 

Based on the source material, learners will understand:
{chr(10).join(['• ' + s for s in key_sentences[:5]])}

Key procedures and implementation steps:
{chr(10).join(['• ' + s for s in key_sentences[5:8] if s])}

Best practices and important considerations:
{chr(10).join(['• ' + s for s in key_sentences[8:] if s])}

This training material ensures learners gain practical, actionable knowledge they can immediately apply in their work environment."""
        
        content_types.append({
            'type': 'text',
            'title': 'Comprehensive Training Guide',
            'description': 'Detailed written material with actionable content',
            'content_data': {
                'text': text_content,
                'key_points': [s.strip() for s in key_sentences[:3] if s.strip()],
                'suggested_length': '3-4 paragraphs',
                'learning_objectives': ['Master key concepts', 'Apply procedures correctly', 'Follow best practices']
            }
        })
        
        # Generate substantial knowledge check content
        knowledge_questions = []
        knowledge_answers = []
        
        for i, sentence in enumerate(key_sentences[:3]):
            if sentence:
                question = f"What is the correct approach for: {sentence[:50]}...?"
                answer = f"The correct approach involves: {sentence}. This ensures proper implementation and compliance with established procedures."
                knowledge_questions.append(question)
                knowledge_answers.append(answer)
        
        content_types.append({
            'type': 'knowledge_check',
            'title': 'Comprehensive Knowledge Assessment',
            'description': 'Detailed questions based on training content',
            'content_data': {
                'questions': knowledge_questions if knowledge_questions else ['What are the main concepts covered in this training?', 'How do you properly implement these procedures?', 'What are the key safety and compliance considerations?'],
                'answers': knowledge_answers if knowledge_answers else ['Main concepts include the core training material covering essential procedures and best practices', 'Proper implementation requires following established protocols and guidelines', 'Key considerations include safety protocols, compliance requirements, and quality standards'],
                'question_type': 'comprehensive assessment',
                'difficulty_level': 'intermediate',
                'assessment_criteria': ['Understanding of concepts', 'Application ability', 'Procedural knowledge']
            }
        })
        
        # Generate substantial video content with Veo3
        video_script = f"""
SCENE 1: Introduction (0:00-1:00)
- Welcome to the training module
- Overview of key concepts to be covered
- Learning objectives and expected outcomes

SCENE 2: Core Content Demonstration (1:00-3:30)
- Visual demonstration of main procedures
- Step-by-step walkthrough of key processes
- Real-world application examples
- Common mistakes and how to avoid them

SCENE 3: Best Practices (3:30-4:30)
- Industry best practices and standards
- Quality assurance procedures
- Safety considerations and compliance requirements

SCENE 4: Summary and Assessment (4:30-5:00)
- Key takeaways and learning points
- Assessment preparation guidance
- Next steps for learners
"""
        
        content_types.append({
            'type': 'video',
            'title': 'Professional Training Video (Veo3)',
            'description': 'AI-generated video demonstration using Veo3',
            'content_data': {
                'video_script': video_script,
                'video_duration': '5 minutes',
                'video_summary': f'Professional training video covering: {original_content[:100]}...',
                'scenes': ['Introduction and objectives', 'Core demonstration', 'Best practices', 'Summary and assessment'],
                'generated_with': 'Veo3',
                'video_status': 'generating',
                'learning_outcomes': ['Visual understanding', 'Procedural knowledge', 'Practical application']
            }
        })
        
        return content_types[:3]
        
    except Exception as e:
        debug_print(f"⚠️ Detailed content parsing failed: {str(e)}")
        return generate_fallback_content_types(original_content)

def save_enhanced_pathways_to_session(enhanced_pathway_data):
    """
    Save enhanced pathway data back to session state to prevent loss during switching
    """
    try:
        import streamlit as st
        if enhanced_pathway_data and 'pathways' in enhanced_pathway_data:
            # Update the original generated_pathway with enhanced data
            st.session_state['generated_pathway'] = enhanced_pathway_data
            
            # Clear editable_pathways to force regeneration with new data
            if 'editable_pathways' in st.session_state:
                del st.session_state['editable_pathways']
            if 'editable_pathways_pathway_idx' in st.session_state:
                del st.session_state['editable_pathways_pathway_idx']
                
            debug_print("✅ Enhanced pathway data saved to session state")
    except Exception as e:
        debug_print(f"⚠️ Failed to save enhanced data to session: {str(e)}")

def generate_unique_content_seed():
    """
    Generate truly unique seeds for content generation to prevent similarity
    """
    import uuid
    import hashlib
    
    # Create unique seed using UUID and current context
    unique_id = str(uuid.uuid4())
    timestamp = str(time.time())
    context_hash = hashlib.md5(f"{unique_id}{timestamp}".encode()).hexdigest()
    
    return context_hash[:8]  # Use first 8 chars for brevity

def validate_and_enhance_pathway_modules(pathway_data, min_modules_per_section=6, min_sections_per_pathway=4, training_context=None):
    """
    Validate and enhance pathway data to ensure adequate module generation with decimal numbering,
    goal alignment, and content type diversity
    """
    try:
        debug_print(f"🔍 Starting validation with minimum {min_modules_per_section} modules per section")
        
        if not pathway_data or 'pathways' not in pathway_data:
            debug_print("⚠️ No pathway data to validate")
            return pathway_data
        
        debug_print(f"📋 Found {len(pathway_data['pathways'])} pathways to validate")
        
        for pathway_idx, pathway in enumerate(pathway_data['pathways']):
            debug_print(f"🛤️ Validating pathway {pathway_idx + 1}: {pathway.get('pathway_name', 'Unknown')}")
            
            if 'sections' not in pathway:
                pathway['sections'] = []
                debug_print(f"⚠️ Pathway {pathway_idx + 1} has no sections, creating empty sections list")
            
            sections = pathway['sections']
            
            # Validate minimum sections per pathway
            if len(sections) < min_sections_per_pathway:
                debug_print(f"⚠️ Pathway {pathway_idx + 1} has only {len(sections)} sections, enhancing to {min_sections_per_pathway}")
                
                # Generate additional sections
                while len(sections) < min_sections_per_pathway:
                    section_number = len(sections) + 1
                    additional_section = generate_enhanced_section(pathway.get('pathway_name', 'Training'), section_number)
                    sections.append(additional_section)
                    debug_print(f"➕ Added section {section_number}: {additional_section['title']}")
                
                pathway['sections'] = sections
                debug_print(f"✅ Enhanced pathway {pathway_idx + 1} to {len(sections)} sections")
            else:
                debug_print(f"✅ Pathway {pathway_idx + 1} already has sufficient sections ({len(sections)})")
                
            for section_idx, section in enumerate(pathway['sections']):
                if 'modules' not in section:
                    section['modules'] = []
                
                modules = section['modules']
                section_title = section.get('title', 'Training Section')
                section_number = section_idx + 1
                
                # Check if section has enough modules
                debug_print(f"📊 Section {section_number} '{section_title}' has {len(modules)} modules (minimum required: {min_modules_per_section})")
                
                if len(modules) < min_modules_per_section:
                    debug_print(f"⚠️ Section {section_number} '{section_title}' has only {len(modules)} modules, enhancing to {min_modules_per_section}")
                    
                    # Generate additional modules with decimal numbering
                    while len(modules) < min_modules_per_section:
                        module_number = len(modules) + 1
                        decimal_module_number = f"{section_number}.{module_number}"
                        additional_module = generate_enhanced_module(section_title, decimal_module_number)
                        modules.append(additional_module)
                        debug_print(f"➕ Added module {decimal_module_number}: {additional_module['title']}")
                    
                    section['modules'] = modules
                    debug_print(f"✅ Enhanced section {section_number} '{section_title}' to {len(modules)} modules (modules {section_number}.1 to {section_number}.{len(modules)})")
                else:
                    debug_print(f"✅ Section {section_number} '{section_title}' already has sufficient modules ({len(modules)})")
                
                # NEW: Validate content types and goal alignment for each module
                validate_module_content_requirements(modules, training_context, section_number)
        
        # NEW: Validate overall pathway goal alignment
        if training_context:
            validate_pathway_goal_alignment(pathway_data, training_context)
        
        # Save enhanced data back to session state to prevent loss during pathway switching
        save_enhanced_pathways_to_session(pathway_data)
        
        return pathway_data
        
    except Exception as e:
        debug_print(f"❌ Pathway validation failed: {str(e)}")
        return pathway_data

def validate_module_content_requirements(modules, training_context, section_number):
    """
    Validate that each module meets content type and goal alignment requirements
    """
    try:
        primary_goals = training_context.get('primary_goals', '') if training_context else ''
        
        for module_idx, module in enumerate(modules):
            module_number = f"{section_number}.{module_idx + 1}"
            debug_print(f"🔍 Validating module {module_number}: {module.get('title', 'Unknown')}")
            
            # Validate content types requirement (3+ distinct types)
            content_types = module.get('content_types', [])
            if len(content_types) < 3:
                debug_print(f"⚠️ Module {module_number} has only {len(content_types)} content types, adding more")
                # Add missing content types
                available_types = ['text', 'list', 'image', 'video', 'flashcard', 'survey', 'knowledge_check', 'accordion', 'tabs', 'assignment']
                for content_type in available_types:
                    if content_type not in content_types and len(content_types) < 5:
                        content_types.append(content_type)
                        debug_print(f"➕ Added content type '{content_type}' to module {module_number}")
                
                module['content_types'] = content_types
            
            # Validate content_blocks structure
            if 'content_blocks' not in module:
                module['content_blocks'] = []
                debug_print(f"⚠️ Module {module_number} missing content_blocks, creating structure")
                
                # Create content blocks for each content type with actual content
                for content_type in content_types[:3]:  # Ensure at least 3 blocks
                    content_block = generate_goal_aligned_content_block(content_type, module.get('title', 'Module'), module.get('content', ''), primary_goals)
                    module['content_blocks'].append(content_block)
                    debug_print(f"➕ Added content block '{content_type}' to module {module_number}")
            
            # Validate goal alignment in content
            if primary_goals and training_context:
                validate_module_goal_alignment(module, primary_goals, module_number)
                
    except Exception as e:
        debug_print(f"❌ Module content validation failed: {str(e)}")

def validate_pathway_goal_alignment(pathway_data, training_context):
    """
    Validate that pathways align with user's primary training goals
    """
    try:
        primary_goals = training_context.get('primary_goals', '')
        success_metrics = training_context.get('success_metrics', '')
        
        if not primary_goals:
            debug_print("⚠️ No primary goals specified, skipping goal alignment validation")
            return
            
        debug_print(f"🎯 Validating pathway alignment with goals: {primary_goals}")
        
        for pathway_idx, pathway in enumerate(pathway_data.get('pathways', [])):
            pathway_name = pathway.get('pathway_name', '')
            
            # Check if pathway name references user goals
            if primary_goals.lower() not in pathway_name.lower():
                debug_print(f"⚠️ Pathway {pathway_idx + 1} name doesn't reference user goals, updating")
                pathway['pathway_name'] = f"Goal-Focused Training for {primary_goals}"
                debug_print(f"✅ Updated pathway name to reference user goals")
            
            # Add goal alignment metadata
            pathway['goal_alignment'] = f"This pathway directly supports achieving: {primary_goals}"
            pathway['success_metrics'] = success_metrics
            
            debug_print(f"✅ Pathway {pathway_idx + 1} validated for goal alignment")
            
    except Exception as e:
        debug_print(f"❌ Pathway goal alignment validation failed: {str(e)}")

def validate_module_goal_alignment(module, primary_goals, module_number):
    """
    Validate that individual module content aligns with user goals
    """
    try:
        module_content = module.get('content', '')
        
        # Check if module content references user goals
        if primary_goals.lower() not in module_content.lower():
            debug_print(f"⚠️ Module {module_number} content doesn't reference user goals, enhancing")
            
            # Enhance content to include goal alignment
            enhanced_content = f"This module directly supports achieving your PRIMARY TRAINING GOALS: {primary_goals}. " + module_content
            module['content'] = enhanced_content
            
            debug_print(f"✅ Enhanced module {module_number} content for goal alignment")
        
        # Add goal contribution metadata
        module['goal_contribution'] = f"Advances user's primary training goals: {primary_goals}"
        
    except Exception as e:
        debug_print(f"❌ Module goal alignment validation failed: {str(e)}")

def generate_enhanced_section(pathway_name, section_number):
    """
    Generate an enhanced section for a pathway with unique content
    """
    # Generate unique seed for this specific section
    section_seed = generate_unique_content_seed()
    
    section_topics = [
        "Fundamentals and Overview",
        "Procedures and Implementation", 
        "Best Practices and Standards",
        "Advanced Concepts and Applications",
        "Assessment and Evaluation",
        "Quality Assurance and Compliance",
        "Practical Applications",
        "Safety and Compliance",
        "Technology Integration",
        "Performance Optimization"
    ]
    
    # Use hash to select topic based on pathway name and section number for uniqueness
    import hashlib
    context_hash = hashlib.md5(f"{pathway_name}_{section_number}_{section_seed}".encode()).hexdigest()
    topic_index = int(context_hash, 16) % len(section_topics)
    topic = section_topics[topic_index]
    
    section = {
        'title': f"Section {section_number}: {topic}",
        'description': f"Comprehensive coverage of {topic.lower()} for {pathway_name} (ID: {section_seed})",
        'modules': [],
        'unique_id': section_seed
    }
    
    # Generate 6 modules for this section with unique content
    for module_num in range(1, 7):
        module = generate_enhanced_module(section['title'], f"{section_number}.{module_num}", section_seed)
        section['modules'].append(module)
    
    return section

def generate_content_block(content_type, section_title, content_variation, block_seed, block_number):
    """
    Generate a specific content block for a given content type
    """
    import hashlib
    
    # Create unique content based on content type
    content_hash = hashlib.md5(f"{content_type}_{section_title}_{block_seed}".encode()).hexdigest()[:8]
    
    content_block = {
        'type': content_type,
        'title': f"Content Block {block_number}: {content_type.title()}",
        'block_id': block_seed,
        'content_data': {}
    }
    
    if content_type == 'text':
        content_block['content_data'] = {
            'text': f"Comprehensive exploration of {content_variation} within {section_title}. This detailed analysis provides practical implementation strategies, evidence-based methodologies, and professional development insights. The material emphasizes critical thinking, strategic planning, and competency advancement through structured learning approaches. (Block ID: {content_hash})",
            'key_points': [f"{content_variation.title()}", "Evidence-based methodologies", "Strategic implementation"],
            'suggested_length': '3-4 paragraphs',
            'content_id': content_hash
        }
    
    elif content_type == 'video':
        content_block['content_data'] = {
            'video_script': f"Scene 1: Introduction to {content_variation} in {section_title}. Scene 2: Detailed demonstration of key concepts and procedures. Scene 3: Real-world applications and case studies. Scene 4: Best practices and implementation strategies. Scene 5: Summary and next steps.",
            'video_duration': '8-12 minutes',
            'video_summary': f"Comprehensive video covering {content_variation} in {section_title}",
            'scenes': ['Introduction', 'Demonstration', 'Applications', 'Best Practices', 'Summary'],
            'generated_with': 'Veo3',
            'content_id': content_hash
        }
    
    elif content_type == 'knowledge_check':
        questions = [
            f"What are the key principles of {content_variation} in {section_title}?",
            f"How would you implement {content_variation} in a real-world scenario?",
            f"What are the best practices for {content_variation} in {section_title}?",
            f"How do you measure success when applying {content_variation}?"
        ]
        answers = [
            f"Key principles include systematic approach, evidence-based methodology, and continuous improvement in {section_title}",
            f"Implementation requires careful planning, stakeholder engagement, and phased execution of {content_variation}",
            f"Best practices include thorough preparation, regular monitoring, quality assurance, and documentation",
            f"Success is measured through performance metrics, stakeholder feedback, and achievement of defined objectives"
        ]
        content_block['content_data'] = {
            'questions': questions,
            'answers': answers,
            'question_type': 'comprehensive assessment',
            'difficulty_level': 'intermediate to advanced',
            'content_id': content_hash
        }
    
    elif content_type == 'list':
        content_block['content_data'] = {
            'list_items': [
                f"Fundamental concepts of {content_variation}",
                f"Step-by-step implementation procedures for {section_title}",
                f"Quality assurance and validation methods",
                f"Common challenges and mitigation strategies",
                f"Performance monitoring and optimization techniques",
                f"Documentation and reporting requirements"
            ],
            'list_type': 'procedure',
            'instructions': f"Follow these steps to successfully implement {content_variation} in {section_title}",
            'content_id': content_hash
        }
    
    elif content_type == 'assignment':
        content_block['content_data'] = {
            'assignment_task': f"Develop a comprehensive implementation plan for {content_variation} in your specific {section_title} context. Include stakeholder analysis, resource requirements, timeline, and success metrics.",
            'deliverables': f"Submit a detailed plan document, presentation slides, and implementation timeline for {content_variation}",
            'evaluation_criteria': "Completeness, feasibility, alignment with best practices, and practical applicability",
            'estimated_time': '45-60 minutes',
            'content_id': content_hash
        }
    
    elif content_type == 'flashcard':
        content_block['content_data'] = {
            'flashcard_front': f"What is the primary objective of {content_variation} in {section_title}?",
            'flashcard_back': f"The primary objective is to achieve systematic improvement and optimal performance through evidence-based {content_variation} methodologies within {section_title} operations.",
            'difficulty_level': 'intermediate',
            'category': f"{section_title} - {content_variation}",
            'content_id': content_hash
        }
    
    elif content_type == 'image':
        content_block['content_data'] = {
            'image_description': f"Detailed infographic showing the implementation flow of {content_variation} in {section_title}, including key stages, decision points, and outcome measures",
            'image_purpose': f"Visual representation helps learners understand the systematic approach to {content_variation}",
            'suggested_format': 'infographic',
            'alt_text': f"{content_variation} implementation flow for {section_title}",
            'content_id': content_hash
        }
    
    elif content_type == 'file':
        content_block['content_data'] = {
            'file_description': f"Comprehensive reference document covering {content_variation} methodologies for {section_title}",
            'file_type': 'PDF guide',
            'file_purpose': f"Detailed reference material for implementing {content_variation}",
            'file_size': 'Approximately 15-20 pages',
            'content_id': content_hash
        }
    
    elif content_type == 'accordion':
        content_block['content_data'] = {
            'accordion_sections': [
                {
                    'title': f"Overview of {content_variation}",
                    'content': f"Fundamental principles and concepts underlying {content_variation} in {section_title}"
                },
                {
                    'title': 'Implementation Steps',
                    'content': f"Step-by-step guide for implementing {content_variation} effectively"
                },
                {
                    'title': 'Best Practices',
                    'content': f"Industry-proven best practices for {content_variation} in {section_title}"
                },
                {
                    'title': 'Common Challenges',
                    'content': f"Typical challenges and proven solutions for {content_variation} implementation"
                }
            ],
            'default_open': 0,
            'content_id': content_hash
        }
    
    elif content_type == 'tabs':
        content_block['content_data'] = {
            'tab_sections': [
                {
                    'tab_title': 'Theory',
                    'tab_content': f"Theoretical foundations of {content_variation} in {section_title}"
                },
                {
                    'tab_title': 'Practice',
                    'tab_content': f"Practical implementation strategies for {content_variation}"
                },
                {
                    'tab_title': 'Examples',
                    'tab_content': f"Real-world examples and case studies of {content_variation}"
                },
                {
                    'tab_title': 'Resources',
                    'tab_content': f"Additional resources and references for {content_variation}"
                }
            ],
            'default_tab': 0,
            'content_id': content_hash
        }
    
    elif content_type == 'survey':
        content_block['content_data'] = {
            'survey_questions': [
                {
                    'question': f"How familiar are you with {content_variation} concepts?",
                    'type': 'multiple_choice',
                    'options': ['Very familiar', 'Somewhat familiar', 'Limited familiarity', 'Not familiar']
                },
                {
                    'question': f"What aspects of {content_variation} are most relevant to your role?",
                    'type': 'checkbox',
                    'options': ['Strategic planning', 'Implementation', 'Quality assurance', 'Performance monitoring']
                },
                {
                    'question': f"What challenges do you anticipate in implementing {content_variation}?",
                    'type': 'text_area',
                    'placeholder': 'Please describe your anticipated challenges...'
                }
            ],
            'survey_purpose': f"Assess learner readiness and expectations for {content_variation} training",
            'content_id': content_hash
        }
    
    elif content_type == 'divider':
        content_block['content_data'] = {
            'divider_text': f"--- {content_variation.title()} Section ---",
            'divider_style': 'horizontal_line',
            'section_marker': True,
            'content_id': content_hash
        }
    
    else:
        # Generic content block for any unhandled content types
        content_block['content_data'] = {
            'detailed_content': f"Specialized content for {content_type} focusing on {content_variation} within {section_title}",
            'purpose': f"Enhance learning through {content_type} format",
            'content_id': content_hash
        }
    
    return content_block

def generate_goal_aligned_content_block(content_type, module_title, module_content, primary_goals):
    """
    Generate a content block aligned with user's primary training goals
    """
    try:
        content_block = {
            'type': content_type,
            'title': f"{content_type.title().replace('_', ' ')} for Goal Achievement",
            'content_data': {}
        }
        
        # Base content that incorporates module content and goals
        goal_context = f"This content directly supports achieving your PRIMARY TRAINING GOALS: {primary_goals}"
        module_context = module_content[:200] if module_content else "training content"
        
        if content_type == 'text':
            content_block['content_data'] = {
                'text': f"{goal_context}. Based on {module_title}: {module_context}. This training material provides specific knowledge and practical skills necessary to advance toward your goals through structured learning and application.",
                'key_points': [
                    f"Direct support for achieving: {primary_goals[:50]}..." if len(primary_goals) > 50 else f"Direct support for achieving: {primary_goals}",
                    "Practical application strategies",
                    "Measurable progress indicators",
                    "Goal-specific learning outcomes"
                ]
            }
            
        elif content_type == 'video':
            content_block['content_data'] = {
                'video_script': f"Introduction: How this module advances your PRIMARY TRAINING GOALS: {primary_goals}. Main Content: {module_context}. Application: Practical steps to achieve your specific goals. Conclusion: Next steps toward goal achievement.",
                'video_duration': '5-8 minutes',
                'video_summary': f"Goal-focused training video for {module_title} specifically designed to advance: {primary_goals}",
                'video_status': 'completed'
            }
            
        elif content_type == 'knowledge_check':
            content_block['content_data'] = {
                'questions': [
                    f"How does {module_title} help you achieve your PRIMARY TRAINING GOALS: {primary_goals}?",
                    f"What specific knowledge from this module will you apply toward your goals?",
                    f"How will you measure progress toward achieving: {primary_goals}?"
                ],
                'answers': [
                    f"This module provides specific knowledge and skills that directly advance: {primary_goals}",
                    f"Key applications include practical implementation of concepts from: {module_content[:100]}...",
                    f"Progress can be measured through goal-specific metrics and practical application of learning"
                ],
                'question_type': 'Goal-focused assessment',
                'difficulty_level': 'Intermediate'
            }
            
        elif content_type == 'flashcard':
            content_block['content_data'] = {
                'flashcard_front': f"How does {module_title} advance your PRIMARY TRAINING GOALS?",
                'flashcard_back': f"This module directly supports achieving: {primary_goals} by providing: {module_context}"
            }
            
        elif content_type == 'list':
            content_block['content_data'] = {
                'list_items': [
                    f"Review how this module advances: {primary_goals}",
                    f"Identify key concepts from: {module_title}",
                    "Apply learning to goal achievement",
                    "Measure progress toward objectives",
                    "Plan next steps for continued advancement"
                ],
                'instructions': f"Follow this checklist to maximize learning toward your PRIMARY TRAINING GOALS: {primary_goals}"
            }
            
        elif content_type == 'survey':
            content_block['content_data'] = {
                'survey_questions': [
                    {
                        'question': f"How confident are you in applying {module_title} content toward your PRIMARY TRAINING GOALS: {primary_goals}?",
                        'type': 'multiple_choice',
                        'options': ['Very confident', 'Confident', 'Somewhat confident', 'Need more practice']
                    },
                    {
                        'question': f"Which aspects of this module are most relevant to achieving: {primary_goals}?",
                        'type': 'checkbox',
                        'options': ['Conceptual understanding', 'Practical application', 'Skill development', 'Goal alignment']
                    },
                    {
                        'question': 'How will you apply this learning to advance toward your goals?',
                        'type': 'text_area',
                        'placeholder': 'Describe your specific application plans...'
                    }
                ]
            }
            
        elif content_type == 'assignment':
            content_block['content_data'] = {
                'assignment_task': f"Create a practical action plan showing how you will apply {module_title} concepts to achieve your PRIMARY TRAINING GOALS: {primary_goals}",
                'deliverables': 'Written action plan with specific steps and timeline',
                'evaluation_criteria': 'Alignment with goals, practical applicability, and measurable outcomes'
            }
            
        elif content_type == 'accordion':
            content_block['content_data'] = {
                'accordion_sections': [
                    {
                        'title': 'Goal Alignment',
                        'content': f"How this module advances your PRIMARY TRAINING GOALS: {primary_goals}"
                    },
                    {
                        'title': 'Key Concepts',
                        'content': f"Essential concepts from {module_title}: {module_context}"
                    },
                    {
                        'title': 'Practical Application',
                        'content': f"How to apply this learning toward achieving: {primary_goals}"
                    },
                    {
                        'title': 'Success Metrics',
                        'content': "How to measure progress and success in goal achievement"
                    }
                ]
            }
            
        elif content_type == 'tabs':
            content_block['content_data'] = {
                'tab_sections': [
                    {
                        'tab_title': 'Goals',
                        'tab_content': f"How this module advances: {primary_goals}"
                    },
                    {
                        'tab_title': 'Content',
                        'tab_content': f"Key learning from {module_title}: {module_context}"
                    },
                    {
                        'tab_title': 'Application',
                        'tab_content': f"Practical steps to apply learning toward: {primary_goals}"
                    },
                    {
                        'tab_title': 'Assessment',
                        'tab_content': "How to evaluate progress toward goal achievement"
                    }
                ]
            }
            
        else:
            # Generic content for other types
            content_block['content_data'] = {
                'content': f"{goal_context}. Content from {module_title}: {module_context}",
                'goal_alignment': f"Supports achieving: {primary_goals}",
                'application': f"Apply this {content_type} content to advance toward your training goals"
            }
        
        return content_block
        
    except Exception as e:
        debug_print(f"⚠️ Goal-aligned content block generation failed: {str(e)}")
        # Return basic fallback content
        return {
            'type': content_type,
            'title': f"{content_type.title().replace('_', ' ')} Content",
            'content_data': {
                'content': f"Goal-focused {content_type} content for {module_title}",
                'goal_alignment': f"Supports achieving: {primary_goals}"
            }
        }

def generate_enhanced_module(section_title, module_number, section_seed=None):
    """
    Generate an enhanced module for a section with unique content and 3+ content types
    """
    # Generate unique seed for this module if not provided
    if section_seed is None:
        section_seed = generate_unique_content_seed()
    
    module_seed = generate_unique_content_seed()
    
    # All available content types including missing ones
    all_content_types = [
        'text', 'video', 'knowledge_check', 'list', 'assignment', 
        'flashcard', 'image', 'file', 'accordion', 'divider', 
        'tabs', 'survey'
    ]
    
    # Select 3-5 distinct content types for this module
    import hashlib
    import random
    
    # Use module seed to create deterministic but unique selection
    random.seed(int(hashlib.md5(module_seed.encode()).hexdigest()[:8], 16))
    num_types = random.randint(3, 5)  # 3-5 content types per module
    selected_types = random.sample(all_content_types, min(num_types, len(all_content_types)))
    
    # Primary content type (first selected)
    primary_content_type = selected_types[0]
    
    # Generate unique content based on seeds to prevent similarity
    content_variations = [
        "comprehensive analysis and implementation strategies",
        "practical applications and real-world scenarios", 
        "systematic methodology and best practices",
        "innovative approaches and advanced techniques",
        "quality assurance and continuous improvement",
        "strategic planning and execution frameworks",
        "performance optimization and efficiency methods",
        "collaborative processes and team dynamics"
    ]
    
    type_hash = hashlib.md5(f"{section_title}_{module_number}_{module_seed}".encode()).hexdigest()
    variation_index = int(type_hash[:8], 16) % len(content_variations)
    content_variation = content_variations[variation_index]
    
    module = {
        'title': f"Module {module_number}: {section_title} - {content_variation.title()}",
        'description': f"Multi-format training on {content_variation} for {section_title}",
        'content': f"This comprehensive module explores {content_variation} within {section_title} through multiple content formats. Learners will engage with diverse learning materials including interactive elements, assessments, and practical applications. The curriculum emphasizes multi-modal learning experiences to accommodate different learning preferences and ensure comprehensive understanding.",
        'content_type': primary_content_type,  # Primary content type
        'content_types': selected_types,  # All content types in this module
        'learning_objectives': [
            f"Master {content_variation} in {section_title}",
            "Engage with multi-format learning materials", 
            "Demonstrate competency through diverse assessments"
        ],
        'key_points': [
            f"{content_variation.title()}",
            "Multi-modal learning approach",
            "Comprehensive skill development"
        ],
        'source': [f'Generated content for {section_title} (ID: {module_seed})'],
        'engagement_level': 'very high',
        'estimated_time': '25-35 minutes',
        'unique_id': module_seed,
        'content_blocks': []  # Will store multiple content type blocks
    }
    
    # Generate content blocks for each selected content type
    for i, content_type in enumerate(selected_types):
        block_seed = generate_unique_content_seed()
        content_block = generate_content_block(content_type, section_title, content_variation, block_seed, i+1)
        module['content_blocks'].append(content_block)
    
    # Set primary content_data to first content block for backward compatibility
    if module['content_blocks']:
        module['content_data'] = module['content_blocks'][0]['content_data']
    else:
        # Fallback content_data if no content blocks were generated
        module['content_data'] = {
            'detailed_content': f"Multi-format training content for {content_variation} within {section_title}",
            'purpose': f"Comprehensive learning through diverse content formats",
            'content_id': module_seed
        }
    
    return module

def generate_fallback_content_types(content):
    """Generate fallback content types with substantial, actual content"""
    
    # Extract meaningful content from the source material
    content_preview = content[:500] if content else "comprehensive training material"
    
    # Generate detailed text content
    detailed_text = f"""This comprehensive training module delivers essential knowledge and practical skills needed for professional development. 

The content covers key concepts and procedures derived from the source material:
{content_preview}

Learners will gain practical understanding through:
• Step-by-step procedural guidance
• Real-world application examples
• Best practice implementations
• Quality assurance protocols
• Safety and compliance requirements

This training ensures participants develop the competency and confidence needed to apply their learning effectively in their work environment. The material is designed to be immediately actionable and provides clear guidance for successful implementation."""
    
    # Generate detailed video script
    comprehensive_video_script = f"""
OPENING SEQUENCE (0:00-1:00)
- Professional introduction to the training module
- Clear statement of learning objectives
- Overview of content structure and benefits

MAIN CONTENT SECTION (1:00-4:00)
- Detailed visual demonstration of key procedures
- Step-by-step walkthrough with clear explanations
- Real-world scenarios and applications
- Common challenges and solution strategies
- Best practices and industry standards

PRACTICAL APPLICATION (4:00-5:30)
- Hands-on examples and case studies
- Quality control and verification methods
- Troubleshooting common issues
- Safety protocols and compliance measures

CONCLUSION AND NEXT STEPS (5:30-6:00)
- Summary of key learning points
- Implementation roadmap for learners
- Resources for continued development
- Assessment preparation guidance

This professional training video uses Veo3 AI to deliver engaging, visual learning content that reinforces theoretical knowledge with practical application."""
    
    return [
        {
            'type': 'text',
            'title': 'Comprehensive Training Manual',
            'description': 'Detailed written guide with actionable content',
            'content_data': {
                'text': detailed_text,
                'key_points': [
                    'Step-by-step procedural guidance and implementation',
                    'Real-world application examples and best practices',
                    'Quality assurance protocols and safety requirements',
                    'Professional development and competency building'
                ],
                'suggested_length': '4-5 paragraphs',
                'learning_objectives': [
                    'Master essential procedures and concepts',
                    'Apply knowledge in real-world scenarios',
                    'Implement quality and safety standards',
                    'Develop professional competency'
                ]
            }
        },
        {
            'type': 'video',
            'title': 'Professional Training Video (Veo3)',
            'description': 'AI-generated comprehensive video demonstration',
            'content_data': {
                'video_script': comprehensive_video_script,
                'video_duration': '6 minutes',
                'video_summary': f'Professional training video covering: {content_preview}...',
                'scenes': [
                    'Professional introduction and objectives',
                    'Detailed procedure demonstrations',
                    'Practical application examples',
                    'Summary and implementation guidance'
                ],
                'generated_with': 'Veo3',
                'video_status': 'generating',
                'learning_outcomes': [
                    'Visual understanding of procedures',
                    'Practical application knowledge',
                    'Quality and safety awareness'
                ]
            }
        },
        {
            'type': 'knowledge_check',
            'title': 'Comprehensive Assessment',
            'description': 'Detailed questions to verify understanding and application',
            'content_data': {
                'questions': [
                    'What are the essential steps in the primary procedure covered in this training?',
                    'How do you ensure quality control and compliance during implementation?',
                    'What safety protocols must be followed and why are they important?',
                    'How would you troubleshoot common issues that might arise?',
                    'What best practices should be applied for optimal results?'
                ],
                'answers': [
                    'Essential steps include systematic preparation, careful execution following established protocols, quality verification, and proper documentation of results',
                    'Quality control requires systematic verification at each step, use of appropriate tools and measurements, compliance with established standards, and thorough documentation',
                    'Safety protocols include proper equipment use, risk assessment, environmental considerations, and emergency procedures to prevent accidents and ensure worker protection',
                    'Troubleshooting involves systematic problem identification, root cause analysis, application of proven solution strategies, and verification of resolution effectiveness',
                    'Best practices include thorough preparation, systematic approach, quality verification, continuous improvement, and knowledge sharing with team members'
                ],
                'question_type': 'comprehensive assessment',
                'difficulty_level': 'intermediate to advanced',
                'assessment_criteria': [
                    'Procedural knowledge and understanding',
                    'Quality and safety awareness',
                    'Problem-solving capabilities',
                    'Practical application skills'
                ]
            }
        }
    ]

def get_parallel_config():
    """
    Get configuration for parallel processing based on system capabilities
    (Optimized for speed: reduced AI calls and faster processing)
    """
    return {
        'max_file_workers': 2,      # Reduced workers to avoid timeouts
        'max_section_workers': 2,   # Reduced AI workers
        'max_topic_workers': 2,     # Reduced topic analysis workers
        'timeout_seconds': 60,      # Reduced timeout for faster processing
        'max_modules_per_file': 8,  # Increased module limit to allow more comprehensive content
        'batch_ai_calls': False,    # Disable batching to avoid timeouts
        'parallel_ai_processing': False  # Disable parallel AI for reliability
    }

def extract_and_transform_content(content, training_context):
    """
    Universal content extraction and transformation system
    Works with ANY file type and ANY subject matter for onboarding
    """
    try:
        # Universal content analysis - works for any type of content
        content_lower = content.lower()
        
        # Universal content type detection
        content_type = detect_content_type(content)
        print(f"🔍 **Universal Content Analysis:**")
        print(f"   Content type: {content_type}")
        print(f"   Content length: {len(content)} characters")
        print(f"   Content preview: {content[:200]}...")
        
        # Apply universal transformation based on content type
        if content_type == "structured_training":
            return apply_conservative_transformation(content, training_context)
        elif content_type == "conversational":
            return apply_comprehensive_transformation(content, training_context)
        elif content_type == "technical_documentation":
            return apply_technical_transformation(content, training_context)
        elif content_type == "procedural":
            return apply_procedural_transformation(content, training_context)
        else:
            # Default to comprehensive transformation for unknown types
            return apply_comprehensive_transformation(content, training_context)
            
    except Exception as e:
        print(f"⚠️ Universal content transformation failed: {str(e)}")
        return None

def detect_content_type(content):
    """
    Universal content type detection - works for any file type and subject
    """
    try:
        if not content or len(content.strip()) < 10:
            return "conversational"
            
        content_lower = content.lower()
        
        # Check for meeting transcript patterns first (these should override other detection)
        meeting_patterns = [
            r'teams meeting',
            r'meet meeting', 
            r'meeting transcript',
            r'\d{1,2}:\d{2}\s*-\s*[A-Za-z]',  # Time stamps like "0:00 - Name"
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday),\s*\w+\s+\d{1,2},\s*\d{4}',  # Date patterns
            r'yeah,\s*\w+',  # Conversational patterns
            r'um,\s*\w+',
            r'uh,\s*\w+'
        ]
        
        # Check for meeting patterns
        meeting_matches = 0
        import re
        for pattern in meeting_patterns:
            if re.search(pattern, content_lower):
                meeting_matches += 1
        
        # If content has meeting indicators, it's conversational regardless of other scores
        if meeting_matches >= 1:  # Any meeting indicator means it's conversational
            print(f"   Detected content type: conversational (meeting transcript - {meeting_matches} indicators)")
            return "conversational"
        
        # Universal content type indicators
        content_types = {
            "structured_training": {
                "indicators": [
                    'training', 'onboarding', 'guide', 'manual', 'procedure', 'process',
                    'instruction', 'tutorial', 'workflow', 'standard operating procedure',
                    'sop', 'policy', 'guideline', 'best practice', 'step-by-step',
                    'how to', 'overview', 'introduction', 'getting started', 'admin',
                    'user guide', 'reference', 'documentation', 'handbook'
                ],
                "patterns": [
                    r'\d+\.\s',  # Numbered sections
                    r'[•\-\*]\s',  # Bullet points
                    r'^[A-Z][A-Z\s]+$',  # Headers
                    r'step\s+\d+',  # Step-by-step
                    r'procedure\s+\d+',  # Procedures
                ]
            },
            "conversational": {
                "indicators": [
                    'meeting transcript', 'teams meeting', 'meet meeting', 'zoom meeting',
                    'conference call', 'video call', 'meeting recording', 'call transcript',
                    'um', 'uh', 'yeah', 'okay', 'right', 'so', 'well', 'you know',
                    'can you hear me', 'is that working', 'are you there'
                ],
                "patterns": [
                    r'\d{1,2}:\d{2}\s*-\s*[A-Za-z]',  # Time stamps
                    r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',  # Days
                    r'yeah,\s*\w+',  # Conversational patterns
                    r'um,\s*\w+',
                    r'uh,\s*\w+'
                ]
            },
       
            "technical_documentation": {
                "indicators": [
                    'specification', 'technical', 'engineering', 'design', 'architecture',
                    'system', 'component', 'module', 'interface', 'api', 'database',
                    'configuration', 'installation', 'setup', 'deployment'
                ],
                "patterns": [
                    r'[A-Z]{2,}\s+\d+',  # Technical codes
                    r'version\s+\d+',  # Version numbers
                    r'api\s+endpoint',  # API references
                    r'configuration\s+file',  # Config references
                ]
            },
            "procedural": {
                "indicators": [
                    'procedure', 'process', 'workflow', 'method', 'technique',
                    'operation', 'maintenance', 'calibration', 'inspection',
                    'quality control', 'safety', 'compliance'
                ],
                "patterns": [
                    r'step\s+\d+',  # Step procedures
                    r'check\s+list',  # Checklists
                    r'verify\s+that',  # Verification steps
                    r'ensure\s+that',  # Safety checks
                ]
            }
        }
        
        # Score each content type
        content_scores = {}
        
        for content_type, detection in content_types.items():
            score = 0
            
            # Count indicator matches
            indicator_matches = sum(1 for indicator in detection["indicators"] if indicator in content_lower)
            score += indicator_matches * 2  # Weight indicators more heavily
            
            # Count pattern matches
            pattern_matches = 0
            for pattern in detection["patterns"]:
                if re.search(pattern, content, re.IGNORECASE):
                    pattern_matches += 1
            score += pattern_matches * 3  # Weight patterns even more heavily
            
            content_scores[content_type] = score
        
        # Find the content type with highest score
        best_type = "conversational"  # Default
        best_score = 0
        
        if content_scores:
            try:
                # Fix the max() function type issue
                best_type = max(content_scores.keys(), key=lambda k: content_scores[k])
                best_score = content_scores[best_type]
            except Exception as e:
                print(f"⚠️ Error finding best content type: {e}")
                best_type = "conversational"
                best_score = 0
        
        # Only classify if we have a clear winner
        if best_score >= 3:
            print(f"   Detected content type: {best_type} (score: {best_score})")
            return best_type
        
        # Default to conversational if unclear
        print(f"   Defaulting to conversational content type")
        return "conversational"
        
    except Exception as e:
        print(f"⚠️ Content type detection failed: {str(e)}")
        return "conversational"

def apply_technical_transformation(content, training_context):
    """
    Transform technical documentation into onboarding material using simple methods
    """
    try:
        # Use simple content cleaning instead of AI
        cleaned_content = clean_content_basic(content)
        
        if len(cleaned_content) < 100:
            print("⚠️ Technical transformation failed, using original content")
            return content
        
        print(f"✅ Applied technical transformation for onboarding")
        return cleaned_content
        
    except Exception as e:
        print(f"⚠️ Technical transformation failed: {str(e)}")
        return content

def apply_procedural_transformation(content, training_context):
    """
    Transform procedural content into onboarding material using simple methods
    """
    try:
        # Use simple content cleaning instead of AI
        cleaned_content = clean_content_basic(content)
        
        if len(cleaned_content) < 100:
            print("⚠️ Procedural transformation failed, using original content")
            return content
        
        print(f"✅ Applied procedural transformation for onboarding")
        return cleaned_content
        
    except Exception as e:
        print(f"⚠️ Procedural transformation failed: {str(e)}")
        return content

def apply_conservative_transformation(content, training_context):
    """
    Apply minimal transformation to preserve original training content using simple methods
    """
    try:
        # Use simple content cleaning instead of AI
        cleaned_content = clean_content_basic(content)
        
        if len(cleaned_content) < 100:
            print("⚠️ Conservative transformation failed, using original content")
            return content
        
        print(f"✅ Applied conservative transformation, preserved original content")
        return cleaned_content
        
    except Exception as e:
        print(f"⚠️ Conservative transformation failed: {str(e)}")
        return content

def apply_comprehensive_transformation(content, training_context):
    """
    Apply comprehensive transformation for unstructured content using Gemini API
    """
    try:
        if not model:
            # Fallback to basic transformation if no API key
            cleaned_content = clean_content_basic(content)
            
            if len(cleaned_content) < 100:
                print(f"⚠️ Content too short after cleaning")
                return None
            
            # Check if content has relevant training information
            training_keywords = get_training_keywords(training_context)
            content_lower = cleaned_content.lower()
            
            # Count keyword matches
            keyword_matches = sum(1 for keyword in training_keywords if keyword in content_lower)
            
            if keyword_matches >= 2:  # At least 2 keyword matches
                print(f"✅ Content has relevant training information ({keyword_matches} keywords)")
                return cleaned_content
            else:
                print(f"⚠️ No relevant content found for transformation")
                return None
        
        # Use Gemini API for comprehensive transformation
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        primary_goals = training_context.get('primary_goals', '')
        
        prompt = f"""
        Transform this unstructured content into professional training material.
        
        Original Content:
        {content[:3000]}
        
        Training Context:
        - Type: {training_type}
        - Target Audience: {target_audience}
        - Industry: {industry}
        - Primary Goals: {primary_goals}
        
        REQUIREMENTS:
        1. Extract and structure training-relevant information
        2. Remove conversational elements and informal language
        3. Convert to professional training format
        4. Organize into clear sections with headings
        5. Focus on actionable training content
        6. Make it suitable for {target_audience} in {industry}
        7. Align with training goals: {primary_goals}
        8. Preserve important technical information and procedures
        
        If the content contains valuable training information, transform it into professional training material.
        If the content is not suitable for training, return "NO_TRAINING_CONTENT".
        
        Return the transformed professional training content or "NO_TRAINING_CONTENT".
        """
        
        response = model.generate_content(prompt)
        transformed_content = response.text.strip()
        
        # Check if Gemini determined there's no training content
        if "NO_TRAINING_CONTENT" in transformed_content.upper():
            print(f"⚠️ No relevant training content found")
            return None
        
        # Ensure we have meaningful content
        if len(transformed_content) < 100:
            print(f"⚠️ Transformed content too short")
            return None
        
        print(f"✅ Content transformed using Gemini API")
        return transformed_content
            
    except Exception as e:
        print(f"⚠️ Comprehensive transformation failed: {str(e)}")
        return None

def extract_training_information_from_content(content, training_context):
    """
    Extract training-relevant information from content using simple methods
    Focus on actual file content and training goals
    """
    try:
        print(f"🔍 **Extracting training information from content**")
        print(f"📄 Content length: {len(content)} characters")
        print(f"🎯 Training goals: {training_context.get('primary_goals', 'Not specified')}")
        
        # Get training goals for content analysis
        primary_goals = training_context.get('primary_goals', '')
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        
        print(f"📋 Training type: {training_type}")
        print(f"👥 Target audience: {target_audience}")
        print(f"🏢 Industry: {industry}")
        
        # First, try to extract and transform any relevant content
        transformed_content = extract_and_transform_content(content, training_context)
        
        if not transformed_content:
            print("⚠️ No transformed content available, using original content")
            transformed_content = content
        
        # Use training goals to generate relevant keywords
        relevant_keywords = get_training_keywords_from_goals(training_context)
        
        print(f"🎯 **Keywords from training goals:** {relevant_keywords[:10]}...")
        
        # Extract sentences that match training goals
        training_sentences = extract_goal_aligned_sentences(transformed_content, training_context)
        
        # If no goal-aligned sentences, try broader extraction
        if not training_sentences:
            print("🔄 No goal-aligned sentences found, trying broader content extraction...")
            training_sentences = extract_broader_training_content(transformed_content, training_context)
        
        # If still no sentences, use the original content
        if not training_sentences:
            print("🔄 No training sentences found, using original content sections...")
            training_sentences = extract_content_sections(transformed_content)
        
        print(f"📄 **Training sentences extracted:** {len(training_sentences)}")
        
        # Group related sentences into training sections
        training_sections = group_sentences_basic(training_sentences)
        
        print(f"📚 **Training sections created:** {len(training_sections)}")
        
        return training_sections
        
    except Exception as e:
        print(f"⚠️ Training information extraction failed: {str(e)}")
        # Fallback to basic extraction
        return extract_training_information_basic(content, training_context)

def get_training_keywords_from_goals(training_context):
    """
    Generate keywords based on training goals and context
    """
    try:
        primary_goals = training_context.get('primary_goals', '').lower()
        training_type = training_context.get('training_type', '').lower()
        target_audience = training_context.get('target_audience', '').lower()
        industry = training_context.get('industry', '').lower()
        
        keywords = []
        
        # Extract keywords from primary goals
        if primary_goals:
            goal_words = [word for word in primary_goals.split() 
                         if len(word) >= 4 and word not in ['the', 'and', 'for', 'with', 'that', 'this', 'how', 'what', 'when', 'where', 'why']]
            keywords.extend(goal_words)
        
        # Add context-specific keywords
        if 'bridge' in primary_goals or 'fabrication' in primary_goals:
            keywords.extend(['bridge', 'fabrication', 'welding', 'steel', 'construction', 'assembly'])
        
        if 'process' in training_type:
            keywords.extend(['process', 'procedure', 'workflow', 'method', 'technique'])
        
        if 'safety' in training_type or 'safety' in primary_goals:
            keywords.extend(['safety', 'ppe', 'protective', 'hazard', 'risk'])
        
        if 'quality' in training_type or 'quality' in primary_goals:
            keywords.extend(['quality', 'inspection', 'testing', 'verification', 'standard'])
        
        if 'manufacturing' in industry:
            keywords.extend(['manufacturing', 'production', 'assembly', 'equipment', 'tool'])
        
        if 'transportation' in industry:
            keywords.extend(['transportation', 'logistics', 'delivery', 'routing', 'fleet'])
        
        # Add general training keywords
        keywords.extend(['training', 'learning', 'skill', 'knowledge', 'competency'])
        
        # Remove duplicates and limit
        unique_keywords = list(set(keywords))
        return unique_keywords[:20]
        
    except Exception as e:
        print(f"⚠️ Keyword generation failed: {str(e)}")
        return ['training', 'learning', 'skill', 'knowledge']

def extract_goal_aligned_sentences(content, training_context):
    """
    Extract sentences that align with training goals
    """
    try:
        primary_goals = training_context.get('primary_goals', '').lower()
        keywords = get_training_keywords_from_goals(training_context)
        
        sentences = re.split(r'[.!?]+', content)
        aligned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Minimum sentence length
                sentence_lower = sentence.lower()
                
                # Check if sentence contains goal-related keywords
                keyword_matches = sum(1 for keyword in keywords if keyword in sentence_lower)
                
                # Accept if it has keyword matches OR contains goal-related content
                if keyword_matches >= 1:
                    aligned_sentences.append(sentence)
                elif primary_goals and any(goal_word in sentence_lower for goal_word in primary_goals.split()):
                    aligned_sentences.append(sentence)
                # Also accept substantial sentences that might contain valuable info
                elif len(sentence) > 50:
                    aligned_sentences.append(sentence)
        
        return aligned_sentences
        
    except Exception as e:
        print(f"⚠️ Goal-aligned extraction failed: {str(e)}")
        return []

def extract_content_sections(content):
    """
    Extract content sections when no training-specific content is found
    """
    try:
        sentences = re.split(r'[.!?]+', content)
        content_sections = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30:  # Accept substantial sentences
                content_sections.append(sentence)
        
        return content_sections
        
    except Exception as e:
        print(f"⚠️ Content section extraction failed: {str(e)}")
        return []

def extract_broader_training_content(content, training_context):
    """
    Extract training content more broadly when keyword matching fails
    """
    try:
        sentences = re.split(r'[.!?]+', content)
        training_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Minimum sentence length
                # Accept sentences that contain training-related concepts
                sentence_lower = sentence.lower()
                
                # Check for training-related patterns
                training_patterns = [
                    'process', 'procedure', 'workflow', 'method', 'technique',
                    'safety', 'quality', 'inspection', 'testing', 'verification',
                    'equipment', 'tool', 'operation', 'maintenance', 'calibration',
                    'material', 'handling', 'storage', 'transportation',
                    'documentation', 'record', 'report', 'form', 'checklist',
                    'standard', 'specification', 'requirement', 'guideline',
                    'training', 'learning', 'skill', 'knowledge', 'competency'
                ]
                
                # Accept if sentence contains any training pattern
                if any(pattern in sentence_lower for pattern in training_patterns):
                    training_sentences.append(sentence)
                # Also accept substantial sentences (they might contain valuable info)
                elif len(sentence) > 50:
                    training_sentences.append(sentence)
        
        return training_sentences
        
    except Exception as e:
        print(f"⚠️ Broader content extraction failed: {str(e)}")
        return []

def generate_dynamic_keywords(content, training_context):
    """
    Use AI to dynamically generate relevant keywords based on content and training context
    """
    try:
        prompt = f"""
        Analyze this content and training context to generate relevant keywords for identifying training material.
        
        Content preview: {content[:2000]}
        
        Training Context:
        - Type: {training_context.get('training_type', 'General')}
        - Audience: {training_context.get('target_audience', 'Employees')}
        - Industry: {training_context.get('industry', 'General')}
        - Goals: {training_context.get('primary_goals', 'General training')}
        
        Generate 15-20 relevant keywords that would help identify training-relevant content from this material.
        Focus on:
        - Industry-specific terminology
        - Training-related concepts
        - Important procedures or policies
        - Key skills or competencies
        - Relevant standards or requirements
        
        Return as a JSON array: ["keyword1", "keyword2", "keyword3"]
        """
        
        if not model:
            return ['training', 'learning', 'skill', 'knowledge']
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            raw = str(response.text).strip()
        else:
            return ['training', 'learning', 'skill', 'knowledge']
        
        # Extract keywords from response
        keywords = extract_json_from_ai_response(raw)
        if keywords and isinstance(keywords, list):
            return keywords
        else:
            # Fallback: extract keywords from text
            import re
            keyword_matches = re.findall(r'"([^"]+)"', raw)
            return keyword_matches if keyword_matches else ['training', 'learning', 'skill', 'knowledge']
            
    except Exception as e:
        print(f"⚠️ Dynamic keyword generation failed: {str(e)}")
        return ['training', 'learning', 'skill', 'knowledge']

def ai_extract_training_sentences(content, keywords, training_context):
    """
    Use AI to identify training-relevant sentences from transformed content
    """
    try:
        prompt = f"""
        Identify training-relevant sentences from this transformed content based on the provided keywords and context.
        
        Keywords: {', '.join(keywords[:10])}
        
        Content: {content[:3000]}
        
        Training Context:
        - Type: {training_context.get('training_type', 'General')}
        - Industry: {training_context.get('industry', 'General')}
        
        CRITICAL: Extract ONLY sentences that contain valuable training information from the provided text.
        The content has already been transformed to professional training material, so focus on extracting the most relevant instructional content.
        
        Return only the training-relevant sentences from the content, one per line, without numbering or formatting.
        Focus on sentences that contain:
        - Instructional information, procedures, or workflows
        - Important concepts, skills, or competencies
        - Guidelines, standards, or requirements
        - Company-specific information or terminology
        - Safety information or best practices
        - Quality standards or operational procedures
        
        Prioritize sentences that would be most valuable for training purposes.
        """
        
        if not model:
            return extract_training_sentences_basic(content, keywords)
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            sentences = [s.strip() for s in str(response.text).split('\n') if s.strip() and len(s.strip()) > 30]
        else:
            return extract_training_sentences_basic(content, keywords)
        
        return sentences
        
    except Exception as e:
        print(f"⚠️ AI sentence extraction failed: {str(e)}")
        # Fallback to basic sentence extraction
        return extract_training_sentences_basic(content, keywords)

def ai_group_training_sections(sentences, training_context):
    """
    Use AI to group related sentences into cohesive training sections
    """
    try:
        if not sentences:
            return []
        
        # Join sentences for AI analysis
        content_text = '. '.join(sentences)
        
        prompt = f"""
        Group these training-related sentences into cohesive sections for {training_context.get('training_type', 'General')} training.
        
        Sentences: {content_text[:4000]}
        
        Training Context:
        - Type: {training_context.get('training_type', 'General')}
        - Industry: {training_context.get('industry', 'General')}
        
        Create 3-5 logical sections by grouping related sentences together.
        Each section should focus on a specific topic or skill area.
        
        Return as JSON array of sections:
        [
            {{
                "title": "Section title",
                "content": "Combined sentences for this section"
            }}
        ]
        """
        
        if not model:
            return group_sentences_basic(sentences)
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            sections_data = extract_json_from_ai_response(str(response.text))
        else:
            return group_sentences_basic(sentences)
        
        if sections_data and isinstance(sections_data, list):
            return [section.get('content', '') for section in sections_data if section.get('content')]
        else:
            # Fallback: simple grouping
            return group_sentences_basic(sentences)
            
    except Exception as e:
        print(f"⚠️ AI section grouping failed: {str(e)}")
        return group_sentences_basic(sentences)

def extract_training_information_basic(content, training_context):
    """
    Basic fallback for training information extraction
    """
    # Simple sentence splitting and filtering
    sentences = re.split(r'[.!?]+', content)
    training_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 50 and len(sentence) < 500:
            # Basic filtering
            if not any(conv in sentence.lower() for conv in ['um', 'uh', 'yeah', 'okay']):
                training_sentences.append(sentence)
    
    # Simple grouping
    return group_sentences_basic(training_sentences)

def extract_training_sentences_basic(content, keywords):
    """
    Basic fallback for sentence extraction
    """
    sentences = re.split(r'[.!?]+', content)
    relevant_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 30:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in keywords):
                relevant_sentences.append(sentence)
    
    return relevant_sentences

def group_sentences_basic(sentences):
    """
    Basic fallback for sentence grouping
    """
    if not sentences:
        return []
    
    # Simple grouping: 3 sentences per section
    sections = []
    current_section = []
    
    for sentence in sentences:
        current_section.append(sentence)
        if len(current_section) >= 3:
            sections.append('. '.join(current_section) + '.')
            current_section = []
    
    # Add remaining sentences
    if current_section:
        sections.append('. '.join(current_section) + '.')
    
    return sections

def extract_json_from_ai_response(raw_text):
    """
    Extract JSON from AI response with robust error handling
    """
    try:
        # Check if response is empty or None
        if not raw_text or not raw_text.strip():
            print("⚠️ Empty AI response received")
            return None
            
        # Clean up the response
        cleaned_text = raw_text.strip()
        
        # Remove markdown code blocks
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text.split('```', 1)[-1].strip()
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3].strip()
        
        # Remove JSON prefix if present
        if cleaned_text.startswith('json'):
            cleaned_text = cleaned_text[4:].strip()
        
        # Try to find JSON object/array
        import re
        
        # Look for JSON object
        start = cleaned_text.find('{')
        if start != -1:
            brace_count = 0
            end = start
            for i, char in enumerate(cleaned_text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            if end > start:
                json_str = cleaned_text[start:end]
                # Remove trailing commas
                json_str = re.sub(r',([ \t\r\n]*[\]}])', r'\1', json_str)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON decode error: {e}")
                    # Try to fix common JSON issues
                    json_str = re.sub(r'([^\\])"([^"]*)"([^\\])', r'\1"\2"\3', json_str)
                    try:
                        return json.loads(json_str)
                    except:
                        print(f"⚠️ JSON fix failed")
                        return None
        
        # Look for JSON array
        start = cleaned_text.find('[')
        if start != -1:
            bracket_count = 0
            end = start
            for i, char in enumerate(cleaned_text[start:], start):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end = i + 1
                        break
            if end > start:
                json_str = cleaned_text[start:end]
                # Remove trailing commas
                json_str = re.sub(r',([ \t\r\n]*[\]}])', r'\1', json_str)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON decode error: {e}")
                    # Try to fix common JSON issues
                    json_str = re.sub(r'([^\\])"([^"]*)"([^\\])', r'\1"\2"\3', json_str)
                    try:
                        return json.loads(json_str)
                    except:
                        print(f"⚠️ JSON fix failed")
                        return None
        
        # If no JSON found, try to extract simple list from text
        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
        if lines:
            # Try to extract simple list items
            items = []
            for line in lines:
                # Remove common prefixes
                line = re.sub(r'^[\d\-\.\s]+', '', line)
                if line and len(line) > 2:
                    items.append(line)
            if items:
                return items
        
        print(f"⚠️ No valid JSON found in response")
        return None
        
    except Exception as e:
        print(f"⚠️ JSON extraction failed: {str(e)}")
        return None

def extract_key_topics_from_content(content, max_topics=5):
    """
    Extract key topics from uploaded content using AI
    """
    try:
        if model is None:
            st.warning("Gemini API not available for topic extraction")
            return []
            
        if not content or len(content.strip()) < 50:
            return []
        
        # Use Gemini to extract key topics
        prompt = f"""
        Extract the top {max_topics} most important topics or concepts from this training content:
        
        {content[:2000]}
        
        Return only the topic names, separated by commas. Keep them short and relevant.
        """
        
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text') and response.text:
            topics = [topic.strip() for topic in str(response.text).split(',') if topic.strip()]
        else:
            topics = []
        return topics[:max_topics]
    except Exception as e:
        st.warning(f"Could not extract topics from content: {str(e)}")
        return []

def calculate_text_dimensions(text, max_width, max_height):
    """
    Calculate appropriate dimensions for text widgets based on content length
    """
    # Base dimensions
    base_width = 200
    base_height = 60
    
    # Adjust based on text length
    text_length = len(text)
    
    if text_length <= 30:
        width = base_width
        height = base_height
    elif text_length <= 60:
        width = base_width + 50
        height = base_height + 20
    elif text_length <= 100:
        width = base_width + 100
        height = base_height + 40
    else:
        width = base_width + 150
        height = base_height + 60
    
    # Ensure we don't exceed maximum dimensions
    width = min(width, max_width)
    height = min(height, max_height)
    
    return width, height

def gemini_generate_module_description(content: str) -> str:
    """
    Use Gemini to generate a grammatically correct, concise, and clear description for a module.
    """
    try:
        if not content or len(content.strip()) < 20:
            return "Module extracted from uploaded file."
        prompt = f"""
        Summarize the following training module content in 1-2 clear, grammatically correct sentences. The summary should be concise, legible, and suitable as a description for an onboarding module. Do not repeat the title. Do not use generic phrases like 'this module'.

        Content:
        {content[:2000]}
        """
        if not model:
            return "Module extracted from uploaded file."
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            desc = str(response.text).strip().replace('\n', ' ')
        else:
            return "Module extracted from uploaded file."
        return desc
    except Exception as e:
        st.warning(f"Could not generate module description: {str(e)}")
        return "Module extracted from uploaded file."

def gemini_group_modules_into_sections(modules):
    """
    Use Gemini to group modules into logical sections and generate section titles.
    modules: list of dicts with 'title' and 'content'.
    Returns: list of dicts: { 'section_title': str, 'module_indices': [int, ...] }
    """
    try:
        if not modules or len(modules) < 2:
            return [{ 'section_title': 'General', 'module_indices': list(range(len(modules))) }]
        module_list_str = "\n".join([f"{i+1}. {m['title']}: {m['content'][:100]}" for i, m in enumerate(modules)])
        prompt = f"""
        You are an expert instructional designer. Given the following list of onboarding modules (with their titles and a content excerpt), group them into logical sections for an onboarding program. For each section, provide a clear, descriptive section title and list the module numbers that belong in that section. Return the result as JSON in the format: [{{"section_title": str, "module_indices": [int, ...]}}].

        Modules:
        {module_list_str}
        """
        if not model:
            return [{ 'section_title': 'General', 'module_indices': list(range(len(modules))) }]
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            raw = str(response.text).strip()
        else:
            return [{ 'section_title': 'General', 'module_indices': list(range(len(modules))) }]
        if raw.startswith("```"):
            raw = raw.split("```", 1)[-1].strip()
        raw = raw.replace("'", '"')
        # Remove trailing commas before closing brackets
        raw = re.sub(r',([ \t\r\n]*[\]}])', r'\1', raw)
        # Fix unescaped double quotes in section titles (e.g., Manager"s -> Manager's)
        raw = re.sub(r'([A-Za-z])\"s', r"\1's", raw)
        # Extract the first JSON array
        match = re.search(r'(\[.*\])', raw, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = raw
        try:
            sections = json.loads(json_str)
            if isinstance(sections, list) and all('section_title' in s and 'module_indices' in s for s in sections):
                return sections
        except Exception as e:
            st.warning(f"Could not parse Gemini section grouping: {str(e)}\nRaw response:\n{json_str}")
            st.text_area("Raw Gemini Output (fix manually if needed):", value=json_str, height=200)
        return [{ 'section_title': 'General', 'module_indices': list(range(len(modules))) }]
    except Exception as e:
        st.warning(f"Could not group modules into sections: {str(e)}")
        return [{ 'section_title': 'General', 'module_indices': list(range(len(modules))) }]

def gemini_generate_complete_pathway(training_context, extracted_file_contents, file_inventory, bypass_filtering=False, preserve_original_content=False):
    """
    Generate AI-powered pathways using optimized Gemini agents for speed and quality
    Returns: dict with 'pathways': list of pathway dicts
    """
    try:
        import streamlit as st
        from modules.fast_ai_agents import OptimizedPathwayOrchestrator
        
        st.write("🚀 **Optimized AI Pathway Generation:**")
        st.write("• Using fast Gemini agents for optimal speed and quality")
        st.write("• Processing content with parallel optimization")
        
        # Initialize the optimized orchestrator
        orchestrator = OptimizedPathwayOrchestrator()
        
        # Generate pathways using optimized AI processing
        st.write("⚡ Generating pathways with optimized AI...")
        
        try:
            result = orchestrator.generate_optimized_pathways(
                extracted_file_contents, 
                training_context, 
                file_inventory
            )
            debug_print(f"✅ OptimizedPathwayOrchestrator returned: {type(result)} with {len(result.get('pathways', [])) if result else 0} pathways")
        except Exception as orchestrator_error:
            debug_print(f"❌ OptimizedPathwayOrchestrator failed: {str(orchestrator_error)}")
            st.write(f"⚠️ Optimized AI failed: {str(orchestrator_error)}")
            result = None
        
        if result and 'pathways' in result and result['pathways']:
            st.write(f"✅ **Optimized AI Success:** Generated {len(result['pathways'])} unique pathways in record time!")
            
            # Display pathway summary with content types
            for i, pathway in enumerate(result['pathways'], 1):
                sections_count = len(pathway.get('sections', []))
                modules_count = sum(len(section.get('modules', [])) for section in pathway.get('sections', []))
                
                # Count content types
                content_types = []
                for section in pathway.get('sections', []):
                    for module in section.get('modules', []):
                        content_type = module.get('content_type', 'text')
                        content_types.append(content_type)
                
                unique_types = list(set(content_types))
                st.write(f"   📚 Pathway {i}: **{pathway.get('pathway_name', 'Unknown')}**")
                st.write(f"      📊 {sections_count} sections, {modules_count} modules")
                st.write(f"      🎨 Content types: {', '.join(unique_types[:5])}")  # Show first 5 types
            
            # Validate and enhance pathway modules
            result = validate_and_enhance_pathway_modules(result, min_modules_per_section=6, min_sections_per_pathway=4, training_context=training_context)
            
            return result
        else:
            st.write("⚠️ Optimized AI generation failed, using fallback...")
            # Fallback to improved pathway generation
            return gemini_generate_complete_pathway_fallback(training_context, extracted_file_contents, file_inventory)
            
    except Exception as e:
        debug_print(f"❌ Optimized AI pathway generation failed: {str(e)}")
        st.write(f"⚠️ AI pathway generation error: {str(e)}")
        
        # Fallback to improved pathway generation
        return gemini_generate_complete_pathway_fallback(training_context, extracted_file_contents, file_inventory)

def gemini_generate_complete_pathway_fallback(training_context, extracted_file_contents, file_inventory):
    """
    Fallback pathway generation when AI agents are not available
    """
    try:
        import streamlit as st
        from modules.fast_ai_agents import FastPathwayAgent
        
        st.write("🔄 Using fallback pathway generation with basic AI agent...")
        
        # Use the FastPathwayAgent directly (without orchestrator)
        agent = FastPathwayAgent()
        result = agent.generate_complete_pathways_fast(
            extracted_file_contents, training_context, file_inventory
        )
        
        if result and 'pathways' in result and result['pathways']:
            st.write(f"✅ **Fallback Success:** Generated {len(result['pathways'])} pathways with content types")
            # Validate and enhance pathway modules
            result = validate_and_enhance_pathway_modules(result, min_modules_per_section=6, min_sections_per_pathway=4, training_context=training_context)
            return result
        else:
            st.write("⚠️ AI fallback failed, creating basic pathways...")
            # Create basic pathways with content types
            basic_pathways = create_basic_pathways_with_content_types(training_context, extracted_file_contents)
            result = {"pathways": basic_pathways}
            # Validate and enhance pathway modules
            result = validate_and_enhance_pathway_modules(result, min_modules_per_section=6, min_sections_per_pathway=4, training_context=training_context)
            return result
        
    except Exception as e:
        debug_print(f"❌ Fallback pathway generation failed: {str(e)}")
        st.write("⚠️ Creating emergency fallback pathways...")
        basic_pathways = create_basic_pathways_with_content_types(training_context, extracted_file_contents)
        result = {"pathways": basic_pathways}
        # Validate and enhance pathway modules
        result = validate_and_enhance_pathway_modules(result, training_context=training_context)
        return result

def create_basic_pathways_with_content_types(training_context, extracted_file_contents):
    """
    Create basic pathways with content types when all AI fails
    """
    industry = training_context.get('industry', 'Professional')
    audience = training_context.get('target_audience', 'Team Members')
    
    pathways = []
    files = list(extracted_file_contents.items())
    
    for i, (filename, content) in enumerate(files[:2]):
        base_name = filename.replace('.pdf', '').replace('.docx', '').replace('_', ' ').title()
        
        pathway = {
            "pathway_name": f"{base_name} Training Program",
            "description": f"Professional training based on {filename} for {audience}",
            "sections": [
                {
                    "title": f"{base_name} Fundamentals", 
                    "description": "Core concepts and procedures",
                    "modules": [
                        {
                            "title": f"{base_name} Overview",
                            "description": "Introduction to key concepts and fundamentals",
                            "content": f"This training module covers essential {base_name.lower()} concepts, procedures, and best practices for {audience.lower()}. Understanding these fundamentals is critical for success in your role and maintaining professional standards.",
                            "content_type": "text",
                            "content_data": {
                                "text": f"Comprehensive overview of {base_name.lower()} fundamentals including key concepts, procedures, and professional standards."
                            },
                            "learning_objectives": ["Understand core concepts", "Apply best practices", "Follow professional standards"],
                            "key_points": ["Core fundamentals", "Professional standards", "Best practices"],
                            "engagement_level": "medium",
                            "estimated_time": "15 minutes"
                        },
                        {
                            "title": f"{base_name} Procedures",
                            "description": "Step-by-step implementation procedures",
                            "content": f"Practical procedures for implementing {base_name.lower()} in your daily work. Follow established workflows, maintain professional standards, and ensure proper documentation.",
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
                            "title": f"{base_name} Assessment",
                            "description": "Knowledge verification and competency evaluation",
                            "content": f"Evaluate your understanding of {base_name.lower()} concepts, procedures, and best practices to ensure you meet professional competency standards.",
                            "content_type": "knowledge_check",
                            "content_data": {
                                "questions": [
                                    f"What are the key requirements for {base_name.lower()} in your role?",
                                    f"How should {base_name.lower()} activities be properly documented?"
                                ],
                                "answers": [
                                    "Follow all established procedures and maintain professional standards appropriate to your role",
                                    "Document activities clearly with appropriate detail and required approvals"
                                ]
                            },
                            "learning_objectives": ["Demonstrate understanding", "Apply knowledge effectively", "Meet competency standards"],
                            "key_points": ["Knowledge verification", "Competency validation", "Performance standards"],
                            "engagement_level": "high",
                            "estimated_time": "10 minutes"
                        }
                    ]
                }
            ]
        }
        pathways.append(pathway)
    
    return pathways

def extract_modules_from_file_content(filename, content, training_context, bypass_filtering=False, preserve_original_content=False):
    """
    Extract content from uploaded files that aligns with primary training goals.
    Focus on actual file content and training goals.
    """
    try:
        print(f"📄 **Extracting content from {filename}**")
        print(f"📄 Content length: {len(content)} characters")
        print(f"🎯 Training goals: {training_context.get('primary_goals', 'Not specified')}")
        
        if not content or len(content.strip()) < 50:
            print(f"⚠️ {filename} has insufficient content for extraction")
            return []
        
        # Get training goals for content analysis
        primary_goals = training_context.get('primary_goals', '')
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        
        print(f"📋 Training type: {training_type}")
        print(f"👥 Target audience: {target_audience}")
        print(f"🏢 Industry: {industry}")
        
        # Extract training-relevant information directly from content
        if preserve_original_content:
            # For structured content, preserve original with minimal processing
            training_info = [content] if content and len(content.strip()) > 100 else []
        else:
            # Use training goals to extract relevant content
            training_info = extract_training_information_from_content(content, training_context)
        
        if not training_info:
            print(f"⚠️ No training-relevant information found in {filename}")
            # Use original content as fallback
            print(f"🔄 Using original content as fallback")
            training_info = [content] if content and len(content.strip()) > 100 else []
        
        print(f"📄 **Training Information Extracted:** {len(training_info)} sections")
        
        modules = []
        
        # Get performance configuration
        config = get_parallel_config()
        max_modules = config.get('max_modules_per_file', 10)
        batch_ai_calls = config.get('batch_ai_calls', True)
        
        # Create modules from training-relevant information
        for i, info_section in enumerate(training_info[:max_modules]):  # Limit modules for speed
            if len(info_section.strip()) > 100:  # Minimum length for quality
                print(f"🔧 Creating module {i+1} from content section")
                print(f"📄 Section content length: {len(info_section)} characters")
                
                # Use AI-powered module creation with optimized approach
                cohesive_module = create_cohesive_module_content_optimized(info_section, training_context, i+1, batch_ai_calls)
                if cohesive_module:
                    modules.append({
                        'title': cohesive_module['title'],
                        'description': cohesive_module['description'],
                        'content': cohesive_module['content'],
                        'source': clean_source_field(f'Training information from {filename}'),
                        'key_points': extract_key_points_from_content(info_section, training_context),
                        'relevance_score': 0.9,  # High relevance since it's filtered and cohesive
                        'full_reason': f'Cohesive training content focused on {cohesive_module["core_topic"]}'
                    })
                    print(f"✅ Module {i+1} created successfully")
                else:
                    print(f"⚠️ Module {i+1} creation failed")
        
        print(f"✅ Extracted {len(modules)} cohesive training modules from {filename}")
        return modules
        
    except Exception as e:
        print(f"⚠️ Training content extraction failed for {filename}: {str(e)}")
        return []

def create_fast_module_content(content, training_context, module_number):
    """
    Create module content quickly without excessive AI calls
    """
    try:
        # First, validate that the content is actually meaningful
        if not is_meaningful_training_content(content, training_context):
            return None
        
        # Use simple, fast approach without multiple AI calls
        title = extract_first_sentence_title(content)
        description = f"Training content from uploaded file - Module {module_number}"
        
        # Clean content without AI calls
        cleaned_content = clean_content_basic(content)
        
        return {
            'title': f'Module {module_number}: {title}',
            'description': description,
            'content': cleaned_content,
            'core_topic': 'Training Content',
            'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge']
        }
            
    except Exception as e:
        print(f"⚠️ Fast module creation failed: {str(e)}")
        return None

def clean_content_basic(content):
    """
    Clean content without AI calls for speed
    """
    try:
        import re
        
        # Basic cleaning without AI
        cleaned = content.strip()
        
        # Remove common conversational elements
        conversational_elements = ['um', 'uh', 'yeah', 'okay', 'right', 'so', 'well', 'you know']
        for element in conversational_elements:
            pattern = re.escape(element)
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned if len(cleaned) > 50 else content
        
    except Exception as e:
        return content

def create_cohesive_module_content_optimized(content, training_context, module_number, batch_ai_calls=True):
    """
    Create cohesive title, description, and content that work together as a unit
    Focus on actual file content and training goals
    """
    try:
        print(f"🔧 **Creating module {module_number} from content**")
        print(f"📄 Content length: {len(content)} characters")
        print(f"🎯 Training goals: {training_context.get('primary_goals', 'Not specified')}")
        
        # First, validate that the content is actually meaningful
        if not is_meaningful_training_content(content, training_context):
            print(f"⚠️ Module {module_number}: Content not meaningful, using anyway")
        
        if not model:
            # Fallback to simple approach without AI
            title = extract_first_sentence_title(content)
            description = f"Training content from uploaded file - Module {module_number}"
            cleaned_content = clean_content_basic(content)
            
            return {
                'title': f'Module {module_number}: {title}',
                'description': description,
                'content': cleaned_content,
                'core_topic': 'Training Content',
                'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge']
            }
        
        # Use Gemini API to create better titles and descriptions
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        primary_goals = training_context.get('primary_goals', '')
        
        prompt = f"""
        Create a professional training module from this content.
        
        Content:
        {content[:2000]}
        
        Training Context:
        - Type: {training_type}
        - Target Audience: {target_audience}
        - Industry: {industry}
        - Primary Goals: {primary_goals}
        - Module Number: {module_number}
        
        REQUIREMENTS:
        1. Create a clear, professional title (max 60 characters) that reflects the actual content
        2. Write a concise description (1-2 sentences) that describes what the module covers
        3. Transform the content into professional training material
        4. Focus on actionable training information from the actual content
        5. Make it suitable for {target_audience} in {industry}
        6. Remove conversational elements and informal language
        7. Structure content with clear sections
        8. Extract and preserve important technical information and procedures
        9. Use the actual content, not generic placeholder text
        10. If the content contains specific procedures, processes, or technical information, highlight these
        11. Align with training goals: {primary_goals}
        
        Return as JSON:
        {{
            "title": "Professional module title based on actual content",
            "description": "Clear description of what this specific module covers",
            "content": "Transformed professional training content from the actual file"
        }}
        """
        
        if not model:
            # Fallback to simple approach without AI
            title = extract_first_sentence_title(content)
            description = f"Training content from uploaded file - Module {module_number}"
            cleaned_content = clean_content_basic(content)
            
            return {
                'title': f'Module {module_number}: {title}',
                'description': description,
                'content': cleaned_content,
                'core_topic': 'Training Content',
                'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge']
            }
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            raw = str(response.text).strip()
        else:
            # Fallback to simple approach when model fails
            title = extract_first_sentence_title(content)
            description = f"Training content from uploaded file - Module {module_number}"
            cleaned_content = clean_content_basic(content)
            
            return {
                'title': f'Module {module_number}: {title}',
                'description': description,
                'content': cleaned_content,
                'core_topic': 'Training Content',
                'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge']
            }
        
        # Extract JSON from response with better error handling
        module_data = extract_json_from_ai_response(raw)
        
        if module_data and isinstance(module_data, dict):
            title = module_data.get('title', f'Module {module_number}')
            description = module_data.get('description', f'Training content from uploaded file - Module {module_number}')
            transformed_content = module_data.get('content', content)
            
            # Validate the extracted data
            if not title or len(title.strip()) < 3:
                title = f'Module {module_number}'
            if not description or len(description.strip()) < 10:
                description = f'Training content from uploaded file - Module {module_number}'
            if not transformed_content or len(transformed_content.strip()) < 50:
                transformed_content = clean_content_basic(content)
            
            return {
                'title': f'Module {module_number}: {title}',
                'description': description,
                'content': transformed_content,
                'core_topic': 'Training Content',
                'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge']
            }
        else:
            # Fallback to simple approach when JSON parsing fails
            print(f"⚠️ Module {module_number}: JSON parsing failed, using fallback")
            title = extract_first_sentence_title(content)
            description = f"Training content from uploaded file - Module {module_number}"
            cleaned_content = clean_content_basic(content)
            
            return {
                'title': f'Module {module_number}: {title}',
                'description': description,
                'content': cleaned_content,
                'core_topic': 'Training Content',
                'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge']
            }
            
    except Exception as e:
        print(f"⚠️ Optimized module creation failed: {str(e)}")
        # Ultimate fallback
        try:
            title = extract_first_sentence_title(content)
            description = f"Training content from uploaded file - Module {module_number}"
            cleaned_content = clean_content_basic(content)
            
            return {
                'title': f'Module {module_number}: {title}',
                'description': description,
                'content': cleaned_content,
                'core_topic': 'Training Content',
                'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge']
            }
        except Exception as fallback_error:
            print(f"⚠️ Ultimate fallback also failed: {str(fallback_error)}")
            return None

def is_meaningful_training_content(content, training_context):
    """
    Validate that content is meaningful training content
    More lenient to preserve actual file content from meeting transcripts
    """
    try:
        if not content or len(content.strip()) < 20:  # Reduced minimum length
            return False
        
        content_lower = content.lower()
        
        # Check for training keywords (more lenient)
        training_keywords = get_training_keywords(training_context)
        keyword_matches = sum(1 for keyword in training_keywords if keyword in content_lower)
        
        # Accept content if it has keywords OR is substantial content
        if keyword_matches >= 1 or len(content) > 100:  # More lenient
            return True
        
        # Check for meaningful structure (more lenient)
        sentences = content.split('.')
        meaningful_sentences = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 15:  # Reduced minimum sentence length
                meaningful_sentences += 1
        
        # Accept if it has meaningful sentences OR is substantial content
        return meaningful_sentences >= 1 or len(content) > 80  # More lenient
        
    except Exception as e:
        # If validation fails, accept the content to preserve file content
        return True

def create_cohesive_module_content_batched(content, training_context, module_number):
    """
    Create cohesive module content using universal approach
    Works with ANY subject matter and content type
    """
    import re  # Import at function level to avoid scope issues
    
    try:
        # Validate that we have actual content to work with
        if not content or len(content.strip()) < 50:
            print(f"⚠️ Module {module_number}: Insufficient content for processing")
            return None
        
        # Universal content analysis
        content_type = detect_content_type(content)
        print(f"🔍 **Universal Module Creation:**")
        print(f"   Module {module_number}: {content_type} content")
        print(f"   Content length: {len(content)} characters")
        
        # Use simple, fast approach without complex AI calls
        title = extract_first_sentence_title(content)
        description = f"Training content from uploaded file - Module {module_number}"
        
        # Clean content without AI calls for speed
        cleaned_content = clean_content_basic(content)
        
        return {
            'title': f'Module {module_number}: {title}',
            'description': description,
            'content': cleaned_content,
            'core_topic': 'Training Content',
            'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge']
        }
        
    except Exception as e:
        print(f"⚠️ Universal module creation failed: {str(e)}")
        return create_cohesive_module_content_individual(content, training_context, module_number)

def create_cohesive_module_content_individual(content, training_context, module_number):
    """
    Create cohesive module content using individual AI calls (original method)
    """
    try:
        # Extract the core topic from content
        core_topic = extract_core_topic(content, training_context)
        
        # Create cohesive title
        title = create_cohesive_title(content, core_topic, training_context, module_number)
        
        # Create cohesive description
        description = create_cohesive_description(content, core_topic, training_context)
        
        # Transform conversational content into professional training content
        professional_content = transform_conversational_to_professional(content, core_topic, training_context)
        
        return {
            'title': title,
            'description': description,
            'content': professional_content,
            'core_topic': core_topic
        }
        
    except Exception as e:
        print(f"⚠️ Cohesive module creation failed: {str(e)}")
        return None

def extract_core_topic(content, training_context):
    """
    Extract the core topic from content for cohesive module creation
    """
    try:
        content_lower = content.lower()
        training_type = training_context.get('training_type', '').lower()
        
        # Define topic categories
        topics = {
            'safety': ['safety', 'ppe', 'protective', 'emergency', 'hazard', 'risk'],
            'quality': ['quality', 'inspection', 'standard', 'specification', 'verification'],
            'process': ['process', 'procedure', 'workflow', 'step', 'sequence', 'method'],
            'equipment': ['equipment', 'tool', 'operation', 'maintenance', 'calibration'],
            'material': ['material', 'fabrication', 'assembly', 'welding', 'cutting'],
            'documentation': ['documentation', 'record', 'report', 'form', 'checklist']
        }
        
        # Find the most prominent topic
        topic_scores = {}
        for topic, keywords in topics.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            topic_scores[topic] = score
        
        # Get the topic with highest score
        if topic_scores:
            try:
                primary_topic = max(topic_scores.keys(), key=lambda k: topic_scores[k])
                if topic_scores[primary_topic] > 0:
                    return primary_topic
            except Exception as e:
                print(f"⚠️ Error finding primary topic: {e}")
                return 'general'
        
        # Fallback based on training type
        if 'safety' in training_type:
            return 'safety'
        elif 'quality' in training_type:
            return 'quality'
        elif 'process' in training_type:
            return 'process'
        else:
            return 'general'
            
    except Exception as e:
        return 'general'

def create_cohesive_title(content, core_topic, training_context, module_number):
    """
    Create a cohesive title that reflects the core topic and content
    """
    try:
        import hashlib
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Create topic-specific titles
        topic_titles = {
            'safety': f"Safety Procedures for {target_audience.title()}",
            'quality': f"Quality Control and Inspection",
            'process': f"Process and Workflow Management",
            'equipment': f"Equipment Operation and Maintenance",
            'material': f"Material Handling and Fabrication",
            'documentation': f"Documentation and Record Keeping"
        }
        
        base_title = topic_titles.get(core_topic, f"{training_type} Procedures")
        
        # Add specific identifier
        specific_identifier = extract_specific_identifier(content)
        if specific_identifier:
            title = f"{base_title}: {specific_identifier}"
        else:
            title = f"{base_title} - Module {module_number}"
        
        # Add hash for uniqueness
        return f"{title} [{content_hash[:4]}]"
        
    except Exception as e:
        return f"Training Module {module_number}"

def create_cohesive_description(content, core_topic, training_context):
    """
    Create a cohesive description that matches the title and content, making each module unique
    """
    try:
        import hashlib
        target_audience = training_context.get('target_audience', 'employees')
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Extract specific content details for uniqueness
        specific_phrases = extract_specific_phrases_from_content(content)
        specific_procedures = extract_specific_procedures(content)
        meaningful_snippet = extract_meaningful_content_snippet(content)
        
        # Create content-specific description approaches
        description_approaches = []
        
        # Approach 1: Use specific procedures if available
        if specific_procedures:
            procedure_desc = f"Focuses on {specific_procedures[0]} procedures"
            if meaningful_snippet:
                procedure_desc += f". Example: {meaningful_snippet[:60]}..."
            description_approaches.append(procedure_desc)
        
        # Approach 2: Use specific phrases if available
        if specific_phrases:
            phrase_desc = f"Covers {specific_phrases[0]} techniques and methods"
            if len(specific_phrases) > 1:
                phrase_desc += f" including {specific_phrases[1]}"
            description_approaches.append(phrase_desc)
        
        # Approach 3: Use meaningful snippet with context
        if meaningful_snippet and len(meaningful_snippet) > 30:
            snippet_desc = f"Addresses {meaningful_snippet[:80]}..."
            description_approaches.append(snippet_desc)
        
        # Approach 4: Use core topic with specific content details
        topic_descriptions = {
            'safety': f"Essential safety procedures for {target_audience}",
            'quality': f"Quality control and inspection processes",
            'process': f"Workflow management and process optimization",
            'equipment': f"Equipment operation and maintenance procedures",
            'material': f"Material handling and fabrication techniques",
            'documentation': f"Documentation and record keeping procedures"
        }
        
        base_topic_desc = topic_descriptions.get(core_topic, f"Training content for {target_audience}")
        
        # Add specific content details to base topic
        if specific_phrases:
            topic_desc = f"{base_topic_desc} with focus on {specific_phrases[0]}"
        elif specific_procedures:
            topic_desc = f"{base_topic_desc} covering {specific_procedures[0]}"
        else:
            topic_desc = base_topic_desc
        
        description_approaches.append(topic_desc)
        
        # Approach 5: Use content length and complexity indicators
        content_words = content.split()
        if len(content_words) > 100:
            complexity_desc = f"Comprehensive training covering multiple aspects of {core_topic} procedures"
        elif len(content_words) > 50:
            complexity_desc = f"Focused training on key {core_topic} procedures"
        else:
            complexity_desc = f"Essential {core_topic} training for {target_audience}"
        
        description_approaches.append(complexity_desc)
        
        # Select the best approach based on content hash for variety
        approach_index = int(content_hash[:2], 16) % len(description_approaches)
        selected_description = description_approaches[approach_index]
        
        # Add unique identifier to ensure uniqueness
        unique_suffix = f" [{content_hash[:4]}]"
        
        return f"{selected_description}{unique_suffix}"
        
    except Exception as e:
        return f"Training content for {training_context.get('target_audience', 'employees')}."

def transform_conversational_to_professional(content, core_topic, training_context):
    """
    Transform conversational content into professional training material using Gemini API
    """
    try:
        if not model:
            # Fallback to basic transformation if no API key
            return transform_conversational_basic(content, core_topic, training_context)
        
        # Use Gemini to transform conversational content into professional training material
        training_type = training_context.get('training_type', 'Process Training')
        target_audience = training_context.get('target_audience', 'fabricators')
        industry = training_context.get('industry', 'manufacturing')
        
        prompt = f"""
        Transform this conversational meeting content into professional training material.
        
        Original Content:
        {content[:3000]}
        
        Training Context:
        - Type: {training_type}
        - Target Audience: {target_audience}
        - Industry: {industry}
        - Core Topic: {core_topic}
        
        REQUIREMENTS:
        1. Remove all conversational elements (um, uh, yeah, okay, etc.)
        2. Convert informal language to professional training language
        3. Extract and structure actual training content
        4. Organize into clear sections with headings
        5. Focus on actionable training information
        6. Make it suitable for {target_audience} in {industry}
        7. Preserve important technical information and procedures
        8. Add professional formatting and structure
        
        Return the transformed professional training content.
        """
        
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            professional_content = str(response.text).strip()
        else:
            return transform_conversational_basic(content, core_topic, training_context)
        
        # Ensure we have meaningful content
        if len(professional_content) < 100:
            return transform_conversational_basic(content, core_topic, training_context)
        
        return professional_content
        
    except Exception as e:
        print(f"⚠️ Gemini conversational transformation failed: {str(e)}")
        # Fallback to basic transformation
        return transform_conversational_basic(content, core_topic, training_context)

def transform_conversational_basic(content, core_topic, training_context):
    """
    Basic transformation when AI is not available
    """
    try:
        import re
        
        # Clean up conversational elements
        content_clean = content.strip()
        
        # Use AI to dynamically identify and remove conversational elements
        conversational_elements = ai_identify_conversational_elements(content_clean)
        
        # Remove identified conversational elements
        for element in conversational_elements:
            import re
            pattern = re.escape(element)
            content_clean = re.sub(pattern, '', content_clean, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and punctuation
        content_clean = re.sub(r'\s+', ' ', content_clean)
        content_clean = re.sub(r'[.!?]+', '.', content_clean)
        content_clean = content_clean.strip()
        
        # If content is too short after cleaning, use AI to generate professional content
        if len(content_clean) < 100:
            return generate_professional_content_from_topic(core_topic, training_context)
        
        # Transform the cleaned content into professional training language
        training_type = training_context.get('training_type', 'Process Training')
        target_audience = training_context.get('target_audience', 'fabricators')
        industry = training_context.get('industry', 'manufacturing')
        
        professional_content = f"""
Module Overview: {core_topic.title()} in {industry.title()}

In this module, we'll focus on {core_topic.lower()} and its importance in {industry} processes.

{content_clean}

This training is essential for {training_type.lower()} and helps ensure proper {core_topic.lower()} procedures are followed by {target_audience} in {industry} environments.
"""
        
        return professional_content.strip()
        
    except Exception as e:
        # Fallback to generating professional content from topic
        return generate_professional_content_from_topic(core_topic, training_context)

def generate_professional_content_from_topic(core_topic, training_context):
    """
    Generate professional training content from topic when conversational content is insufficient
    """
    try:
        training_type = training_context.get('training_type', 'Process Training')
        target_audience = training_context.get('target_audience', 'fabricators')
        industry = training_context.get('industry', 'manufacturing')
        
        professional_content = f"""
In this module, we'll walk through the {core_topic.lower()} process step-by-step.

**Overview:**
{core_topic} is a critical component of {training_type.lower()} in {industry}. This module provides comprehensive training for {target_audience} to understand and execute {core_topic.lower()} procedures effectively.

**Learning Objectives:**
- Understand the fundamentals of {core_topic.lower()}
- Learn proper procedures and best practices
- Identify potential challenges and solutions
- Apply knowledge in real-world scenarios

**Key Components:**
The {core_topic.lower()} process involves several key steps that must be followed in sequence to ensure quality and safety standards are met.
"""
        
        return professional_content.strip()
        
    except Exception as e:
        return f"Professional training content for {core_topic}."

def extract_specific_identifier(content):
    """
    Extract a specific identifier from content using AI-driven approach
    """
    try:
        # Use AI to identify the most relevant technical term
        technical_terms = extract_ai_driven_terminology(content, {}, "technical")
        if technical_terms:
            return technical_terms[0].title()
        
        # Fallback to basic extraction
        basic_terms = extract_basic_terminology(content, {}, "technical")
        if basic_terms:
            return basic_terms[0].title()
        
        return None
        
    except Exception as e:
        return None

def extract_specific_phrases_from_content(content):
    """
    Extract specific phrases from content using AI-driven approach
    """
    try:
        # Use AI to extract relevant phrases
        phrases = extract_ai_driven_terminology(content, {}, "all")
        if phrases:
            return phrases[:4]
        
        # Fallback to basic extraction
        return extract_basic_terminology(content, {}, "all")[:4]
        
    except Exception as e:
        return []

def extract_specific_procedures(content, training_context=None):
    """
    Extract specific procedures from content using AI
    """
    try:
        # Use AI to extract process elements (which include procedures)
        if not training_context:
            training_context = {'industry': 'general', 'training_type': 'Training'}
        
        procedures = ai_extract_process_elements(content, training_context)
        
        if procedures:
            return procedures[:3]  # Return top 3
        
        return []
        
    except Exception as e:
        return []

def extract_meaningful_content_snippet(content, training_context=None):
    """
    Extract a meaningful snippet from content using AI
    """
    try:
        # Use AI to extract meaningful content
        if not training_context:
            training_context = {'industry': 'general', 'training_type': 'Training'}
        
        meaningful_content = ai_extract_meaningful_content(content, training_context)
        
        if meaningful_content and len(meaningful_content) > 50:
            return meaningful_content
        
        # Simple fallback to first substantial sentence
        sentences = content.split('.')
        for sentence in sentences:
            if len(sentence.strip()) > 20:
                return sentence.strip()
        
        return content[:100] + "..." if len(content) > 100 else content
        
    except Exception as e:
        return content[:100] + "..." if len(content) > 100 else content

def extract_first_sentence_title(content):
    """
    Extract a title from the first meaningful sentence of content
    """
    try:
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and len(sentence) < 100:
                # Clean up the sentence
                sentence = re.sub(r'^\w+:\s*', '', sentence)  # Remove speaker prefixes
                sentence = sentence.strip()
                
                if len(sentence) > 10:
                    return sentence[:60] + "..." if len(sentence) > 60 else sentence
        
        # Fallback: use first 50 characters
        return content[:50] + "..." if len(content) > 50 else content
        
    except Exception as e:
        return "Training Content"

def clean_source_field(source):
    """
    Clean the source field to ensure it's a proper string without character splitting
    """
    if isinstance(source, str):
        # If it's already a string, return as is
        return source
    elif isinstance(source, (list, tuple)):
        # If it's a list/tuple of characters, join them
        return ''.join(source)
    else:
        # Convert to string
        return str(source)

def extract_key_points_from_content(content, training_context):
    """
    Extract key learning points from content based on training goals
    """
    try:
        content_lower = content.lower()
        key_points = []
        
        # Look for specific training-related terms
        if any(word in content_lower for word in ['safety', 'ppe', 'protective']):
            key_points.extend(['Safety Procedures', 'Personal Protective Equipment', 'Hazard Identification'])
        if any(word in content_lower for word in ['quality', 'inspection', 'standard']):
            key_points.extend(['Quality Control', 'Inspection Procedures', 'Quality Standards'])
        if any(word in content_lower for word in ['process', 'procedure', 'workflow']):
            key_points.extend(['Process Procedures', 'Workflow Management', 'Process Optimization'])
        if any(word in content_lower for word in ['equipment', 'tool', 'operation']):
            key_points.extend(['Equipment Operation', 'Tool Usage', 'Maintenance Procedures'])
        if any(word in content_lower for word in ['material', 'handling', 'storage']):
            key_points.extend(['Material Handling', 'Storage Procedures', 'Transportation Safety'])
        if any(word in content_lower for word in ['documentation', 'record', 'report']):
            key_points.extend(['Documentation', 'Record Keeping', 'Reporting Procedures'])
        
        # Remove duplicates and limit
        unique_points = list(set(key_points))
        return unique_points[:5]
        
    except Exception as e:
        return []

def get_training_keywords(training_context):
    """
    Get training-relevant keywords using AI-driven approach
    """
    try:
        # Create a sample content from training context
        context_content = f"""
        Training goals: {training_context.get('primary_goals', '')}
        Training type: {training_context.get('training_type', '')}
        Target audience: {training_context.get('target_audience', '')}
        Industry: {training_context.get('industry', '')}
        Success metrics: {training_context.get('success_metrics', '')}
        """
        
        # Use AI to extract relevant keywords
        keywords = extract_ai_driven_terminology(context_content, training_context, "all")
        if keywords:
            return keywords[:30]
        
        # Fallback to basic extraction
        return extract_basic_terminology(context_content, training_context, "all")[:30]
        
    except Exception as e:
        # Ultimate fallback
        return [
            'process', 'procedure', 'workflow', 'system', 'method', 'technique',
            'quality', 'safety', 'compliance', 'standard', 'specification',
            'inspection', 'testing', 'verification', 'documentation', 'record',
            'equipment', 'tool', 'material', 'resource', 'maintenance',
            'operation', 'installation', 'configuration', 'calibration',
            'training', 'learning', 'skill', 'knowledge', 'competency'
        ]

def extract_ai_driven_terminology(content, training_context, terminology_type="all"):
    """
    Use AI to dynamically extract relevant terminology from content and context
    Replaces hardcoded lists of technical terms, action words, and industry terms
    
    Args:
        content: The content to analyze
        training_context: Training context for relevance
        terminology_type: "technical", "action", "industry", or "all"
    
    Returns:
        List of relevant terms/phrases
    """
    try:
        if not model:
            # Fallback to basic extraction if no API key
            return extract_basic_terminology(content, training_context, terminology_type)
        
        # Create context-aware prompt
        training_goals = training_context.get('primary_goals', '')
        training_type = training_context.get('training_type', '')
        target_audience = training_context.get('target_audience', '')
        industry = training_context.get('industry', '')
        
        prompt = f"""
        Analyze the following content and extract relevant terminology for training purposes.
        
        Training Context:
        - Goals: {training_goals}
        - Type: {training_type}
        - Audience: {target_audience}
        - Industry: {industry}
        
        Content to analyze: {content[:2000]}...
        
        Extract {terminology_type} terminology that would be relevant for training modules.
        Focus on terms that are:
        1. Specific to the industry/domain
        2. Action-oriented for procedures
        3. Technical concepts that need explanation
        4. Relevant to the training goals
        
        Return only the terms/phrases, one per line, without explanations.
        Limit to 10-15 most relevant terms.
        """
        
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text') and response.text:
            # Parse the response into a list of terms
            terms = [term.strip() for term in str(response.text).split('\n') if term.strip()]
            # Clean up any AI formatting artifacts
            cleaned_terms = []
            for term in terms:
                # Remove numbering, bullets, etc.
                term = re.sub(r'^[\d\-\.\s]+', '', term)
                if term and len(term) > 2:
                    cleaned_terms.append(term)
            return cleaned_terms[:15]  # Limit to 15 terms
        
        return []
        
    except Exception as e:
        print(f"AI terminology extraction failed: {e}")
        # Fallback to basic extraction
        return extract_basic_terminology(content, training_context, terminology_type)

def extract_basic_terminology(content, training_context, terminology_type="all"):
    """
    Basic fallback terminology extraction when AI is not available
    Uses simple pattern matching and context awareness
    """
    try:
        content_lower = content.lower()
        terms = []
        
        # Extract from training context
        if training_context.get('primary_goals'):
            goal_words = [word for word in training_context['primary_goals'].lower().split() 
                         if len(word) >= 4 and word not in ['the', 'and', 'for', 'with', 'that', 'this']]
            terms.extend(goal_words)
        
        # Extract from content using basic patterns
        sentences = content.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Look for technical/procedural patterns
            if any(word in sentence_lower for word in ['procedure', 'process', 'method', 'technique', 'system']):
                # Extract noun phrases around these words
                words = sentence.split()
                for i, word in enumerate(words):
                    if any(tech in word.lower() for tech in ['procedure', 'process', 'method', 'technique', 'system']):
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        phrase = ' '.join(words[start:end])
                        if len(phrase) > 5 and len(phrase) < 50:
                            terms.append(phrase.strip())
                        break
            
            # Look for action words
            action_patterns = ['check', 'verify', 'inspect', 'test', 'measure', 'assemble', 'install', 'configure']
            for action in action_patterns:
                if action in sentence_lower:
                    # Extract the action phrase
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if action in word.lower():
                            start = max(0, i-1)
                            end = min(len(words), i+2)
                            phrase = ' '.join(words[start:end])
                            if len(phrase) > 3 and len(phrase) < 40:
                                terms.append(phrase.strip())
                            break
        
        # Remove duplicates and limit
        unique_terms = list(set(terms))
        return unique_terms[:10]
        
    except Exception as e:
        return []

def ai_enhanced_content_cleaning(content, training_context):
    """
    Enhanced AI-powered content cleaning with Gemini API
    """
    try:
        if not content or len(content.strip()) < 50:
            return content
        
        if not model:
            # Fallback to basic cleaning if no API key
            return clean_content_basic(content)
        
        # Use Gemini to clean and transform content
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        
        prompt = f"""
        Clean and transform this content into professional training material.
        
        Original Content:
        {content[:3000]}
        
        Training Context:
        - Type: {training_type}
        - Target Audience: {target_audience}
        - Industry: {industry}
        
        REQUIREMENTS:
        1. Remove all conversational elements (um, uh, yeah, okay, etc.)
        2. Remove personal anecdotes and off-topic comments
        3. Extract and preserve important training information
        4. Convert informal language to professional language
        5. Structure content with clear sections and headings
        6. Focus on actionable training content
        7. Make it suitable for {target_audience} in {industry}
        8. Preserve technical information and procedures
        
        Return the cleaned and transformed professional training content.
        """
        
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            cleaned_content = str(response.text).strip()
        else:
            return clean_content_basic(content)
        
        # Ensure we have meaningful content
        if len(cleaned_content) < 100:
            return clean_content_basic(content)
        
        return cleaned_content
        
    except Exception as e:
        print(f"⚠️ Gemini content cleaning failed: {str(e)}")
        return clean_content_basic(content)

def ai_identify_conversational_elements(content):
    """
    Use AI to identify specific conversational, informal, or filler elements that should be removed
    Industry-agnostic approach that works for any type of content
    """
    try:
        if not content or len(content.strip()) < 50:
            return []
        
        prompt = f"""
        Analyze this content and identify conversational, informal, or filler elements that should be removed for professional training material.
        
        Look for ANY of these types of elements:
        - Filler words and phrases (um, uh, yeah, okay, right, so, well, you know, etc.)
        - Informal greetings and closings (hello, goodbye, thanks, bye, see you, etc.)
        - Technical difficulties or meeting issues (can you hear me, is that working, etc.)
        - Casual or conversational language that's not instructional
        - Repetitive statements or redundant phrases
        - Personal references or off-topic comments
        - Questions directed at the audience or presenter
        - Apologies or excuses
        - Background noise references
        - Any other conversational elements that don't contribute to training content
        
        Content to analyze:
        {content[:2000]}
        
        Return a JSON list of specific phrases, words, or patterns to remove. Be comprehensive and include:
        - Exact phrases as they appear in the text
        - Individual filler words
        - Informal expressions
        - Any conversational elements that would make the content unprofessional
        
        Format: ["phrase1", "word2", "expression3", ...]
        
        Focus on elements that would make this unsuitable as professional training material.
        """
        
        if not model:
            return ['um', 'uh', 'yeah', 'okay', 'right', 'so', 'well', 'you know']
        response = model.generate_content(prompt)
        
        # Try to parse JSON response
        try:
            import json
            import re
            
            # Clean up the response to extract JSON
            text = response.text.strip()
            if text.startswith('```'):
                text = text.split('```', 1)[-1].strip()
            if text.endswith('```'):
                text = text[:-3].strip()
            
            # Remove JSON prefix if present
            if text.startswith('json'):
                text = text[4:].strip()
            
            patterns = json.loads(text)
            if isinstance(patterns, list):
                # Filter out empty strings and very short patterns
                filtered_patterns = [p for p in patterns if p and len(p.strip()) > 1]
                return filtered_patterns
        except Exception as json_error:
            print(f"⚠️ JSON parsing failed: {json_error}")
        
        # Fallback: extract patterns from text response using regex
        import re
        # Look for quoted strings
        quoted_patterns = re.findall(r'"([^"]+)"', response.text)
        # Look for patterns after colons or dashes
        list_patterns = re.findall(r'[-•]\s*([^\n]+)', response.text)
        # Look for patterns in brackets
        bracket_patterns = re.findall(r'\[([^\]]+)\]', response.text)
        
        all_patterns = quoted_patterns + list_patterns + bracket_patterns
        # Clean and filter patterns
        cleaned_patterns = []
        for pattern in all_patterns:
            pattern = pattern.strip()
            if pattern and len(pattern) > 1 and not pattern.isdigit():
                cleaned_patterns.append(pattern)
        
        return cleaned_patterns[:20]  # Limit to 20 patterns
        
    except Exception as e:
        print(f"⚠️ AI conversational element identification failed: {str(e)}")
        # Return basic fallback patterns
        return ['um', 'uh', 'yeah', 'okay', 'right', 'so', 'well', 'you know']

def ai_extract_process_elements(content, training_context):
    """
    Use AI to automatically identify and extract process elements from content
    """
    try:
        if not content or len(content.strip()) < 50:
            return []
        
        industry = training_context.get('industry', 'general')
        training_type = training_context.get('training_type', 'Training')
        
        prompt = f"""
        Analyze this content and identify process-related elements, procedures, and technical components.
        
        Content to analyze:
        {content[:2000]}
        
        Look for:
        - Processes and procedures mentioned
        - Technical components and systems
        - Workflow elements (procedures, methods, techniques, approaches)
        - Quality control and assurance processes
        - Safety procedures and requirements
        - Equipment, tools, and technologies mentioned
        - Materials, resources, and specifications
        - Key operational elements
        
        Return a JSON list of identified process elements, like:
        ["process1", "component2", "procedure3", "system4", "technique5"]
        """
        
        if not model:
            return []
        response = model.generate_content(prompt)
        
        try:
            import json
            
            # Clean up the response to extract JSON
            text = response.text.strip()
            if text.startswith('```'):
                text = text.split('```', 1)[-1].strip()
            if text.endswith('```'):
                text = text[:-3].strip()
            
            elements = json.loads(text)
            if isinstance(elements, list):
                return elements[:5]  # Return top 5 elements
        except:
            pass
        
        # Fallback: extract elements from text response
        import re
        elements = re.findall(r'"([^"]+)"', response.text)
        return elements[:5]
        
    except Exception as e:
        return []

def ai_extract_meaningful_content(content, training_context):
    """
    Use AI to identify and extract the most meaningful content snippets
    """
    try:
        if not content or len(content.strip()) < 50:
            return content[:100] + "..." if len(content) > 100 else content
        
        industry = training_context.get('industry', 'general')
        training_type = training_context.get('training_type', 'Training')
        
        prompt = f"""
        Analyze this content and identify the most meaningful and relevant snippets for training purposes.
        
        Content to analyze:
        {content[:3000]}
        
        Look for:
        - Processes and procedures
        - Technical specifications and requirements
        - Safety information and guidelines
        - Quality control and assurance procedures
        - Equipment operation and maintenance instructions
        - Resource handling and management procedures
        - Important concepts, definitions, and best practices
        - Compliance and regulatory requirements
        
        Return the most meaningful content snippet (100-200 words) that would be valuable for training.
        Focus on practical, actionable information.
        """
        
        if not model:
            return extract_meaningful_content_snippet(content)
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            meaningful_content = str(response.text).strip()
        else:
            return extract_meaningful_content_snippet(content)
        
        # Ensure we have reasonable content length
        if len(meaningful_content) < 50:
            return extract_meaningful_content_snippet(content)
        
        return meaningful_content
        
    except Exception as e:
        return extract_meaningful_content_snippet(content) 

def group_modules_into_multiple_pathways_parallel(modules, training_context, num_pathways=3, sections_per_pathway=6, modules_per_section=8):
    """
    Use parallel processing to group modules into multiple pathways using AI
    """
    try:
        if not modules:
            return []
        
        print(f"🚀 **Parallel AI Pathway Creation:** {len(modules)} modules → {num_pathways} pathways")
        
        # Get performance configuration
        config = get_parallel_config()
        max_workers = min(config['max_section_workers'], num_pathways)
        
        def create_single_pathway(pathway_index):
            """Create a single pathway using AI"""
            try:
                pathway_name = f"Pathway {pathway_index + 1}"
                
                # Calculate modules for this pathway
                start_idx = pathway_index * (len(modules) // num_pathways)
                end_idx = start_idx + (len(modules) // num_pathways)
                pathway_modules = modules[start_idx:end_idx]
                
                if not pathway_modules:
                    return None
                
                # Use AI to group modules into sections
                sections = group_modules_into_sections_ai(pathway_modules, training_context, sections_per_pathway, modules_per_section)
                
                return {
                    'pathway_name': pathway_name,
                    'sections': sections,
                    'module_count': len(pathway_modules)
                }
                
            except Exception as e:
                print(f"⚠️ Pathway {pathway_index + 1} creation failed: {str(e)}")
                return None
        
        # Create pathways in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_pathway = {executor.submit(create_single_pathway, i): i for i in range(num_pathways)}
            
            pathways = []
            for future in concurrent.futures.as_completed(future_to_pathway, timeout=config['timeout_seconds']):
                try:
                    pathway = future.result(timeout=60)
                    if pathway:
                        pathways.append(pathway)
                except Exception as e:
                    pathway_index = future_to_pathway[future]
                    print(f"⚠️ Pathway {pathway_index + 1} failed: {str(e)}")
        
        return pathways
        
    except Exception as e:
        print(f"⚠️ Parallel pathway creation failed: {str(e)}")
        return group_modules_into_multiple_pathways(modules, training_context, num_pathways, sections_per_pathway, modules_per_section)

def group_modules_into_multiple_pathways(modules, training_context, num_pathways=3, sections_per_pathway=6, modules_per_section=8):
    """
    Use AI to group modules into multiple pathways with sections
    """
    try:
        if not modules:
            return []
        
        print(f"🤖 **AI Pathway Creation:** {len(modules)} modules → {num_pathways} pathways")
        
        pathways = []
        
        for pathway_index in range(num_pathways):
            pathway_name = f"Pathway {pathway_index + 1}"
            
            # Calculate modules for this pathway
            start_idx = pathway_index * (len(modules) // num_pathways)
            end_idx = start_idx + (len(modules) // num_pathways)
            pathway_modules = modules[start_idx:end_idx]
            
            if not pathway_modules:
                continue
            
            # Use AI to group modules into sections
            sections = group_modules_into_sections_ai(pathway_modules, training_context, sections_per_pathway, modules_per_section)
            
            pathways.append({
                'pathway_name': pathway_name,
                'sections': sections,
                'module_count': len(pathway_modules)
            })
        
        return pathways
        
    except Exception as e:
        print(f"⚠️ AI pathway creation failed: {str(e)}")
        return create_fallback_pathways(modules, training_context)

def group_modules_into_sections_ai(modules, training_context, max_sections=6, max_modules_per_section=8):
    """
    Use AI to group modules into logical sections
    """
    try:
        if not modules:
            return []
        
        # Use existing AI grouping function
        sections_data = gemini_group_modules_into_sections(modules)
        
        # Convert to the expected format
        sections = []
        for section_data in sections_data[:max_sections]:
            section_title = section_data.get('section_title', 'General')
            module_indices = section_data.get('module_indices', [])
            
            # Get modules for this section
            section_modules = []
            for idx in module_indices[:max_modules_per_section]:
                if 0 <= idx < len(modules):
                    section_modules.append(modules[idx])
            
            if section_modules:
                sections.append({
                    'title': section_title,
                    'modules': section_modules
                })
        
        return sections
        
    except Exception as e:
        print(f"⚠️ AI section grouping failed: {str(e)}")
        return group_modules_into_sections_basic(modules, max_sections, max_modules_per_section)

def group_modules_into_sections_basic(modules, max_sections=6, max_modules_per_section=8):
    """
    Basic fallback for grouping modules into sections
    """
    try:
        if not modules:
            return []
        
        sections = []
        modules_per_section = max(1, len(modules) // max_sections)
        
        for i in range(0, len(modules), modules_per_section):
            if len(sections) >= max_sections:
                break
            
            section_modules = modules[i:i + modules_per_section]
            if section_modules:
                sections.append({
                    'title': f'Section {len(sections) + 1}',
                    'modules': section_modules
                })
        
        return sections
        
    except Exception as e:
        print(f"⚠️ Basic section grouping failed: {str(e)}")
        return []

def create_fallback_pathways(modules, training_context):
    """
    Create universal pathways that work for any subject matter
    """
    try:
        if not modules:
            return []
        
        print(f"🔄 **Universal Pathway Creation:** {len(modules)} modules")
        
        # Get training context for pathway naming
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        
        # Create universal pathways based on module count and content
        if len(modules) <= 3:
            # Single comprehensive pathway
            return [{
                'pathway_name': f'{training_type} Complete Pathway',
                'sections': [{
                    'title': f'{training_type} Fundamentals',
                    'modules': modules
                }],
                'module_count': len(modules)
            }]
        elif len(modules) <= 8:
            # Two logical pathways
            mid_point = len(modules) // 2
            return [
                {
                    'pathway_name': f'{training_type} Foundation Pathway',
                    'sections': [{
                        'title': 'Core Concepts and Fundamentals',
                        'modules': modules[:mid_point]
                    }],
                    'module_count': mid_point
                },
                {
                    'pathway_name': f'{training_type} Advanced Pathway',
                    'sections': [{
                        'title': 'Advanced Topics and Applications',
                        'modules': modules[mid_point:]
                    }],
                    'module_count': len(modules) - mid_point
                }
            ]
        else:
            # Three comprehensive pathways
            third = len(modules) // 3
            return [
                {
                    'pathway_name': f'{training_type} Foundation Pathway',
                    'sections': [{
                        'title': 'Essential Fundamentals',
                        'modules': modules[:third]
                    }],
                    'module_count': third
                },
                {
                    'pathway_name': f'{training_type} Intermediate Pathway',
                    'sections': [{
                        'title': 'Intermediate Skills and Processes',
                        'modules': modules[third:2*third]
                    }],
                    'module_count': third
                },
                {
                    'pathway_name': f'{training_type} Advanced Pathway',
                    'sections': [{
                        'title': 'Advanced Applications and Specializations',
                        'modules': modules[2*third:]
                    }],
                    'module_count': len(modules) - 2*third
                }
            ]
        
    except Exception as e:
        print(f"⚠️ Universal pathway creation failed: {str(e)}")
        return []

def create_generic_pathway(training_context, inventory_summary):
    """
    Create a generic pathway when no file content is available
    """
    try:
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        company_size = training_context.get('company_size', 'Medium')
        
        # Create generic modules based on training context
        generic_modules = create_generic_modules(training_context)
        
        # Group into sections
        sections = group_generic_modules_into_sections(generic_modules, training_context)
        
        return {
            'pathway_name': f'{training_type} Pathway',
            'sections': sections,
            'module_count': len(generic_modules)
        }
        
    except Exception as e:
        print(f"⚠️ Generic pathway creation failed: {str(e)}")
        return {
            'pathway_name': 'Training Pathway',
            'sections': [{
                'title': 'General Training',
                'modules': []
            }],
            'module_count': 0
        }

def create_generic_modules(training_context):
    """
    Create generic modules based on training context
    """
    try:
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        
        # Create context-specific generic modules
        if 'safety' in training_type.lower():
            return [
                {
                    'title': 'Safety Fundamentals',
                    'description': 'Introduction to workplace safety principles and procedures',
                    'content': f'This module covers essential safety principles for {target_audience} in {industry}.',
                    'source': 'Generic Safety Training',
                    'key_points': ['Safety Procedures', 'Hazard Identification', 'Emergency Response'],
                    'relevance_score': 0.8,
                    'full_reason': 'Core safety training for new employees'
                },
                {
                    'title': 'Personal Protective Equipment',
                    'description': 'Understanding and using PPE correctly',
                    'content': f'Learn about the proper use of personal protective equipment in {industry} environments.',
                    'source': 'Generic Safety Training',
                    'key_points': ['PPE Types', 'Proper Usage', 'Maintenance'],
                    'relevance_score': 0.8,
                    'full_reason': 'Essential PPE training'
                }
            ]
        elif 'quality' in training_type.lower():
            return [
                {
                    'title': 'Quality Control Basics',
                    'description': 'Introduction to quality control and assurance procedures',
                    'content': f'This module introduces quality control principles for {target_audience} in {industry}.',
                    'source': 'Generic Quality Training',
                    'key_points': ['Quality Standards', 'Inspection Procedures', 'Documentation'],
                    'relevance_score': 0.8,
                    'full_reason': 'Core quality training'
                }
            ]
        else:
            return [
                {
                    'title': f'{training_type} Introduction',
                    'description': f'Welcome to {training_type} training for {target_audience}',
                    'content': f'This module provides an overview of {training_type} procedures for {target_audience} in {industry}.',
                    'source': f'Generic {training_type} Training',
                    'key_points': ['Training Overview', 'Key Concepts', 'Learning Objectives'],
                    'relevance_score': 0.7,
                    'full_reason': f'Introduction to {training_type} training'
                }
            ]
        
    except Exception as e:
        print(f"⚠️ Generic module creation failed: {str(e)}")
        return []

def group_generic_modules_into_sections(modules, training_context):
    """
    Group generic modules into logical sections
    """
    try:
        if not modules:
            return []
        
        training_type = training_context.get('training_type', 'Training')
        
        return [{
            'title': f'{training_type} Fundamentals',
            'modules': modules
        }]
        
    except Exception as e:
        print(f"⚠️ Generic section grouping failed: {str(e)}")
        return [] 

def is_structured_training_content(content):
    """
    Check if content is already structured training material
    More accurate detection that excludes meeting transcripts
    """
    try:
        content_lower = content.lower()
        
        # First, check for meeting transcript indicators (these should NOT be considered structured)
        meeting_indicators = [
            'meeting transcript', 'teams meeting', 'meet meeting', 'zoom meeting',
            'conference call', 'video call', 'meeting recording', 'call transcript',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
            'september', 'october', 'november', 'december',
            '0:00', '0:01', '0:02', '0:03', '0:04', '0:05', '0:06', '0:07', '0:08', '0:09',
            '1:', '2:', '3:', '4:', '5:', '6:', '7:', '8:', '9:', '10:', '11:', '12:',
            'can you hear me', 'is that working', 'are you there', 'do you see my screen',
            'um', 'uh', 'yeah', 'okay', 'right', 'so', 'well', 'you know'
        ]
        
        # More robust meeting detection - check for patterns
        meeting_patterns = [
            r'teams meeting',
            r'meet meeting', 
            r'meeting transcript',
            r'\d{1,2}:\d{2}\s*-\s*[A-Za-z]',  # Time stamps like "0:00 - Name"
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday),\s*\w+\s+\d{1,2},\s*\d{4}',  # Date patterns
            r'yeah,\s*\w+',  # Conversational patterns
            r'um,\s*\w+',
            r'uh,\s*\w+'
        ]
        
        # Check for meeting patterns
        import re
        meeting_matches = 0
        for pattern in meeting_patterns:
            if re.search(pattern, content_lower):
                meeting_matches += 1
        
        # Also check for meeting indicators
        found_meeting_indicators = [indicator for indicator in meeting_indicators if indicator in content_lower]
        meeting_count = len(found_meeting_indicators) + meeting_matches
        
        # If content has meeting indicators, it's NOT structured training content
        if meeting_count >= 1:  # Any meeting indicator means it's conversational
            print(f"❌ Content appears to be meeting transcript ({meeting_count} indicators found)")
            return False
        
        # Also check for meeting transcript patterns in the first few lines
        first_lines = content[:1000].lower()
        if any(pattern in first_lines for pattern in ['teams meeting', 'meet meeting', 'meeting transcript']):
            print(f"❌ Content appears to be meeting transcript (found in first lines)")
            return False
        
        # Check for indicators that this is already structured training content
        training_indicators = [
            'training', 'onboarding', 'guide', 'manual', 'procedure', 'process',
            'instruction', 'tutorial', 'workflow', 'standard operating procedure',
            'sop', 'policy', 'guideline', 'best practice', 'step-by-step',
            'how to', 'overview', 'introduction', 'getting started', 'admin',
            'user guide', 'reference', 'documentation', 'handbook'
        ]
        
        # Count how many training indicators are present
        found_training_indicators = [indicator for indicator in training_indicators if indicator in content_lower]
        indicator_count = len(found_training_indicators)
        
        # Check for structured formatting
        has_numbered_sections = bool(re.search(r'\d+\.\s', content))
        has_bullet_points = bool(re.search(r'[•\-\*]\s', content))
        has_headers = bool(re.search(r'^[A-Z][A-Z\s]+$', content, re.MULTILINE))
        
        # Check for company-specific content
        company_indicators = ['uber', 'admin', 'transport', 'driver', 'rider', 'partner']
        has_company_content = any(indicator in content_lower for indicator in company_indicators)
        
        # Content is considered structured if it has multiple indicators AND specific formatting
        # AND is not a meeting transcript
        is_structured = (indicator_count >= 3 and  # Increased threshold
                        (has_numbered_sections or has_bullet_points or has_headers or has_company_content))
        
        if is_structured:
            print(f"✅ Content appears to be already structured training material ({indicator_count} indicators found)")
        else:
            print(f"🔄 Content appears to be unstructured, applying comprehensive transformation")
        
        return is_structured
        
    except Exception as e:
        print(f"⚠️ Error checking if content is structured: {str(e)}")
        return False

def create_fast_company_specific_pathways(modules, training_context):
    """
    Create company-specific pathways quickly without AI calls
    """
    try:
        if not modules:
            return []
        
        print(f"🚀 **Fast Company-Specific Pathway Creation:** {len(modules)} modules")
        
        # Get company context for pathway naming
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        
        # Create simple pathways based on module count
        if len(modules) <= 3:
            # Single comprehensive pathway
            return [{
                'pathway_name': f'{training_type} Complete Pathway',
                'sections': [{
                    'title': f'{training_type} Fundamentals',
                    'modules': modules
                }],
                'module_count': len(modules)
            }]
        elif len(modules) <= 6:
            # Two logical pathways
            mid_point = len(modules) // 2
            return [
                {
                    'pathway_name': f'{training_type} Foundation Pathway',
                    'sections': [{
                        'title': 'Core Concepts and Fundamentals',
                        'modules': modules[:mid_point]
                    }],
                    'module_count': mid_point
                },
                {
                    'pathway_name': f'{training_type} Advanced Pathway',
                    'sections': [{
                        'title': 'Advanced Topics and Applications',
                        'modules': modules[mid_point:]
                    }],
                    'module_count': len(modules) - mid_point
                }
            ]
        else:
            # Three comprehensive pathways
            third = len(modules) // 3
            return [
                {
                    'pathway_name': f'{training_type} Foundation Pathway',
                    'sections': [{
                        'title': 'Essential Fundamentals',
                        'modules': modules[:third]
                    }],
                    'module_count': third
                },
                {
                    'pathway_name': f'{training_type} Intermediate Pathway',
                    'sections': [{
                        'title': 'Intermediate Skills and Processes',
                        'modules': modules[third:2*third]
                    }],
                    'module_count': third
                },
                {
                    'pathway_name': f'{training_type} Advanced Pathway',
                    'sections': [{
                        'title': 'Advanced Applications and Specializations',
                        'modules': modules[2*third:]
                    }],
                    'module_count': len(modules) - 2*third
                }
            ]
        
    except Exception as e:
        print(f"⚠️ Fast company-specific pathway creation failed: {str(e)}")
        return create_company_specific_fallback_pathways(modules, training_context)

def create_company_specific_pathways_with_gemini(modules, training_context):
    """
    Use Gemini API to create company-specific pathways from actual content
    """
    try:
        if not modules:
            return []
        
        print(f"🤖 **Gemini Company-Specific Pathway Creation:** {len(modules)} modules")
        
        # Prepare module information for Gemini
        module_info = []
        for i, module in enumerate(modules):
            module_info.append({
                'index': i + 1,
                'title': module.get('title', f'Module {i+1}'),
                'description': module.get('description', ''),
                'content_preview': module.get('content', '')[:500],  # First 500 chars
                'source': module.get('source', ''),
                'key_points': module.get('key_points', [])
            })
        
        # Create Gemini prompt for company-specific pathway creation
        prompt = f"""
        Create company-specific onboarding pathways from these training modules.
        
        Training Context:
        - Type: {training_context.get('training_type', 'Onboarding')}
        - Audience: {training_context.get('target_audience', 'New Employees')}
        - Industry: {training_context.get('industry', 'General')}
        - Goals: {training_context.get('primary_goals', 'General onboarding')}
        - Company Size: {training_context.get('company_size', 'Medium')}
        
        Available Modules ({len(modules)} total):
        {chr(10).join([f"{m['index']}. {m['title']} - {m['description']}" for m in module_info])}
        
        REQUIREMENTS:
        - Create 1-3 meaningful pathways based on the actual content
        - Use company-specific naming (not generic terms)
        - Group modules logically based on their actual content
        - Create pathway names that reflect the company's specific needs
        - Make section titles specific to the company's processes
        - Focus on practical, actionable onboarding for the specific company
        
        Return as JSON array of pathways:
        [
            {{
                "pathway_name": "Company-specific pathway name",
                "sections": [
                    {{
                        "title": "Company-specific section title",
                        "modules": [module_indices]
                    }}
                ],
                "module_count": number_of_modules
            }}
        ]
        
        IMPORTANT: Use the actual module content to create meaningful, company-specific pathways.
        """
        
        if not model:
            return create_company_specific_fallback_pathways(modules, training_context)
        response = model.generate_content(prompt)
        if response and hasattr(response, 'text'):
            raw = str(response.text).strip()
        else:
            return create_company_specific_fallback_pathways(modules, training_context)
        
        # Extract JSON from response
        pathways_data = extract_json_from_ai_response(raw)
        
        if pathways_data and isinstance(pathways_data, list):
            # Convert to actual pathway structure with real modules
            pathways = []
            for pathway_data in pathways_data:
                pathway_name = pathway_data.get('pathway_name', 'Company Pathway')
                sections = pathway_data.get('sections', [])
                
                # Convert section data to actual module objects
                pathway_sections = []
                total_modules = 0
                
                for section_data in sections:
                    section_title = section_data.get('title', 'Section')
                    module_indices = section_data.get('modules', [])
                    
                    # Get actual modules for this section
                    section_modules = []
                    for idx in module_indices:
                        if 0 <= idx - 1 < len(modules):  # Convert to 0-based index
                            section_modules.append(modules[idx - 1])
                    
                    if section_modules:
                        pathway_sections.append({
                            'title': section_title,
                            'modules': section_modules
                        })
                        total_modules += len(section_modules)
                
                if pathway_sections:
                    pathways.append({
                        'pathway_name': pathway_name,
                        'sections': pathway_sections,
                        'module_count': total_modules
                    })
            
            print(f"✅ Created {len(pathways)} company-specific pathways using Gemini")
            return pathways
        else:
            print("⚠️ Gemini pathway creation failed, using fallback")
            return create_company_specific_fallback_pathways(modules, training_context)
        
    except Exception as e:
        print(f"⚠️ Gemini company-specific pathway creation failed: {str(e)}")
        return create_company_specific_fallback_pathways(modules, training_context)

def create_company_specific_fallback_pathways(modules, training_context):
    """
    Create company-specific pathways without AI when Gemini fails
    """
    try:
        if not modules:
            return []
        
        print(f"🔄 **Company-Specific Fallback Pathway Creation:** {len(modules)} modules")
        
        # Get company context for pathway naming
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        company_size = training_context.get('company_size', 'Medium')
        
        # Create company-specific pathways based on actual content
        if len(modules) <= 3:
            # Single comprehensive pathway
            return [{
                'pathway_name': f'{training_type} Complete Pathway',
                'sections': [{
                    'title': f'{training_type} Fundamentals',
                    'modules': modules
                }],
                'module_count': len(modules)
            }]
        elif len(modules) <= 8:
            # Two logical pathways
            mid_point = len(modules) // 2
            return [
                {
                    'pathway_name': f'{training_type} Foundation Pathway',
                    'sections': [{
                        'title': 'Core Concepts and Fundamentals',
                        'modules': modules[:mid_point]
                    }],
                    'module_count': mid_point
                },
                {
                    'pathway_name': f'{training_type} Advanced Pathway',
                    'sections': [{
                        'title': 'Advanced Topics and Applications',
                        'modules': modules[mid_point:]
                    }],
                    'module_count': len(modules) - mid_point
                }
            ]
        else:
            # Three comprehensive pathways
            third = len(modules) // 3
            return [
                {
                    'pathway_name': f'{training_type} Foundation Pathway',
                    'sections': [{
                        'title': 'Essential Fundamentals',
                        'modules': modules[:third]
                    }],
                    'module_count': third
                },
                {
                    'pathway_name': f'{training_type} Intermediate Pathway',
                    'sections': [{
                        'title': 'Intermediate Skills and Processes',
                        'modules': modules[third:2*third]
                    }],
                    'module_count': third
                },
                {
                    'pathway_name': f'{training_type} Advanced Pathway',
                    'sections': [{
                        'title': 'Advanced Applications and Specializations',
                        'modules': modules[2*third:]
                    }],
                    'module_count': len(modules) - 2*third
                }
            ]
        
    except Exception as e:
        print(f"⚠️ Company-specific fallback pathway creation failed: {str(e)}")
        return []

def create_company_specific_generic_pathway(training_context, inventory_summary):
    """
    Create company-specific generic pathway when no file content is available
    """
    try:
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        company_size = training_context.get('company_size', 'Medium')
        
        # Create company-specific generic modules
        generic_modules = create_company_specific_generic_modules(training_context)
        
        # Group into sections
        sections = group_company_specific_modules_into_sections(generic_modules, training_context)
        
        return {
            'pathway_name': f'{training_type} Company Pathway',
            'sections': sections,
            'module_count': len(generic_modules)
        }
        
    except Exception as e:
        print(f"⚠️ Company-specific generic pathway creation failed: {str(e)}")
        return {
            'pathway_name': 'Company Training Pathway',
            'sections': [{
                'title': 'Company Training',
                'modules': []
            }],
            'module_count': 0
        }

def create_company_specific_generic_modules(training_context):
    """
    Create company-specific generic modules based on training context
    """
    try:
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        
        # Create context-specific generic modules
        if 'safety' in training_type.lower():
            return [
                {
                    'title': 'Company Safety Fundamentals',
                    'description': f'Introduction to {industry} safety principles and procedures',
                    'content': f'This module covers essential safety principles for {target_audience} in {industry}.',
                    'source': f'{industry} Safety Training',
                    'key_points': ['Safety Procedures', 'Hazard Identification', 'Emergency Response'],
                    'relevance_score': 0.8,
                    'full_reason': f'Core safety training for {target_audience}'
                },
                {
                    'title': 'Company Personal Protective Equipment',
                    'description': f'Understanding and using PPE correctly in {industry}',
                    'content': f'Learn about the proper use of personal protective equipment in {industry} environments.',
                    'source': f'{industry} Safety Training',
                    'key_points': ['PPE Types', 'Proper Usage', 'Maintenance'],
                    'relevance_score': 0.8,
                    'full_reason': f'Essential PPE training for {target_audience}'
                }
            ]
        elif 'quality' in training_type.lower():
            return [
                {
                    'title': f'{industry} Quality Control Basics',
                    'description': f'Introduction to quality control and assurance procedures in {industry}',
                    'content': f'This module introduces quality control principles for {target_audience} in {industry}.',
                    'source': f'{industry} Quality Training',
                    'key_points': ['Quality Standards', 'Inspection Procedures', 'Documentation'],
                    'relevance_score': 0.8,
                    'full_reason': f'Core quality training for {target_audience}'
                }
            ]
        else:
            return [
                {
                    'title': f'{training_type} Company Introduction',
                    'description': f'Welcome to {training_type} training for {target_audience}',
                    'content': f'This module provides an overview of {training_type} procedures for {target_audience} in {industry}.',
                    'source': f'{industry} {training_type} Training',
                    'key_points': ['Training Overview', 'Key Concepts', 'Learning Objectives'],
                    'relevance_score': 0.7,
                    'full_reason': f'Introduction to {training_type} training for {target_audience}'
                }
            ]
        
    except Exception as e:
        print(f"⚠️ Company-specific generic module creation failed: {str(e)}")
        return []

def group_company_specific_modules_into_sections(modules, training_context):
    """
    Group company-specific modules into logical sections
    """
    try:
        if not modules:
            return []
        
        training_type = training_context.get('training_type', 'Training')
        industry = training_context.get('industry', 'General')
        
        return [{
            'title': f'{industry} {training_type} Fundamentals',
            'modules': modules
        }]
        
    except Exception as e:
        print(f"⚠️ Company-specific section grouping failed: {str(e)}")
        return [] 

def create_fast_ai_pathways(modules, training_context):
    """
    Create company-specific pathways using actual content analysis
    """
    try:
        if not modules:
            return []
        
        print(f"🚀 **Fast AI Pathway Creation:** {len(modules)} modules")
        
        # Get company context for pathway naming
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        
        # Analyze module content to create meaningful pathways
        pathway_themes = analyze_module_themes(modules, training_context)
        
        if len(modules) <= 2:
            # Single comprehensive pathway with actual content
            return [{
                'pathway_name': f'{training_type} Complete Pathway',
                'sections': [{
                    'title': f'{training_type} Fundamentals',
                    'modules': modules
                }],
                'module_count': len(modules)
            }]
        elif len(modules) <= 6:
            # Two logical pathways based on content themes
            mid_point = len(modules) // 2
            pathway1_modules = modules[:mid_point]
            pathway2_modules = modules[mid_point:]
            
            pathway1_theme = analyze_pathway_theme(pathway1_modules, training_context)
            pathway2_theme = analyze_pathway_theme(pathway2_modules, training_context)
            
            return [
                {
                    'pathway_name': f'{training_type} {pathway1_theme} Pathway',
                    'sections': [{
                        'title': f'{pathway1_theme} Fundamentals',
                        'modules': pathway1_modules
                    }],
                    'module_count': len(pathway1_modules)
                },
                {
                    'pathway_name': f'{training_type} {pathway2_theme} Pathway',
                    'sections': [{
                        'title': f'{pathway2_theme} Applications',
                        'modules': pathway2_modules
                    }],
                    'module_count': len(pathway2_modules)
                }
            ]
        else:
            # Three comprehensive pathways based on content analysis
            third = len(modules) // 3
            pathway1_modules = modules[:third]
            pathway2_modules = modules[third:2*third]
            pathway3_modules = modules[2*third:]
            
            theme1 = analyze_pathway_theme(pathway1_modules, training_context)
            theme2 = analyze_pathway_theme(pathway2_modules, training_context)
            theme3 = analyze_pathway_theme(pathway3_modules, training_context)
            
            return [
                {
                    'pathway_name': f'{training_type} {theme1} Pathway',
                    'sections': [{
                        'title': f'{theme1} Fundamentals',
                        'modules': pathway1_modules
                    }],
                    'module_count': len(pathway1_modules)
                },
                {
                    'pathway_name': f'{training_type} {theme2} Pathway',
                    'sections': [{
                        'title': f'{theme2} Intermediate Skills',
                        'modules': pathway2_modules
                    }],
                    'module_count': len(pathway2_modules)
                },
                {
                    'pathway_name': f'{training_type} {theme3} Pathway',
                    'sections': [{
                        'title': f'{theme3} Advanced Applications',
                        'modules': pathway3_modules
                    }],
                    'module_count': len(pathway3_modules)
                }
            ]
        
    except Exception as e:
        print(f"⚠️ Fast AI pathway creation failed: {str(e)}")
        return create_fast_company_specific_pathways(modules, training_context)

def analyze_module_themes(modules, training_context):
    """
    Analyze modules to identify common themes for pathway creation
    """
    try:
        themes = []
        for module in modules:
            content = module.get('content', '').lower()
            title = module.get('title', '').lower()
            
            # Extract themes from content
            if any(word in content for word in ['safety', 'ppe', 'protective']):
                themes.append('Safety')
            if any(word in content for word in ['quality', 'inspection', 'control']):
                themes.append('Quality')
            if any(word in content for word in ['process', 'procedure', 'workflow']):
                themes.append('Process')
            if any(word in content for word in ['equipment', 'tool', 'operation']):
                themes.append('Equipment')
            if any(word in content for word in ['communication', 'meeting', 'collaboration']):
                themes.append('Communication')
            if any(word in content for word in ['documentation', 'record', 'report']):
                themes.append('Documentation')
        
        # Return most common themes
        from collections import Counter
        theme_counts = Counter(themes)
        return [theme for theme, count in theme_counts.most_common(3)]
        
    except Exception as e:
        print(f"⚠️ Theme analysis failed: {str(e)}")
        return ['Fundamentals', 'Applications', 'Advanced']

def analyze_pathway_theme(modules, training_context):
    """
    Analyze a group of modules to determine the pathway theme
    """
    try:
        themes = analyze_module_themes(modules, training_context)
        if themes:
            return themes[0]  # Return the most common theme
        else:
            return 'Core'
        
    except Exception as e:
        print(f"⚠️ Pathway theme analysis failed: {str(e)}")
        return 'Core'

def extract_technical_content_professional(content):
    """
    Extract technical content and transform it into professional, concise training material
    """
    import re
    
    # Remove timestamps and speaker names
    content = re.sub(r'\d{1,2}:\d{2}:\d{2}\s*-\s*[^:]+:', '', content)
    content = re.sub(r'\d{1,2}:\d{2}\s*-\s*[^:]+:', '', content)
    content = re.sub(r'\b\d+\s*-\s*[A-Za-z\s]+', '', content)  # Remove "30 - Mike Wright" patterns
    
    # Remove conversational fillers and phrases
    fillers = ['um', 'uh', 'you know', 'like', 'so', 'well', 'basically', 'actually', 'really', 'just', 'simply', 'obviously', 'clearly', 'sort of', 'kind of', 'okay', 'right', 'yeah', 'sure', 'I mean', 'you see']
    for filler in fillers:
        content = re.sub(rf'\b{filler}\b', '', content, flags=re.IGNORECASE)
    
    # Remove conversational patterns
    content = re.sub(r'Oh,\s*it makes total sense\.?\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Personnel hope operators don\'t mind me.*?\.', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Personnel\'ll\s+', 'The team will ', content, flags=re.IGNORECASE)
    content = re.sub(r'the team don\'t do', 'the team does not handle', content, flags=re.IGNORECASE)
    
    # Remove incomplete sentences and fragments
    sentences = re.split(r'[.!?]+', content)
    complete_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        # Skip conversational starters and short fragments
        if (len(sentence) > 30 and 
            not sentence.lower().startswith(('so', 'well', 'yeah', 'okay', 'right', 'oh', 'and', 'but')) and
            not re.match(r'^\w+,?\s*$', sentence) and  # Skip single words
            not 'chopping and changing' in sentence.lower()):
            
            # Convert to professional language
            sentence = re.sub(r'\bI\b', 'The operator', sentence)
            sentence = re.sub(r'\bwe\b', 'the team', sentence, flags=re.IGNORECASE)
            sentence = re.sub(r'\byou\b', 'personnel', sentence, flags=re.IGNORECASE)
            sentence = re.sub(r'\bPersonnel\'ll\b', 'The team will', sentence, flags=re.IGNORECASE)
            sentence = re.sub(r'\bthe team\'ll\b', 'the team will', sentence, flags=re.IGNORECASE)
            
            # Fix grammar and structure
            sentence = re.sub(r'\s+', ' ', sentence)  # Clean multiple spaces
            sentence = sentence.strip()
            
            # Capitalize first letter and ensure proper sentence structure
            if sentence:
                sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
                complete_sentences.append(sentence)
    
    # Join and clean final result
    result = '. '.join(complete_sentences[:15])  # Limit to 15 sentences for conciseness
    result = re.sub(r'\s+', ' ', result)  # Clean multiple spaces
    result = re.sub(r'\.+', '.', result)  # Fix multiple periods
    
    return result

def create_professional_training_modules(content, training_context):
    """
    Create professional training modules from content
    """
    professional_content = extract_technical_content_professional(content)
    
    if not professional_content:
        return []
    
    # Split content into logical sections
    content_chunks = professional_content.split('. ')
    chunk_size = max(3, len(content_chunks) // 4)  # Aim for 4 modules max
    
    # Extract keywords for better module titles
    content_keywords = extract_content_keywords(professional_content)
    
    modules = []
    module_titles = [
        "Preparation and Setup",
        "Core Process Execution", 
        "Quality and Safety Standards",
        "Completion and Documentation"
    ]
    
    for i in range(0, len(content_chunks), chunk_size):
        chunk = '. '.join(content_chunks[i:i+chunk_size])
        
        if len(chunk) > 100:  # Only create modules with substantial content
            module_index = len(modules)
            
            # Create dynamic title based on content
            if content_keywords and module_index < len(content_keywords):
                title = f"{content_keywords[module_index].title()} Training"
            elif module_index < len(module_titles):
                title = module_titles[module_index]
            else:
                title = f"Advanced Training Module {module_index + 1}"
            
            module = {
                'title': title,
                'description': f"Specialized training module focusing on {title.lower()} for {training_context.get('target_audience', 'team members')}",
                'content': format_professional_content(chunk, training_context, title),
                'learning_objectives': generate_learning_objectives(chunk, training_context),
                'key_points': extract_key_points(chunk)
            }
            modules.append(module)
    
    return modules[:4]  # Maximum 4 modules

def format_professional_content(content, training_context, module_title="Professional Training"):
    """
    Format content into professional training structure
    """
    formatted = f"""TRAINING MODULE: {module_title}

Target Audience: {training_context.get('target_audience', 'Team Members')}
Industry Context: {training_context.get('industry', 'Operations')}
Module Focus: {module_title.replace(' Training', '')}

LEARNING CONTENT:
{content}

IMPLEMENTATION GUIDELINES:
• Follow established safety protocols and procedures
• Maintain quality standards throughout all operations
• Ensure compliance with industry regulations
• Document all processes and maintain records
• Apply best practices consistently

ASSESSMENT CRITERIA:
• Demonstrate understanding of core concepts
• Apply knowledge in practical scenarios
• Meet established performance standards
• Complete module evaluation successfully
"""
    return formatted

def generate_learning_objectives(content, training_context):
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

def extract_key_points(content):
    """
    Extract key points from content
    """
    sentences = content.split('. ')
    key_points = []
    
    for sentence in sentences[:5]:  # Take first 5 sentences
        if len(sentence) > 20:
            key_points.append(sentence.strip())
    
    return key_points

def create_multiple_sections(modules, training_context):
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
    
    modules_per_section = 6
    
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

def generate_improved_pathway(content, training_context, filename):
    """
    Generate improved pathway with multiple sections and professional content
    """
    # Create professional training modules
    modules = create_professional_training_modules(content, training_context)
    
    if not modules:
        return create_fallback_pathway_improved(training_context, filename)
    
    # Organize into multiple sections
    sections = create_multiple_sections(modules, training_context)
    
    # Generate unique pathway name based on content and filename
    content_keywords = extract_content_keywords(content)
    base_filename = filename.replace('.pdf', '').replace('.docx', '').replace('.txt', '').replace('_', ' ').title()
    
    if content_keywords:
        pathway_name = f"{base_filename} - {content_keywords[0].title()} Training"
    else:
        pathway_name = f"{base_filename} Training Program"
    
    pathway = {
        'pathways': [{
            'pathway_name': pathway_name,
            'description': f"Specialized training based on {filename} for {training_context.get('target_audience', 'team members')} in {training_context.get('industry', 'operations')}",
            'sections': sections,
            'source_files': [filename],
            'total_modules': len(modules)
        }]
    }
    
    return pathway

def extract_content_keywords(content):
    """
    Extract key terms from content to create unique names
    """
    import re
    
    # Common technical keywords to look for
    keywords = []
    
    # Look for process-related terms
    process_terms = ['construction', 'fabrication', 'assembly', 'installation', 'maintenance', 'safety', 'quality', 'inspection', 'bridge', 'welding', 'equipment', 'procedure', 'operation', 'manufacturing']
    
    content_lower = content.lower()
    for term in process_terms:
        if term in content_lower:
            keywords.append(term)
    
    # Extract capitalized words that might be important
    capitalized_words = re.findall(r'\b[A-Z][a-z]{3,}\b', content)
    keywords.extend(capitalized_words[:3])  # Add first 3 capitalized words
    
    return keywords[:5]  # Return top 5 keywords

def create_fallback_pathway_improved(training_context, filename):
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

 