#!/usr/bin/env python3
"""
Simple script to test your Gemini API key
Run this to verify your API key is working before using the main app
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key():
    """Test if the API key is valid"""
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ No API key found!")
        print("Please set GEMINI_API_KEY environment variable")
        print("Example: export GEMINI_API_KEY='your_key_here'")
        return False
    
    print(f"🔑 API Key found: {api_key[:4]}...{api_key[-4:]}")
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Test by listing models
        print("🧠 Testing API connection...")
        models = genai.list_models()
        
        # Filter for generateContent models
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        print(f"✅ API key is valid!")
        print(f"📋 Available models: {len(available_models)}")
        
        for model in available_models[:5]:  # Show first 5 models
            print(f"   - {model}")
        
        if len(available_models) > 5:
            print(f"   ... and {len(available_models) - 5} more")
        
        # Test a simple generation with Flash model (higher free tier limits)
        print("\n🧪 Testing model generation...")
        
        # Try Flash model first (higher free tier limits)
        flash_models = [m for m in available_models if 'flash' in m.lower()]
        if flash_models:
            test_model = flash_models[0]
            print(f"   Using Flash model: {test_model}")
        else:
            test_model = available_models[0]
            print(f"   Using model: {test_model}")
        
        model = genai.GenerativeModel(test_model)
        response = model.generate_content("Say 'Hello, API is working!'")
        print(f"✅ Generation test successful: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ API key test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Gemini API Key...")
    print("=" * 50)
    
    success = test_api_key()
    
    print("=" * 50)
    if success:
        print("🎉 Your API key is working perfectly!")
        print("You can now use the AI Task Planner app.")
    else:
        print("💡 Troubleshooting tips:")
        print("1. Get a new API key from: https://makersuite.google.com/app/apikey")
        print("2. Make sure the key is set correctly:")
        print("   export GEMINI_API_KEY='your_actual_key_here'")
        print("3. Check that the key doesn't have extra spaces or quotes")
        print("4. Verify your Google account has access to Gemini API")
