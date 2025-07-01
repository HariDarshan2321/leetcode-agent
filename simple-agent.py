from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools
from phi.tools.duckduckgo import DuckDuckGo
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
Groq.api_key = os.getenv("GROQ_API_KEY")

# Web Search Agent
web_search_agent = Agent(
    name="Web Search Agent",
    role="Search the web for up-to-date information.",
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    tools=[DuckDuckGo()],
    instructions=[
        "Always include sources in your answer.",
        "Cite links using markdown format."
    ],
    show_tool_calls=True,
    markdown=True,
)

# Financial Analyst Agent
finance_agent = Agent(
    name="Finance AI Agent",
    role="Provide stock data, analysis, and financial news.",
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            company_news=True,
        )
    ],
    show_tool_calls=True,
    markdown=True,
)

# Multi-agent system
multi_ai_agent = Agent(
    team=[web_search_agent, finance_agent],
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    instructions=[
        "Use tables for data presentation where appropriate."
    ],
    show_tool_calls=True,
    markdown=True,
)

# Run a query through the multi-agent system
multi_ai_agent.print_response(
    "Summarize analyst recommendations and share the latest news for Google",
    stream=True
)
