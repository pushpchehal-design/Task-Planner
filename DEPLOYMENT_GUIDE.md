# 🚀 Streamlit Cloud Deployment Guide

## 📋 Prerequisites
- GitHub repository with your code
- Google Gemini API key
- Streamlit Cloud account

## 🔑 Setting Up API Key for Deployment

### Step 1: Get Your Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### Step 2: Deploy to Streamlit Cloud

#### Option A: Deploy via Streamlit Cloud Website
1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Select your repository**: `Task-Planner`
5. **Set main file path**: `app.py`
6. **Click "Deploy"**

#### Option B: Deploy via GitHub Integration
1. **Push your code to GitHub**
2. **Go to Streamlit Cloud**
3. **Connect your repository**
4. **Deploy the app**

### Step 3: Configure API Key in Streamlit Cloud

#### Method 1: Using Streamlit Cloud Secrets
1. **Go to your deployed app** on Streamlit Cloud
2. **Click the "Settings" button** (⚙️)
3. **Go to "Secrets" tab**
4. **Add your API key**:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```
5. **Click "Save"**

#### Method 2: Using Environment Variables
1. **In Streamlit Cloud settings**
2. **Go to "Environment variables"**
3. **Add**: `GEMINI_API_KEY` = `your_actual_api_key_here`
4. **Save changes**

### Step 4: Restart Your App
1. **Go to your app's main page**
2. **Click "Restart app"** in the settings
3. **Wait for the app to restart**

## 🔍 Troubleshooting Deployment Issues

### API Key Not Working
- **Check**: API key is correctly set in Streamlit secrets
- **Verify**: No extra spaces or quotes in the API key
- **Test**: API key works locally first

### Model Not Found Error
- **Check**: App is using the latest code with model fixes
- **Verify**: Dependencies are installed correctly
- **Restart**: The app after making changes

### App Not Loading
- **Check**: All files are pushed to GitHub
- **Verify**: `requirements.txt` includes all dependencies
- **Check**: No syntax errors in the code

## 📁 Required Files for Deployment

Make sure these files are in your repository:
```
Task-Planner/
├── app.py                 # Main application
├── ai_service.py          # AI service module
├── requirements.txt       # Dependencies
├── .streamlit/
│   ├── config.toml       # Streamlit configuration
│   └── secrets.toml      # Local secrets (don't commit)
├── README.md             # Documentation
└── setup_instructions.md # Setup guide
```

## 🚀 Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` updated with all dependencies
- [ ] API key configured in Streamlit Cloud secrets
- [ ] App deployed and accessible
- [ ] AI features working in deployed app
- [ ] No errors in the logs

## 🔒 Security Best Practices

- **Never commit API keys** to GitHub
- **Use Streamlit secrets** for sensitive data
- **Rotate API keys** regularly
- **Monitor usage** to prevent unexpected charges

## 📞 Support

If you encounter issues:
1. Check the Streamlit Cloud logs
2. Verify your API key is working
3. Test locally first
4. Check the troubleshooting section above

---

**Your AI Task Planner should now work perfectly on Streamlit Cloud!** 🎯✨
