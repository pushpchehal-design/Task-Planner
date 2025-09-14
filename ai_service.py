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
        
        # Configure the API
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            st.sidebar.success("✅ AI Service Ready")
        except Exception as e:
            st.sidebar.error(f"❌ AI Service Error: {str(e)}")
            self.model = None
    
    def generate_milestones(self, task_name: str, category: str, start_date: datetime, end_date: datetime, additional_context: str = ""):
        """Generate AI-powered milestones for a task"""
        
        if not self.model:
            return self._get_fallback_milestones(task_name, category)
        
        try:
            # Calculate task duration
            duration_days = (end_date - start_date).days
            
            # Create the prompt
            prompt = f"""
            Break down this task into 3-5 specific, actionable steps: "{task_name}"
            
            Task Details:
            - Category: {category}
            - Total time available: {duration_days} days
            - Additional context: {additional_context}
            
            Create specific action steps that someone would actually do to complete this task. Each step should be a concrete action, not a category or date.
            
            Format your response as a simple numbered list:
            
            1. [Specific action step] - [X days]
            2. [Specific action step] - [X days]
            3. [Specific action step] - [X days]
            4. [Specific action step] - [X days]
            5. [Specific action step] - [X days]
            
            Examples of GOOD milestones:
            - "Research and gather materials" - 2 days
            - "Practice basic skills" - 3 days
            - "Complete hands-on training" - 4 days
            - "Take final assessment" - 1 day
            
            Examples of BAD milestones (DO NOT USE):
            - "Category" - 1 day
            - "Start Date" - 1 day
            - "Total Duration" - 1 day
            
            Make sure the total days add up to {duration_days} days.
            """
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response.text:
                # Debug: Show raw response in sidebar
                st.sidebar.text_area("AI Response:", response.text, height=150)
                return self._parse_ai_response(response.text, task_name)
            else:
                return self._get_fallback_milestones(task_name, category)
                
        except Exception as e:
            return self._get_fallback_milestones(task_name, category)
    
    def _parse_ai_response(self, response_text: str, task_name: str):
        """Parse AI response into milestone format with time allocation"""
        milestones = []
        lines = response_text.strip().split('\n')
        
        milestone_id = 1
        for line in lines:
            line = line.strip()
            # Skip empty lines and headers
            if not line or line.startswith('#') or line.startswith('*') or line.startswith('**'):
                continue
            
            # Clean up the line
            milestone_name = line
            estimated_days = 1  # Default to 1 day
            
            # Remove common prefixes
            for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '•', '*']:
                if milestone_name.startswith(prefix):
                    milestone_name = milestone_name[len(prefix):].strip()
            
            # Extract time allocation if present (e.g., "Task Name - 3 days")
            if ' - ' in milestone_name:
                parts = milestone_name.split(' - ')
                milestone_name = parts[0].strip()
                time_part = parts[1].strip() if len(parts) > 1 else "1 day"
                
                # Extract number from time part
                import re
                time_match = re.search(r'(\d+)', time_part)
                if time_match:
                    estimated_days = int(time_match.group(1))
            
            # Extract name if there's a colon
            if ':' in milestone_name:
                milestone_name = milestone_name.split(':')[0].strip()
            
            # Skip if it's still empty or too short
            if len(milestone_name) < 3:
                continue
            
            # Filter out bad milestone names (metadata fields)
            bad_names = ['category', 'total duration', 'start date', 'end date', 'additional context', 'task details', 'requirements', 'examples']
            if milestone_name.lower().strip() in bad_names:
                continue
            
            # Skip if it contains metadata keywords
            if any(keyword in milestone_name.lower() for keyword in ['category:', 'duration:', 'date:', 'context:', 'details:']):
                continue
            
            milestones.append({
                'id': milestone_id,
                'name': milestone_name,
                'priority': 'Medium',
                'progress': 0,
                'completed': False,
                'estimated_days': estimated_days,
                'description': f"AI-generated milestone for {task_name} (Estimated: {estimated_days} day{'s' if estimated_days > 1 else ''})"
            })
            milestone_id += 1
        
        # If we didn't get any milestones, use fallback
        if len(milestones) == 0:
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
                'estimated_days': 2,
                'description': f'Initial research and planning phase for {task_name} (Estimated: 2 days)'
            },
            {
                'id': 2,
                'name': f'Implementation of {task_name}',
                'priority': 'High',
                'progress': 0,
                'completed': False,
                'estimated_days': 5,
                'description': f'Main implementation work for {task_name} (Estimated: 5 days)'
            },
            {
                'id': 3,
                'name': f'Review and Finalize {task_name}',
                'priority': 'Medium',
                'progress': 0,
                'completed': False,
                'estimated_days': 3,
                'description': f'Final review and completion of {task_name} (Estimated: 3 days)'
            }
        ]
