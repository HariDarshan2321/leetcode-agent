"""
Leetcode Email Agent - Main package initialization.
"""

from .coordinator import LeetcodeEmailCoordinator
from .config import Config

__version__ = "1.0.0"
__author__ = "Leetcode Email Agent Team"
__description__ = "AI-driven automated system that delivers daily LeetCode-style coding problems via email"

__all__ = ["LeetcodeEmailCoordinator", "Config"]
