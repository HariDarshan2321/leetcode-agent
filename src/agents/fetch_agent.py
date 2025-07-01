"""
Fetch Agent for the Leetcode Email Agent.
This agent is responsible for retrieving coding problems from the data source.
"""

import json
import os
import logging
from typing import Optional, List
from datetime import datetime

try:
    from ..database.models import Problem
    from ..config import Config
except ImportError:
    from src.database.models import Problem
    from src.config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class FetchAgent:
    """
    Agent responsible for fetching coding problems.
    Currently uses a local JSON file, but can be extended to use APIs.
    """

    def __init__(self, problems_file: str = "data/problems.json"):
        """
        Initialize the Fetch Agent.

        Args:
            problems_file: Path to the JSON file containing problems
        """
        self.problems_file = problems_file
        self._problems_cache = None
        logger.info("FetchAgent initialized")

    def _load_problems(self) -> List[dict]:
        """
        Load problems from the JSON file.
        Uses caching to avoid reading the file multiple times.

        Returns:
            List of problem dictionaries
        """
        if self._problems_cache is None:
            try:
                if not os.path.exists(self.problems_file):
                    logger.error(f"Problems file not found: {self.problems_file}")
                    return []

                with open(self.problems_file, 'r', encoding='utf-8') as file:
                    self._problems_cache = json.load(file)
                    logger.info(f"Loaded {len(self._problems_cache)} problems from {self.problems_file}")

            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON file {self.problems_file}: {e}")
                return []
            except Exception as e:
                logger.error(f"Error loading problems file {self.problems_file}: {e}")
                return []

        return self._problems_cache or []

    def get_problem_by_difficulty(self, difficulty: str) -> Optional[Problem]:
        """
        Get a random problem by difficulty level.

        Args:
            difficulty: The difficulty level (easy, medium, hard)

        Returns:
            Problem object if found, None otherwise
        """
        try:
            problems = self._load_problems()
            if not problems:
                logger.warning("No problems available")
                return None

            # Filter problems by difficulty
            filtered_problems = [p for p in problems if p.get('difficulty', '').lower() == difficulty.lower()]

            if not filtered_problems:
                logger.warning(f"No problems found for difficulty: {difficulty}")
                return None

            # For now, just return the first one. In a real implementation,
            # you might want to randomize or track which ones have been used
            problem_data = filtered_problems[0]

            # Convert to Problem object
            problem = Problem(
                title=problem_data.get('title', ''),
                description=problem_data.get('description', ''),
                difficulty=problem_data.get('difficulty', difficulty),
                test_cases=problem_data.get('test_cases', ''),
                constraints=problem_data.get('constraints', ''),
                examples=problem_data.get('examples', ''),
                hints=problem_data.get('hints', ''),
                tags=problem_data.get('tags', ''),
                created_at=datetime.now()
            )

            logger.info(f"Fetched problem: {problem.title} (difficulty: {difficulty})")
            return problem

        except Exception as e:
            logger.error(f"Error fetching problem by difficulty {difficulty}: {e}")
            return None

    def get_problem_by_title(self, title: str) -> Optional[Problem]:
        """
        Get a specific problem by its title.

        Args:
            title: The title of the problem to fetch

        Returns:
            Problem object if found, None otherwise
        """
        try:
            problems = self._load_problems()
            if not problems:
                logger.warning("No problems available")
                return None

            # Find problem by title
            for problem_data in problems:
                if problem_data.get('title', '').lower() == title.lower():
                    problem = Problem(
                        title=problem_data.get('title', ''),
                        description=problem_data.get('description', ''),
                        difficulty=problem_data.get('difficulty', ''),
                        test_cases=problem_data.get('test_cases', ''),
                        constraints=problem_data.get('constraints', ''),
                        examples=problem_data.get('examples', ''),
                        hints=problem_data.get('hints', ''),
                        tags=problem_data.get('tags', ''),
                        created_at=datetime.now()
                    )

                    logger.info(f"Fetched problem by title: {problem.title}")
                    return problem

            logger.warning(f"Problem not found with title: {title}")
            return None

        except Exception as e:
            logger.error(f"Error fetching problem by title {title}: {e}")
            return None

    def get_all_problems(self) -> List[Problem]:
        """
        Get all available problems.

        Returns:
            List of Problem objects
        """
        try:
            problems_data = self._load_problems()
            problems = []

            for problem_data in problems_data:
                problem = Problem(
                    title=problem_data.get('title', ''),
                    description=problem_data.get('description', ''),
                    difficulty=problem_data.get('difficulty', ''),
                    test_cases=problem_data.get('test_cases', ''),
                    constraints=problem_data.get('constraints', ''),
                    examples=problem_data.get('examples', ''),
                    hints=problem_data.get('hints', ''),
                    tags=problem_data.get('tags', ''),
                    created_at=datetime.now()
                )
                problems.append(problem)

            logger.info(f"Fetched all {len(problems)} problems")
            return problems

        except Exception as e:
            logger.error(f"Error fetching all problems: {e}")
            return []

    def get_problems_by_difficulty(self, difficulty: str) -> List[Problem]:
        """
        Get all problems of a specific difficulty.

        Args:
            difficulty: The difficulty level (easy, medium, hard)

        Returns:
            List of Problem objects
        """
        try:
            problems_data = self._load_problems()
            filtered_problems = []

            for problem_data in problems_data:
                if problem_data.get('difficulty', '').lower() == difficulty.lower():
                    problem = Problem(
                        title=problem_data.get('title', ''),
                        description=problem_data.get('description', ''),
                        difficulty=problem_data.get('difficulty', ''),
                        test_cases=problem_data.get('test_cases', ''),
                        constraints=problem_data.get('constraints', ''),
                        examples=problem_data.get('examples', ''),
                        hints=problem_data.get('hints', ''),
                        tags=problem_data.get('tags', ''),
                        created_at=datetime.now()
                    )
                    filtered_problems.append(problem)

            logger.info(f"Fetched {len(filtered_problems)} problems for difficulty: {difficulty}")
            return filtered_problems

        except Exception as e:
            logger.error(f"Error fetching problems by difficulty {difficulty}: {e}")
            return []

    def get_available_difficulties(self) -> List[str]:
        """
        Get all available difficulty levels.

        Returns:
            List of difficulty strings
        """
        try:
            problems = self._load_problems()
            difficulties = set()

            for problem in problems:
                difficulty = problem.get('difficulty', '').lower()
                if difficulty:
                    difficulties.add(difficulty)

            result = sorted(list(difficulties))
            logger.info(f"Available difficulties: {result}")
            return result

        except Exception as e:
            logger.error(f"Error getting available difficulties: {e}")
            return []

    def refresh_cache(self):
        """
        Clear the problems cache to force reload from file.
        Useful when the problems file has been updated.
        """
        self._problems_cache = None
        logger.info("Problems cache refreshed")

    def get_stats(self) -> dict:
        """
        Get statistics about available problems.

        Returns:
            Dictionary with problem statistics
        """
        try:
            problems = self._load_problems()
            if not problems:
                return {"total": 0, "by_difficulty": {}}

            stats = {
                "total": len(problems),
                "by_difficulty": {}
            }

            # Count by difficulty
            for problem in problems:
                difficulty = problem.get('difficulty', 'unknown').lower()
                stats["by_difficulty"][difficulty] = stats["by_difficulty"].get(difficulty, 0) + 1

            logger.info(f"Problem stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error getting problem stats: {e}")
            return {"total": 0, "by_difficulty": {}}
