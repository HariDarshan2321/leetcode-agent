"""
Main entry point for the Leetcode Email Agent.
This script can be used to run the scheduler or perform one-time operations.
"""

import argparse
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.coordinator import LeetcodeEmailCoordinator
from src.scheduler import DailyScheduler
from src.config import Config

def run_scheduler():
    """Run the daily scheduler in the background."""
    print("🚀 Starting LeetCode Email Agent Scheduler...")

    # Validate configuration
    if not Config.validate_config():
        print("❌ Configuration validation failed. Please check your .env file.")
        return False

    try:
        # Initialize coordinator
        coordinator = LeetcodeEmailCoordinator()

        # Test system health
        print("🔍 Testing system health...")
        health = coordinator.test_system_health()

        if not health.get('overall', False):
            print("❌ System health check failed:")
            for component, status in health.items():
                if component != 'overall':
                    status_icon = "✅" if status else "❌"
                    print(f"  {status_icon} {component.replace('_', ' ').title()}")
            return False

        print("✅ All systems healthy!")

        # Initialize scheduler
        scheduler = DailyScheduler(coordinator.process_daily_emails)

        # Start scheduler
        if scheduler.start():
            print(f"📅 Scheduler started! Daily emails will be sent at "
                  f"{Config.SCHEDULER_HOUR:02d}:{Config.SCHEDULER_MINUTE:02d} "
                  f"{Config.SCHEDULER_TIMEZONE}")

            next_run = scheduler.get_next_run_time()
            if next_run:
                print(f"⏰ Next run scheduled for: {next_run}")

            print("🔄 Scheduler is running. Press Ctrl+C to stop.")

            try:
                # Keep the script running
                import time
                while True:
                    time.sleep(60)  # Check every minute

            except KeyboardInterrupt:
                print("\n🛑 Stopping scheduler...")
                scheduler.stop()
                print("✅ Scheduler stopped successfully!")
                return True
        else:
            print("❌ Failed to start scheduler")
            return False

    except Exception as e:
        print(f"❌ Error running scheduler: {e}")
        return False

def run_once():
    """Run the email processing once immediately."""
    print("🚀 Running LeetCode Email Agent once...")

    # Validate configuration
    if not Config.validate_config():
        print("❌ Configuration validation failed. Please check your .env file.")
        return False

    try:
        # Initialize coordinator
        coordinator = LeetcodeEmailCoordinator()

        # Process emails
        print("📧 Processing daily emails...")
        result = coordinator.process_daily_emails()

        # Display results
        print(f"\n📊 Results:")
        print(f"  👥 Total users: {result.get('total_users', 0)}")
        print(f"  ✅ Emails sent: {result.get('emails_sent', 0)}")
        print(f"  ❌ Emails failed: {result.get('emails_failed', 0)}")

        if result.get('errors'):
            print(f"  🚨 Errors:")
            for error in result['errors']:
                print(f"    - {error}")

        duration = (result.get('end_time', datetime.now()) - result.get('start_time', datetime.now())).total_seconds()
        print(f"  ⏱️ Duration: {duration:.2f} seconds")

        return result.get('emails_sent', 0) > 0 or result.get('total_users', 0) == 0

    except Exception as e:
        print(f"❌ Error running email processing: {e}")
        return False

def initialize_data():
    """Initialize the database with sample problems."""
    print("🚀 Initializing sample data...")

    try:
        coordinator = LeetcodeEmailCoordinator()

        print("📚 Loading sample problems...")
        success = coordinator.initialize_sample_data()

        if success:
            print("✅ Sample data initialized successfully!")

            # Show stats
            stats = coordinator.get_system_stats()
            print(f"📊 Loaded {stats.get('total_problems', 0)} problems:")
            for difficulty, count in stats.get('problems_by_difficulty', {}).items():
                print(f"  - {difficulty.title()}: {count}")

            return True
        else:
            print("❌ Failed to initialize sample data")
            return False

    except Exception as e:
        print(f"❌ Error initializing data: {e}")
        return False

def test_system():
    """Test all system components."""
    print("🚀 Testing LeetCode Email Agent system...")

    try:
        coordinator = LeetcodeEmailCoordinator()

        print("🔍 Running system health checks...")
        health = coordinator.test_system_health()

        print("\n🏥 System Health Report:")
        for component, status in health.items():
            if component != 'overall':
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {component.replace('_', ' ').title()}: {'Healthy' if status else 'Error'}")

        overall_status = "🟢 All Systems Operational" if health.get('overall', False) else "🔴 System Issues Detected"
        print(f"\n{overall_status}")

        # Show system stats
        print("\n📊 System Statistics:")
        stats = coordinator.get_system_stats()
        print(f"  👥 Active users: {stats.get('total_active_users', 0)}")
        print(f"  📚 Total problems: {stats.get('total_problems', 0)}")
        print(f"  💻 Supported languages: {len(stats.get('supported_languages', []))}")
        print(f"  🎯 Difficulty levels: {len(stats.get('supported_difficulties', []))}")

        return health.get('overall', False)

    except Exception as e:
        print(f"❌ Error testing system: {e}")
        return False

def show_config():
    """Show current configuration."""
    print("🚀 LeetCode Email Agent Configuration:")
    print("=" * 50)

    # Validate first
    config_valid = Config.validate_config()
    print(f"Configuration Status: {'✅ Valid' if config_valid else '❌ Invalid'}")
    print()

    # Show config summary
    config_summary = Config.get_config_summary()

    print("📧 Email Schedule:")
    print(f"  Time: {config_summary.get('scheduler_time', 'N/A')}")
    print(f"  Timezone: {config_summary.get('scheduler_timezone', 'N/A')}")
    print()

    print("🗄️ Database:")
    print(f"  Path: {config_summary.get('database_path', 'N/A')}")
    print()

    print("🛠️ Features:")
    print(f"  Debug Mode: {config_summary.get('debug_mode', 'N/A')}")
    print(f"  Log Level: {config_summary.get('log_level', 'N/A')}")
    print()

    print("💻 Supported Languages:")
    for lang in config_summary.get('supported_languages', []):
        print(f"  - {Config.SUPPORTED_LANGUAGES.get(lang, lang)}")
    print()

    print("🎯 Difficulty Levels:")
    for diff in config_summary.get('difficulty_levels', []):
        print(f"  - {Config.DIFFICULTY_LEVELS.get(diff, diff)}")

def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="LeetCode Email Agent - Daily coding challenges via email",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --scheduler          # Run the daily scheduler
  python main.py --run-once          # Send emails once immediately
  python main.py --init-data         # Initialize sample problems
  python main.py --test              # Test system health
  python main.py --config            # Show configuration
        """
    )

    parser.add_argument(
        "--scheduler",
        action="store_true",
        help="Run the daily scheduler (keeps running until stopped)"
    )

    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Process and send emails once immediately"
    )

    parser.add_argument(
        "--init-data",
        action="store_true",
        help="Initialize database with sample problems"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Test system health and show diagnostics"
    )

    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration"
    )

    args = parser.parse_args()

    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return

    success = True

    if args.config:
        show_config()

    if args.test:
        success = test_system() and success

    if args.init_data:
        success = initialize_data() and success

    if args.run_once:
        success = run_once() and success

    if args.scheduler:
        success = run_scheduler() and success

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
