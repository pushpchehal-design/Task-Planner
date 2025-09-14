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
            
            🚨 CRITICAL REQUIREMENT: You have exactly {duration_days} days total to complete this task. You MUST distribute ALL {duration_days} days across your milestones. DO NOT leave any days unallocated.
            
            Task Details:
            - Category: {category}
            - Total time available: {duration_days} days (MUST USE ALL {duration_days} DAYS)
            - Additional context: {additional_context}
            
            Create specific action steps that someone would actually do to complete this task. Each step should be a concrete action, not a category or date.
            
            Format your response EXACTLY like this:
            
            1. [Specific action step] - [X days]
            
            2. [Specific action step] - [X days]
            
            3. [Specific action step] - [X days]
            
            4. [Specific action step] - [X days]
            
            5. [Specific action step] - [X days]
            
            🚨 MANDATORY: The sum of all milestone days MUST equal exactly {duration_days} days. NO EXCEPTIONS.
            
            Example for a 10-day task:
            1. Research and planning - 2 days
            2. Initial setup and preparation - 2 days
            3. Main implementation work - 4 days
            4. Testing and refinement - 1 day
            5. Final review and completion - 1 day
            Total: 2+2+4+1+1 = 10 days ✓
            
            Example for a 30-day task:
            1. Research and planning - 5 days
            2. Initial setup and preparation - 5 days
            3. Main implementation work - 15 days
            4. Testing and refinement - 3 days
            5. Final review and completion - 2 days
            Total: 5+5+15+3+2 = 30 days ✓
            
            Example for a 108-day task:
            1. Research and planning - 20 days
            2. Initial setup and preparation - 25 days
            3. Main implementation work - 45 days
            4. Testing and refinement - 12 days
            5. Final review and completion - 6 days
            Total: 20+25+45+12+6 = 108 days ✓
            
            For your {duration_days}-day task, distribute the time appropriately across milestones. The total MUST equal {duration_days} days.
            """
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            if response.text:
                # Show AI response in sidebar for reference
                st.sidebar.markdown("### 🤖 AI Response")
                st.sidebar.text_area("AI Generated Content:", response.text, height=200, key="ai_response", label_visibility="collapsed")
                return self._parse_ai_response(response.text, task_name, duration_days)
            else:
                return self._get_fallback_milestones(task_name, category, duration_days)
                
        except Exception as e:
            return self._get_fallback_milestones(task_name, category)
    
    def _parse_ai_response(self, response_text: str, task_name: str, expected_total_days: int):
        """Parse AI response into milestone format with time allocation"""
        import re
        milestones = []
        lines = response_text.strip().split('\n')
        
        milestone_id = 1
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('#'):
                continue
            
            # Skip lines that are just asterisks or formatting
            if line.strip() in ['*', '**', '***'] or line.strip().startswith('*') and len(line.strip()) <= 3:
                continue
            
            # Skip lines that are clearly not milestones
            if any(skip_word in line.lower() for skip_word in ['example', 'total:', 'requirements', 'important:', 'format', 'critical', 'for your', 'distribute the time', 'break down', 'task details', 'additional context']):
                continue
            
            # Look for numbered list items (1., 2., 3., etc.)
            if re.match(r'^\d+\.', line):
                # Extract milestone name and time
                milestone_name = line
                estimated_days = 1  # Default to 1 day
                
                # Remove the number prefix (1., 2., etc.)
                milestone_name = re.sub(r'^\d+\.\s*', '', milestone_name)
                
                # Look for time pattern: " - X days" or " - X day"
                time_match = re.search(r'-\s*(\d+)\s*days?', line.lower())
                if time_match:
                    estimated_days = int(time_match.group(1))
                    # Remove the time part from the name
                    milestone_name = re.sub(r'\s*-\s*\d+\s*days?', '', milestone_name, flags=re.IGNORECASE)
                
                # Clean up the milestone name
                milestone_name = milestone_name.strip()
                
                # Skip if it's still empty or too short
                if len(milestone_name) < 3:
                    continue
                
                # Filter out bad milestone names
                bad_names = ['category', 'total duration', 'start date', 'end date', 'additional context', 'task details', 'requirements', 'examples', 'important', 'format', 'critical']
                if milestone_name.lower().strip() in bad_names:
                    continue
                
                # Skip if it contains metadata keywords
                if any(keyword in milestone_name.lower() for keyword in ['category:', 'duration:', 'date:', 'context:', 'details:', 'example', 'total:', 'requirements']):
                    continue
                
                milestones.append({
                    'id': milestone_id,
                    'name': milestone_name,
                    'priority': 'Medium',
                    'progress': 0,
                    'completed': False,
                    'estimated_days': estimated_days,
                    'description': line.strip()
                })
                milestone_id += 1
        
        # If we didn't get any milestones, use fallback
        if len(milestones) == 0:
            return self._get_fallback_milestones(task_name, "General", expected_total_days)
        
        # Validate total time allocation
        total_allocated = sum(milestone.get('estimated_days', 1) for milestone in milestones)
        
        # If total doesn't match expected, adjust the last milestone
        if total_allocated != expected_total_days and len(milestones) > 0:
            difference = expected_total_days - total_allocated
            milestones[-1]['estimated_days'] = max(1, milestones[-1]['estimated_days'] + difference)
            milestones[-1]['description'] = f"AI-generated milestone for {task_name} (Estimated: {milestones[-1]['estimated_days']} day{'s' if milestones[-1]['estimated_days'] > 1 else ''})"
        
        # Ensure we have at least 3 milestones
        if len(milestones) < 3:
            fallback_milestones = self._get_fallback_milestones(task_name, "General", expected_total_days)
            milestones.extend(fallback_milestones[:3-len(milestones)])
        
        return milestones[:5]  # Max 5 milestones
    
    def _get_fallback_milestones(self, task_name: str, category: str, total_days: int = 10):
        """Fallback milestones when AI fails"""
        # Distribute days across milestones
        milestone1_days = max(1, total_days // 4)
        milestone2_days = max(1, total_days // 2)
        milestone3_days = max(1, total_days - milestone1_days - milestone2_days)
        
        return [
            {
                'id': 1,
                'name': f'Research and Planning for {task_name}',
                'priority': 'High',
                'progress': 0,
                'completed': False,
                'estimated_days': milestone1_days,
                'description': f'Initial research and planning phase for {task_name} (Estimated: {milestone1_days} day{"s" if milestone1_days > 1 else ""})'
            },
            {
                'id': 2,
                'name': f'Implementation of {task_name}',
                'priority': 'High',
                'progress': 0,
                'completed': False,
                'estimated_days': milestone2_days,
                'description': f'Main implementation work for {task_name} (Estimated: {milestone2_days} day{"s" if milestone2_days > 1 else ""})'
            },
            {
                'id': 3,
                'name': f'Review and Finalize {task_name}',
                'priority': 'Medium',
                'progress': 0,
                'completed': False,
                'estimated_days': milestone3_days,
                'description': f'Final review and completion of {task_name} (Estimated: {milestone3_days} day{"s" if milestone3_days > 1 else ""})'
            }
        ]
