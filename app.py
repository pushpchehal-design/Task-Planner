import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import uuid
from ai_service import AITaskPlanner

# Page configuration
st.set_page_config(
    page_title="🎯 AI Task Planner",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        border-left-color: #2ca02c;
    }
    .warning-card {
        border-left-color: #ff7f0e;
    }
    .danger-card {
        border-left-color: #d62728;
    }
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Data storage functions
def load_data():
    """Load tasks data from JSON file"""
    if os.path.exists('tasks_data.json'):
        with open('tasks_data.json', 'r') as f:
            return json.load(f)
    return {"tasks": [], "completed_tasks": []}

def save_data(data):
    """Save tasks data to JSON file"""
    with open('tasks_data.json', 'w') as f:
        json.dump(data, f, indent=2, default=str)

# Initialize AI service - removed cache to force reload
def get_ai_service():
    """Get AI service instance"""
    return AITaskPlanner()

def calculate_efficiency_score(tasks_data: Dict) -> float:
    """Calculate overall efficiency score based on task completion patterns"""
    if not tasks_data["completed_tasks"]:
        return 0.0
    
    total_tasks = len(tasks_data["completed_tasks"])
    on_time_tasks = sum(1 for task in tasks_data["completed_tasks"] 
                       if task.get("completed_on_time", True))
    
    # Calculate time accuracy
    time_accuracy = 0
    for task in tasks_data["completed_tasks"]:
        if task.get("estimated_duration") and task.get("actual_duration"):
            accuracy = min(1.0, task["estimated_duration"] / task["actual_duration"])
            time_accuracy += accuracy
    
    time_accuracy = time_accuracy / total_tasks if total_tasks > 0 else 0
    
    # Combine on-time rate and time accuracy
    efficiency = (on_time_tasks / total_tasks * 0.6) + (time_accuracy * 0.4)
    return round(efficiency * 10, 1)

def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 AI Task Planner</h1>', unsafe_allow_html=True)
    
    # Load data
    data = load_data()
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox("Choose a page", [
        "🏠 Dashboard",
        "➕ Create Task", 
        "📋 My Tasks",
        "📊 Analytics & Reports"
    ])
    
    # API Key Management
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔑 AI Configuration")
    
    # Check if API key is configured
    ai_service = get_ai_service()
    if ai_service.api_key:
        st.sidebar.success("✅ Gemini API Connected")
    else:
        st.sidebar.warning("⚠️ API Key Required")
        st.sidebar.markdown("""
        **To enable AI features:**
        1. Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Set environment variable: `GEMINI_API_KEY`
        3. Or add to Streamlit secrets
        """)
    
    # Deploy button in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚀 Deploy to Streamlit")
    if st.sidebar.button("Deploy App", type="primary"):
        st.sidebar.success("🚀 Ready for deployment!")
        st.sidebar.markdown("""
        **Deployment Steps:**
        1. Push code to GitHub
        2. Connect to Streamlit Cloud
        3. Deploy with one click!
        """)
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        show_dashboard(data)
    elif page == "➕ Create Task":
        show_create_task(data)
    elif page == "📋 My Tasks":
        show_my_tasks(data)
    elif page == "📊 Analytics & Reports":
        show_analytics(data)

def show_dashboard(data):
    """Display the main dashboard"""
    st.header("📊 Dashboard Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Tasks", len(data["tasks"]) + len(data["completed_tasks"]))
    
    with col2:
        active_tasks = len(data["tasks"])
        st.metric("🔄 Active Tasks", active_tasks)
    
    with col3:
        completed_tasks = len(data["completed_tasks"])
        st.metric("✅ Completed Tasks", completed_tasks)
    
    with col4:
        efficiency = calculate_efficiency_score(data)
        st.metric("🎯 Efficiency Score", f"{efficiency}/10")
    
    # Recent tasks
    st.subheader("📋 Recent Tasks")
    if data["tasks"]:
        for task in data["tasks"][-5:]:  # Show last 5 tasks
            with st.expander(f"🎯 {task['name']} ({task['category']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Start Date:** {task['start_date']}")
                    st.write(f"**End Date:** {task['end_date']}")
                with col2:
                    progress = task.get('progress', 0)
                    st.progress(progress / 100)
                    st.write(f"**Progress:** {progress}%")
                
                if task.get('milestones'):
                    st.write("**Milestones:**")
                    for i, milestone in enumerate(task['milestones']):
                        status = "✅" if milestone.get('completed', False) else "⏳"
                        st.write(f"{status} {milestone['name']}")
    else:
        st.info("No active tasks. Create your first task to get started!")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Create New Task", type="primary"):
            st.success("✅ Navigate to '➕ Create Task' in the sidebar to start creating your task!")
    
    with col2:
        if st.button("📋 View All Tasks"):
            st.success("✅ Navigate to '📋 My Tasks' in the sidebar to view and manage your tasks!")
    
    with col3:
        if st.button("📊 View Analytics"):
            st.success("✅ Navigate to '📊 Analytics & Reports' in the sidebar to view your productivity insights!")
    
    # Navigation instructions
    st.info("💡 **Tip:** Use the sidebar navigation menu to switch between different sections of the app.")

