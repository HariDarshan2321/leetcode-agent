"""
Setup script for the LeetCode Email Agent.
This script helps users get started quickly with the application.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print a welcome banner."""
    print("=" * 60)
    print("🚀 LeetCode Email Agent Setup")
    print("=" * 60)
    print("Welcome! This script will help you set up the LeetCode Email Agent.")
    print("Let's get you started with daily coding challenges! 📧💻")
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")

    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required.")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again.")
        return False

    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")

    try:
        # Check if pip is available
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      check=True, capture_output=True)

        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            return True
        else:
            print("❌ Failed to install dependencies:")
            print(result.stderr)
            return False

    except subprocess.CalledProcessError:
        print("❌ pip is not available. Please install pip and try again.")
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found. Please run this script from the project root.")
        return False

def setup_environment():
    """Set up the environment configuration."""
    print("\n⚙️ Setting up environment configuration...")

    # Check if .env already exists
    if os.path.exists(".env"):
        response = input("📝 .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("✅ Keeping existing .env file")
            return True

    # Copy .env.example to .env
    try:
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from template")

        print("\n🔧 Now you need to configure your credentials in the .env file:")
        print("   1. Get a Groq API key from: https://console.groq.com")
        print("   2. Set up Gmail app password (see README.md for instructions)")
        print("   3. Edit .env file with your credentials")
        print()

        # Ask if user wants to edit now
        response = input("📝 Would you like to edit the .env file now? (y/N): ").strip().lower()
        if response == 'y':
            edit_env_file()

        return True

    except FileNotFoundError:
        print("❌ .env.example not found. Please run this script from the project root.")
        return False
    except Exception as e:
        print(f"❌ Error setting up environment: {e}")
        return False

def edit_env_file():
    """Help user edit the .env file."""
    print("\n📝 Let's configure your .env file...")

    # Read current .env file
    try:
        with open(".env", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

    # Get user inputs
    print("\nPlease provide the following information:")

    groq_key = input("🤖 Groq API Key: ").strip()
    if groq_key:
        content = content.replace("your_groq_api_key_here", groq_key)

    email = input("📧 Your Gmail address: ").strip()
    if email:
        content = content.replace("your_email@gmail.com", email)

    password = input("🔑 Gmail app password: ").strip()
    if password:
        content = content.replace("your_app_password_here", password)

    # Optional scheduler settings
    print("\n⏰ Scheduler settings (press Enter for defaults):")
    hour = input("📅 Hour to send emails (0-23, default 9): ").strip()
    if hour and hour.isdigit() and 0 <= int(hour) <= 23:
        content = content.replace("SCHEDULER_HOUR=9", f"SCHEDULER_HOUR={hour}")

    minute = input("🕐 Minute to send emails (0-59, default 0): ").strip()
    if minute and minute.isdigit() and 0 <= int(minute) <= 59:
        content = content.replace("SCHEDULER_MINUTE=0", f"SCHEDULER_MINUTE={minute}")

    # Write updated content
    try:
        with open(".env", "w") as f:
            f.write(content)
        print("✅ .env file updated successfully!")
        return True
    except Exception as e:
        print(f"❌ Error writing .env file: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating directories...")

    directories = ["data", "logs"]

    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")
            return False

    return True

def initialize_database():
    """Initialize the database with sample data."""
    print("\n🗄️ Initializing database...")

    try:
        # Import here to avoid issues if dependencies aren't installed yet
        sys.path.append("src")
        from coordinator import LeetcodeEmailCoordinator

        coordinator = LeetcodeEmailCoordinator()
        success = coordinator.initialize_sample_data()

        if success:
            print("✅ Database initialized with sample problems!")

            # Show stats
            stats = coordinator.get_system_stats()
            print(f"📊 Loaded {stats.get('total_problems', 0)} problems:")
            for difficulty, count in stats.get('problems_by_difficulty', {}).items():
                print(f"   - {difficulty.title()}: {count}")

            return True
        else:
            print("❌ Failed to initialize database")
            return False

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        print("   You can initialize it later with: python main.py --init-data")
        return False

def test_system():
    """Test the system configuration."""
    print("\n🧪 Testing system...")

    try:
        sys.path.append("src")
        from coordinator import LeetcodeEmailCoordinator

        coordinator = LeetcodeEmailCoordinator()
        health = coordinator.test_system_health()

        print("\n🏥 System Health Report:")
        for component, status in health.items():
            if component != 'overall':
                status_icon = "✅" if status else "❌"
                print(f"   {status_icon} {component.replace('_', ' ').title()}")

        overall_status = "🟢 All Systems Operational" if health.get('overall', False) else "🔴 System Issues Detected"
        print(f"\n{overall_status}")

        return health.get('overall', False)

    except Exception as e:
        print(f"❌ Error testing system: {e}")
        return False

def show_next_steps():
    """Show next steps to the user."""
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)

    print("\n🚀 Next Steps:")
    print("1. Start the web interface:")
    print("   streamlit run ui/streamlit_app.py")
    print()
    print("2. Or use the command line:")
    print("   python main.py --test          # Test system")
    print("   python main.py --run-once     # Send emails once")
    print("   python main.py --scheduler    # Run scheduler")
    print()
    print("3. Open your browser to: http://localhost:8501")
    print("4. Subscribe with your email to start receiving challenges!")
    print()
    print("📚 For more information, see README.md")
    print()
    print("Happy coding! 🎯")

def main():
    """Main setup function."""
    print_banner()

    # Check Python version
    if not check_python_version():
        return False

    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation.")
        return False

    # Set up environment
    if not setup_environment():
        print("\n❌ Setup failed at environment configuration.")
        return False

    # Create directories
    if not create_directories():
        print("\n❌ Setup failed at directory creation.")
        return False

    # Initialize database
    if not initialize_database():
        print("\n⚠️ Database initialization failed, but you can continue.")

    # Test system
    if not test_system():
        print("\n⚠️ System test failed. Please check your configuration.")
        print("   You can test later with: python main.py --test")

    # Show next steps
    show_next_steps()

    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)
