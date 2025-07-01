"""
Solve Agent for the Leetcode Email Agent.
This agent uses Groq API to generate solutions for coding problems.
"""

import logging
from typing import Optional, Dict, Any
from groq import Groq

try:
    from ..database.models import Problem, Solution
    from ..config import Config
except ImportError:
    from src.database.models import Problem, Solution
    from src.config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class SolveAgent:
    """
    Agent responsible for generating solutions to coding problems using Groq API.
    Supports multiple programming languages and provides detailed explanations.
    """

    def __init__(self):
        """Initialize the Solve Agent with Groq client."""
        try:
            self.client = Groq(api_key=Config.GROQ_API_KEY)
            logger.info("SolveAgent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SolveAgent: {e}")
            self.client = None

    def _get_language_template(self, language: str) -> Dict[str, str]:
        """
        Get language-specific templates and instructions.

        Args:
            language: Programming language (python, java, cpp, etc.)

        Returns:
            Dictionary with language-specific templates
        """
        templates = {
            "python": {
                "comment_style": "#",
                "function_template": "def solution():\n    pass",
                "example": "def two_sum(nums, target):\n    # Your solution here\n    pass"
            },
            "java": {
                "comment_style": "//",
                "function_template": "public class Solution {\n    public void solution() {\n        // Your code here\n    }\n}",
                "example": "public class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Your solution here\n        return new int[0];\n    }\n}"
            },
            "cpp": {
                "comment_style": "//",
                "function_template": "class Solution {\npublic:\n    void solution() {\n        // Your code here\n    }\n};",
                "example": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Your solution here\n        return {};\n    }\n};"
            },
            "javascript": {
                "comment_style": "//",
                "function_template": "function solution() {\n    // Your code here\n}",
                "example": "function twoSum(nums, target) {\n    // Your solution here\n    return [];\n}"
            },
            "go": {
                "comment_style": "//",
                "function_template": "func solution() {\n    // Your code here\n}",
                "example": "func twoSum(nums []int, target int) []int {\n    // Your solution here\n    return []int{}\n}"
            },
            "rust": {
                "comment_style": "//",
                "function_template": "fn solution() {\n    // Your code here\n}",
                "example": "fn two_sum(nums: Vec<i32>, target: i32) -> Vec<i32> {\n    // Your solution here\n    vec![]\n}"
            }
        }

        return templates.get(language.lower(), templates["python"])

    def _create_solution_prompt(self, problem: Problem, language: str) -> str:
        """
        Create a detailed prompt for the Groq API to generate a solution.

        Args:
            problem: The Problem object to solve
            language: Programming language for the solution

        Returns:
            Formatted prompt string
        """
        lang_template = self._get_language_template(language)

        prompt = f"""
You are an expert software engineer. Please solve the following coding problem in {language.upper()}.

PROBLEM TITLE: {problem.title}

PROBLEM DESCRIPTION:
{problem.description}

CONSTRAINTS:
{problem.constraints}

EXAMPLES:
{problem.examples}

REQUIREMENTS:
1. Provide a complete, working solution in {language.upper()}
2. Include detailed comments explaining the approach
3. Analyze time and space complexity
4. Provide a clear explanation of the algorithm
5. Make sure the solution handles all edge cases mentioned in the constraints

Please structure your response as follows:

SOLUTION:
```{language}
[Your complete solution code here]
```

EXPLANATION:
[Detailed explanation of your approach and algorithm]

TIME COMPLEXITY:
[Big O time complexity analysis]

SPACE COMPLEXITY:
[Big O space complexity analysis]

APPROACH:
[Step-by-step breakdown of the solution approach]
"""

        return prompt

    def generate_solution(self, problem: Problem, language: str = "python") -> Optional[Solution]:
        """
        Generate a solution for the given problem in the specified language.

        Args:
            problem: The Problem object to solve
            language: Programming language for the solution (default: python)

        Returns:
            Solution object if successful, None otherwise
        """
        if not self.client:
            logger.error("Groq client not initialized")
            return None

        try:
            # Validate language
            if language.lower() not in Config.SUPPORTED_LANGUAGES:
                logger.warning(f"Unsupported language: {language}. Using Python instead.")
                language = "python"

            # Create the prompt
            prompt = self._create_solution_prompt(problem, language)

            logger.info(f"Generating solution for '{problem.title}' in {language}")

            # Call Groq API
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",  # Using Llama3 model (Mixtral was decommissioned)
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software engineer and competitive programmer. Provide clear, efficient, and well-commented solutions to coding problems."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent code generation
                max_tokens=2000,
                top_p=1,
                stream=False
            )

            if not response.choices:
                logger.error("No response from Groq API")
                return None

            content = response.choices[0].message.content

            # Parse the response to extract different sections
            solution_data = self._parse_solution_response(content, language)

            # Create Solution object
            solution = Solution(
                problem_id=problem.id,
                language=language.lower(),
                solution_code=solution_data.get("code", ""),
                explanation=solution_data.get("explanation", ""),
                time_complexity=solution_data.get("time_complexity", ""),
                space_complexity=solution_data.get("space_complexity", ""),
                humor_comments="",  # Will be filled by HumorAgent
            )

            logger.info(f"Successfully generated solution for '{problem.title}' in {language}")
            return solution

        except Exception as e:
            logger.error(f"Error generating solution for '{problem.title}': {e}")
            return None

    def _parse_solution_response(self, content: str, language: str) -> Dict[str, str]:
        """
        Parse the Groq API response to extract different sections.

        Args:
            content: Raw response content from Groq API
            language: Programming language used

        Returns:
            Dictionary with parsed sections
        """
        result = {
            "code": "",
            "explanation": "",
            "time_complexity": "",
            "space_complexity": "",
            "approach": ""
        }

        try:
            lines = content.split('\n')
            current_section = None
            current_content = []

            for line in lines:
                line_lower = line.lower().strip()

                # Detect section headers
                if line_lower.startswith('solution:'):
                    current_section = "code"
                    current_content = []
                elif line_lower.startswith('explanation:'):
                    if current_section == "code":
                        result["code"] = self._extract_code_block('\n'.join(current_content), language)
                    current_section = "explanation"
                    current_content = []
                elif line_lower.startswith('time complexity:'):
                    if current_section == "explanation":
                        result["explanation"] = '\n'.join(current_content).strip()
                    current_section = "time_complexity"
                    current_content = []
                elif line_lower.startswith('space complexity:'):
                    if current_section == "time_complexity":
                        result["time_complexity"] = '\n'.join(current_content).strip()
                    current_section = "space_complexity"
                    current_content = []
                elif line_lower.startswith('approach:'):
                    if current_section == "space_complexity":
                        result["space_complexity"] = '\n'.join(current_content).strip()
                    current_section = "approach"
                    current_content = []
                else:
                    if current_section:
                        current_content.append(line)

            # Handle the last section
            if current_section == "code":
                result["code"] = self._extract_code_block('\n'.join(current_content), language)
            elif current_section == "explanation":
                result["explanation"] = '\n'.join(current_content).strip()
            elif current_section == "time_complexity":
                result["time_complexity"] = '\n'.join(current_content).strip()
            elif current_section == "space_complexity":
                result["space_complexity"] = '\n'.join(current_content).strip()
            elif current_section == "approach":
                result["approach"] = '\n'.join(current_content).strip()

            # If parsing failed, try to extract code block from anywhere in the content
            if not result["code"]:
                result["code"] = self._extract_code_block(content, language)

            # If no explanation found, use the whole content as explanation
            if not result["explanation"]:
                result["explanation"] = content.strip()

        except Exception as e:
            logger.warning(f"Error parsing solution response: {e}")
            # Fallback: try to extract code block and use rest as explanation
            result["code"] = self._extract_code_block(content, language)
            result["explanation"] = content.strip()

        return result

    def _extract_code_block(self, content: str, language: str) -> str:
        """
        Extract code block from markdown-style code fences.

        Args:
            content: Content containing code block
            language: Expected programming language

        Returns:
            Extracted code string
        """
        try:
            # Look for code blocks with language specification
            import re

            # Pattern for code blocks: ```language\ncode\n```
            pattern = rf'```{language}\s*\n(.*?)\n```'
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

            if match:
                return match.group(1).strip()

            # Try without language specification
            pattern = r'```\s*\n(.*?)\n```'
            match = re.search(pattern, content, re.DOTALL)

            if match:
                return match.group(1).strip()

            # If no code block found, return empty string
            return ""

        except Exception as e:
            logger.warning(f"Error extracting code block: {e}")
            return ""

    def test_connection(self) -> bool:
        """
        Test the connection to Groq API.

        Returns:
            True if connection is successful, False otherwise
        """
        if not self.client:
            return False

        try:
            # Simple test request
            response = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "user",
                        "content": "Hello, please respond with 'Connection successful'"
                    }
                ],
                max_tokens=10
            )

            return bool(response.choices)

        except Exception as e:
            logger.error(f"Groq API connection test failed: {e}")
            return False

    def get_supported_languages(self) -> list:
        """
        Get list of supported programming languages.

        Returns:
            List of supported language strings
        """
        return list(Config.SUPPORTED_LANGUAGES.keys())
