"""
Mail Agent for the Leetcode Email Agent.
This agent handles sending emails with coding problems and solutions.
"""

import logging
import yagmail
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from ..database.models import Problem, Solution, User
    from ..config import Config
except ImportError:
    from src.database.models import Problem, Solution, User
    from src.config import Config

# Set up logging
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class MailAgent:
    """
    Agent responsible for sending emails with coding problems and solutions.
    Uses yagmail for simplified email sending.
    """

    def __init__(self):
        """Initialize the Mail Agent with email configuration."""
        try:
            self.smtp = yagmail.SMTP(
                user=Config.EMAIL_ADDRESS,
                password=Config.EMAIL_PASSWORD
            )
            logger.info("MailAgent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MailAgent: {e}")
            self.smtp = None

    def send_daily_problem(self, user: User, problem: Problem, solution: Solution) -> bool:
        """
        Send a daily coding problem with solution to a user.

        Args:
            user: User object containing email and preferences
            problem: Problem object with the coding challenge
            solution: Solution object with the generated solution

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.smtp:
            logger.error("SMTP client not initialized")
            return False

        try:
            # Generate email content
            subject = self._generate_subject(problem, user)
            html_content = self._generate_html_content(user, problem, solution)
            text_content = self._generate_text_content(user, problem, solution)

            # Send email
            self.smtp.send(
                to=user.email,
                subject=subject,
                contents=[text_content, html_content]
            )

            logger.info(f"Successfully sent daily problem '{problem.title}' to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {user.email}: {e}")
            return False

    def _generate_subject(self, problem: Problem, user: User) -> str:
        """
        Generate email subject line.

        Args:
            problem: Problem object
            user: User object

        Returns:
            Email subject string
        """
        today = datetime.now().strftime("%Y-%m-%d")
        difficulty_emoji = {
            "easy": "🟢",
            "medium": "🟡",
            "hard": "🔴"
        }

        emoji = difficulty_emoji.get(problem.difficulty.lower(), "💻")

        return f"{emoji} Daily LeetCode Challenge - {problem.title} ({today})"

    def _generate_html_content(self, user: User, problem: Problem, solution: Solution) -> str:
        """
        Generate HTML email content.

        Args:
            user: User object
            problem: Problem object
            solution: Solution object

        Returns:
            HTML content string
        """
        # Get examples and test cases
        examples = problem.get_examples()
        test_cases = problem.get_test_cases()
        hints = problem.get_hints()

        # Format examples
        examples_html = ""
        if examples:
            examples_html = "<h3>📝 Examples:</h3>"
            for i, example in enumerate(examples, 1):
                examples_html += f"""
                <div style="background-color: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; border-radius: 4px;">
                    <strong>Example {i}:</strong><br>
                    <strong>Input:</strong> {example.get('input', 'N/A')}<br>
                    <strong>Output:</strong> {example.get('output', 'N/A')}<br>
                    {f"<strong>Explanation:</strong> {example.get('explanation', '')}<br>" if example.get('explanation') else ""}
                </div>
                """

        # Format test cases
        test_cases_html = ""
        if test_cases:
            test_cases_html = "<h3>🧪 Test Cases:</h3>"
            for i, test_case in enumerate(test_cases[:3], 1):  # Show first 3 test cases
                test_cases_html += f"""
                <div style="background-color: #f1f3f4; padding: 10px; margin: 5px 0; border-radius: 4px; font-family: monospace;">
                    <strong>Test {i}:</strong> Input: {test_case.get('input', 'N/A')} → Output: {test_case.get('output', 'N/A')}
                </div>
                """

        # Format hints
        hints_html = ""
        if hints:
            hints_html = "<h3>💡 Hints:</h3><ul>"
            for hint in hints[:2]:  # Show first 2 hints
                hints_html += f"<li style='margin: 5px 0;'>{hint}</li>"
            hints_html += "</ul>"

        # Format solution code
        solution_code_html = f"""
        <pre style="background-color: #2d3748; color: #e2e8f0; padding: 20px; border-radius: 8px; overflow-x: auto; font-family: 'Courier New', monospace; line-height: 1.4;">
{solution.solution_code}
        </pre>
        """

        # Main HTML template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily LeetCode Challenge</title>
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 28px;">🚀 Daily LeetCode Challenge</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Hello {user.email.split('@')[0]}! Ready to code?</p>
            </div>

            <!-- Problem Section -->
            <div style="background-color: #ffffff; border: 1px solid #e1e5e9; border-radius: 8px; padding: 25px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="display: flex; align-items: center; margin-bottom: 20px;">
                    <h2 style="margin: 0; color: #2c3e50; flex-grow: 1;">{problem.title}</h2>
                    <span style="background-color: {'#28a745' if problem.difficulty.lower() == 'easy' else '#ffc107' if problem.difficulty.lower() == 'medium' else '#dc3545'}; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase;">
                        {problem.difficulty}
                    </span>
                </div>

                <h3>📋 Problem Description:</h3>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
                    {problem.description.replace(chr(10), '<br>')}
                </div>

                {examples_html}

                <h3>⚠️ Constraints:</h3>
                <div style="background-color: #fff3cd; padding: 15px; border-radius: 6px; border-left: 4px solid #ffc107;">
                    {problem.constraints.replace(chr(10), '<br>')}
                </div>

                {test_cases_html}
                {hints_html}
            </div>

            <!-- Solution Section -->
            <div style="background-color: #ffffff; border: 1px solid #e1e5e9; border-radius: 8px; padding: 25px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="color: #2c3e50; margin-bottom: 20px;">💡 Solution in {solution.language.title()}</h2>

                {solution_code_html}

                <h3>📖 Explanation:</h3>
                <div style="background-color: #e8f5e8; padding: 20px; border-radius: 6px; border-left: 4px solid #28a745;">
                    {solution.explanation.replace(chr(10), '<br>')}
                </div>

                <div style="display: flex; gap: 20px; margin-top: 20px;">
                    <div style="flex: 1; background-color: #e3f2fd; padding: 15px; border-radius: 6px;">
                        <strong>⏱️ Time Complexity:</strong><br>
                        {solution.time_complexity}
                    </div>
                    <div style="flex: 1; background-color: #f3e5f5; padding: 15px; border-radius: 6px;">
                        <strong>💾 Space Complexity:</strong><br>
                        {solution.space_complexity}
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; color: #6c757d;">
                <p style="margin: 0; font-size: 14px;">
                    🎯 Keep coding, keep growing! Tomorrow brings a new challenge.<br>
                    <small>Powered by LeetCode Email Agent | Language: {solution.language.title()} | Difficulty: {problem.difficulty.title()}</small>
                </p>
                <p style="margin: 10px 0 0 0; font-size: 12px;">
                    <a href="#" style="color: #007bff; text-decoration: none;">Unsubscribe</a> |
                    <a href="#" style="color: #007bff; text-decoration: none;">Update Preferences</a>
                </p>
            </div>

        </body>
        </html>
        """

        return html_content

    def _generate_text_content(self, user: User, problem: Problem, solution: Solution) -> str:
        """
        Generate plain text email content as fallback.

        Args:
            user: User object
            problem: Problem object
            solution: Solution object

        Returns:
            Plain text content string
        """
        today = datetime.now().strftime("%Y-%m-%d")

        # Get examples and format them
        examples = problem.get_examples()
        examples_text = ""
        if examples:
            examples_text = "\n📝 EXAMPLES:\n"
            for i, example in enumerate(examples, 1):
                examples_text += f"\nExample {i}:\n"
                examples_text += f"Input: {example.get('input', 'N/A')}\n"
                examples_text += f"Output: {example.get('output', 'N/A')}\n"
                if example.get('explanation'):
                    examples_text += f"Explanation: {example.get('explanation')}\n"

        # Get hints
        hints = problem.get_hints()
        hints_text = ""
        if hints:
            hints_text = "\n💡 HINTS:\n"
            for i, hint in enumerate(hints[:2], 1):
                hints_text += f"{i}. {hint}\n"

        text_content = f"""
🚀 DAILY LEETCODE CHALLENGE - {today}

Hello {user.email.split('@')[0]}!

Today's challenge: {problem.title} ({problem.difficulty.upper()})

📋 PROBLEM DESCRIPTION:
{problem.description}

{examples_text}

⚠️ CONSTRAINTS:
{problem.constraints}

{hints_text}

💡 SOLUTION IN {solution.language.upper()}:

{solution.solution_code}

📖 EXPLANATION:
{solution.explanation}

⏱️ TIME COMPLEXITY: {solution.time_complexity}
💾 SPACE COMPLEXITY: {solution.space_complexity}

🎯 Keep coding, keep growing! Tomorrow brings a new challenge.

---
Powered by LeetCode Email Agent
Language: {solution.language.title()} | Difficulty: {problem.difficulty.title()}
        """

        return text_content.strip()

    def send_welcome_email(self, user: User) -> bool:
        """
        Send a welcome email to a new subscriber.

        Args:
            user: User object for the new subscriber

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.smtp:
            logger.error("SMTP client not initialized")
            return False

        try:
            subject = "🎉 Welcome to Daily LeetCode Challenges!"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Welcome to LeetCode Email Agent</title>
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                    <h1 style="margin: 0;">🎉 Welcome to Daily LeetCode Challenges!</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px;">Get ready to level up your coding skills!</p>
                </div>

                <div style="background-color: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
                    <h2 style="color: #2c3e50;">Hello {user.email.split('@')[0]}! 👋</h2>

                    <p>Welcome to the most fun way to practice coding! Here's what you can expect:</p>

                    <ul style="padding-left: 20px;">
                        <li>📅 <strong>Daily Challenges:</strong> Fresh coding problems delivered to your inbox every morning</li>
                        <li>🎯 <strong>Your Preferences:</strong> Problems in <strong>{user.preferred_language.title()}</strong> at <strong>{user.preferred_difficulty.title()}</strong> difficulty</li>
                        <li>😄 <strong>Humor Included:</strong> Solutions with funny comments to make learning enjoyable</li>
                        <li>📊 <strong>Detailed Explanations:</strong> Complete solutions with time/space complexity analysis</li>
                        <li>🏆 <strong>Skill Building:</strong> Gradually improve your problem-solving abilities</li>
                    </ul>

                    <p>Your first challenge will arrive tomorrow morning. Get ready to code! 🚀</p>
                </div>

                <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; text-align: center;">
                    <h3 style="margin-top: 0; color: #2c3e50;">🎮 Pro Tips for Success:</h3>
                    <p style="margin-bottom: 0;">
                        • Try solving the problem yourself first<br>
                        • Read the explanation even if you got it right<br>
                        • Pay attention to the complexity analysis<br>
                        • Have fun with the humor! 😄
                    </p>
                </div>

                <div style="text-align: center; margin-top: 30px; color: #6c757d; font-size: 14px;">
                    <p>Happy coding! 🎯</p>
                    <p><small>Powered by LeetCode Email Agent</small></p>
                </div>

            </body>
            </html>
            """

            text_content = f"""
🎉 WELCOME TO DAILY LEETCODE CHALLENGES!

Hello {user.email.split('@')[0]}! 👋

Welcome to the most fun way to practice coding! Here's what you can expect:

📅 DAILY CHALLENGES: Fresh coding problems delivered to your inbox every morning
🎯 YOUR PREFERENCES: Problems in {user.preferred_language.title()} at {user.preferred_difficulty.title()} difficulty
😄 HUMOR INCLUDED: Solutions with funny comments to make learning enjoyable
📊 DETAILED EXPLANATIONS: Complete solutions with time/space complexity analysis
🏆 SKILL BUILDING: Gradually improve your problem-solving abilities

Your first challenge will arrive tomorrow morning. Get ready to code! 🚀

🎮 PRO TIPS FOR SUCCESS:
• Try solving the problem yourself first
• Read the explanation even if you got it right
• Pay attention to the complexity analysis
• Have fun with the humor! 😄

Happy coding! 🎯

---
Powered by LeetCode Email Agent
            """

            self.smtp.send(
                to=user.email,
                subject=subject,
                contents=[text_content.strip(), html_content]
            )

            logger.info(f"Successfully sent welcome email to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Error sending welcome email to {user.email}: {e}")
            return False

    def send_unsubscribe_confirmation(self, email: str) -> bool:
        """
        Send unsubscribe confirmation email.

        Args:
            email: Email address of the unsubscribed user

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.smtp:
            logger.error("SMTP client not initialized")
            return False

        try:
            subject = "👋 Unsubscribed from Daily LeetCode Challenges"

            content = f"""
Hello!

You have been successfully unsubscribed from Daily LeetCode Challenges.

We're sorry to see you go! If you change your mind, you can always resubscribe using our web interface.

Thank you for being part of our coding community! 🎯

---
LeetCode Email Agent Team
            """

            self.smtp.send(
                to=email,
                subject=subject,
                contents=content.strip()
            )

            logger.info(f"Successfully sent unsubscribe confirmation to {email}")
            return True

        except Exception as e:
            logger.error(f"Error sending unsubscribe confirmation to {email}: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test the email connection.

        Returns:
            True if connection is successful, False otherwise
        """
        if not self.smtp:
            return False

        try:
            # Try to send a test email to the configured email address
            self.smtp.send(
                to=Config.EMAIL_ADDRESS,
                subject="🧪 LeetCode Email Agent - Connection Test",
                contents="This is a test email to verify the email configuration is working correctly."
            )
            logger.info("Email connection test successful")
            return True

        except Exception as e:
            logger.error(f"Email connection test failed: {e}")
            return False

    def close_connection(self):
        """Close the SMTP connection."""
        if self.smtp:
            try:
                self.smtp.close()
                logger.info("SMTP connection closed")
            except Exception as e:
                logger.warning(f"Error closing SMTP connection: {e}")
