"""
Configuration management for the Leetcode Email Agent.
This file handles all application settings and environment variables.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv(override=True)

class Config:
    """
    Configuration class that manages all application settings.
    This makes it easy to access settings throughout the application.
    """

    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Email Configuration
    EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")

    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/leetcode.db")

    # Scheduler Configuration
    SCHEDULER_HOUR: int = int(os.getenv("SCHEDULER_HOUR", "9"))
    SCHEDULER_MINUTE: int = int(os.getenv("SCHEDULER_MINUTE", "0"))
    SCHEDULER_TIMEZONE: str = os.getenv("SCHEDULER_TIMEZONE", "UTC")

    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Supported programming languages
    SUPPORTED_LANGUAGES: Dict[str, str] = {
        "python": "Python",
        "java": "Java",
        "cpp": "C++",
        "javascript": "JavaScript",
        "go": "Go",
        "rust": "Rust"
    }

    # Problem difficulty levels
    DIFFICULTY_LEVELS: Dict[str, str] = {
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard"
    }

    @classmethod
    def validate_config(cls) -> bool:
        """
        Validates that all required configuration values are present.
        Returns True if valid, False otherwise.
        """
        required_fields = [
            cls.GROQ_API_KEY,
            cls.EMAIL_ADDRESS,
            cls.EMAIL_PASSWORD
        ]

        missing_fields = [field for field in required_fields if not field]

        if missing_fields:
            print("❌ Missing required configuration:")
            if not cls.GROQ_API_KEY:
                print("  - GROQ_API_KEY")
            if not cls.EMAIL_ADDRESS:
                print("  - EMAIL_ADDRESS")
            if not cls.EMAIL_PASSWORD:
                print("  - EMAIL_PASSWORD")
            return False

        print("✅ Configuration validated successfully!")
        return True

    @classmethod
    def get_config_summary(cls) -> Dict[str, Any]:
        """
        Returns a summary of current configuration (without sensitive data).
        Useful for debugging and logging.
        """
        return {
            "database_path": cls.DATABASE_PATH,
            "scheduler_time": f"{cls.SCHEDULER_HOUR:02d}:{cls.SCHEDULER_MINUTE:02d}",
            "scheduler_timezone": cls.SCHEDULER_TIMEZONE,
            "debug_mode": cls.DEBUG,
            "log_level": cls.LOG_LEVEL,
            "supported_languages": list(cls.SUPPORTED_LANGUAGES.keys()),
            "difficulty_levels": list(cls.DIFFICULTY_LEVELS.keys())
        }
