# Setup Instructions

## Google Gemini & Veo2 API Configuration

1. **Get a Google Gemini API Key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy your API key

2. **Set up Google Cloud Project for Veo2:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Vertex AI API
   - Create a service account and download credentials
   - Note your Project ID

3. **Configure Environment Variables:**
   - Create a `.env` file in the project root
   - Add your API keys:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project_id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the App:**
   ```bash
   python3 -m streamlit run app.py
   ```

## Features
- ✅ File upload (.txt, .pdf, .docx)
- ✅ AI-powered content generation using Gemini
- ✅ **Real video generation using Google Veo2**
- ✅ Interactive tabs and accordions
- ✅ Video download functionality
- ✅ Error handling with fallback options 