def show_create_task(data):
    """Display the task creation form"""
    st.header("➕ Create New Task")
    
    with st.form("create_task_form"):
        # Task name
        task_name = st.text_input("📝 Task Name", placeholder="Enter your task name...")
        
        # Category selection
        category = st.selectbox(
            "📂 Category",
            ["Personal", "Official", "Health", "Learning", "Finance", "Other"]
        )
        
        # Date selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("📅 Start Date", value=datetime.now().date())
        with col2:
            end_date = st.date_input("📅 End Date", value=datetime.now().date() + timedelta(days=7))
        
        # Additional context input
        additional_context = st.text_area(
            "💭 Additional Context (Optional)", 
            placeholder="Provide any additional details about your task, goals, or constraints..."
        )
        
        # Submit button
        submitted = st.form_submit_button("🤖 Generate AI Milestones", type="primary")
        
        if submitted:
            if not task_name:
                st.error("Please enter a task name!")
            elif end_date <= start_date:
                st.error("End date must be after start date!")
            else:
                # Get AI service and generate milestones
                ai_service = get_ai_service()
                with st.spinner("🧠 AI is analyzing your task and generating intelligent milestones..."):
                    milestones = ai_service.generate_milestones(task_name, category, start_date, end_date, additional_context)
                
                # Create task object
                task = {
                    "id": str(uuid.uuid4()),
                    "name": task_name,
                    "category": category,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "milestones": [{"name": m["name"], "duration": m["duration"], 
                                  "description": m["description"], "completed": False} for m in milestones],
                    "progress": 0,
                    "status": "active"
                }
                
                # Add to data
                data["tasks"].append(task)
                save_data(data)
                
                st.success("✅ Task created successfully!")
                st.balloons()
                
                # Show generated milestones
                st.subheader("🧠 AI-Generated Milestones")
                for i, milestone in enumerate(milestones):
                    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(milestone.get('priority', 'medium'), "🟡")
                    st.write(f"**{i+1}. {milestone['name']}** {priority_emoji} ({milestone['duration']} days)")
                    st.write(f"   {milestone['description']}")
                    
                    # Show dependencies if any
                    if milestone.get('dependencies'):
                        st.write(f"   📋 *Depends on: {', '.join(milestone['dependencies'])}*")
                
                st.info("🎯 Your task has been created! You can now track your progress in the 'My Tasks' section.")

