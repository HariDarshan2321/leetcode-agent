"""
Database manager for the Leetcode Email Agent.
This file handles all database operations using SQLite.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import logging

try:
    from .models import User, Problem, SentProblem, Solution
    from ..config import Config
except ImportError:
    from src.database.models import User, Problem, SentProblem, Solution
    from src.config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages all database operations for the Leetcode Email Agent.
    Uses SQLite for simplicity and ease of deployment.
    """

    def __init__(self, db_path: str = None):
        """
        Initialize the database manager.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path or Config.DATABASE_PATH
        self._ensure_database_directory()
        self._initialize_database()

    def _ensure_database_directory(self):
        """Create the database directory if it doesn't exist."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created database directory: {db_dir}")

    def _get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection with proper configuration.

        Returns:
            SQLite connection object
        """
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        return conn

    def _initialize_database(self):
        """Create all necessary tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    preferred_language TEXT DEFAULT 'python',
                    preferred_difficulty TEXT DEFAULT 'medium',
                    solution_delivery TEXT DEFAULT 'with_problem',
                    solution_delay_hours INTEGER DEFAULT 24,
                    preferred_time TEXT DEFAULT '09:00',
                    timezone TEXT DEFAULT 'UTC',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create problems table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS problems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    test_cases TEXT,
                    constraints TEXT,
                    examples TEXT,
                    hints TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create sent_problems table (tracks what was sent to whom)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sent_problems (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    problem_id INTEGER NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    email_status TEXT DEFAULT 'pending',
                    solution_language TEXT DEFAULT 'python',
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (problem_id) REFERENCES problems (id),
                    UNIQUE(user_id, problem_id)
                )
            """)

            # Create solutions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    problem_id INTEGER NOT NULL,
                    language TEXT NOT NULL,
                    solution_code TEXT NOT NULL,
                    explanation TEXT,
                    time_complexity TEXT,
                    space_complexity TEXT,
                    humor_comments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (problem_id) REFERENCES problems (id)
                )
            """)

            conn.commit()
            logger.info("Database initialized successfully")

    # User management methods
    def add_user(self, email: str, preferred_language: str = "python",
                 preferred_difficulty: str = "medium", solution_delivery: str = "with_problem",
                 solution_delay_hours: int = 24) -> Optional[User]:
        """
        Add a new user to the database.

        Args:
            email: User's email address
            preferred_language: User's preferred programming language
            preferred_difficulty: User's preferred problem difficulty

        Returns:
            User object if successful, None otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (email, preferred_language, preferred_difficulty, solution_delivery, solution_delay_hours)
                    VALUES (?, ?, ?, ?, ?)
                """, (email, preferred_language, preferred_difficulty, solution_delivery, solution_delay_hours))

                user_id = cursor.lastrowid
                conn.commit()

                logger.info(f"Added new user: {email}")
                return self.get_user_by_id(user_id)

        except sqlite3.IntegrityError:
            logger.warning(f"User with email {email} already exists")
            return None
        except Exception as e:
            logger.error(f"Error adding user {email}: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email address."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()

                if row:
                    return User(
                        id=row["id"],
                        email=row["email"],
                        preferred_language=row["preferred_language"],
                        preferred_difficulty=row["preferred_difficulty"],
                        solution_delivery=row["solution_delivery"] if "solution_delivery" in row.keys() else "with_problem",
                        solution_delay_hours=row["solution_delay_hours"] if "solution_delay_hours" in row.keys() else 24,
                        preferred_time=row["preferred_time"] if "preferred_time" in row.keys() else "09:00",
                        timezone=row["timezone"] if "timezone" in row.keys() else "UTC",
                        is_active=bool(row["is_active"]),
                        created_at=datetime.fromisoformat(row["created_at"]),
                        updated_at=datetime.fromisoformat(row["updated_at"])
                    )
                return None

        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by their ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()

                if row:
                    return User(
                        id=row["id"],
                        email=row["email"],
                        preferred_language=row["preferred_language"],
                        preferred_difficulty=row["preferred_difficulty"],
                        solution_delivery=row["solution_delivery"] if "solution_delivery" in row.keys() else "with_problem",
                        solution_delay_hours=row["solution_delay_hours"] if "solution_delay_hours" in row.keys() else 24,
                        preferred_time=row["preferred_time"] if "preferred_time" in row.keys() else "09:00",
                        timezone=row["timezone"] if "timezone" in row.keys() else "UTC",
                        is_active=bool(row["is_active"]),
                        created_at=datetime.fromisoformat(row["created_at"]),
                        updated_at=datetime.fromisoformat(row["updated_at"])
                    )
                return None

        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

    def update_user_preferences(self, email: str, preferred_language: str = None,
                               preferred_difficulty: str = None) -> bool:
        """Update user preferences."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                updates = []
                params = []

                if preferred_language:
                    updates.append("preferred_language = ?")
                    params.append(preferred_language)

                if preferred_difficulty:
                    updates.append("preferred_difficulty = ?")
                    params.append(preferred_difficulty)

                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(email)

                    query = f"UPDATE users SET {', '.join(updates)} WHERE email = ?"
                    cursor.execute(query, params)
                    conn.commit()

                    logger.info(f"Updated preferences for user: {email}")
                    return cursor.rowcount > 0

                return False

        except Exception as e:
            logger.error(f"Error updating user preferences for {email}: {e}")
            return False

    def deactivate_user(self, email: str) -> bool:
        """Deactivate a user (unsubscribe)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE email = ?
                """, (email,))
                conn.commit()

                logger.info(f"Deactivated user: {email}")
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error deactivating user {email}: {e}")
            return False

    def get_active_users(self) -> List[User]:
        """Get all active users."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE is_active = 1")
                rows = cursor.fetchall()

                users = []
                for row in rows:
                    users.append(User(
                        id=row["id"],
                        email=row["email"],
                        preferred_language=row["preferred_language"],
                        preferred_difficulty=row["preferred_difficulty"],
                        solution_delivery=row["solution_delivery"] if "solution_delivery" in row.keys() else "with_problem",
                        solution_delay_hours=row["solution_delay_hours"] if "solution_delay_hours" in row.keys() else 24,
                        preferred_time=row["preferred_time"] if "preferred_time" in row.keys() else "09:00",
                        timezone=row["timezone"] if "timezone" in row.keys() else "UTC",
                        is_active=bool(row["is_active"]),
                        created_at=datetime.fromisoformat(row["created_at"]),
                        updated_at=datetime.fromisoformat(row["updated_at"])
                    ))

                return users

        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []

    # Problem management methods
    def add_problem(self, problem: Problem) -> Optional[Problem]:
        """Add a new problem to the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO problems (title, description, difficulty, test_cases,
                                        constraints, examples, hints, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    problem.title,
                    problem.description,
                    problem.difficulty,
                    problem.test_cases,
                    problem.constraints,
                    problem.examples,
                    problem.hints,
                    problem.tags
                ))

                problem_id = cursor.lastrowid
                conn.commit()

                logger.info(f"Added new problem: {problem.title}")
                return self.get_problem_by_id(problem_id)

        except Exception as e:
            logger.error(f"Error adding problem {problem.title}: {e}")
            return None

    def get_problem_by_id(self, problem_id: int) -> Optional[Problem]:
        """Get a problem by its ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
                row = cursor.fetchone()

                if row:
                    return Problem(
                        id=row["id"],
                        title=row["title"],
                        description=row["description"],
                        difficulty=row["difficulty"],
                        test_cases=row["test_cases"] or "",
                        constraints=row["constraints"] or "",
                        examples=row["examples"] or "",
                        hints=row["hints"] or "",
                        tags=row["tags"] or "",
                        created_at=datetime.fromisoformat(row["created_at"])
                    )
                return None

        except Exception as e:
            logger.error(f"Error getting problem by ID {problem_id}: {e}")
            return None

    def get_unsent_problem_for_user(self, user_id: int, difficulty: str) -> Optional[Problem]:
        """Get a problem that hasn't been sent to the user yet."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.* FROM problems p
                    WHERE p.difficulty = ?
                    AND p.id NOT IN (
                        SELECT sp.problem_id FROM sent_problems sp
                        WHERE sp.user_id = ?
                    )
                    ORDER BY RANDOM()
                    LIMIT 1
                """, (difficulty, user_id))

                row = cursor.fetchone()

                if row:
                    return Problem(
                        id=row["id"],
                        title=row["title"],
                        description=row["description"],
                        difficulty=row["difficulty"],
                        test_cases=row["test_cases"] or "",
                        constraints=row["constraints"] or "",
                        examples=row["examples"] or "",
                        hints=row["hints"] or "",
                        tags=row["tags"] or "",
                        created_at=datetime.fromisoformat(row["created_at"])
                    )
                return None

        except Exception as e:
            logger.error(f"Error getting unsent problem for user {user_id}: {e}")
            return None

    # Sent problems tracking
    def mark_problem_sent(self, user_id: int, problem_id: int,
                         solution_language: str, email_status: str = "sent") -> bool:
        """Mark a problem as sent to a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO sent_problems
                    (user_id, problem_id, solution_language, email_status)
                    VALUES (?, ?, ?, ?)
                """, (user_id, problem_id, solution_language, email_status))
                conn.commit()

                logger.info(f"Marked problem {problem_id} as sent to user {user_id}")
                return True

        except Exception as e:
            logger.error(f"Error marking problem sent: {e}")
            return False

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get statistics for a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Count total problems sent
                cursor.execute("""
                    SELECT COUNT(*) as total_sent FROM sent_problems
                    WHERE user_id = ? AND email_status = 'sent'
                """, (user_id,))
                total_sent = cursor.fetchone()["total_sent"]

                # Count by difficulty
                cursor.execute("""
                    SELECT p.difficulty, COUNT(*) as count
                    FROM sent_problems sp
                    JOIN problems p ON sp.problem_id = p.id
                    WHERE sp.user_id = ? AND sp.email_status = 'sent'
                    GROUP BY p.difficulty
                """, (user_id,))

                difficulty_stats = {row["difficulty"]: row["count"] for row in cursor.fetchall()}

                return {
                    "total_sent": total_sent,
                    "by_difficulty": difficulty_stats
                }

        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return {"total_sent": 0, "by_difficulty": {}}
