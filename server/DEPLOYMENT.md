# Ask Siri - Deployment Guide

## 🚀 Quick Deployment

### Windows (Recommended)
1. **Double-click `run.bat`** - This will automatically:
   - Check Python installation
   - Create virtual environment
   - Install dependencies
   - Set up database
   - Start the application

2. **Configure API Key** (First time only):
   - Get a free Gemini API key from [Google AI Studio](https://ai.google.dev/)
   - Edit the `.env` file and replace `your-gemini-api-key-here` with your actual key

3. **Access the application**:
   - Open browser to `http://127.0.0.1:5000`
   - Login with demo credentials: `demo` / `demo`

## 📋 Manual Setup

### Prerequisites
- Python 3.8 or higher
- Internet connection
- Google Gemini API key (free)

### Step-by-Step Installation

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# Create/edit .env file with your API key
echo SECRET_KEY=your-secret-key-here > .env
echo AI_API_KEY=your-gemini-api-key-here >> .env

# 4. Start the application
python app.py
```

## 🔑 API Key Setup

### Getting Your Gemini API Key
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new project or use existing
5. Copy your API key

### Configuration
1. Open `.env` file in a text editor
2. Replace `your-gemini-api-key-here` with your actual API key
3. Save the file
4. Restart the application

## 🖥 System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04, or equivalent
- **RAM**: 2GB available memory
- **Storage**: 500MB free disk space
- **Python**: Version 3.8 or higher
- **Internet**: Stable connection for AI analysis

### Recommended Requirements
- **OS**: Windows 11, macOS 12+, Ubuntu 20.04+
- **RAM**: 4GB available memory
- **Storage**: 1GB free disk space
- **Python**: Version 3.10 or higher
- **Internet**: High-speed connection for optimal performance

## 🌐 Network Requirements

### Firewall Settings
- **Outbound HTTPS (443)**: Required for Gemini AI API
- **Outbound HTTP (80)**: For package installation
- **Local Port 5000**: For web interface access

### Proxy Configuration
If behind a corporate proxy, set environment variables:
```bash
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080
```

## 🔧 Troubleshooting

### Common Issues

**Python Not Found**
```
Solution: Install Python from python.org and ensure it's in PATH
```

**Permission Denied**
```
Solution: Run Command Prompt as Administrator
```

**API Key Invalid**
```
Solution: 
1. Verify API key is correct in .env file
2. Check quota at ai.google.dev
3. Ensure no extra spaces in .env file
```

**Port 5000 Already in Use**
```
Solution: 
1. Stop other applications using port 5000
2. Or modify app.py to use different port:
   app.run(host='127.0.0.1', port=5001, debug=True)
```

**Dependencies Installation Failed**
```
Solution:
1. Check internet connection
2. Update pip: python -m pip install --upgrade pip
3. Try: pip install --no-cache-dir -r requirements.txt
```

## 📊 Production Deployment

### For Production Environments

**1. Security Considerations**
- Change default passwords
- Use strong SECRET_KEY
- Enable HTTPS
- Implement proper logging

**2. Performance Optimization**
- Use production WSGI server (Gunicorn)
- Configure reverse proxy (Nginx)
- Set up load balancing if needed
- Implement caching

**3. Monitoring**
- Set up application monitoring
- Configure log aggregation
- Implement health checks
- Monitor API usage

### Example Production Setup (Linux)
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With systemd service
sudo systemctl enable asksiri
sudo systemctl start asksiri
```

## 📞 Support

### Logs Location
- Application logs: Console output
- Access logs: Not configured by default
- Error logs: Python traceback in console

### Debug Mode
To enable debug mode for troubleshooting:
1. Edit `app.py`
2. Change `debug=False` to `debug=True`
3. Restart application

### Getting Help
1. Check the troubleshooting section above
2. Review application logs
3. Verify all requirements are met
4. Test with minimal configuration

## 🔄 Updates

### Updating the Application
1. Stop the application (Ctrl+C)
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Check for database migrations if needed
4. Restart the application

### Backup
Before updates, backup:
- `instance/asksiri.db` (user data)
- `.env` (configuration)
- Any custom modifications

---
**Developer**: Anand Ankilla
**Version**: 1.0.0  
**Last Updated**: August 2025  
**Support**: Professional Edition
