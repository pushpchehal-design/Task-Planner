# 🚀 AI Task Planner Setup Instructions

## 🔑 Google Gemini API Setup

### Step 1: Get Your API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### Step 2: Configure API Key

#### Option A: Environment Variable (Recommended for Local Development)
```bash
# Create a .env file in your project directory
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

#### Option B: Streamlit Secrets (For Deployment)
1. Create a `.streamlit/secrets.toml` file:
```toml
GEMINI_API_KEY = "your_actual_api_key_here"
```

#### Option C: System Environment Variable
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

## 🛠️ Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```

## 🎯 Features Enabled with AI

### ✅ With API Key:
- **Intelligent Milestone Generation**: AI analyzes your task and creates context-aware milestones
- **Smart Task Breakdown**: Considers task complexity, category, and duration
- **Priority Assignment**: AI assigns high/medium/low priorities to milestones
- **Dependency Mapping**: Identifies which milestones depend on others
- **Personalized Insights**: AI-generated productivity recommendations
- **Context-Aware Suggestions**: Uses additional context you provide

### ⚠️ Without API Key:
- **Fallback Milestones**: Basic milestone generation based on task type
- **Generic Insights**: Standard productivity tips
- **Limited Intelligence**: No context-aware analysis

## 🔧 Troubleshooting

### API Key Issues
- **Error**: "API key not found"
  - **Solution**: Ensure your API key is properly set in environment variables or secrets
- **Error**: "Invalid API key"
  - **Solution**: Verify your API key is correct and active

### Rate Limiting
- **Error**: "Rate limit exceeded"
  - **Solution**: Wait a few minutes before making more requests

### Network Issues
- **Error**: "Connection failed"
  - **Solution**: Check your internet connection and try again

## 📊 API Usage

The app uses Google's Gemini API for:
- Task milestone generation
- Productivity insights
- Smart recommendations

**Cost**: Google Gemini API offers free tier with generous limits for personal use.

## 🚀 Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Connect to Streamlit Cloud
3. Add your API key to Streamlit secrets
4. Deploy!

### Local Production
1. Set environment variables
2. Run with production settings
3. Use reverse proxy for HTTPS

## 🔒 Security Notes

- **Never commit API keys** to version control
- **Use environment variables** or secrets management
- **Rotate API keys** regularly
- **Monitor usage** to prevent unexpected charges

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify your API key setup
3. Review the error messages
4. Check Google AI Studio documentation

---

**Your AI Task Planner is now ready with real AI intelligence!** 🎯✨
