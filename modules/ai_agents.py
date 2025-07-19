#!/usr/bin/env python3
"""
AI Agents for Pathway Generation using Google Gemini
Specialized agents for creating optimal training pathways, sections, and modules
"""

import json
import re
from modules.config import model
from modules.utils import debug_print

class PathwayPlannerAgent:
    """
    AI agent responsible for analyzing content and creating strategic pathway plans
    """
    
    def __init__(self):
        self.model = model
        
    def analyze_and_plan_pathways(self, extracted_content, training_context, file_inventory):
        """
        Analyze all content and create a comprehensive pathway plan
        """
        try:
            if not self.model:
                debug_print("⚠️ Gemini model not available for pathway planning")
                return self._create_fallback_plan(extracted_content, training_context)
            
            # Create comprehensive analysis prompt
            prompt = self._build_pathway_analysis_prompt(extracted_content, training_context, file_inventory)
            
            debug_print("🤖 PathwayPlannerAgent: Analyzing content for optimal pathway structure...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return self._parse_pathway_plan(response.text)
            else:
                debug_print("⚠️ No response from PathwayPlannerAgent, using fallback")
                return self._create_fallback_plan(extracted_content, training_context)
                
        except Exception as e:
            debug_print(f"⚠️ PathwayPlannerAgent error: {str(e)}")
            return self._create_fallback_plan(extracted_content, training_context)
    
    def _build_pathway_analysis_prompt(self, extracted_content, training_context, file_inventory):
        """
        Build comprehensive prompt for pathway analysis
        """
        content_summary = ""
        for filename, content in extracted_content.items():
            content_preview = content[:500] if content else "No content"
            content_summary += f"\n\nFile: {filename}\nContent Preview: {content_preview}"
        
        prompt = f"""
You are an expert Training Pathway Architect. Analyze the provided content and create an optimal training pathway structure.

TRAINING CONTEXT:
- Industry: {training_context.get('industry', 'General')}
- Target Audience: {training_context.get('target_audience', 'Employees')}
- Training Type: {training_context.get('training_type', 'Skills Training')}
- Company Size: {training_context.get('company_size', 'Medium')}

CONTENT TO ANALYZE:
{content_summary}

FILE INVENTORY:
- Process Documents: {file_inventory.get('process_docs', 0)}
- Training Materials: {file_inventory.get('training_materials', 0)}
- Technical Docs: {file_inventory.get('technical_docs', 0)}
- Policy Documents: {file_inventory.get('policies', 0)}

TASK: Create 2-3 distinct, professional training pathways. Each pathway should be unique and serve different learning objectives.

REQUIREMENTS:
1. Each pathway must have a unique, professional name (not generic)
2. Each pathway should focus on different aspects of the content
3. Pathways should be progressive (Basic → Intermediate → Advanced OR different specializations)
4. Each pathway should have 2-4 distinct sections
5. Each section should contain 2-4 modules

OUTPUT FORMAT (JSON):
{{
  "pathways": [
    {{
      "pathway_name": "Professional, specific name based on content",
      "description": "Clear description of what this pathway teaches",
      "target_level": "Beginner/Intermediate/Advanced",
      "estimated_duration": "X hours/days",
      "sections": [
        {{
          "section_name": "Specific section name",
          "section_description": "What this section covers",
          "focus_area": "Main learning focus",
          "modules": [
            {{
              "module_title": "Specific module name",
              "module_description": "What this module teaches",
              "learning_objectives": ["objective1", "objective2", "objective3"],
              "content_type": "theory/practical/assessment",
              "estimated_time": "X minutes"
            }}
          ]
        }}
      ]
    }}
  ]
}}

Make each pathway truly unique and professional. Focus on creating value-driven, specific names and descriptions.
"""
        return prompt
    
    def _parse_pathway_plan(self, response_text):
        """
        Parse the AI response into structured pathway plan
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                plan = json.loads(json_str)
                debug_print(f"✅ PathwayPlannerAgent: Successfully parsed {len(plan.get('pathways', []))} pathways")
                return plan
            else:
                debug_print("⚠️ Could not extract JSON from pathway plan response")
                return None
        except Exception as e:
            debug_print(f"⚠️ Error parsing pathway plan: {str(e)}")
            return None
    
    def _create_fallback_plan(self, extracted_content, training_context):
        """
        Create a basic fallback plan when AI is unavailable
        """
        return {
            "pathways": [
                {
                    "pathway_name": f"{training_context.get('industry', 'Professional')} Foundation Training",
                    "description": f"Essential training for {training_context.get('target_audience', 'team members')}",
                    "target_level": "Beginner",
                    "estimated_duration": "4 hours",
                    "sections": [
                        {
                            "section_name": "Fundamentals",
                            "section_description": "Core concepts and principles",
                            "focus_area": "Foundation knowledge",
                            "modules": [
                                {
                                    "module_title": "Introduction and Overview",
                                    "module_description": "Basic introduction to key concepts",
                                    "learning_objectives": ["Understand basic principles", "Identify key components"],
                                    "content_type": "theory",
                                    "estimated_time": "30 minutes"
                                }
                            ]
                        }
                    ]
                }
            ]
        }


class SectionGeneratorAgent:
    """
    AI agent responsible for generating detailed section content based on pathway plans
    """
    
    def __init__(self):
        self.model = model
    
    def generate_section_content(self, section_plan, content_chunk, training_context):
        """
        Generate detailed content for a specific section
        """
        try:
            if not self.model:
                debug_print("⚠️ Gemini model not available for section generation")
                return self._create_fallback_section(section_plan, content_chunk)
            
            prompt = self._build_section_prompt(section_plan, content_chunk, training_context)
            
            debug_print(f"🤖 SectionGeneratorAgent: Generating section '{section_plan.get('section_name', 'Unknown')}'...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return self._parse_section_content(response.text, section_plan)
            else:
                return self._create_fallback_section(section_plan, content_chunk)
                
        except Exception as e:
            debug_print(f"⚠️ SectionGeneratorAgent error: {str(e)}")
            return self._create_fallback_section(section_plan, content_chunk)
    
    def _build_section_prompt(self, section_plan, content_chunk, training_context):
        """
        Build prompt for section content generation
        """
        prompt = f"""
You are an expert Training Content Developer. Create detailed section content based on the plan and source material.

SECTION PLAN:
- Section Name: {section_plan.get('section_name', 'Training Section')}
- Description: {section_plan.get('section_description', 'Training content')}
- Focus Area: {section_plan.get('focus_area', 'General learning')}

TRAINING CONTEXT:
- Industry: {training_context.get('industry', 'General')}
- Target Audience: {training_context.get('target_audience', 'Employees')}

SOURCE CONTENT:
{content_chunk[:1000] if content_chunk else 'No specific content provided'}

TASK: Create a professional, comprehensive section with the planned modules.

REQUIREMENTS:
1. Transform raw content into professional training material
2. Remove any conversational language, meeting artifacts, or personal references
3. Create clear, actionable content
4. Structure content logically
5. Include practical implementation guidance

OUTPUT FORMAT (JSON):
{{
  "section": {{
    "title": "Professional section title",
    "description": "Clear section description",
    "overview": "Brief overview of what learners will gain",
    "modules": [
      {{
        "title": "Professional module title",
        "description": "What this module covers",
        "content": "Professional, structured training content (no conversational language)",
        "learning_objectives": ["specific objective 1", "specific objective 2"],
        "key_takeaways": ["key point 1", "key point 2"],
        "practical_applications": ["application 1", "application 2"]
      }}
    ]
  }}
}}

Ensure all content is professional, clear, and actionable. No conversational tone or meeting artifacts.
"""
        return prompt
    
    def _parse_section_content(self, response_text, section_plan):
        """
        Parse AI response into structured section content
        """
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                section_data = json.loads(json_str)
                debug_print(f"✅ SectionGeneratorAgent: Generated section with {len(section_data.get('section', {}).get('modules', []))} modules")
                return section_data.get('section', {})
            else:
                return self._create_fallback_section(section_plan, "")
        except Exception as e:
            debug_print(f"⚠️ Error parsing section content: {str(e)}")
            return self._create_fallback_section(section_plan, "")
    
    def _create_fallback_section(self, section_plan, content_chunk):
        """
        Create fallback section content
        """
        return {
            "title": section_plan.get('section_name', 'Training Section'),
            "description": section_plan.get('section_description', 'Training content section'),
            "overview": f"This section covers {section_plan.get('focus_area', 'essential concepts')}",
            "modules": [
                {
                    "title": module.get('module_title', 'Training Module'),
                    "description": module.get('module_description', 'Training content'),
                    "content": f"Professional training content for {module.get('module_title', 'this module')}.",
                    "learning_objectives": module.get('learning_objectives', ['Understand key concepts']),
                    "key_takeaways": ['Key learning point'],
                    "practical_applications": ['Practical application']
                } for module in section_plan.get('modules', [{'module_title': 'Default Module'}])
            ]
        }


class ModuleContentAgent:
    """
    AI agent responsible for creating detailed, professional module content
    """
    
    def __init__(self):
        self.model = model
    
    def enhance_module_content(self, module_data, source_content, training_context):
        """
        Enhance module content with detailed, professional material
        """
        try:
            if not self.model:
                debug_print("⚠️ Gemini model not available for module enhancement")
                return module_data
            
            prompt = self._build_module_enhancement_prompt(module_data, source_content, training_context)
            
            debug_print(f"🤖 ModuleContentAgent: Enhancing module '{module_data.get('title', 'Unknown')}'...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                enhanced = self._parse_enhanced_module(response.text, module_data)
                return enhanced
            else:
                return module_data
                
        except Exception as e:
            debug_print(f"⚠️ ModuleContentAgent error: {str(e)}")
            return module_data
    
    def _build_module_enhancement_prompt(self, module_data, source_content, training_context):
        """
        Build prompt for module content enhancement
        """
        prompt = f"""
You are an expert Instructional Designer. Enhance this training module with comprehensive, professional content.

MODULE TO ENHANCE:
- Title: {module_data.get('title', 'Training Module')}
- Description: {module_data.get('description', 'Training content')}
- Current Content: {module_data.get('content', 'Basic content')}

TRAINING CONTEXT:
- Industry: {training_context.get('industry', 'General')}
- Target Audience: {training_context.get('target_audience', 'Employees')}

SOURCE MATERIAL:
{source_content[:800] if source_content else 'No additional source material'}

TASK: Create comprehensive, professional training module content.

REQUIREMENTS:
1. Expand content to be detailed and actionable
2. Use professional language (no conversational tone)
3. Include clear procedures and guidelines
4. Add safety considerations where relevant
5. Include assessment criteria
6. Structure content logically with clear headings

OUTPUT FORMAT:
Create detailed, professional training content formatted as:

MODULE: [Title]

OVERVIEW:
[Professional overview of what learners will achieve]

CORE CONTENT:
[Detailed, structured training material - use bullet points, procedures, and clear organization]

SAFETY CONSIDERATIONS:
[Relevant safety guidelines and precautions]

IMPLEMENTATION PROCEDURES:
[Step-by-step procedures where applicable]

QUALITY STANDARDS:
[Standards and requirements to maintain]

ASSESSMENT CRITERIA:
[How performance will be evaluated]

Make the content comprehensive, professional, and actionable. No conversational language or meeting references.
"""
        return prompt
    
    def _parse_enhanced_module(self, response_text, original_module):
        """
        Parse enhanced module content from AI response
        """
        try:
            # Extract the structured content
            enhanced_content = response_text.strip()
            
            # Update the module with enhanced content
            enhanced_module = original_module.copy()
            enhanced_module['content'] = enhanced_content
            
            debug_print(f"✅ ModuleContentAgent: Enhanced module content ({len(enhanced_content)} characters)")
            return enhanced_module
            
        except Exception as e:
            debug_print(f"⚠️ Error parsing enhanced module: {str(e)}")
            return original_module


class PathwayOrchestrator:
    """
    Main orchestrator that coordinates all AI agents to generate optimal pathways
    """
    
    def __init__(self):
        self.planner = PathwayPlannerAgent()
        self.section_generator = SectionGeneratorAgent()
        self.module_enhancer = ModuleContentAgent()
    
    def generate_ai_powered_pathways(self, extracted_content, training_context, file_inventory):
        """
        Orchestrate the complete AI-powered pathway generation process
        """
        try:
            debug_print("🚀 Starting AI-powered pathway generation with specialized agents...")
            
            # Step 1: Plan pathways using AI analysis
            pathway_plan = self.planner.analyze_and_plan_pathways(extracted_content, training_context, file_inventory)
            
            if not pathway_plan or 'pathways' not in pathway_plan:
                debug_print("❌ Failed to generate pathway plan")
                return None
            
            debug_print(f"📋 Generated plan for {len(pathway_plan['pathways'])} pathways")
            
            # Step 2: Generate detailed content for each pathway
            final_pathways = []
            content_files = list(extracted_content.items())
            
            for i, pathway_plan_item in enumerate(pathway_plan['pathways']):
                debug_print(f"🛤️ Generating pathway {i+1}: {pathway_plan_item.get('pathway_name', 'Unknown')}")
                
                # Assign content chunks to pathways
                content_chunk = ""
                if i < len(content_files):
                    filename, file_content = content_files[i]
                    content_chunk = file_content
                elif content_files:
                    # Use all content for additional pathways
                    content_chunk = " ".join([content for _, content in content_files])
                
                # Generate sections for this pathway
                generated_sections = []
                for section_plan in pathway_plan_item.get('sections', []):
                    section_content = self.section_generator.generate_section_content(
                        section_plan, content_chunk, training_context
                    )
                    
                    # Enhance modules within the section
                    enhanced_modules = []
                    for module in section_content.get('modules', []):
                        enhanced_module = self.module_enhancer.enhance_module_content(
                            module, content_chunk, training_context
                        )
                        enhanced_modules.append(enhanced_module)
                    
                    section_content['modules'] = enhanced_modules
                    generated_sections.append(section_content)
                
                # Create final pathway structure
                final_pathway = {
                    'pathway_name': pathway_plan_item.get('pathway_name', f'Training Pathway {i+1}'),
                    'description': pathway_plan_item.get('description', 'Professional training pathway'),
                    'target_level': pathway_plan_item.get('target_level', 'Intermediate'),
                    'estimated_duration': pathway_plan_item.get('estimated_duration', '4 hours'),
                    'sections': generated_sections,
                    'source_files': list(extracted_content.keys()),
                    'total_modules': sum(len(section.get('modules', [])) for section in generated_sections)
                }
                
                final_pathways.append(final_pathway)
                debug_print(f"✅ Completed pathway: {final_pathway['pathway_name']}")
            
            debug_print(f"🎯 AI-powered pathway generation complete: {len(final_pathways)} unique pathways created")
            return {'pathways': final_pathways}
            
        except Exception as e:
            debug_print(f"❌ PathwayOrchestrator error: {str(e)}")
            return None