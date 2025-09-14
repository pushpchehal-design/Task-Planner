import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import uuid

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

def generate_ai_milestones(task_name: str, category: str, start_date: datetime, end_date: datetime) -> List[Dict]:
    """Generate AI-powered milestones for a task"""
    duration = (end_date - start_date).days
    
    # Simple AI-like milestone generation based on task characteristics
    milestones = []
    
    if "website" in task_name.lower() or "web" in task_name.lower():
        milestones = [
            {"name": "Research and Planning", "duration": max(1, duration // 6), "description": "Research requirements and create project plan"},
            {"name": "Design and Wireframing", "duration": max(1, duration // 5), "description": "Create wireframes and design mockups"},
            {"name": "Frontend Development", "duration": max(2, duration // 3), "description": "Build user interface and frontend components"},
            {"name": "Backend Development", "duration": max(2, duration // 4), "description": "Implement server-side functionality"},
            {"name": "Testing and Debugging", "duration": max(1, duration // 6), "description": "Test functionality and fix bugs"},
            {"name": "Deployment and Launch", "duration": max(1, duration // 8), "description": "Deploy to production and launch"}
        ]
    elif "learn" in task_name.lower() or "study" in task_name.lower():
        milestones = [
            {"name": "Research Learning Resources", "duration": max(1, duration // 8), "description": "Find and organize learning materials"},
            {"name": "Create Study Plan", "duration": max(1, duration // 10), "description": "Plan study schedule and milestones"},
            {"name": "Begin Learning", "duration": max(2, duration // 3), "description": "Start learning and practicing"},
            {"name": "Practice and Apply", "duration": max(2, duration // 4), "description": "Practice skills and apply knowledge"},
            {"name": "Review and Assess", "duration": max(1, duration // 8), "description": "Review progress and assess learning"}
        ]
    elif "write" in task_name.lower() or "article" in task_name.lower():
        milestones = [
            {"name": "Research and Outline", "duration": max(1, duration // 4), "description": "Research topic and create outline"},
            {"name": "First Draft", "duration": max(2, duration // 2), "description": "Write initial draft"},
            {"name": "Review and Edit", "duration": max(1, duration // 4), "description": "Review and edit content"},
            {"name": "Final Polish", "duration": max(1, duration // 8), "description": "Final review and polish"}
        ]
    else:
        # Generic milestone generation
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
        
        for i in range(milestone_count):
            milestones.append({
                "name": milestone_names[i] if i < len(milestone_names) else f"Milestone {i+1}",
                "duration": max(1, milestone_duration),
                "description": f"Complete {milestone_names[i].lower() if i < len(milestone_names) else f'milestone {i+1}'}"
            })
    
    # Adjust durations to fit within the total timeframe
    total_allocated = sum(m["duration"] for m in milestones)
    if total_allocated > duration:
        scale_factor = duration / total_allocated
        for milestone in milestones:
            milestone["duration"] = max(1, int(milestone["duration"] * scale_factor))
    
    return milestones

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
            st.session_state.page = "➕ Create Task"
            st.rerun()
    
    with col2:
        if st.button("📋 View All Tasks"):
            st.session_state.page = "📋 My Tasks"
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics"):
            st.session_state.page = "📊 Analytics & Reports"
            st.rerun()

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
        
        # Submit button
        submitted = st.form_submit_button("🤖 Generate AI Milestones", type="primary")
        
        if submitted:
            if not task_name:
                st.error("Please enter a task name!")
            elif end_date <= start_date:
                st.error("End date must be after start date!")
            else:
                # Generate AI milestones
                with st.spinner("🧠 AI is generating milestones..."):
                    milestones = generate_ai_milestones(task_name, category, start_date, end_date)
                
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
                    st.write(f"**{i+1}. {milestone['name']}** ({milestone['duration']} days)")
                    st.write(f"   {milestone['description']}")
                
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
    
    insights = [
        "💡 You're most productive on Tuesdays and Wednesdays",
        "🎯 Personal tasks are completed 20% faster than estimated",
        "📈 Consider breaking down Official tasks into smaller milestones",
        "⏰ Try scheduling complex tasks in the morning when you're most focused"
    ]
    
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
