import os
import json
import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import google.generativeai as genai
import re
from collections import Counter
import PyPDF2

# Application Information
__version__ = "1.0.0"
__app_name__ = "Ask Siri - AI-Powered Log Analysis Tool"
__author__ = "Professional Development Team"

# Load API key from .env file
load_dotenv()

# The Flask app instance
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///asksiri.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configure the Gemini API with your key
genai.configure(api_key=os.getenv("AI_API_KEY"))

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='Developer')  # Admin, DevOps, Developer
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    analyses = db.relationship('Analysis', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Analysis History Model
class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), default='uploaded_logs')
    prompt = db.Column(db.Text, nullable=False)
    log_summary = db.Column(db.Text)
    ai_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    error_count = db.Column(db.Integer, default=0)
    warning_count = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Utility functions
def parse_log_content(log_content):
    """Parse log content and extract statistics"""
    lines = log_content.split('\n')
    stats = {
        'total_lines': len(lines),
        'error_count': 0,
        'warning_count': 0,
        'info_count': 0,
        'critical_count': 0,
        'timeline': []
    }
    
    for line in lines:
        line_lower = line.lower()
        # Match various timestamp formats: YYYY-MM-DD HH:MM:SS, YYYY-MM-DDTHH:MM:SS, MM/DD/YYYY HH:MM:SS, etc.
        timestamp_patterns = [
            r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}',  # 2024-08-25 10:30:15 or 2024-08-25T10:30:15
            r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}',    # 08/25/2024 10:30:15
            r'\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}',      # Aug 25 10:30:15
            r'\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2}'     # 25-08-2024 10:30:15
        ]
        
        timestamp_match = None
        try:
            for pattern in timestamp_patterns:
                timestamp_match = re.search(pattern, line)
                if timestamp_match:
                    break
        except re.error:
            # Skip regex errors silently in production
            timestamp_match = None
        
        if 'error' in line_lower:
            stats['error_count'] += 1
            if timestamp_match:
                stats['timeline'].append({'time': timestamp_match.group(), 'type': 'ERROR', 'message': line})
        elif 'warning' in line_lower or 'warn' in line_lower:
            stats['warning_count'] += 1
            if timestamp_match:
                stats['timeline'].append({'time': timestamp_match.group(), 'type': 'WARNING', 'message': line})
        elif 'critical' in line_lower or 'fatal' in line_lower:
            stats['critical_count'] += 1
            if timestamp_match:
                stats['timeline'].append({'time': timestamp_match.group(), 'type': 'CRITICAL', 'message': line})
        elif 'info' in line_lower:
            stats['info_count'] += 1
    
    return stats

# Routes

@app.route('/')
def index():
    """Home page with project overview"""
    return render_template('index.html')