def show_my_tasks(data):
    """Display all tasks with management options"""
    st.header("📋 My Tasks")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(set([task["category"] for task in data["tasks"]])))
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Active", "Completed"])
    
    # Display tasks
    filtered_tasks = data["tasks"]
    if category_filter != "All":
        filtered_tasks = [task for task in filtered_tasks if task["category"] == category_filter]
    
    if not filtered_tasks:
        st.info("No tasks found. Create your first task to get started!")
        return
    
    for task in filtered_tasks:
        with st.expander(f"🎯 {task['name']} ({task['category']}) - {task['progress']}% Complete"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Start Date:** {task['start_date']}")
                st.write(f"**End Date:** {task['end_date']}")
                st.write(f"**Created:** {task['created_at']}")
                
                # Progress bar
                st.progress(task['progress'] / 100)
                
                # Milestones
                st.write("**Milestones:**")
                for i, milestone in enumerate(task['milestones']):
                    status = "✅" if milestone.get('completed', False) else "⏳"
                    col_m1, col_m2 = st.columns([3, 1])
                    with col_m1:
                        st.write(f"{status} {milestone['name']}")
                    with col_m2:
                        if not milestone.get('completed', False):
                            if st.button(f"Complete", key=f"complete_{task['id']}_{i}"):
                                milestone['completed'] = True
                                # Recalculate progress
                                completed_milestones = sum(1 for m in task['milestones'] if m.get('completed', False))
                                task['progress'] = int((completed_milestones / len(task['milestones'])) * 100)
                                save_data(data)
                                st.rerun()
            
            with col2:
                # Days remaining calculation
                end_date = datetime.strptime(task['end_date'], "%Y-%m-%d").date()
                days_remaining = (end_date - datetime.now().date()).days
                
                if days_remaining > 0:
                    st.metric("Days Remaining", days_remaining)
                else:
                    st.metric("Days Overdue", abs(days_remaining))
                
                # Action buttons
                if st.button("📝 Edit", key=f"edit_{task['id']}"):
                    st.info("Edit functionality coming soon!")
                
                if st.button("🗑️ Delete", key=f"delete_{task['id']}"):
                    data["tasks"] = [t for t in data["tasks"] if t["id"] != task["id"]]
                    save_data(data)
                    st.rerun()
                
                if task['progress'] == 100:
                    if st.button("✅ Mark Complete", key=f"complete_task_{task['id']}"):
                        # Move to completed tasks
                        task['completed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        task['status'] = 'completed'
                        data["completed_tasks"].append(task)
                        data["tasks"] = [t for t in data["tasks"] if t["id"] != task["id"]]
                        save_data(data)
                        st.success("🎉 Task completed!")
                        st.rerun()

def show_analytics(data):
    """Display analytics and reports"""
    st.header("📊 Analytics & Performance Reports")
    
    if not data["completed_tasks"] and not data["tasks"]:
        st.info("No data available yet. Complete some tasks to see analytics!")
        return
    
    # Performance Overview
    st.subheader("📈 Performance Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = len(data["completed_tasks"])
    on_time_tasks = sum(1 for task in data["completed_tasks"] if task.get("completed_on_time", True))
    efficiency = calculate_efficiency_score(data)
    
    with col1:
        st.metric("Total Tasks Completed", total_tasks)
    with col2:
        avg_completion = "85%" if total_tasks > 0 else "0%"
        st.metric("Avg Completion Time", avg_completion)
    with col3:
        on_time_rate = f"{(on_time_tasks/total_tasks*100):.0f}%" if total_tasks > 0 else "0%"
        st.metric("On-Time Rate", on_time_rate)
    with col4:
        st.metric("Efficiency Score", f"{efficiency}/10")
    
    # Category Performance
    st.subheader("🎯 Category Performance")
    if data["completed_tasks"]:
        category_data = {}
        for task in data["completed_tasks"]:
            cat = task["category"]
            if cat not in category_data:
                category_data[cat] = {"total": 0, "completed": 0}
            category_data[cat]["total"] += 1
            category_data[cat]["completed"] += 1
        
        # Create category performance chart
        categories = list(category_data.keys())
        efficiency_scores = [80, 60, 90, 85][:len(categories)]  # Mock data
        
        fig = px.bar(
            x=categories,
            y=efficiency_scores,
            title="Efficiency by Category",
            labels={"x": "Category", "y": "Efficiency Score"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Timeline Analysis
    st.subheader("📅 Timeline Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("This Month", f"{len(data['completed_tasks'])}/{len(data['tasks']) + len(data['completed_tasks'])}")
    with col2:
        st.metric("Last Month", "6/8")
    with col3:
        st.metric("This Week", "4/6")
    
    # AI Insights
    st.subheader("🧠 AI-Powered Insights & Recommendations")
    
    # Generate AI insights
    ai_service = get_ai_service()
    with st.spinner("🧠 Generating personalized insights..."):
        insights = ai_service.generate_insights(data)
    
    for insight in insights:
        st.write(insight)
    
    # Export options
    st.subheader("🔍 Export Reports")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Export to PDF"):
            st.info("PDF export coming soon!")
    
    with col2:
        if st.button("📊 Export to CSV"):
            st.info("CSV export coming soon!")
    
    with col3:
        if st.button("📧 Email Report"):
            st.info("Email report coming soon!")

if __name__ == "__main__":
    main()
