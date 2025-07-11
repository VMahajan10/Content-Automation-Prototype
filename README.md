# 🚀 Gateway Content Automation

An AI-powered training content generation and management platform that creates comprehensive training pathways, mind maps, and multimedia content from uploaded files using Google Gemini API.

## ✨ Core Features

### 🤖 AI-Powered Training Discovery
- **Comprehensive Needs Analysis**: Multi-step training assessment and planning
- **Goal-Aligned Content Generation**: AI filters content to match specific training objectives
- **Semantic Content Processing**: Advanced AI analysis for relevant training information
- **Professional Content Cleaning**: Automatically transforms conversational content into professional training material

### 🛤️ Training Pathway Generation
- **Multi-Pathway Creation**: Generate multiple training pathways from single content
- **Section-Based Organization**: Structured learning modules with clear progression
- **Content Type Generation**: Automatic creation of flashcards, quizzes, videos, and more
- **Enhanced Content Mode**: Comprehensive modules with detailed explanations

### 🧠 Mind Mapping & Visualization
- **Markmap Component**: Local mind map visualization
- **Hierarchical Organization**: Structured knowledge representation
- **Interactive Visualization**: Dynamic mind map rendering
- **Export Capabilities**: Share mind maps across platforms

### 💬 AI Chatbot Assistant
- **Context-Aware Responses**: Understands training content and pathway structure
- **File-Based Updates**: Upload new files and update specific modules/sections
- **Content Search**: Search for specific topics across pathways
- **Past Pathway Integration**: Reference and merge content from previous sessions
- **Professional Tone Control**: Adjust module tone and style

### 📁 Advanced File Processing
- **Multi-Format Support**: PDF, DOCX, TXT, MP4, AVI, MOV files
- **Large File Handling**: Backend server for files >200MB
- **Audio/Video Transcription**: Automatic speech-to-text conversion
- **Parallel Processing**: Fast AI processing with multiple workers
- **Fallback Extraction**: Robust content extraction when AI fails

### 🎨 Content Management
- **Editable Pathways**: Modify modules, sections, and content in real-time
- **Module Reordering**: Drag-and-drop module organization
- **Section Management**: Move modules between sections
- **Content Types**: Generate flashcards, quizzes, videos, and documents
- **Export Options**: JSON export for external use

## 🚀 Quick Start

### 1. **Installation**
```bash
git clone <repository-url>
cd Gateway-Content-Automation
pip install -r requirements.txt
```

### 2. **Configuration**
```bash
cp env_template.txt .env
# Edit .env with your API keys:
# GEMINI_API_KEY=your_gemini_api_key
# MINDMEISTER_CLIENT_ID=your_mindmeister_client_id
# MINDMEISTER_CLIENT_SECRET=your_mindmeister_client_secret
```

### 3. **Launch Application**
```bash
# Automatic startup (recommended)
python start_app.py

# Or manual startup
streamlit run app.py
```

## 🔧 Configuration

### Required API Keys

1. **Google Gemini API Key** (Required)
   - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Powers AI content generation and chatbot

2. **Additional APIs** (Optional - for extended features)
   - Various third-party integrations available
   - Enables additional content generation capabilities

## 📋 Feature Breakdown

### Training Discovery Process
1. **Training Context**: Define audience, goals, timeline, and industry
2. **File Inventory**: Upload existing materials and categorize content
3. **Pathway Generation**: AI creates goal-aligned training pathways
4. **Review & Refine**: Edit and customize generated content

### AI Chatbot Capabilities
- **Module Updates**: "Update module 2 with new file"
- **Section Management**: "Add content to safety section"
- **Pathway Integration**: "Update pathway 1 section 3"
- **Content Search**: "Find safety procedures in pathways"
- **Tone Adjustment**: "Make module 1 more professional"
- **Past Pathway Access**: "Show past pathways" or "Integrate from pathway 2"

### Content Processing Features
- **Professional Cleaning**: Removes conversational elements and timestamps
- **Semantic Analysis**: AI understands context and relevance
- **Goal Alignment**: Content filtered to match training objectives
- **Fallback Processing**: Robust extraction when AI unavailable
- **Parallel Processing**: Fast multi-file processing

### Generated Content Types
1. **Training Modules**: Structured learning content
2. **Interactive Flashcards**: Memory aids for key concepts
3. **Assessment Quizzes**: Knowledge testing materials
4. **Document Templates**: Professional training materials
5. **Mind Maps**: Visual knowledge organization
6. **Content Scripts**: Multimedia content preparation

## 🎯 Use Cases

