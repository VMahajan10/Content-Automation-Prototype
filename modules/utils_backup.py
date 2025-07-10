#!/usr/bin/env python3
"""
Fixed version of utils.py with correct indentation
"""

import json
import re
import concurrent.futures
import streamlit as st
from modules.config import model

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
        'max_modules_per_file': 2,  # Reduced module limit for speed
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
                best_type = max(content_scores, key=content_scores.get)
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
        
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
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
        
        response = model.generate_content(prompt)
        sentences = [s.strip() for s in response.text.split('\n') if s.strip() and len(s.strip()) > 30]
        
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
        
        response = model.generate_content(prompt)
        sections_data = extract_json_from_ai_response(response.text)
        
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
        topics = [topic.strip() for topic in response.text.split(',') if topic.strip()]
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
        response = model.generate_content(prompt)
        desc = response.text.strip().replace('\n', ' ')
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
        response = model.generate_content(prompt)
        raw = response.text.strip()
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
    Use Gemini to generate one or more complete pathway structures including sections and modules
    based on the training context and extracted content.
    Returns: dict with 'pathways': list of pathway dicts
    """
    try:
        st.write("🔧 **AI Function Debug:**")
        if model is None:
            st.error("❌ Gemini API is not configured. Please check your GEMINI_API_KEY in the .env file.")
            return None
        st.write("✅ Model is available")
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        company_size = training_context.get('company_size', 'Medium')
        st.write(f"📋 Training Context: {training_type}, {target_audience}, {industry}")
        if not training_context:
            training_context = {
                'training_type': 'Onboarding',
                'target_audience': 'New Employees',
                'industry': 'General',
                'company_size': 'Medium'
            }
        file_based_modules = []
        content_analysis = []
        st.write(f"📁 Processing {len(extracted_file_contents)} files...")
        
        # Use parallel processing for multiple files
        if len(extracted_file_contents) > 1:
            print(f"🚀 **Using parallel processing for {len(extracted_file_contents)} files**")
            
            def process_single_file(file_data):
                """Process a single file for modules"""
                filename, content = file_data
                
                # Skip video files that might cause timeouts
                if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    print(f"⏭️ Skipping video file: {filename} (will process separately if needed)")
                    return {
                        'filename': filename,
                        'modules': [],
                        'success': False,
                        'reason': 'Video file skipped for speed'
                    }
                
                if content and len(content.strip()) > 50:
                    print(f"🔍 Processing file: {filename} (content length: {len(content)})")
                    
                    try:
                        # Extract modules from file with better error handling
                        file_modules = extract_modules_from_file_content(filename, content, training_context, bypass_filtering, preserve_original_content)
                    
                        return {
                            'filename': filename,
                            'modules': file_modules,
                            'success': True
                        }
                    except Exception as e:
                        print(f"⚠️ Error processing {filename}: {str(e)}")
                        return {
                            'filename': filename,
                            'modules': [],
                            'success': False,
                            'reason': f'Processing error: {str(e)}'
                        }
                else:
                    return {
                        'filename': filename,
                        'modules': [],
                        'success': False,
                        'reason': 'No content or too short'
                    }
            
            # Process files in parallel with better error handling and progress tracking
            config = get_parallel_config()
            max_workers = min(config['max_file_workers'], len(extracted_file_contents))
            
            print(f"🚀 Starting parallel processing with {max_workers} workers, timeout: {config['timeout_seconds']}s")
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {executor.submit(process_single_file, file_data): file_data for file_data in extracted_file_contents.items()}
                
                # Collect results with better timeout handling and progress tracking
                completed_files = 0
                total_files = len(extracted_file_contents)
                
                try:
                    for future in concurrent.futures.as_completed(future_to_file, timeout=config['timeout_seconds']):
                        try:
                            result = future.result(timeout=60)  # Increased individual file timeout
                            if result['success']:
                                file_based_modules.extend(result['modules'])
                                content_analysis.append(f"File: {result['filename']}\nExtracted {len(result['modules'])} content modules")
                                print(f"✅ [{completed_files + 1}/{total_files}] Extracted {len(result['modules'])} modules from {result['filename']}")
                            else:
                                print(f"⚠️ [{completed_files + 1}/{total_files}] Skipping {result['filename']} - {result['reason']}")
                            completed_files += 1
                        except concurrent.futures.TimeoutError:
                            # Handle individual file timeout
                            file_data = future_to_file[future]
                            filename = file_data[0]
                            print(f"⚠️ [{completed_files + 1}/{total_files}] File {filename} processing timed out - skipping")
                            content_analysis.append(f"File: {filename}\nTimed out - skipped")
                            completed_files += 1
                        except Exception as e:
                            # Handle other errors
                            file_data = future_to_file[future]
                            filename = file_data[0]
                            print(f"⚠️ [{completed_files + 1}/{total_files}] Error processing {filename}: {str(e)}")
                            content_analysis.append(f"File: {filename}\nError: {str(e)}")
                            completed_files += 1
                            
                except concurrent.futures.TimeoutError:
                    # Handle overall timeout
                    unfinished = len([f for f in future_to_file if not f.done()])
                    print(f"⚠️ Overall timeout reached. {unfinished} files still processing.")
                    
                    # Cancel unfinished futures
                    for future in future_to_file:
                        if not future.done():
                            future.cancel()
                    
                    # Check if we have any results
                    if not file_based_modules:
                        print("⚠️ No modules extracted from parallel processing, trying fallback...")
                        # Fallback to processing files sequentially
                        for filename, content in extracted_file_contents.items():
                            if content and len(content.strip()) > 50:
                                print(f"🔄 Fallback processing: {filename}")
                                file_modules = extract_modules_from_file_content(filename, content, training_context, bypass_filtering, preserve_original_content)
                                file_based_modules.extend(file_modules)
                                content_analysis.append(f"File: {filename}\nFallback extracted {len(file_modules)} modules")

                # Check if we have any results
                if not file_based_modules:
                    print("⚠️ No modules extracted from parallel processing, trying fallback...")
                    # Fallback to processing files sequentially
                    for filename, content in extracted_file_contents.items():
                        if content and len(content.strip()) > 50:
                            print(f"🔄 Fallback processing: {filename}")
                            file_modules = extract_modules_from_file_content(filename, content, training_context, bypass_filtering)
                            file_based_modules.extend(file_modules)
                            content_analysis.append(f"File: {filename}\nFallback extracted {len(file_modules)} modules")
        else:
            # Single file processing (original method)
            for filename, content in extracted_file_contents.items():
                if content and len(content.strip()) > 50:
                    print(f"🔍 Processing file: {filename} (content length: {len(content)})")
                    
                    # Extract actual content from files
                    file_modules = extract_modules_from_file_content(filename, content, training_context, bypass_filtering, preserve_original_content)
                    
                    file_based_modules.extend(file_modules)
                    content_analysis.append(f"File: {filename}\nExtracted {len(file_modules)} content modules")
                    print(f"✅ Extracted {len(file_modules)} content modules from {filename}")
                else:
                    print(f"⚠️ Skipping {filename} - no content or too short")
        
        print(f"📊 Total modules extracted: {len(file_based_modules)}")
        inventory_summary = []
        if file_inventory.get('process_docs'):
            inventory_summary.append(f"Process documents: {file_inventory['process_docs']}")
        if file_inventory.get('training_materials'):
            inventory_summary.append(f"Training materials: {file_inventory['training_materials']}")
        if file_inventory.get('policies'):
            inventory_summary.append(f"Policies: {file_inventory['policies']}")
        if file_inventory.get('technical_docs'):
            inventory_summary.append(f"Technical documentation: {file_inventory['technical_docs']}")
        print(f"📝 Inventory summary: {inventory_summary}")
        
        # --- MULTI-PATHWAY LOGIC ---
        if file_based_modules:
            print("🛤️ Creating company-specific pathways using fast methods...")
            print(f"📊 Modules to organize: {len(file_based_modules)}")
            for i, module in enumerate(file_based_modules[:3]):  # Show first 3 modules
                print(f"   Module {i+1}: {module.get('title', 'No title')} - {len(module.get('content', ''))} chars")
            
            # Use fast pathway creation for speed
            try:
                print("🚀 Using fast pathway creation...")
                
                # Create company-specific pathways using fast methods
                pathways = create_fast_ai_pathways(file_based_modules, training_context)
                
                print(f"✅ Company-specific pathways created: {len(pathways)}")
                
                # Debug pathway structure
                for i, pathway in enumerate(pathways):
                    print(f"   Pathway {i+1}: {pathway.get('pathway_name', 'Unknown')}")
                    sections = pathway.get('sections', [])
                    print(f"   Sections: {len(sections)}")
                    for j, section in enumerate(sections):
                        modules = section.get('modules', [])
                        print(f"     Section {j+1}: {section.get('title', 'Unknown')} - {len(modules)} modules")
                
                return {"pathways": pathways}
            except Exception as e:
                print(f"⚠️ Fast pathway creation failed: {str(e)}")
                print("🔄 Falling back to basic pathway creation...")
                
                # Create basic pathways without AI
                fallback_pathways = create_company_specific_fallback_pathways(file_based_modules, training_context)
                if fallback_pathways:
                    print(f"✅ Company-specific fallback pathways created: {len(fallback_pathways)}")
                    return {"pathways": fallback_pathways}
                else:
                    print("❌ Company-specific fallback pathway creation also failed")
                    return None
        else:
            print("🛤️ Creating company-specific generic pathway...")
            result = create_company_specific_generic_pathway(training_context, inventory_summary)
            print(f"✅ Company-specific generic pathway created: {result}")
            return {"pathways": [result]}
            
    except Exception as e:
        st.error(f"❌ Error generating pathway with AI: {str(e)}")
        st.info("💡 This might be due to:")
        st.info("• Network connectivity issues")
        st.info("• Invalid API key")
        st.info("• API rate limits")
        st.info("• Insufficient training context")
        import traceback
        st.code(traceback.format_exc())
        return None 

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
        
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
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
            primary_topic = max(topic_scores, key=topic_scores.get)
            if topic_scores[primary_topic] > 0:
                return primary_topic
        
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
        professional_content = response.text.strip()
        
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
        if response.text:
            # Parse the response into a list of terms
            terms = [term.strip() for term in response.text.split('\n') if term.strip()]
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
        cleaned_content = response.text.strip()
        
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
        
        response = model.generate_content(prompt)
        meaningful_content = response.text.strip()
        
        # Ensure we have reasonable content length
        if len(meaningful_content) < 50:
            return extract_meaningful_content_snippet(content)
        
        return meaningful_content
        
    except Exception as e:
        return extract_meaningful_content_snippet(content) 

def group_modules_into_multiple_pathways_parallel(modules, training_context, num_pathways=3, sections_per_pathway=6, modules_per_section=4):
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

def group_modules_into_multiple_pathways(modules, training_context, num_pathways=3, sections_per_pathway=6, modules_per_section=4):
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

def group_modules_into_sections_ai(modules, training_context, max_sections=6, max_modules_per_section=4):
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

def group_modules_into_sections_basic(modules, max_sections=6, max_modules_per_section=4):
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
        
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
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