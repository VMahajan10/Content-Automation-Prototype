# Environment Variables Setup

Create a `.env` file in your project root with the following variables:

## Required Variables

### 1. Gemini API Key
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
**How to get it:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key and paste it in your `.env` file

### 2. Google Cloud Project ID (for Veo2)
```
GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project_id
```
**How to get it:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Copy the Project ID from the top of the console
4. Paste it in your `.env` file

### 3. Google Cloud Location (optional)
```
GOOGLE_CLOUD_LOCATION=us-central1
```
This defaults to `us-central1` if not set.

## Example .env file:
```
GEMINI_API_KEY=AIzaSyC...
GOOGLE_CLOUD_PROJECT_ID=my-project-123456
GOOGLE_CLOUD_LOCATION=us-central1
```

## After setting up:
1. Save the `.env` file
2. Restart your Streamlit app
3. The warnings should disappear 