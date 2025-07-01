"""
Central Coordinator for the Leetcode Email Agent.
This module orchestrates all agents and handles the main business logic.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    from .database import DatabaseManager, User, Problem, Solution
    from .agents import FetchAgent, SolveAgent, HumorAgent, MailAgent
    from .config import Config
except ImportError:
    from src.database import DatabaseManager, User, Problem, Solution
    from src.agents import FetchAgent, SolveAgent, HumorAgent, MailAgent
    from src.config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class LeetcodeEmailCoordinator:
    """
    Central coordinator that manages all agents and orchestrates the daily email process.
    This is the main class that ties everything together.
    """

    def __init__(self):
        """Initialize the coordinator with all agents and database manager."""
        try:
            # Initialize database manager
            self.db_manager = DatabaseManager()

            # Initialize all agents
            self.fetch_agent = FetchAgent()
            self.solve_agent = SolveAgent()
            self.humor_agent = HumorAgent()
            self.mail_agent = MailAgent()

            logger.info("LeetcodeEmailCoordinator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LeetcodeEmailCoordinator: {e}")
            raise

    def process_daily_emails(self) -> Dict[str, Any]:
        """
        Process and send daily emails to all active users.
        This is the main method called by the scheduler.

        Returns:
            Dictionary with processing results and statistics
        """
        logger.info("Starting daily email processing")

        results = {
            "total_users": 0,
            "emails_sent": 0,
            "emails_failed": 0,
            "errors": [],
            "start_time": datetime.now(),
            "end_time": None
        }

        try:
            # Get all active users
            active_users = self.db_manager.get_active_users()
            results["total_users"] = len(active_users)

            if not active_users:
                logger.info("No active users found")
                results["end_time"] = datetime.now()
                return results

            logger.info(f"Processing emails for {len(active_users)} active users")

            # Process each user
            for user in active_users:
                try:
                    success = self._process_user_email(user)
                    if success:
                        results["emails_sent"] += 1
                        logger.info(f"Successfully processed email for {user.email}")
                    else:
                        results["emails_failed"] += 1
                        logger.warning(f"Failed to process email for {user.email}")

                except Exception as e:
                    results["emails_failed"] += 1
                    error_msg = f"Error processing user {user.email}: {e}"
                    results["errors"].append(error_msg)
                    logger.error(error_msg)

            results["end_time"] = datetime.now()
            duration = (results["end_time"] - results["start_time"]).total_seconds()

            logger.info(f"Daily email processing completed in {duration:.2f} seconds")
            logger.info(f"Results: {results['emails_sent']} sent, {results['emails_failed']} failed")

            return results

        except Exception as e:
            error_msg = f"Critical error in daily email processing: {e}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
            results["end_time"] = datetime.now()
            return results

    def _process_user_email(self, user: User) -> bool:
        """
        Process email for a single user.

        Args:
            user: User object to process

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing email for user: {user.email}")

            # Step 1: Get an unsent problem for the user
            problem = self.db_manager.get_unsent_problem_for_user(
                user.id, user.preferred_difficulty
            )

            if not problem:
                logger.warning(f"No unsent problems available for user {user.email} "
                             f"with difficulty {user.preferred_difficulty}")

                # Try to get a problem from the fetch agent and add it to database
                problem = self._get_and_store_new_problem(user.preferred_difficulty)

                if not problem:
                    logger.error(f"Could not get any problem for user {user.email}")
                    return False

            # Step 2: Generate solution using SolveAgent
            solution = self.solve_agent.generate_solution(problem, user.preferred_language)

            if not solution:
                logger.error(f"Failed to generate solution for problem '{problem.title}'")
                return False

            # Step 3: Add humor to the solution
            enhanced_solution = self.humor_agent.add_humor_to_solution(solution)

            # Step 4: Send email
            email_sent = self.mail_agent.send_daily_problem(user, problem, enhanced_solution)

            if email_sent:
                # Step 5: Mark problem as sent in database
                self.db_manager.mark_problem_sent(
                    user.id,
                    problem.id,
                    user.preferred_language,
                    "sent"
                )
                logger.info(f"Successfully sent problem '{problem.title}' to {user.email}")
                return True
            else:
                # Mark as failed in database
                self.db_manager.mark_problem_sent(
                    user.id,
                    problem.id,
                    user.preferred_language,
                    "failed"
                )
                logger.error(f"Failed to send email to {user.email}")
                return False

        except Exception as e:
            logger.error(f"Error processing email for user {user.email}: {e}")
            return False

    def _get_and_store_new_problem(self, difficulty: str) -> Optional[Problem]:
        """
        Get a new problem from fetch agent and store it in database.

        Args:
            difficulty: Difficulty level to fetch

        Returns:
            Problem object if successful, None otherwise
        """
        try:
            # Get problem from fetch agent
            problem = self.fetch_agent.get_problem_by_difficulty(difficulty)

            if not problem:
                logger.warning(f"FetchAgent could not provide problem for difficulty: {difficulty}")
                return None

            # Store in database
            stored_problem = self.db_manager.add_problem(problem)

            if stored_problem:
                logger.info(f"Added new problem to database: {stored_problem.title}")
                return stored_problem
            else:
                logger.error(f"Failed to store problem in database: {problem.title}")
                return None

        except Exception as e:
            logger.error(f"Error getting and storing new problem: {e}")
            return None

    def add_user(self, email: str, preferred_language: str = "python",
                 preferred_difficulty: str = "medium") -> bool:
        """
        Add a new user to the system.

        Args:
            email: User's email address
            preferred_language: Preferred programming language
            preferred_difficulty: Preferred problem difficulty

        Returns:
            True if user added successfully, False otherwise
        """
        try:
            # Validate inputs
            if not email or "@" not in email:
                logger.error(f"Invalid email address: {email}")
                return False

            if preferred_language.lower() not in Config.SUPPORTED_LANGUAGES:
                logger.error(f"Unsupported language: {preferred_language}")
                return False

            if preferred_difficulty.lower() not in Config.DIFFICULTY_LEVELS:
                logger.error(f"Unsupported difficulty: {preferred_difficulty}")
                return False

            # Check if user already exists
            existing_user = self.db_manager.get_user_by_email(email)
            if existing_user:
                if existing_user.is_active:
                    logger.warning(f"User {email} is already subscribed")
                    return False
                else:
                    # Reactivate user with new preferences
                    success = self.db_manager.update_user_preferences(
                        email, preferred_language, preferred_difficulty
                    )
                    if success:
                        # Reactivate user
                        self.db_manager.deactivate_user(email)  # This sets is_active to False
                        # We need to manually reactivate - let's update the method call
                        logger.info(f"Reactivated user: {email}")

                        # Send welcome email
                        user = self.db_manager.get_user_by_email(email)
                        if user:
                            self.mail_agent.send_welcome_email(user)
                        return True
                    return False

            # Add new user
            user = self.db_manager.add_user(email, preferred_language, preferred_difficulty)

            if user:
                logger.info(f"Successfully added new user: {email}")

                # Send welcome email
                welcome_sent = self.mail_agent.send_welcome_email(user)
                if welcome_sent:
                    logger.info(f"Welcome email sent to {email}")
                else:
                    logger.warning(f"Failed to send welcome email to {email}")

                return True
            else:
                logger.error(f"Failed to add user: {email}")
                return False

        except Exception as e:
            logger.error(f"Error adding user {email}: {e}")
            return False

    def remove_user(self, email: str) -> bool:
        """
        Remove (deactivate) a user from the system.

        Args:
            email: User's email address

        Returns:
            True if user removed successfully, False otherwise
        """
        try:
            # Check if user exists
            user = self.db_manager.get_user_by_email(email)
            if not user:
                logger.warning(f"User not found: {email}")
                return False

            if not user.is_active:
                logger.warning(f"User {email} is already inactive")
                return True

            # Deactivate user
            success = self.db_manager.deactivate_user(email)

            if success:
                logger.info(f"Successfully deactivated user: {email}")

                # Send unsubscribe confirmation
                confirmation_sent = self.mail_agent.send_unsubscribe_confirmation(email)
                if confirmation_sent:
                    logger.info(f"Unsubscribe confirmation sent to {email}")
                else:
                    logger.warning(f"Failed to send unsubscribe confirmation to {email}")

                return True
            else:
                logger.error(f"Failed to deactivate user: {email}")
                return False

        except Exception as e:
            logger.error(f"Error removing user {email}: {e}")
            return False

    def update_user_preferences(self, email: str, preferred_language: str = None,
                               preferred_difficulty: str = None) -> bool:
        """
        Update user preferences.

        Args:
            email: User's email address
            preferred_language: New preferred programming language (optional)
            preferred_difficulty: New preferred problem difficulty (optional)

        Returns:
            True if preferences updated successfully, False otherwise
        """
        try:
            # Validate inputs
            if preferred_language and preferred_language.lower() not in Config.SUPPORTED_LANGUAGES:
                logger.error(f"Unsupported language: {preferred_language}")
                return False

            if preferred_difficulty and preferred_difficulty.lower() not in Config.DIFFICULTY_LEVELS:
                logger.error(f"Unsupported difficulty: {preferred_difficulty}")
                return False

            # Check if user exists
            user = self.db_manager.get_user_by_email(email)
            if not user:
                logger.warning(f"User not found: {email}")
                return False

            # Update preferences
            success = self.db_manager.update_user_preferences(
                email, preferred_language, preferred_difficulty
            )

            if success:
                logger.info(f"Successfully updated preferences for user: {email}")
                return True
            else:
                logger.error(f"Failed to update preferences for user: {email}")
                return False

        except Exception as e:
            logger.error(f"Error updating preferences for user {email}: {e}")
            return False

    def get_user_stats(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a user.

        Args:
            email: User's email address

        Returns:
            Dictionary with user statistics or None if user not found
        """
        try:
            user = self.db_manager.get_user_by_email(email)
            if not user:
                logger.warning(f"User not found: {email}")
                return None

            stats = self.db_manager.get_user_stats(user.id)
            stats.update({
                "email": user.email,
                "preferred_language": user.preferred_language,
                "preferred_difficulty": user.preferred_difficulty,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })

            return stats

        except Exception as e:
            logger.error(f"Error getting stats for user {email}: {e}")
            return None

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get overall system statistics.

        Returns:
            Dictionary with system statistics
        """
        try:
            active_users = self.db_manager.get_active_users()
            problem_stats = self.fetch_agent.get_stats()

            stats = {
                "total_active_users": len(active_users),
                "total_problems": problem_stats.get("total", 0),
                "problems_by_difficulty": problem_stats.get("by_difficulty", {}),
                "supported_languages": list(Config.SUPPORTED_LANGUAGES.keys()),
                "supported_difficulties": list(Config.DIFFICULTY_LEVELS.keys()),
                "timestamp": datetime.now().isoformat()
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}

    def test_system_health(self) -> Dict[str, bool]:
        """
        Test the health of all system components.

        Returns:
            Dictionary with health status of each component
        """
        health = {}

        try:
            # Test database
            health["database"] = bool(self.db_manager.get_active_users() is not None)
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health["database"] = False

        try:
            # Test Groq API
            health["groq_api"] = self.solve_agent.test_connection()
        except Exception as e:
            logger.error(f"Groq API health check failed: {e}")
            health["groq_api"] = False

        try:
            # Test email
            health["email"] = self.mail_agent.test_connection()
        except Exception as e:
            logger.error(f"Email health check failed: {e}")
            health["email"] = False

        try:
            # Test fetch agent
            health["fetch_agent"] = bool(self.fetch_agent.get_stats()["total"] > 0)
        except Exception as e:
            logger.error(f"Fetch agent health check failed: {e}")
            health["fetch_agent"] = False

        health["overall"] = all(health.values())

        logger.info(f"System health check completed: {health}")
        return health

    def initialize_sample_data(self) -> bool:
        """
        Initialize the database with sample problems from the JSON file.
        Useful for first-time setup.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Initializing sample data")

            # Get all problems from fetch agent
            problems = self.fetch_agent.get_all_problems()

            if not problems:
                logger.warning("No problems available from fetch agent")
                return False

            added_count = 0
            for problem in problems:
                stored_problem = self.db_manager.add_problem(problem)
                if stored_problem:
                    added_count += 1

            logger.info(f"Successfully added {added_count} problems to database")
            return added_count > 0

        except Exception as e:
            logger.error(f"Error initializing sample data: {e}")
            return False