@app.route('/upload')
def upload_page():
    """Upload and analyze logs page"""
    return render_template('upload.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_logs():
    """API endpoint for log analysis"""
    try:
        
        prompt = request.form.get('prompt', '')
        log_text = request.form.get('log_text', '')
        log_files = request.files.getlist('log_files')

        all_logs = [log_text] if log_text.strip() else []
        filenames = []
        
        # Process uploaded files (accept all file formats, extract text from PDFs)
        for file in log_files:
            if file.filename:
                filename = secure_filename(file.filename)
                filenames.append(filename)
                try:
                    if filename.lower().endswith('.pdf'):
                        # Extract text from PDF
                        try:
                            file.seek(0)
                            pdf_reader = PyPDF2.PdfReader(file)
                            pdf_text = ""
                            for page in pdf_reader.pages:
                                pdf_text += page.extract_text() or ""
                            all_logs.append(f"\n--- PDF File: {filename} ---\n{pdf_text}\n")
                        except Exception as e:
                            all_logs.append(f"\n--- PDF File: {filename} ---\n[Could not extract text from PDF: {str(e)}]\n")
                    elif filename.lower().endswith('.txt'):
                        # Read as plain text
                        try:
                            file.seek(0)
                            file_content = file.read().decode('utf-8', errors='ignore')
                            all_logs.append(f"\n--- TXT File: {filename} ---\n{file_content}\n")
                        except Exception:
                            all_logs.append(f"\n--- TXT File: {filename} ---\n[Could not read text file]\n")
                    else:
                        # Try reading as text
                        try:
                            file.seek(0)
                            file_content = file.read().decode('utf-8', errors='ignore')
                            all_logs.append(f"\n--- Log File: {filename} ---\n{file_content}\n")
                        except Exception:
                            all_logs.append(f"\n--- File: {filename} (binary or unsupported text encoding) ---\n[Binary file content not displayed]\n")
                except Exception as e:
                    return jsonify({'error': f'Error reading file {filename}: {str(e)}'}), 400

        if not all_logs:
            return jsonify({'error': 'No log content provided'}), 400

        full_log_content = "\n".join(all_logs)
        
        # Parse log statistics
        try:
            stats = parse_log_content(full_log_content)
        except Exception:
            # Provide default stats if parsing fails
            stats = {
                'total_lines': len(full_log_content.split('\n')),
                'error_count': full_log_content.lower().count('error'),
                'warning_count': full_log_content.lower().count('warning') + full_log_content.lower().count('warn'),
                'info_count': full_log_content.lower().count('info'),
                'critical_count': full_log_content.lower().count('critical') + full_log_content.lower().count('fatal'),
                'timeline': []
            }
        
        # Create AI prompt
        ai_prompt_text = f"""
You are an expert log analyst. Analyze the following logs and provide:

1. **Summary of Key Issues**: Brief overview of what happened
2. **Error Classification**: Categorize errors by type and severity
3. **Timeline Analysis**: Sequence of events leading to issues
4. **Root Cause Analysis**: Identify underlying causes
5. **Actionable Recommendations**: Specific steps to resolve issues

User Request: {prompt if prompt else 'General log analysis'}

Log Data:
{full_log_content[:5000]}{"... (truncated)" if len(full_log_content) > 5000 else ""}
"""
        
        # Gemini AI analysis
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(ai_prompt_text)
        result = response.text
        
        # Save analysis to database if user is logged in
        if current_user.is_authenticated:
            try:
                analysis = Analysis(
                    user_id=current_user.id,
                    filename=', '.join(filenames) if filenames else 'text_input',
                    prompt=prompt,
                    log_summary=f"Lines: {stats['total_lines']}, Errors: {stats['error_count']}, Warnings: {stats['warning_count']}",
                    ai_response=result,
                    error_count=stats['error_count'],
                    warning_count=stats['warning_count']
                )
                db.session.add(analysis)
                db.session.commit()
            except Exception:
                # Continue even if database save fails
                pass
        
        return jsonify({
            'result': result,
            'stats': stats,
            'status': 'success'
        })

    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """Advanced chat endpoint for AI assistant with enhanced responses"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Enhanced AI prompt for more intelligent responses
        ai_prompt = f"""
You are Ask Siri, an advanced AI assistant powered by Google Gemini. You are:
- Highly intelligent and knowledgeable across all domains
- Specialized in technical support, log analysis, DevOps, and programming
- Professional yet friendly and conversational
- Capable of providing detailed, actionable solutions
- Always helpful and never refuse reasonable requests

Context: This is a real-time chat interface where users expect quick, intelligent responses.

User Message: "{message}"

Instructions:
1. Analyze the user's intent and provide the most helpful response
2. If technical: Give specific, actionable steps with examples
3. If general: Provide comprehensive, well-structured information
4. Use appropriate formatting (bullet points, numbered lists, code blocks)
5. Be conversational but professional
6. Always offer follow-up assistance
7. Use emojis sparingly but effectively to enhance readability

Provide a response that demonstrates your advanced AI capabilities while being practical and useful.
"""
        
        # Configure the model for optimal performance
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
        # Safety settings for better responses
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        # Initialize model with enhanced configuration
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Generate response
        response = model.generate_content(ai_prompt)
        ai_response = response.text
        
        # Enhanced response formatting
        formatted_response = format_advanced_chat_response(ai_response)
        
        return jsonify({
            'status': 'success',
            'response': formatted_response,
            'message_id': str(datetime.datetime.now().timestamp()),
            'model': 'gemini-1.5-flash',
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        # Enhanced error response
        error_response = f"""
        <div style="color: #ea4335; padding: 12px; border-left: 4px solid #ea4335; background: #fef7f0; border-radius: 8px;">
            <strong>⚠️ Technical Issue</strong><br>
            I encountered a problem while processing your request. This could be due to:
            <ul style="margin: 8px 0; padding-left: 20px;">
                <li>Network connectivity issues</li>
                <li>AI service temporary unavailability</li>
                <li>Request processing overload</li>
            </ul>
            Please try again in a moment. If the problem persists, I'm still here to help through alternative means.
        </div>
        """
        
        return jsonify({
            'error': error_response,
            'status': 'error',
            'timestamp': datetime.datetime.now().isoformat()
        }), 500


def format_advanced_chat_response(text):
    """Enhanced formatting for AI responses with better styling"""
    formatted = text
    
    # Convert markdown-style formatting to HTML with enhanced styling
    # Bold text with custom styling
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #1a73e8;">\1</strong>', formatted)
    
    # Italic text
    formatted = re.sub(r'\*(.*?)\*', r'<em>\1</em>', formatted)
    
    # Code blocks with syntax highlighting
    formatted = re.sub(
        r'```(\w+)?\n(.*?)```', 
        r'<pre style="background: #f8f9fa; border: 1px solid #e8eaed; border-radius: 8px; padding: 16px; margin: 12px 0; overflow-x: auto;"><code>\2</code></pre>', 
        formatted, 
        flags=re.DOTALL
    )
    
    # Inline code
    formatted = re.sub(
        r'`([^`]+)`', 
        r'<code style="background: #f1f3f4; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.9em;">\1</code>', 
        formatted
    )
    
    # Headers
    formatted = re.sub(r'^### (.*$)', r'<h4 style="color: #1a73e8; margin: 16px 0 8px 0;">\1</h4>', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^## (.*$)', r'<h3 style="color: #1a73e8; margin: 20px 0 12px 0;">\1</h3>', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^# (.*$)', r'<h2 style="color: #1a73e8; margin: 24px 0 16px 0;">\1</h2>', formatted, flags=re.MULTILINE)
    
    # Lists with better spacing
    formatted = re.sub(r'^- (.*)$', r'<li style="margin: 4px 0;">\1</li>', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^(\d+)\. (.*)$', r'<li style="margin: 4px 0;">\2</li>', formatted, flags=re.MULTILINE)
    
    # Wrap consecutive list items in ul tags
    formatted = re.sub(r'(<li.*?</li>\s*)+', lambda m: f'<ul style="margin: 12px 0; padding-left: 24px;">{m.group(0)}</ul>', formatted)
    
    # Line breaks for better readability
    formatted = re.sub(r'\n\n', '<br><br>', formatted)
    formatted = re.sub(r'\n', '<br>', formatted)
    
    # Add some emoji support for common patterns
    emoji_patterns = {
        r'\b(error|ERROR)\b': '❌ \\1',
        r'\b(warning|WARNING)\b': '⚠️ \\1',
        r'\b(success|SUCCESS|completed)\b': '✅ \\1',
        r'\b(info|INFO|information)\b': 'ℹ️ \\1',
        r'\b(tip|TIP|hint)\b': '💡 \\1',
        r'\b(important|IMPORTANT|note)\b': '📌 \\1'
    }
    
    for pattern, replacement in emoji_patterns.items():
        formatted = re.sub(pattern, replacement, formatted, flags=re.IGNORECASE)
    
    return formatted


def format_chat_response(text):
    """Format AI response for better chat display"""
    # Convert markdown-style formatting to HTML
    formatted = text
    
    # Bold text
    formatted = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', formatted)
    
    # Code blocks
    formatted = re.sub(r'`([^`]+)`', r'<code>\1</code>', formatted)
    
    # Lists
    lines = formatted.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('- ') or line.startswith('• '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            result_lines.append(f'<li>{line[2:]}</li>')
        elif line.startswith(('1. ', '2. ', '3. ', '4. ', '5. ')):
            if not in_list:
                result_lines.append('<ol>')
                in_list = True
            result_lines.append(f'<li>{line[3:]}</li>')
        else:
            if in_list:
                result_lines.append('</ul>' if '•' in result_lines[-2] or '-' in result_lines[-2] else '</ol>')
                in_list = False
            if line:
                result_lines.append(f'<p>{line}</p>')
    
    if in_list:
        result_lines.append('</ul>')
    
    return ''.join(result_lines)

@app.route('/dashboard')
def dashboard():
    """Educational dashboard with log learning cards"""
    # Get user's recent analyses if logged in
    recent_analyses = []
    if current_user.is_authenticated:
        recent_analyses = Analysis.query.filter_by(user_id=current_user.id)\
                                      .order_by(Analysis.created_at.desc())\
                                      .limit(5).all()
    
    return render_template('dashboard.html', recent_analyses=recent_analyses)

@app.route('/realtime')
def realtime():
    """Real-time log monitoring page"""
    return render_template('realtime.html')

@app.route('/api/realtime-logs')
def get_realtime_logs():
    """API endpoint for real-time log data simulation"""
    # Simulate real-time logs (in production, this would read from actual log files)
    import random
    log_levels = ['INFO', 'WARNING', 'ERROR', 'CRITICAL']
    messages = [
        "Database connection established",
        "User authentication successful",
        "High memory usage detected",
        "Connection timeout occurred",
        "Service started successfully",
        "Disk space low warning",
        "Critical error in payment processor",
        "Cache invalidation completed"
    ]
    
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level = random.choice(log_levels)
    message = random.choice(messages)
    
    log_entry = {
        'timestamp': current_time,
        'level': level,
        'message': f"[{level}] {message}",
        'color': {
            'INFO': 'success',
            'WARNING': 'warning', 
            'ERROR': 'danger',
            'CRITICAL': 'dark'
        }.get(level, 'secondary')
    }
    
    return jsonify(log_entry)

@app.route('/assistant')
def assistant():
    """Query assistant page"""
    return render_template('assistant.html')

@app.route('/knowledge')
def knowledge():
    """Knowledge base page"""
    return render_template('knowledge.html')

@app.route('/knowledge/<topic>')
def knowledge_detail(topic):
    """Detailed knowledge base pages"""
    
    # Define educational content for each topic
    content_data = {
        'what-are-logs': {
            'title': 'What are Logs?',
            'subtitle': 'Understanding the fundamentals of log files and their importance in system monitoring',
            'category': 'fundamentals',
            'read_time': 8,
            'last_updated': 'August 2025'
        },
        'log-types': {
            'title': 'Types of Log Files',
            'subtitle': 'Explore different categories of logs and their specific purposes',
            'category': 'fundamentals',
            'read_time': 10,
            'last_updated': 'August 2025'
        },
        'common-errors': {
            'title': 'Common Log Errors',
            'subtitle': 'Identify and understand frequently encountered error patterns',
            'category': 'troubleshooting',
            'read_time': 12,
            'last_updated': 'August 2025'
        },
        'analysis-techniques': {
            'title': 'Log Analysis Techniques',
            'subtitle': 'Master advanced methods for effective log analysis',
            'category': 'advanced',
            'read_time': 15,
            'last_updated': 'August 2025'
        },
        'best-practices': {
            'title': 'Log Management Best Practices',
            'subtitle': 'Industry standards for log handling, retention, and security',
            'category': 'best-practices',
            'read_time': 10,
            'last_updated': 'August 2025'
        },
        'troubleshooting': {
            'title': 'Troubleshooting Guide',
            'subtitle': 'Step-by-step methodologies for systematic problem resolution',
            'category': 'troubleshooting',
            'read_time': 18,
            'last_updated': 'August 2025'
        }
    }
    
    # Get content data or default values
    data = content_data.get(topic, {
        'title': 'Educational Content',
        'subtitle': 'Learn more about log analysis and system monitoring',
        'category': 'general',
        'read_time': 5,
        'last_updated': 'August 2025'
    })
    
    return render_template('knowledge_detail.html', 
                         topic=topic,
                         article_title=data['title'],
                         article_subtitle=data['subtitle'],
                         category=data['category'],
                         read_time=data['read_time'],
                         last_updated=data['last_updated'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'Developer')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    analyses = Analysis.query.filter_by(user_id=current_user.id)\
                            .order_by(Analysis.created_at.desc())\
                            .all()
    return render_template('profile.html', analyses=analyses)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Update database schema if needed (for existing databases)
        try:
            # Try to add filename column if it doesn't exist
            with db.engine.connect() as conn:
                conn.execute('ALTER TABLE analysis ADD COLUMN filename VARCHAR(255) DEFAULT "uploaded_logs"')
                conn.commit()
        except Exception:
            # Column already exists or other error - this is normal
            pass
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@asksiri.com').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@asksiri.com',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            
    # Production ready settings
    print(f"\n🚀 {__app_name__}")
    print(f"📊 Version: {__version__}")
    print(f"🌐 Server starting at: http://127.0.0.1:5000")
    print(f"🔑 Demo Login: demo / demo")
    print(f"👑 Admin Login: admin / admin123")
    print("="*50)
    
    app.run(host='127.0.0.1', port=5000, debug=False)