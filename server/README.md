# Ask Siri - AI-Powered Log Analysis Tool

A professional web application that provides intelligent log analysis using Google's Gemini AI technology. This tool helps developers, system administrators, and DevOps engineers quickly identify and troubleshoot issues in log files.

## 🚀 Features

### Core Functionality
- **AI-Powered Analysis**: Advanced log analysis using Google Gemini AI
- **Real-time Chat Assistant**: Interactive AI assistant for log troubleshooting
- **Multi-format Support**: Handles various log formats and timestamps
- **Smart Pattern Recognition**: Automatically detects errors, warnings, and critical issues
- **Educational Dashboard**: Learn log analysis best practices

### User Experience
- **Modern Web Interface**: Responsive design that works on all devices
- **User Authentication**: Secure login system with role-based access
- **Analysis History**: Track and review previous log analyses
- **Knowledge Base**: Built-in learning resources and tutorials

### Technical Features
- **File Upload Support**: Drag-and-drop log file uploads
- **Real-time Processing**: Live log analysis and streaming
- **Export Capabilities**: Download analysis reports
- **API Integration**: RESTful API for programmatic access

## 📋 Requirements

- **Python 3.8+**
- **Internet Connection** (for AI analysis)
- **Google Gemini API Key** (free tier available)

## 🛠 Installation & Setup

### Quick Start (Recommended)

1. **Download and Extract** the project files
2. **Double-click `run.bat`** to automatically set up and start the application
3. **Configure API Key** when prompted
4. **Open your browser** to `http://127.0.0.1:5000`

### Manual Installation

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create .env file with:
SECRET_KEY=your-secret-key-here
AI_API_KEY=your-gemini-api-key-here

# 5. Run the application
python app.py
```

## 🔑 API Key Setup

1. **Get a free Gemini API key**:
   - Visit [Google AI Studio](https://ai.google.dev/)
   - Create a free account
   - Generate your API key

2. **Configure the application**:
   - Edit the `.env` file
   - Replace `your-gemini-api-key-here` with your actual API key

## 🎯 Usage

### Getting Started
1. **Launch the application** using `run.bat`
2. **Login** with demo credentials:
   - Username: `demo`
   - Password: `demo`
3. **Upload log files** or paste log content
4. **Get instant AI analysis** and recommendations

### Main Features

#### 📤 Log Upload & Analysis
- Navigate to "Upload Logs"
- Drag & drop log files or paste content
- Get comprehensive AI-powered analysis
- View error patterns and recommendations

#### 🤖 AI Assistant
- Access the interactive chat assistant
- Ask questions about your logs
- Get real-time troubleshooting help
- Learn log analysis best practices

#### 📊 Dashboard
- View your analysis history
- Track learning progress
- Access educational resources
- Monitor system insights

#### 📚 Knowledge Base
- Learn log analysis fundamentals
- Explore common error patterns
- Best practices and tutorials
- Troubleshooting guides

## 🏗 Architecture

### Technology Stack
- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, JavaScript
- **AI Engine**: Google Gemini 1.5 Flash
- **Authentication**: Flask-Login

### Project Structure
```
asksiri/
├── server/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── run.bat            # Windows deployment script
│   ├── .env               # Environment variables
│   ├── static/            # CSS, JS, assets
│   ├── templates/         # HTML templates
│   └── instance/          # Database storage
```

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `AI_API_KEY`: Your Google Gemini API key

### Database
- SQLite database stored in `instance/asksiri.db`
- Automatic schema creation on first run
- User accounts and analysis history

## 🚀 Deployment

### Local Development
```bash
python app.py
# Access at http://127.0.0.1:5000
```

### Production Deployment
For production deployment, consider:
- Using a production WSGI server (e.g., Gunicorn)
- Setting up proper environment variables
- Configuring reverse proxy (e.g., Nginx)
- Implementing proper logging and monitoring

## 📞 Support

### Default Accounts
- **Demo User**: `demo` / `demo`
- **Admin User**: `admin` / `admin123`

### Common Issues

**"AI API Key not configured"**
- Ensure your Gemini API key is set in the `.env` file
- Verify the API key is valid and has quota

**"Database errors"**
- Delete `instance/asksiri.db` to reset the database
- Restart the application to recreate tables

**"Dependencies not found"**
- Run `pip install -r requirements.txt`
- Ensure you're in the correct virtual environment

## 📄 License

This is a commercial software product. All rights reserved.

## 🎉 About

Ask Siri is a professional-grade log analysis tool designed to streamline debugging and system monitoring processes. Built with modern web technologies and powered by advanced AI, it provides both novice and expert users with powerful insights into their log data.

**Developer**: Anand Ankilla
**Version**: 1.0.0  
**Last Updated**: August 2025  
**Support**: Professional Edition
