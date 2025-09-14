import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from ai_service import AITaskPlanner

# Page configuration
st.set_page_config(
    page_title="AI Task Planner",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .task-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .milestone-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
    }
    .completed {
        border-left-color: #28a745;
        background: #d4edda;
    }
    .in-progress {
        border-left-color: #ffc107;
        background: #fff3cd;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Load tasks from file
def load_tasks():
    if os.path.exists('tasks_data.json'):
        try:
            with open('tasks_data.json', 'r') as f:
                st.session_state.tasks = json.load(f)
        except:
            st.session_state.tasks = []

# Save tasks to file
def save_tasks():
    with open('tasks_data.json', 'w') as f:
        json.dump(st.session_state.tasks, f, indent=2, default=str)

# Load tasks on startup
load_tasks()

# Initialize AI service
@st.cache_resource
def get_ai_service():
    return AITaskPlanner()

ai_service = get_ai_service()

# Main header
st.markdown('<h1 class="main-header">🤖 AI Task Planner</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Create Task", "My Tasks", "Analytics"])

# Dashboard Page
if page == "Dashboard":
    st.header("📊 Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    total_tasks = len(st.session_state.tasks)
    completed_tasks = len([t for t in st.session_state.tasks if t.get('status') == 'completed'])
    in_progress_tasks = len([t for t in st.session_state.tasks if t.get('status') == 'in_progress'])
    pending_tasks = total_tasks - completed_tasks - in_progress_tasks
    
    with col1:
        st.metric("Total Tasks", total_tasks)
    with col2:
        st.metric("Completed", completed_tasks)
    with col3:
        st.metric("In Progress", in_progress_tasks)
    with col4:
        st.metric("Pending", pending_tasks)
    
    # Recent tasks
    st.subheader("📋 Recent Tasks")
    if st.session_state.tasks:
        recent_tasks = st.session_state.tasks[-5:]  # Last 5 tasks
        for task in reversed(recent_tasks):
            with st.container():
                st.markdown(f"""
                <div class="task-card">
                    <h4>{task['name']}</h4>
                    <p><strong>Category:</strong> {task['category']}</p>
                    <p><strong>Status:</strong> {task.get('status', 'pending').title()}</p>
                    <p><strong>Due:</strong> {task['end_date']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No tasks yet. Create your first task!")

# Create Task Page
elif page == "Create Task":
    st.header("➕ Create New Task")
    
    with st.form("create_task_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            task_name = st.text_input("Task Name", placeholder="Enter task name...")
            category = st.selectbox("Category", ["Personal", "Work", "Health", "Learning", "Finance", "Other"])
        
        with col2:
            start_date = st.date_input("Start Date", value=datetime.now().date())
            end_date = st.date_input("End Date", value=datetime.now().date() + timedelta(days=7))
        
        additional_context = st.text_area("Additional Context (Optional)", 
                                        placeholder="Provide any additional details about this task...")
        
        submitted = st.form_submit_button("Create Task with AI Milestones", type="primary")
        
        if submitted:
            if task_name and start_date and end_date:
                if end_date > start_date:
                    # Generate AI milestones
                    with st.spinner("🤖 Generating AI-powered milestones..."):
                        milestones = ai_service.generate_milestones(
                            task_name, category, start_date, end_date, additional_context
                        )
                    
                    # Create task
                    new_task = {
                        'id': len(st.session_state.tasks) + 1,
                        'name': task_name,
                        'category': category,
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'end_date': end_date.strftime('%Y-%m-%d'),
                        'status': 'pending',
                        'milestones': milestones,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    st.session_state.tasks.append(new_task)
                    save_tasks()
                    
                    st.success(f"✅ Task '{task_name}' created successfully with {len(milestones)} AI-generated milestones!")
                    
                    # Show generated milestones
                    st.subheader("🎯 Generated Milestones")
                    for milestone in milestones:
                        st.markdown(f"""
                        <div class="milestone-item">
                            <strong>{milestone['name']}</strong><br>
                            Priority: {milestone['priority']}<br>
                            {milestone['description']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("End date must be after start date!")
            else:
                st.error("Please fill in all required fields!")

# My Tasks Page
elif page == "My Tasks":
    st.header("📋 My Tasks")
    
    if st.session_state.tasks:
        for task in st.session_state.tasks:
            with st.expander(f"{task['name']} - {task['category']} ({task.get('status', 'pending').title()})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Start Date:** {task['start_date']}")
                    st.write(f"**End Date:** {task['end_date']}")
                    st.write(f"**Status:** {task.get('status', 'pending').title()}")
                
                with col2:
                    if st.button(f"Mark Complete", key=f"complete_{task['id']}"):
                        task['status'] = 'completed'
                        save_tasks()
                        st.rerun()
                
                # Show milestones
                if 'milestones' in task:
                    st.subheader("Milestones")
                    for milestone in task['milestones']:
                        milestone_status = "✅ Completed" if milestone.get('completed', False) else "⏳ Pending"
                        st.write(f"• {milestone['name']} - {milestone_status}")
                        
                        if st.button(f"Toggle Milestone", key=f"milestone_{task['id']}_{milestone['id']}"):
                            milestone['completed'] = not milestone.get('completed', False)
                            save_tasks()
                            st.rerun()
    else:
        st.info("No tasks created yet. Go to 'Create Task' to get started!")

# Analytics Page
elif page == "Analytics":
    st.header("📈 Analytics")
    
    if st.session_state.tasks:
        # Task completion rate
        completed = len([t for t in st.session_state.tasks if t.get('status') == 'completed'])
        total = len(st.session_state.tasks)
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        st.metric("Task Completion Rate", f"{completion_rate:.1f}%")
        
        # Category breakdown
        categories = {}
        for task in st.session_state.tasks:
            cat = task['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            df = pd.DataFrame(list(categories.items()), columns=['Category', 'Count'])
            fig = px.pie(df, values='Count', names='Category', title="Tasks by Category")
            st.plotly_chart(fig, use_container_width=True)
        
        # Status breakdown
        statuses = {}
        for task in st.session_state.tasks:
            status = task.get('status', 'pending')
            statuses[status] = statuses.get(status, 0) + 1
        
        if statuses:
            df_status = pd.DataFrame(list(statuses.items()), columns=['Status', 'Count'])
            fig_status = px.bar(df_status, x='Status', y='Count', title="Tasks by Status")
            st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("No data available yet. Create some tasks to see analytics!")

# Footer
st.markdown("---")
st.markdown("🤖 **AI Task Planner** - Powered by Google Gemini AI")
