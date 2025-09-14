import os
import streamlit as st
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AITaskPlanner:
    def __init__(self):
        # Get API key from environment
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            st.error("❌ GEMINI_API_KEY not found in environment variables")
            st.info("Please create a .env file with: GEMINI_API_KEY=your_key_here")
            self.model = None
            return
        
        # Show API key status
        masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if len(self.api_key) > 8 else "***"
        st.sidebar.info(f"🔑 API Key: {masked_key}")
        
        # Configure the API
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            st.sidebar.success("✅ AI Service initialized successfully")
        except Exception as e:
            st.sidebar.error(f"❌ Failed to initialize AI service: {str(e)}")
            self.model = None
    
    def generate_milestones(self, task_name: str, category: str, start_date: datetime, end_date: datetime, additional_context: str = ""):
        """Generate AI-powered milestones for a task"""
        
        if not self.model:
            st.sidebar.warning("⚠️ AI model not available, using fallback milestones")
            return self._get_fallback_milestones(task_name, category)
        
        try:
            # Calculate task duration
            duration_days = (end_date - start_date).days
            
            st.sidebar.info(f"🤖 Generating AI milestones for: {task_name}")
            
            # Create the prompt
            prompt = f"""
            Create a detailed task breakdown for: "{task_name}"
            
            Category: {category}
            Duration: {duration_days} days
            Start Date: {start_date.strftime('%Y-%m-%d')}
            End Date: {end_date.strftime('%Y-%m-%d')}
            
            Additional Context: {additional_context}
            
            Please provide exactly 3-5 specific, actionable milestones. Format each milestone as:
            
            1. [Milestone Name]
            2. [Milestone Name]
            3. [Milestone Name]
            4. [Milestone Name]
            5. [Milestone Name]
            
            Each milestone should be a clear, specific action step for completing "{task_name}".
            Make the milestone names descriptive and actionable.
            """
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response.text:
                st.sidebar.success("✅ AI milestones generated successfully!")
                return self._parse_ai_response(response.text, task_name)
            else:
                st.sidebar.warning("⚠️ Empty AI response, using fallback")
                return self._get_fallback_milestones(task_name, category)
                
        except Exception as e:
            st.sidebar.error(f"❌ AI generation failed: {str(e)}")
            return self._get_fallback_milestones(task_name, category)
    
    def _parse_ai_response(self, response_text: str, task_name: str):
        """Parse AI response into milestone format"""
        milestones = []
        lines = response_text.strip().split('\n')
        
        # Debug: Show the raw AI response
        st.sidebar.text_area("Raw AI Response:", response_text, height=100)
        
        milestone_id = 1
        for line in lines:
            line = line.strip()
            # Skip empty lines and headers
            if not line or line.startswith('#') or line.startswith('*') or line.startswith('**'):
                continue
            
            # Clean up the line
            milestone_name = line
            # Remove common prefixes
            for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '•', '*']:
                if milestone_name.startswith(prefix):
                    milestone_name = milestone_name[len(prefix):].strip()
            
            # Extract name if there's a colon
            if ':' in milestone_name:
                milestone_name = milestone_name.split(':')[0].strip()
            
            # Skip if it's still empty or too short
            if len(milestone_name) < 3:
                continue
            
            milestones.append({
                'id': milestone_id,
                'name': milestone_name,
                'priority': 'Medium',
                'progress': 0,
                'completed': False,
                'description': f"AI-generated milestone for {task_name}"
            })
            milestone_id += 1
        
        # If we didn't get any milestones, use fallback
        if len(milestones) == 0:
            st.sidebar.warning("⚠️ Could not parse AI response, using fallback milestones")
            return self._get_fallback_milestones(task_name, "General")
        
        # Ensure we have at least 3 milestones
        if len(milestones) < 3:
            fallback_milestones = self._get_fallback_milestones(task_name, "General")
            milestones.extend(fallback_milestones[:3-len(milestones)])
        
        return milestones[:5]  # Max 5 milestones
    
    def _get_fallback_milestones(self, task_name: str, category: str):
        """Fallback milestones when AI fails"""
        return [
            {
                'id': 1,
                'name': f'Research and Planning for {task_name}',
                'priority': 'High',
                'progress': 0,
                'completed': False,
                'description': f'Initial research and planning phase for {task_name}'
            },
            {
                'id': 2,
                'name': f'Implementation of {task_name}',
                'priority': 'High',
                'progress': 0,
                'completed': False,
                'description': f'Main implementation work for {task_name}'
            },
            {
                'id': 3,
                'name': f'Review and Finalize {task_name}',
                'priority': 'Medium',
                'progress': 0,
                'completed': False,
                'description': f'Final review and completion of {task_name}'
            }
        ]