### Corporate Training
- **Employee Onboarding**: Create structured training pathways
- **Process Training**: Document procedures and workflows
- **Compliance Training**: Generate regulatory training materials
- **Skill Development**: Build competency-based training

### Educational Content
- **Course Development**: Transform materials into structured courses
- **Study Materials**: Create comprehensive learning resources
- **Knowledge Management**: Organize and present information
- **Assessment Creation**: Generate quizzes and evaluations

### Content Creation
- **Training Documentation**: Create professional training manuals
- **Presentations**: Generate slide content and materials
- **Interactive Learning**: Build engaging training experiences
- **Content Scripts**: Prepare multimedia content outlines

## 💡 Best Practices

### Content Preparation
1. **Quality Source Materials**: Use well-structured documents
2. **Clear Training Goals**: Define specific learning objectives
3. **Audience Definition**: Specify target learner characteristics
4. **Industry Context**: Provide relevant industry information

### AI Chatbot Usage
1. **Be Specific**: "Update module 2 with new safety procedures"
2. **Use File Uploads**: Upload files before making update requests
3. **Reference Past Content**: "Integrate from pathway 1 section 2"
4. **Search for Content**: "Find quality control procedures"

### Pathway Management
1. **Review Generated Content**: Check AI-generated pathways
2. **Customize Modules**: Edit titles, descriptions, and content
3. **Reorganize Structure**: Move modules between sections
4. **Export Results**: Save pathways for external use

## 🔒 Privacy & Security

- **Local Processing**: File processing happens on your system
- **Secure API Calls**: Encrypted communication with AI services
- **Temporary Storage**: Content not permanently stored
- **Environment Variables**: API keys secured in .env file

## 🛠️ Technical Architecture

### Frontend
- **Streamlit**: Modern web interface
- **Real-time Updates**: Live content editing and preview
- **Responsive Design**: Works on desktop and mobile

### Backend
- **FastAPI Server**: Large file upload handling
- **File Management**: Secure storage and retrieval
- **CORS Support**: Cross-origin request handling

### AI Integration
- **Google Gemini**: Advanced content generation and analysis
- **Parallel Processing**: Multi-threaded AI operations
- **Fallback Systems**: Robust error handling and recovery
- **Caching**: Optimized API call management

### Content Processing
- **Multi-format Support**: PDF, DOCX, TXT, audio, video
- **Professional Cleaning**: Conversational content transformation
- **Semantic Analysis**: Context-aware content understanding
- **Goal Alignment**: Training objective filtering

## 📊 Performance Features

- **Parallel Processing**: Multiple AI workers for speed
- **Caching System**: Reduces API calls and improves performance
- **Fallback Extraction**: Works when AI is unavailable
- **Large File Support**: Handles files up to several GB
- **Real-time Updates**: Instant content modification

## 🔄 Recent Updates

### v3.0 - AI Chatbot & Professional Content
- **AI Chatbot**: Context-aware assistant for pathway management
- **Professional Content Cleaning**: Transform conversational content
- **File-Based Updates**: Upload files and update specific modules
- **Content Search**: Find topics across pathways
- **Past Pathway Integration**: Reference previous sessions

### v2.0 - Enhanced Pathway Generation
- **Multi-Pathway Creation**: Generate multiple training pathways
- **Enhanced Content Mode**: More comprehensive modules
- **Content Type Generation**: Automatic flashcard/quiz creation
- **Semantic Analysis**: Advanced AI content understanding

### v1.0 - Core Features
- **Training Discovery**: Comprehensive needs analysis
- **Mind Mapping**: MindMeister integration
- **File Processing**: Multi-format support
- **Basic Pathway Generation**: AI-powered content creation

## 📞 Support & Troubleshooting

### Common Issues
1. **API Key Configuration**: Ensure all API keys are properly set
2. **File Upload Problems**: Check file format and size limits
3. **AI Processing Errors**: Verify internet connection and API quotas
4. **Backend Connection**: Ensure backend server is running

### Getting Help
1. Check the troubleshooting documentation
2. Review API key configuration
3. Verify all dependencies are installed
4. Test with smaller files first

## 🎯 Roadmap

### Upcoming Features
- **Advanced Content Generation**: More content creation options
- **Collaborative Editing**: Multi-user pathway editing
- **Advanced Analytics**: Training effectiveness tracking
- **Mobile App**: Native mobile application
- **Integration APIs**: Connect with LMS platforms

---

**Note**: This platform requires valid API keys for full functionality. The AI chatbot and content generation features require a Google Gemini API subscription. 