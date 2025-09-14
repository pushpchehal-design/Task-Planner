import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from ai_service import AITaskPlanner

# Page configuration
st.set_page_config(
    page_title="AI Task Planner - by Pushp Chehal",
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
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        transition: transform 0.2s ease;
    }
    .task-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    .milestone-item {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.2rem;
        border-radius: 10px;
        margin: 0.8rem 0;
        border-left: 4px solid #28a745;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .milestone-item.completed {
        border-left-color: #28a745;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    }
    .milestone-item.in-progress {
        border-left-color: #ffc107;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .stats-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .stats-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .category-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.2rem;
    }
    .category-personal { background: #e3f2fd; color: #1976d2; }
    .category-work { background: #f3e5f5; color: #7b1fa2; }
    .category-health { background: #e8f5e8; color: #388e3c; }
    .category-learning { background: #fff3e0; color: #f57c00; }
    .category-finance { background: #fce4ec; color: #c2185b; }
    .category-other { background: #f5f5f5; color: #616161; }
</style>
""", unsafe_allow_html=True)

# Initialize session state with user-specific data
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# Generate a persistent user ID based on browser/machine
if 'user_id' not in st.session_state:
    import hashlib
    import platform
    import getpass
    import os
    
    try:
        # Create a persistent user ID based on machine info
        machine_info = f"{platform.node()}{getpass.getuser()}{platform.system()}"
        st.session_state.user_id = hashlib.md5(machine_info.encode()).hexdigest()[:8]
    except:
        # Fallback: use environment variables or create a file-based ID
        try:
            fallback_info = f"{os.environ.get('USER', 'user')}{os.environ.get('HOSTNAME', 'host')}"
            st.session_state.user_id = hashlib.md5(fallback_info.encode()).hexdigest()[:8]
        except:
            # Last resort: use a fixed ID for this deployment
            st.session_state.user_id = "default01"

# User-specific file path
def get_user_file_path():
    return f"tasks_data_{st.session_state.user_id}.json"

# Load tasks from user-specific file
def load_tasks():
    file_path = get_user_file_path()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                st.session_state.tasks = json.load(f)
        except:
            st.session_state.tasks = []
    else:
        st.session_state.tasks = []

# Save tasks to user-specific file
def save_tasks():
    file_path = get_user_file_path()
    with open(file_path, 'w') as f:
        json.dump(st.session_state.tasks, f, indent=2, default=str)

# Load tasks on startup
load_tasks()

# Initialize AI service (no caching to ensure updates are deployed)
ai_service = AITaskPlanner()

# Main header
st.markdown('<h1 class="main-header">🤖 AI Task Planner</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("## 🧭 Navigation")
page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Create Task", "My Tasks", "Analytics"])

# Add some spacing
st.sidebar.markdown("---")

# User indicator
st.sidebar.markdown("### 👤 Your Account")
st.sidebar.info(f"User ID: `{st.session_state.user_id}`")
st.sidebar.caption("Your tasks are saved permanently to this machine")

# Add some spacing
st.sidebar.markdown("---")

# Data management
st.sidebar.markdown("### 🗂️ Data Management")
if st.sidebar.button("🗑️ Clear All Tasks", type="secondary"):
    st.session_state.tasks = []
    save_tasks()
    st.sidebar.success("All tasks cleared!")
    st.rerun()

st.sidebar.markdown("---")

# Quick stats in sidebar
if st.session_state.tasks:
    st.sidebar.markdown("### 📊 Quick Stats")
    total_tasks = len(st.session_state.tasks)
    completed_tasks = len([t for t in st.session_state.tasks if t.get('status') == 'completed'])
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Total", total_tasks)
    with col2:
        st.metric("Done", completed_tasks)
    
    if total_tasks > 0:
        completion_rate = (completed_tasks / total_tasks * 100)
        st.sidebar.progress(completion_rate / 100)
        st.sidebar.caption(f"{completion_rate:.1f}% Complete")
    
    st.sidebar.markdown("---")

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
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{total_tasks}</div>
            <div class="stats-label">Total Tasks</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{completed_tasks}</div>
            <div class="stats-label">Completed</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{in_progress_tasks}</div>
            <div class="stats-label">In Progress</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{pending_tasks}</div>
            <div class="stats-label">Pending</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent tasks
    st.subheader("📋 Recent Tasks")
    if st.session_state.tasks:
        recent_tasks = st.session_state.tasks[-5:]  # Last 5 tasks
        for task in reversed(recent_tasks):
            category_class = f"category-{task['category'].lower()}"
            status_emoji = {"completed": "✅", "in_progress": "🔄", "pending": "⏳"}.get(task.get('status', 'pending'), "⏳")
            
            with st.container():
                st.markdown(f"""
                <div class="task-card">
                    <h4>{task['name']}</h4>
                    <p><span class="category-badge {category_class}">{task['category']}</span></p>
                    <p><strong>Status:</strong> {status_emoji} {task.get('status', 'pending').title()}</p>
                    <p><strong>Due:</strong> {task['end_date']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("🎯 No tasks yet. Create your first task to get started!")

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
                    st.subheader("🎯 AI-Generated Milestones")
                    
                    # Calculate total estimated days
                    total_estimated = sum(milestone.get('estimated_days', 1) for milestone in milestones)
                    duration_days = (end_date - start_date).days
                    
                    st.info(f"📅 **Total Task Duration:** {duration_days} days | **Estimated Milestone Time:** {total_estimated} days")
                    
                    for i, milestone in enumerate(milestones, 1):
                        priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(milestone['priority'], "🟡")
                        estimated_days = milestone.get('estimated_days', 1)
                        time_emoji = "⏰" if estimated_days <= 1 else "📅"
                        
                        st.markdown(f"""
                        <div class="milestone-item">
                            <h5>📌 {milestone['name']}</h5>
                            <p><strong>Priority:</strong> {priority_emoji} {milestone['priority']} | <strong>Time:</strong> {time_emoji} {estimated_days} day{'s' if estimated_days > 1 else ''}</p>
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
                    st.subheader("🎯 Milestones")
                    for milestone in task['milestones']:
                        milestone_status = "✅ Completed" if milestone.get('completed', False) else "⏳ Pending"
                        milestone_class = "completed" if milestone.get('completed', False) else ""
                        priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(milestone['priority'], "🟡")
                        
                        col_milestone, col_button = st.columns([4, 1])
                        
                        with col_milestone:
                            estimated_days = milestone.get('estimated_days', 1)
                            time_emoji = "⏰" if estimated_days <= 1 else "📅"
                            
                            st.markdown(f"""
                            <div class="milestone-item {milestone_class}">
                                <h6>📌 {milestone['name']}</h6>
                                <p><strong>Priority:</strong> {priority_emoji} {milestone['priority']} | <strong>Time:</strong> {time_emoji} {estimated_days} day{'s' if estimated_days > 1 else ''} | <strong>Status:</strong> {milestone_status}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_button:
                            if st.button("Toggle", key=f"milestone_{task['id']}_{milestone['id']}", type="secondary"):
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
        
        # Time allocation analysis
        total_estimated_days = 0
        total_actual_days = 0
        
        for task in st.session_state.tasks:
            if 'milestones' in task:
                for milestone in task['milestones']:
                    total_estimated_days += milestone.get('estimated_days', 1)
            
            # Calculate actual task duration
            try:
                start_date = datetime.strptime(task['start_date'], '%Y-%m-%d')
                end_date = datetime.strptime(task['end_date'], '%Y-%m-%d')
                total_actual_days += (end_date - start_date).days
            except:
                pass
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Task Completion Rate", f"{completion_rate:.1f}%")
        
        with col2:
            st.metric("Total Estimated Days", f"{total_estimated_days}")
        
        with col3:
            st.metric("Total Actual Days", f"{total_actual_days}")
        
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
