import google.generativeai as genai
import streamlit as st
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AITaskPlanner:
    def __init__(self):
        """Initialize the AI service with Gemini API"""
        # Try environment variables first (for local development), then Streamlit secrets (for deployment)
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            try:
                self.api_key = st.secrets.get('GEMINI_API_KEY')
            except:
                self.api_key = None
        
        # Debug API key status
        if self.api_key:
            # Show first and last 4 characters for debugging (masked)
            masked_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if len(self.api_key) > 8 else "***"
            st.sidebar.info(f"API Key found: {masked_key}")
            st.sidebar.info(f"Key length: {len(self.api_key)}")
            st.sidebar.info(f"Key source: {'Environment' if os.getenv('GEMINI_API_KEY') else 'Streamlit Secrets'}")
        else:
            st.sidebar.error("❌ No API key found!")
            st.sidebar.error(f"Env var exists: {bool(os.getenv('GEMINI_API_KEY'))}")
            try:
                st.sidebar.error(f"Secrets exist: {bool(st.secrets.get('GEMINI_API_KEY'))}")
            except:
                st.sidebar.error("Secrets: Not accessible")
        
        if self.api_key:
            st.sidebar.info("🔧 Configuring Gemini API...")
            genai.configure(api_key=self.api_key)
            st.sidebar.info("✅ API configured successfully")
            
            # List available models for debugging
            try:
                st.sidebar.info("🔍 Listing available models...")
                models = genai.list_models()
                available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
                st.sidebar.info(f"✅ Found {len(available_models)} models")
                st.sidebar.info(f"Available models: {available_models[:3]}...")  # Show first 3
                
                # Try different model names - prioritize working models
                model_name = None
                
                # Try different model variations - prioritize flash models (higher free tier limits)
                model_candidates = [
                    'models/gemini-1.5-flash',      # Higher free tier limits
                    'models/gemini-1.5-flash-latest', # Latest flash model
                    'models/gemini-1.0-pro',        # Legacy model with different quotas
                    'gemini-1.5-flash',
                    'gemini-1.5-flash-latest',
                    'gemini-1.0-pro',
                    'models/gemini-1.5-pro',        # Lower priority due to quota limits
                    'models/gemini-1.5-pro-latest',
                    'gemini-1.5-pro'
                ]
                
                for candidate in model_candidates:
                    if candidate in available_models:
                        model_name = candidate
                        break
                
                # If no specific model found, use the first available
                if not model_name and available_models:
                    model_name = available_models[0]
                elif not model_name:
                    model_name = 'models/gemini-1.5-flash'  # Default fallback
                
                self.model = genai.GenerativeModel(model_name)
                st.sidebar.success(f"Using model: {model_name}")
                
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower() or "429" in error_msg:
                    st.sidebar.warning("⚠️ API quota exceeded. Using fallback milestones.")
                    st.sidebar.info("💡 Try again later or upgrade your API plan")
                else:
                    st.sidebar.error(f"Error listing models: {error_msg}")
                # Fallback to default
                self.model = genai.GenerativeModel('models/gemini-1.5-flash')
        else:
            self.model = None
            st.warning("⚠️ Gemini API key not found. Please set GEMINI_API_KEY in your environment variables or Streamlit secrets.")
    
    def generate_milestones(self, task_name: str, category: str, start_date: datetime, end_date: datetime, 
                          additional_context: str = "") -> List[Dict[str, Any]]:
        """
        Generate AI-powered milestones for a task using Gemini API
        
        Args:
            task_name: Name of the task
            category: Category of the task (Personal, Official, etc.)
            start_date: Start date of the task
            end_date: End date of the task
            additional_context: Any additional context about the task
            
        Returns:
            List of milestone dictionaries
        """
        if not self.model:
            return self._fallback_milestones(task_name, category, start_date, end_date)
        
        try:
            # Calculate duration
            duration_days = (end_date - start_date).days
            
            # Create the prompt for Gemini
            prompt = self._create_milestone_prompt(task_name, category, duration_days, additional_context)
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response
            milestones = self._parse_ai_response(response.text, duration_days)
            
            return milestones
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                st.warning("⚠️ API quota exceeded. Using intelligent fallback milestones.")
                st.info("💡 Your API key is valid but you've hit the free tier limit. Try again later or upgrade your plan.")
            else:
                st.error(f"Error generating AI milestones: {error_msg}")
            return self._fallback_milestones(task_name, category, start_date, end_date)
    
    def _create_milestone_prompt(self, task_name: str, category: str, duration_days: int, 
                               additional_context: str) -> str:
        """Create a detailed prompt for Gemini to generate milestones"""
        
        prompt = f"""
You are an expert project manager and productivity coach. I need you to break down a task into specific, actionable milestones.

Task Details:
- Task Name: "{task_name}"
- Category: {category}
- Duration: {duration_days} days
- Additional Context: {additional_context if additional_context else "None provided"}

Please create a detailed breakdown of this task into 3-8 specific milestones. Each milestone should be:
1. Specific and actionable
2. Realistic for the given timeframe
3. Logically sequenced
4. Include estimated duration in days
5. Include a brief description of what needs to be done

Consider the category and complexity of the task. For example:
- Learning tasks should include research, practice, and assessment phases
- Development tasks should include planning, implementation, testing phases
- Personal tasks should be broken into manageable steps
- Official tasks should consider business requirements and deadlines

Please respond in the following JSON format:
{{
    "milestones": [
        {{
            "name": "Milestone Name",
            "duration": number_of_days,
            "description": "Detailed description of what needs to be done",
            "priority": "high/medium/low",
            "dependencies": ["previous_milestone_name_if_any"]
        }}
    ]
}}

Make sure the total duration of all milestones equals approximately {duration_days} days.
"""
        return prompt
    
    def _parse_ai_response(self, response_text: str, total_duration: int) -> List[Dict[str, Any]]:
        """Parse the AI response and extract milestones"""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                
                milestones = []
                for milestone in data.get('milestones', []):
                    milestones.append({
                        'name': milestone.get('name', 'Unnamed Milestone'),
                        'duration': max(1, milestone.get('duration', 1)),
                        'description': milestone.get('description', 'No description provided'),
                        'priority': milestone.get('priority', 'medium'),
                        'dependencies': milestone.get('dependencies', []),
                        'completed': False
                    })
                
                # Adjust durations to fit the total timeframe
                self._adjust_milestone_durations(milestones, total_duration)
                
                return milestones
                
        except (json.JSONDecodeError, KeyError) as e:
            st.warning(f"Could not parse AI response: {str(e)}")
        
        # Fallback to generic milestones
        return self._fallback_milestones("", "", datetime.now(), datetime.now() + timedelta(days=total_duration))
    
    def _adjust_milestone_durations(self, milestones: List[Dict], total_duration: int):
        """Adjust milestone durations to fit within the total timeframe"""
        current_total = sum(m['duration'] for m in milestones)
        
        if current_total != total_duration:
            scale_factor = total_duration / current_total
            for milestone in milestones:
                milestone['duration'] = max(1, int(milestone['duration'] * scale_factor))
    
    def _fallback_milestones(self, task_name: str, category: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fallback milestone generation when AI is not available"""
        duration = (end_date - start_date).days
        
        # Simple fallback logic
        if "website" in task_name.lower() or "web" in task_name.lower():
            milestones = [
                {"name": "Research and Planning", "duration": max(1, duration // 6), "description": "Research requirements and create project plan", "priority": "high", "dependencies": [], "completed": False},
                {"name": "Design and Wireframing", "duration": max(1, duration // 5), "description": "Create wireframes and design mockups", "priority": "high", "dependencies": ["Research and Planning"], "completed": False},
                {"name": "Frontend Development", "duration": max(2, duration // 3), "description": "Build user interface and frontend components", "priority": "medium", "dependencies": ["Design and Wireframing"], "completed": False},
                {"name": "Backend Development", "duration": max(2, duration // 4), "description": "Implement server-side functionality", "priority": "medium", "dependencies": ["Frontend Development"], "completed": False},
                {"name": "Testing and Debugging", "duration": max(1, duration // 6), "description": "Test functionality and fix bugs", "priority": "high", "dependencies": ["Backend Development"], "completed": False},
                {"name": "Deployment and Launch", "duration": max(1, duration // 8), "description": "Deploy to production and launch", "priority": "high", "dependencies": ["Testing and Debugging"], "completed": False}
            ]
        else:
            # Generic milestones
            milestone_count = min(6, max(3, duration // 3))
            milestone_duration = duration // milestone_count
            
            milestone_names = [
                "Planning and Research",
                "Initial Setup",
                "Core Development",
                "Testing and Refinement",
                "Final Review",
                "Completion"
            ]
            
            milestones = []
            for i in range(milestone_count):
                milestones.append({
                    "name": milestone_names[i] if i < len(milestone_names) else f"Milestone {i+1}",
                    "duration": max(1, milestone_duration),
                    "description": f"Complete {milestone_names[i].lower() if i < len(milestone_names) else f'milestone {i+1}'}",
                    "priority": "medium",
                    "dependencies": [milestone_names[i-1]] if i > 0 else [],
                    "completed": False
                })
        
        return milestones
    
    def generate_insights(self, tasks_data: Dict) -> List[str]:
        """Generate AI-powered insights about user's productivity patterns"""
        if not self.model:
            return self._fallback_insights()
        
        try:
            # Prepare task data for analysis
            completed_tasks = tasks_data.get('completed_tasks', [])
            active_tasks = tasks_data.get('tasks', [])
            
            if not completed_tasks and not active_tasks:
                return ["Start creating tasks to get personalized insights!"]
            
            # Create prompt for insights
            prompt = self._create_insights_prompt(completed_tasks, active_tasks)
            
            # Generate insights
            response = self.model.generate_content(prompt)
            
            # Parse insights
            insights = self._parse_insights_response(response.text)
            
            return insights
            
        except Exception as e:
            st.error(f"Error generating AI insights: {str(e)}")
            return self._fallback_insights()
    
    def _create_insights_prompt(self, completed_tasks: List, active_tasks: List) -> str:
        """Create prompt for generating productivity insights"""
        
        prompt = f"""
You are a productivity coach analyzing a user's task management patterns. Based on the following data, provide 3-5 actionable insights and recommendations.

Completed Tasks: {len(completed_tasks)}
Active Tasks: {len(active_tasks)}

Task Categories:
- Completed: {[task.get('category', 'Unknown') for task in completed_tasks]}
- Active: {[task.get('category', 'Unknown') for task in active_tasks]}

Please provide insights about:
1. Productivity patterns
2. Category preferences
3. Time management
4. Areas for improvement
5. Personalized recommendations

Format your response as a JSON array of strings:
["Insight 1", "Insight 2", "Insight 3", "Insight 4", "Insight 5"]

Keep insights concise, actionable, and encouraging.
"""
        return prompt
    
    def _parse_insights_response(self, response_text: str) -> List[str]:
        """Parse AI insights response"""
        try:
            # Try to extract JSON array
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                insights = json.loads(json_str)
                return insights if isinstance(insights, list) else [str(insights)]
                
        except (json.JSONDecodeError, KeyError):
            pass
        
        return self._fallback_insights()
    
    def _fallback_insights(self) -> List[str]:
        """Fallback insights when AI is not available"""
        return [
            "💡 You're building great productivity habits!",
            "🎯 Consider breaking down large tasks into smaller milestones",
            "⏰ Try scheduling your most important tasks during your peak hours",
            "📈 Track your progress regularly to stay motivated",
            "🔄 Review and adjust your task estimates based on actual completion times"
        ]
