# Setup Instructions

## OpenAI API Configuration

1. **Get an OpenAI API Key:**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Sign up or log in to your account
   - Navigate to "API Keys" section
   - Create a new API key

2. **Configure Environment Variables:**
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the App:**
   ```bash
   python3 -m streamlit run app.py
   ```

## Features
- ✅ File upload (.txt, .pdf, .docx)
- ✅ AI-powered content generation
- ✅ Interactive tabs and accordions
- ✅ Download functionality
- ✅ Error handling with demo content 