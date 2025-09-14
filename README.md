# 🎯 AI Task Planner

An intelligent task management application built with Streamlit that uses AI to break down complex tasks into manageable milestones and track your productivity.

## ✨ Features

### 🚀 Core Functionality
- **Task Creation**: Create tasks with name, category, and timeline
- **AI-Powered Milestones**: Intelligent task breakdown into smaller, manageable steps
- **Progress Tracking**: Visual progress bars and completion tracking
- **Category Management**: Organize tasks by Personal, Official, Health, Learning, etc.

### 📊 Analytics & Reporting
- **Performance Metrics**: Track completion rates and efficiency scores
- **Timeline Analysis**: Monthly, weekly, and daily performance breakdowns
- **Category Performance**: Compare efficiency across different task types
- **AI Insights**: Smart recommendations for productivity improvement
- **Visual Charts**: Interactive graphs showing trends and patterns

### 🎨 User Experience
- **Modern UI**: Clean, intuitive interface with emoji icons
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Live progress tracking and status updates
- **One-Click Deployment**: Ready for Streamlit Cloud deployment

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Local Development
1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Task-Planner
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

## 🚀 Deployment to Streamlit Cloud

### Quick Deployment
1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Click "Deploy"

### Deployment Configuration
The app is pre-configured for Streamlit Cloud with:
- `requirements.txt` for dependencies
- `.streamlit/config.toml` for theme and settings
- Optimized for cloud deployment

## 📱 How to Use

### 1. Create a Task
- Navigate to "➕ Create Task"
- Enter task name and select category
- Choose start and end dates
- Click "🤖 Generate AI Milestones"

### 2. Track Progress
- View tasks in "📋 My Tasks"
- Mark milestones as complete
- Monitor progress with visual indicators
- Check days remaining

### 3. Analyze Performance
- Visit "📊 Analytics & Reports"
- Review efficiency scores and trends
- Get AI-powered insights
- Export reports for sharing

## 🧠 AI Features

### Smart Milestone Generation
The AI analyzes your task and automatically suggests:
- Logical sequence of milestones
- Estimated time for each step
- Task-specific recommendations
- Optimized workflow

### Performance Insights
Get personalized recommendations:
- Productivity patterns analysis
- Time estimation accuracy
- Category-specific insights
- Improvement suggestions

## 📊 Data Storage

- **Local Storage**: Tasks are saved in `tasks_data.json`
- **Persistent Data**: Your progress is maintained between sessions
- **Export Options**: PDF, CSV, and email reports (coming soon)

## 🎨 Customization

### Themes
The app uses a custom theme defined in `.streamlit/config.toml`:
- Primary color: Blue (#1f77b4)
- Clean, modern design
- Responsive layout

### Categories
Default categories include:
- Personal
- Official
- Health
- Learning
- Finance
- Other

## 🔧 Technical Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **Date Handling**: Python datetime
- **Storage**: JSON files

## 📈 Future Enhancements

- [ ] Real AI integration (OpenAI API)
- [ ] Team collaboration features
- [ ] Mobile app version
- [ ] Advanced reporting
- [ ] Integration with calendar apps
- [ ] Notification system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For support or questions:
- Create an issue on GitHub
- Check the documentation
- Review the code comments

---

**Built with ❤️ using Streamlit and Python**