"""
Humor Agent for the Leetcode Email Agent.
This agent adds funny comments and analogies to make coding solutions more engaging.
"""

import logging
import random
from typing import Optional, List, Dict
import re

try:
    from ..database.models import Solution
    from ..config import Config
except ImportError:
    from src.database.models import Solution
    from src.config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class HumorAgent:
    """
    Agent responsible for adding humor to coding solutions.
    Makes technical content more engaging and fun to read.
    """

    def __init__(self):
        """Initialize the Humor Agent with joke templates."""
        self.humor_templates = self._load_humor_templates()
        logger.info("HumorAgent initialized")

    def _load_humor_templates(self) -> Dict[str, List[str]]:
        """
        Load humor templates for different programming concepts.

        Returns:
            Dictionary of humor templates organized by category
        """
        return {
            "general": [
                "// This code is like a good joke - it works better when you don't explain it",
                "// If debugging is the process of removing bugs, then programming must be the process of putting them in",
                "// Code never lies, comments sometimes do, but this one is telling the truth",
                "// This solution is so elegant, it should be wearing a tuxedo",
                "// Warning: This code may cause sudden understanding and mild euphoria",
                "// Like a fine wine, this algorithm gets better with time complexity analysis",
                "// This function is more reliable than my morning alarm clock",
                "// Roses are red, violets are blue, this code works, and so will you!"
            ],
            "loops": [
                "// This loop is like my motivation on Monday morning - it takes a while to get going",
                "// Loop-de-loop! We're going around more times than a confused GPS",
                "// This while loop is more persistent than a telemarketer",
                "// For loop: because sometimes you need to repeat yourself, repeat yourself, repeat yourself...",
                "// This iteration is brought to you by the letter 'i' and the number of times I've debugged this",
                "// Going in circles? That's just how we roll in programming!"
            ],
            "arrays": [
                "// Arrays: because life is too short to access elements one at a time",
                "// This array is more organized than my desk (which isn't saying much)",
                "// Zero-indexed arrays: because programmers like to start counting from scratch",
                "// Array access faster than my internet connection",
                "// This array has more elements than my periodic table knowledge",
                "// Accessing array elements like a boss (a very methodical, zero-indexed boss)"
            ],
            "hash_tables": [
                "// Hash tables: where every key finds its perfect match (unlike dating apps)",
                "// O(1) lookup time - faster than finding your keys in the morning",
                "// This hash map is more reliable than my memory",
                "// Collision resolution: because even hash functions have relationship problems",
                "// Hash tables: making dictionaries jealous since forever",
                "// Key-value pairs: the ultimate relationship goals"
            ],
            "recursion": [
                "// To understand recursion, you must first understand recursion",
                "// This function calls itself more than I call my mom (sorry mom)",
                "// Recursion: because sometimes the best way out is through... yourself",
                "// Base case: the light at the end of the recursive tunnel",
                "// Stack overflow? More like stack overflow of awesomeness!",
                "// Recursive calls: it's functions all the way down"
            ],
            "sorting": [
                "// Sorting: because chaos is only fun in small doses",
                "// This sort is more organized than my life",
                "// Bubble sort: like gossip, but for numbers",
                "// Quick sort: living up to its name since 1960",
                "// Merge sort: divide and conquer, just like my approach to pizza",
                "// Sorting algorithms: bringing order to the universe, one array at a time"
            ],
            "binary_search": [
                "// Binary search: because linear search is for quitters",
                "// Divide and conquer: the programmer's guide to problem solving and pizza ordering",
                "// This search is more efficient than looking for my car keys",
                "// Binary search: when you need to find something faster than 'Where's Waldo?'",
                "// Logarithmic time: because exponential problems need logarithmic solutions",
                "// Cutting the search space in half, like a digital samurai"
            ],
            "dynamic_programming": [
                "// Dynamic programming: because sometimes you need to remember the past to solve the future",
                "// Memoization: the art of not repeating your mistakes (or calculations)",
                "// This DP solution has more memory than an elephant",
                "// Optimal substructure: like LEGO blocks, but for algorithms",
                "// Trading space for time, like renting a bigger apartment for faster commute",
                "// Bottom-up approach: building solutions like a skyscraper"
            ],
            "edge_cases": [
                "// Edge case handling: because Murphy's Law applies to code too",
                "// This handles edge cases better than I handle Monday mornings",
                "// Edge cases: the plot twists of programming",
                "// Boundary conditions: where algorithms go to test their limits",
                "// Error handling: because optimism is great, but validation is better",
                "// Defensive programming: like wearing a helmet while coding"
            ],
            "optimization": [
                "// Optimized for speed and developer happiness",
                "// This optimization is smoother than my dance moves",
                "// Performance tuning: making code faster than a caffeinated cheetah",
                "// Micro-optimizations: because every nanosecond counts",
                "// This runs faster than my motivation on Friday afternoon",
                "// Efficiency level: over 9000!"
            ]
        }

    def add_humor_to_solution(self, solution: Solution) -> Solution:
        """
        Add humorous comments to a coding solution.

        Args:
            solution: The Solution object to enhance with humor

        Returns:
            Updated Solution object with humor added
        """
        try:
            if not solution.solution_code:
                logger.warning("No solution code to add humor to")
                return solution

            # Analyze the code to determine appropriate humor categories
            humor_categories = self._analyze_code_for_humor(solution.solution_code, solution.language)

            # Generate humorous comments
            humor_comments = self._generate_humor_comments(humor_categories, solution.language)

            # Add humor to the code
            enhanced_code = self._inject_humor_into_code(solution.solution_code, humor_comments, solution.language)

            # Update the solution
            solution.solution_code = enhanced_code
            solution.humor_comments = "\n".join(humor_comments)

            logger.info(f"Added humor to solution in {solution.language}")
            return solution

        except Exception as e:
            logger.error(f"Error adding humor to solution: {e}")
            return solution

    def _analyze_code_for_humor(self, code: str, language: str) -> List[str]:
        """
        Analyze code to determine which humor categories are appropriate.

        Args:
            code: The source code to analyze
            language: Programming language

        Returns:
            List of humor categories that apply to this code
        """
        categories = ["general"]  # Always include general humor
        code_lower = code.lower()

        # Check for different programming concepts
        if any(keyword in code_lower for keyword in ["for", "while", "loop"]):
            categories.append("loops")

        if any(keyword in code_lower for keyword in ["array", "list", "[]", "nums"]):
            categories.append("arrays")

        if any(keyword in code_lower for keyword in ["dict", "map", "hash", "{}", "hashmap"]):
            categories.append("hash_tables")

        if "def " in code_lower and code_lower.count("def ") > 1:  # Likely recursive
            categories.append("recursion")

        if any(keyword in code_lower for keyword in ["sort", "sorted", "quicksort", "mergesort"]):
            categories.append("sorting")

        if any(keyword in code_lower for keyword in ["binary", "search", "left", "right", "mid"]):
            categories.append("binary_search")

        if any(keyword in code_lower for keyword in ["dp", "memo", "cache", "dynamic"]):
            categories.append("dynamic_programming")

        if any(keyword in code_lower for keyword in ["if", "else", "try", "except", "error"]):
            categories.append("edge_cases")

        # Always add optimization category for variety
        categories.append("optimization")

        return categories

    def _generate_humor_comments(self, categories: List[str], language: str) -> List[str]:
        """
        Generate humorous comments based on the identified categories.

        Args:
            categories: List of humor categories to use
            language: Programming language for comment syntax

        Returns:
            List of humorous comments
        """
        comments = []
        comment_prefix = self._get_comment_prefix(language)

        # Select 2-4 random comments from available categories
        num_comments = random.randint(2, 4)

        for _ in range(num_comments):
            category = random.choice(categories)
            if category in self.humor_templates:
                template = random.choice(self.humor_templates[category])
                # Adapt comment syntax for the language
                if not template.startswith("//") and not template.startswith("#"):
                    template = f"{comment_prefix} {template}"
                elif template.startswith("//") and comment_prefix != "//":
                    template = template.replace("//", comment_prefix, 1)
                elif template.startswith("#") and comment_prefix != "#":
                    template = template.replace("#", comment_prefix, 1)

                comments.append(template)

        return comments

    def _get_comment_prefix(self, language: str) -> str:
        """
        Get the appropriate comment prefix for the programming language.

        Args:
            language: Programming language

        Returns:
            Comment prefix string
        """
        comment_styles = {
            "python": "#",
            "java": "//",
            "cpp": "//",
            "javascript": "//",
            "go": "//",
            "rust": "//"
        }

        return comment_styles.get(language.lower(), "//")

    def _inject_humor_into_code(self, code: str, humor_comments: List[str], language: str) -> str:
        """
        Inject humorous comments into the code at appropriate locations.

        Args:
            code: Original source code
            humor_comments: List of humorous comments to inject
            language: Programming language

        Returns:
            Enhanced code with humor injected
        """
        if not humor_comments:
            return code

        lines = code.split('\n')
        enhanced_lines = []
        comment_index = 0

        # Add a funny header comment
        if humor_comments:
            enhanced_lines.append(humor_comments[0])
            enhanced_lines.append("")
            comment_index = 1

        for i, line in enumerate(lines):
            enhanced_lines.append(line)

            # Add humor at strategic points
            if comment_index < len(humor_comments):
                # Add humor after function definitions
                if self._is_function_definition(line, language):
                    enhanced_lines.append(f"    {humor_comments[comment_index]}")
                    comment_index += 1
                # Add humor before return statements
                elif "return" in line.strip() and comment_index < len(humor_comments):
                    indent = self._get_line_indent(line)
                    enhanced_lines.insert(-1, f"{indent}{humor_comments[comment_index]}")
                    comment_index += 1
                # Add humor at the end of loops
                elif self._is_loop_end(line, lines, i, language) and comment_index < len(humor_comments):
                    indent = self._get_line_indent(line)
                    enhanced_lines.append(f"{indent}{humor_comments[comment_index]}")
                    comment_index += 1

        # Add any remaining comments at the end
        if comment_index < len(humor_comments):
            enhanced_lines.append("")
            for remaining_comment in humor_comments[comment_index:]:
                enhanced_lines.append(remaining_comment)

        return '\n'.join(enhanced_lines)

    def _is_function_definition(self, line: str, language: str) -> bool:
        """Check if a line contains a function definition."""
        line_stripped = line.strip()

        if language.lower() == "python":
            return line_stripped.startswith("def ")
        elif language.lower() == "java":
            return "public" in line_stripped and "(" in line_stripped and "{" in line_stripped
        elif language.lower() in ["cpp", "javascript", "go"]:
            return "function" in line_stripped or ("(" in line_stripped and "{" in line_stripped)
        elif language.lower() == "rust":
            return line_stripped.startswith("fn ")

        return False

    def _is_loop_end(self, line: str, lines: List[str], index: int, language: str) -> bool:
        """Check if this might be a good place to add a loop-related comment."""
        # Simple heuristic: look for dedented lines after indented blocks
        if index == 0 or index >= len(lines) - 1:
            return False

        current_indent = len(line) - len(line.lstrip())
        prev_indent = len(lines[index - 1]) - len(lines[index - 1].lstrip())

        return current_indent < prev_indent and prev_indent > 0

    def _get_line_indent(self, line: str) -> str:
        """Get the indentation of a line."""
        return line[:len(line) - len(line.lstrip())]

    def generate_funny_explanation(self, solution: Solution) -> str:
        """
        Generate a funny explanation for the solution approach.

        Args:
            solution: The Solution object

        Returns:
            Humorous explanation string
        """
        try:
            funny_intros = [
                "🎭 Let me break this down like a stand-up comedian explaining quantum physics:",
                "🎪 Imagine this algorithm as a circus act where every variable is a performer:",
                "🍕 Think of this solution like making the perfect pizza - it's all about the right ingredients:",
                "🎮 This algorithm is like a video game strategy guide, but funnier:",
                "🎬 Picture this solution as a movie plot (spoiler alert: it has a happy ending):",
                "🎨 This code is like a masterpiece painting, except it actually works:",
                "🎵 Let's sing the song of this algorithm (warning: may get stuck in your head):"
            ]

            funny_conclusions = [
                "And that's how we turn chaos into order, one line of code at a time! 🎉",
                "Boom! Problem solved faster than you can say 'stack overflow'! 💥",
                "And voilà! We've just performed algorithmic magic! ✨",
                "Mission accomplished! Time to celebrate with some coffee ☕",
                "That's a wrap! This solution is ready for its close-up 🎬",
                "And they all lived efficiently ever after! 📚",
                "Plot twist: the algorithm actually works! 🎭"
            ]

            intro = random.choice(funny_intros)
            conclusion = random.choice(funny_conclusions)

            # Use the original explanation as the middle part
            original_explanation = solution.explanation or "This solution works by applying computer science magic!"

            funny_explanation = f"{intro}\n\n{original_explanation}\n\n{conclusion}"

            logger.info("Generated funny explanation")
            return funny_explanation

        except Exception as e:
            logger.error(f"Error generating funny explanation: {e}")
            return solution.explanation or "This solution is so good, it explains itself!"

    def add_complexity_humor(self, time_complexity: str, space_complexity: str) -> tuple:
        """
        Add humor to complexity analysis.

        Args:
            time_complexity: Original time complexity
            space_complexity: Original space complexity

        Returns:
            Tuple of (funny_time_complexity, funny_space_complexity)
        """
        try:
            time_jokes = {
                "O(1)": "O(1) - Faster than instant noodles! ⚡",
                "O(log n)": "O(log n) - Logarithmically awesome, like compound interest! 📈",
                "O(n)": "O(n) - Linear time, like reading a book page by page 📖",
                "O(n log n)": "O(n log n) - The sweet spot of sorting algorithms! 🍯",
                "O(n²)": "O(n²) - Quadratic time, like nested loops having a party 🎉",
                "O(2^n)": "O(2^n) - Exponential time, use with caution! ⚠️"
            }

            space_jokes = {
                "O(1)": "O(1) - More memory efficient than my brain on Monday morning! 🧠",
                "O(log n)": "O(log n) - Logarithmic space, like a well-organized closet 👔",
                "O(n)": "O(n) - Linear space, proportional to the problem size 📏",
                "O(n²)": "O(n²) - Quadratic space, like hoarding but for algorithms 📦"
            }

            funny_time = time_jokes.get(time_complexity, f"{time_complexity} - Time complexity that gets the job done! ⏰")
            funny_space = space_jokes.get(space_complexity, f"{space_complexity} - Space complexity that's worth the memory! 💾")

            return funny_time, funny_space

        except Exception as e:
            logger.error(f"Error adding complexity humor: {e}")
            return time_complexity, space_complexity

    def get_random_programming_joke(self) -> str:
        """
        Get a random programming joke for general entertainment.

        Returns:
            Random programming joke
        """
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💡",
            "Why do Java developers wear glasses? Because they can't C#! 👓",
            "What's a programmer's favorite hangout place? Foo Bar! 🍺",
            "Why did the programmer quit his job? He didn't get arrays! 📊",
            "How do you comfort a JavaScript bug? You console it! 🎮",
            "Why do programmers hate nature? It has too many bugs! 🌿",
            "What do you call a programmer from Finland? Nerdic! 🇫🇮"
        ]

        return random.choice(jokes)
