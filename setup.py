#!/usr/bin/env python3
"""
Dynamic Pricing System Setup Script
Automates the setup process for both backend and frontend components.
"""

import os
import sys
import subprocess
import platform

def run_command(command, cwd=None, shell=False):
    """Run a command and return success status."""
    try:
        if platform.system() == "Windows":
            shell = True
        result = subprocess.run(command, cwd=cwd, shell=shell, check=True, capture_output=True, text=True)
        print(f"✓ Success: {' '.join(command) if isinstance(command, list) else command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {' '.join(command) if isinstance(command, list) else command}")
        print(f"  {e.stderr}")
        return False

def check_prerequisites():
    """Check if required tools are installed."""
    print("Checking prerequisites...")
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✓ Python: {result.stdout.strip()}")
    except:
        print("✗ Python not found")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✓ Node.js: {result.stdout.strip()}")
    except:
        print("✗ Node.js not found. Please install Node.js 14+ and npm")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        print(f"✓ npm: {result.stdout.strip()}")
    except:
        print("✗ npm not found")
        return False
    
    return True

def setup_backend():
    """Set up the Flask backend."""
    print("\n🔧 Setting up backend...")
    
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        print(f"✗ Backend directory not found: {backend_dir}")
        return False
    
    # Create virtual environment
    venv_command = [sys.executable, "-m", "venv", "venv"]
    if not run_command(venv_command, cwd=backend_dir):
        return False
    
    # Determine activation script path
    if platform.system() == "Windows":
        activate_script = os.path.join(backend_dir, "venv", "Scripts", "activate")
        pip_path = os.path.join(backend_dir, "venv", "Scripts", "pip")
        python_path = os.path.join(backend_dir, "venv", "Scripts", "python")
    else:
        activate_script = os.path.join(backend_dir, "venv", "bin", "activate")
        pip_path = os.path.join(backend_dir, "venv", "bin", "pip")
        python_path = os.path.join(backend_dir, "venv", "bin", "python")
    
    # Install requirements
    pip_command = [pip_path, "install", "-r", "requirements.txt"]
    if not run_command(pip_command, cwd=backend_dir):
        return False
    
    print("✓ Backend setup completed")
    return True

def setup_frontend():
    """Set up the React frontend."""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        print(f"✗ Frontend directory not found: {frontend_dir}")
        return False
    
    # Install npm dependencies
    npm_command = ["npm", "install"]
    if not run_command(npm_command, cwd=frontend_dir):
        return False
    
    print("✓ Frontend setup completed")
    return True

def initialize_database():
    """Initialize the database with sample data."""
    print("\n🔧 Initializing database...")
    
    backend_dir = "backend"
    
    # Determine python path
    if platform.system() == "Windows":
        python_path = os.path.join(backend_dir, "venv", "Scripts", "python")
    else:
        python_path = os.path.join(backend_dir, "venv", "bin", "python")
    
    # Initialize database
    init_command = [python_path, "-c", "from app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"]
    if not run_command(init_command, cwd=backend_dir):
        return False
    
    # Load sample data
    sample_command = [python_path, "data/sample_data.py"]
    if not run_command(sample_command, cwd=backend_dir):
        print("Warning: Could not load sample data. You can run it manually later.")
    
    print("✓ Database initialization completed")
    return True

def create_env_file():
    """Create a basic .env file for the backend."""
    backend_dir = "backend"
    env_path = os.path.join(backend_dir, ".env")
    
    if os.path.exists(env_path):
        print("✓ .env file already exists")
        return
    
    env_content = """# Dynamic Pricing System Environment Variables
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///dynamic_pricing.db
FLASK_ENV=development
ML_MODEL_PATH=models/
COMPETITOR_API_KEY=demo-key
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✓ Created .env file")
    except Exception as e:
        print(f"✗ Could not create .env file: {e}")

def print_startup_instructions():
    """Print instructions for starting the application."""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 To start the application:")
    print("\n1. Start the backend (Terminal 1):")
    if platform.system() == "Windows":
        print("   cd backend")
        print("   venv\\Scripts\\activate")
        print("   python app.py")
    else:
        print("   cd backend")
        print("   source venv/bin/activate")
        print("   python app.py")
    
    print("\n2. Start the frontend (Terminal 2):")
    print("   cd frontend")
    print("   npm start")
    
    print("\n🌐 Access the application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:5000")
    
    print("\n📖 For more information, see README.md")

def main():
    """Main setup function."""
    print("🚀 Dynamic Pricing System Setup")
    print("=" * 40)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed.")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed.")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Initialize database
    if not initialize_database():
        print("\n❌ Database initialization failed.")
        sys.exit(1)
    
    # Print startup instructions
    print_startup_instructions()

if __name__ == "__main__":
    main() 