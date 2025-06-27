# 🤖 Automated Content Generator with Vadoo AI

An AI-powered content generation app that creates comprehensive training materials from uploaded files (.txt, .pdf, .docx) using Google Gemini API and Vadoo AI for video generation.

## ✨ Features

- **📄 Multi-format Support**: Upload .txt, .pdf, and .docx files
- **🤖 AI Content Generation**: Powered by Google Gemini 1.5 Pro
- **🎬 AI Video Generation**: Create videos with Vadoo AI
- **📚 Comprehensive Output**: Generate overviews, key points, analysis, applications, flashcards, and visual resources
- **🎥 Interactive Video Creation**: Generate AI videos with voiceover and custom settings
- **🃏 Interactive Flashcards**: Learn with AI-generated flashcards
- **🎨 Visual Resources**: Get suggestions for visual learning materials

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Gateway-Content-Automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env with your API keys
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

## 🔧 Configuration

### Required API Keys

1. **Google Gemini API Key**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add to `.env`: `GEMINI_API_KEY=your_key_here`

2. **Vadoo AI API Key** (Optional - for video generation)
   - Get your API key from [Vadoo AI](https://vadoo.tv)
   - Add to `.env`: `VADOO_API_KEY=your_key_here`

## 📋 Features Breakdown

### Content Processing
- **Multi-format Support**: Handles .txt, .pdf, and .docx files
- **Smart Content Extraction**: Automatically extracts and processes text content
- **AI-powered Analysis**: Uses Gemini to understand and structure content

### Generated Materials
1. **Content Overview**: High-level summary of uploaded content
2. **Key Points**: Main concepts and important takeaways
3. **Detailed Analysis**: In-depth breakdown and insights
4. **Practical Applications**: Real-world usage examples
5. **Interactive Flashcards**: Learning aids for memorization
6. **AI Video Generation**: Create videos with Vadoo AI
7. **Visual Resources**: Suggestions for visual learning materials

### Video Generation Features
- **Vadoo AI Integration**: Professional AI video generation
- **Custom Duration**: 1-10 minute videos
- **Multiple Aspect Ratios**: 16:9, 9:16, 1:1
- **AI Voiceover**: Built-in narration
- **Custom Themes**: Professional styling options
- **Educational Focus**: Optimized for training content

## 🎯 Use Cases

- **Employee Training**: Create onboarding materials from company documents
- **Educational Content**: Generate study materials from textbooks
- **Content Marketing**: Transform blog posts into video content
- **Knowledge Management**: Organize and present information effectively
- **Learning & Development**: Create interactive training modules

## 💡 Tips for Best Results

1. **Quality Input**: Use well-structured source documents
2. **Clear Content**: Ensure uploaded files have clear, readable text
3. **Specific Prompts**: Be specific about your target audience and goals
4. **Video Settings**: Choose appropriate duration and aspect ratio for your content
5. **Iterative Refinement**: Use the generated content as a starting point

## 🔒 Privacy & Security

- All processing happens locally or through secure API calls
- No content is stored permanently
- API keys are kept secure in environment variables
- Generated content is temporary and not saved

## 🛠️ Technical Details

- **Framework**: Streamlit
- **AI Model**: Google Gemini 1.5 Pro
- **Video Generation**: Vadoo AI
- **File Processing**: PyPDF2, python-docx
- **Environment**: Python 3.8+

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API key configuration
3. Ensure all dependencies are installed
4. Check file format compatibility

## 🔄 Updates

- **v2.0**: Added Vadoo AI video generation
- **v1.0**: Initial release with Gemini integration

---

**Note**: This app requires valid API keys for full functionality. Video generation features require a Vadoo AI subscription. 