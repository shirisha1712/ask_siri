@echo off
REM ====================================================
REM Ask Siri - AI-Powered Log Analysis Tool
REM Professional Deployment Script
REM ====================================================

title Ask Siri - Log Analysis Tool

echo.
echo ===================================
echo    Ask Siri Log Analysis Tool
echo    Professional Deployment Setup
echo ===================================
echo.

REM Change to the server directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [✓] Python is installed
python --version

REM Check if virtual environment exists
if not exist "venv" (
    echo.
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [✓] Virtual environment created
)

REM Activate virtual environment
echo.
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [✓] Virtual environment activated

REM Check if requirements file exists
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found
    echo Please ensure the requirements.txt file is in the same directory
    pause
    exit /b 1
)

REM Install/Update dependencies
echo.
echo [INFO] Installing/Updating dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo [✓] Dependencies installed successfully

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo [WARNING] .env file not found
    echo Creating default .env file...
    echo SECRET_KEY=your-secret-key-change-this-in-production > .env
    echo AI_API_KEY=your-gemini-api-key-here >> .env
    echo.
    echo [IMPORTANT] Please edit .env file and add your actual API keys:
    echo 1. Get a Gemini API key from: https://ai.google.dev/
    echo 2. Replace 'your-gemini-api-key-here' with your actual API key
    echo 3. Replace 'your-secret-key-change-this-in-production' with a secure secret key
    echo.
    pause
)

REM Check if instance directory exists (for database)
if not exist "instance" (
    echo [INFO] Creating instance directory for database...
    mkdir instance
)

REM Start the application
echo.
echo [INFO] Starting Ask Siri Log Analysis Tool...
echo.
echo ========================================
echo   Application is starting...
echo   Open your browser and navigate to:
echo   http://127.0.0.1:5000
echo ========================================
echo.
echo Default login credentials:
echo Username: demo
echo Password: demo
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask application
python app.py

REM If we reach here, the application has stopped
echo.
echo [INFO] Application has stopped
pause
