"""
Database models for the Leetcode Email Agent.
This file defines the structure of our database tables.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

@dataclass
class User:
    """
    Represents a user who has subscribed to receive daily coding problems.
    """
    id: Optional[int] = None
    email: str = ""
    preferred_language: str = "python"  # Default to Python
    preferred_difficulty: str = "medium"  # Default to Medium
    solution_delivery: str = "with_problem"  # "with_problem", "problem_only", "delayed"
    solution_delay_hours: int = 24  # Hours to wait before sending solution (for delayed option)
    preferred_time: str = "09:00"  # Time in HH:MM format when user wants to receive emails
    timezone: str = "UTC"  # User's timezone
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert user object to dictionary for easy serialization."""
        return {
            "id": self.id,
            "email": self.email,
            "preferred_language": self.preferred_language,
            "preferred_difficulty": self.preferred_difficulty,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class Problem:
    """
    Represents a coding problem with all necessary details.
    """
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    difficulty: str = "medium"
    test_cases: str = ""  # JSON string of test cases
    constraints: str = ""
    examples: str = ""  # JSON string of examples
    hints: str = ""  # JSON string of hints
    tags: str = ""  # JSON string of problem tags (e.g., ["array", "sorting"])
    created_at: Optional[datetime] = None

    def get_test_cases(self) -> List[Dict[str, Any]]:
        """Parse test cases from JSON string."""
        try:
            return json.loads(self.test_cases) if self.test_cases else []
        except json.JSONDecodeError:
            return []

    def get_examples(self) -> List[Dict[str, Any]]:
        """Parse examples from JSON string."""
        try:
            return json.loads(self.examples) if self.examples else []
        except json.JSONDecodeError:
            return []

    def get_hints(self) -> List[str]:
        """Parse hints from JSON string."""
        try:
            return json.loads(self.hints) if self.hints else []
        except json.JSONDecodeError:
            return []

    def get_tags(self) -> List[str]:
        """Parse tags from JSON string."""
        try:
            return json.loads(self.tags) if self.tags else []
        except json.JSONDecodeError:
            return []

    def to_dict(self) -> Dict[str, Any]:
        """Convert problem object to dictionary for easy serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "test_cases": self.get_test_cases(),
            "constraints": self.constraints,
            "examples": self.get_examples(),
            "hints": self.get_hints(),
            "tags": self.get_tags(),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

@dataclass
class SentProblem:
    """
    Tracks which problems have been sent to which users to avoid duplicates.
    """
    id: Optional[int] = None
    user_id: int = 0
    problem_id: int = 0
    sent_at: Optional[datetime] = None
    email_status: str = "pending"  # pending, sent, failed
    solution_language: str = "python"

    def to_dict(self) -> Dict[str, Any]:
        """Convert sent problem object to dictionary for easy serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "problem_id": self.problem_id,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "email_status": self.email_status,
            "solution_language": self.solution_language
        }

@dataclass
class Solution:
    """
    Represents a generated solution for a problem.
    """
    id: Optional[int] = None
    problem_id: int = 0
    language: str = "python"
    solution_code: str = ""
    explanation: str = ""
    time_complexity: str = ""
    space_complexity: str = ""
    humor_comments: str = ""  # The funny comments added by humor agent
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert solution object to dictionary for easy serialization."""
        return {
            "id": self.id,
            "problem_id": self.problem_id,
            "language": self.language,
            "solution_code": self.solution_code,
            "explanation": self.explanation,
            "time_complexity": self.time_complexity,
            "space_complexity": self.space_complexity,
            "humor_comments": self.humor_comments,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
