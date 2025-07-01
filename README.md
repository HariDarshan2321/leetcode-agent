# LeetCode Email Agent

An AI-driven automated system that delivers daily LeetCode-style coding problems to users via email. Problems are solved using a multi-agent architecture powered by Groq LLM, with solutions enhanced with humor to make learning more engaging.

## Features

- **Daily Email Delivery**: Automated daily coding challenges sent to subscribers
- **Personalized Experience**: Users can choose their preferred programming language and difficulty level
- **AI-Powered Solutions**: Solutions generated using Groq's Mixtral model
- **Humor Enhancement**: Funny comments and analogies added to make solutions more engaging
- **Smart Problem Management**: SQLite database ensures no problem repetition per user
- **User-Friendly Interface**: Streamlit web UI for subscription management
- ** Flexible Scheduling**: Configurable daily email timing
- **Statistics & Monitoring**: User stats and system health monitoring

## 🏗️ Architecture

### Multi-Agent System
- **Fetch Agent**: Retrieves coding problems from data sources
- **Solve Agent**: Generates solutions using Groq API (Mixtral model)
- **Humor Agent**: Adds funny comments and analogies to solutions
- **Mail Agent**: Sends beautifully formatted emails using yagmail
- **Central Coordinator**: Orchestrates all agents and manages workflow

### Technology Stack
- **Backend**: Python 3.9+
- **AI/LLM**: Groq API with Mixtral-8x7b model
- **Database**: SQLite (simple, no setup required)
- **Email**: yagmail (simplified email sending)
- **Scheduling**: APScheduler (background job scheduling)
- **UI**: Streamlit (web interface)
- **Configuration**: python-dotenv (environment management)

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Groq API key (get one at [console.groq.com](https://console.groq.com))
- Gmail account with app password (for email sending)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd leetcode-email-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` file with your credentials:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password_here
   ```

4. **Initialize sample data**
   ```bash
   python main.py --init-data
   ```

5. **Test the system**
   ```bash
   python main.py --test
   ```

### Running the Application

#### Option 1: Web Interface (Recommended)
```bash
streamlit run ui/streamlit_app.py
```
Then open your browser to `http://localhost:8501`

#### Option 2: Command Line

**Run scheduler (keeps running)**
```bash
python main.py --scheduler
```

**Send emails once immediately**
```bash
python main.py --run-once
```

**Show configuration**
```bash
python main.py --config
```

## Email Setup

### Gmail Configuration
1. Enable 2-factor authentication on your Gmail account
2. Generate an app password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use this app password in your `.env` file

### Other Email Providers
The system uses yagmail, which supports various email providers. Update the configuration in `src/config.py` if needed.

## Usage

### For Users

1. **Subscribe**: Visit the Streamlit web interface and enter your email, preferred language, and difficulty
2. **Receive Daily Challenges**: Get coding problems every morning at the configured time
3. **Learn & Improve**: Each email contains:
   - Problem description with examples and constraints
   - Complete solution with explanations
   - Funny comments to make learning enjoyable
   - Time and space complexity analysis
4. **Manage Subscription**: Update preferences or unsubscribe anytime via the web interface

### For Administrators

- **Monitor System**: Use the admin panel to check system health and statistics
- **Manual Operations**: Send test emails or initialize data through the web interface
- **Command Line Tools**: Use `main.py` for various administrative tasks

## Configuration

### Environment Variables
```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Email Configuration
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# Database Configuration
DATABASE_PATH=data/leetcode.db

# Scheduler Configuration
SCHEDULER_HOUR=9
SCHEDULER_MINUTE=0
SCHEDULER_TIMEZONE=UTC

# Application Configuration
DEBUG=True
LOG_LEVEL=INFO
```

### Supported Languages
- Python
- Java
- C++
- JavaScript
- Go
- Rust

### Difficulty Levels
- Easy
- Medium
- Hard

## 📁 Project Structure

```
leetcode-email-agent/
├── src/
│   ├── agents/
│   │   ├── fetch_agent.py      # Problem retrieval
│   │   ├── solve_agent.py      # Solution generation
│   │   ├── humor_agent.py      # Humor enhancement
│   │   └── mail_agent.py       # Email sending
│   ├── database/
│   │   ├── models.py           # Data models
│   │   └── db_manager.py       # Database operations
│   ├── scheduler/
│   │   └── daily_scheduler.py  # Job scheduling
│   ├── coordinator.py          # Central orchestrator
│   └── config.py              # Configuration management
├── ui/
│   └── streamlit_app.py       # Web interface
├── data/
│   ├── problems.json          # Sample problems
│   └── leetcode.db           # SQLite database
├── main.py                   # CLI entry point
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## 🔧 Development

### Adding New Problems
1. Edit `data/problems.json` to add new problems
2. Run `python main.py --init-data` to load them into the database

### Extending Functionality
- **New Languages**: Update `Config.SUPPORTED_LANGUAGES` in `src/config.py`
- **Custom Humor**: Modify humor templates in `src/agents/humor_agent.py`
- **Email Templates**: Customize email formatting in `src/agents/mail_agent.py`

### Testing
```bash
# Test system health
python main.py --test

# Send test emails
python main.py --run-once

# Check configuration
python main.py --config
```

## 📊 Monitoring

### System Health
The application includes comprehensive health monitoring:
- Database connectivity
- Groq API status
- Email service functionality
- Problem availability

### Logging
Logs are configured based on the `LOG_LEVEL` environment variable:
- `DEBUG`: Detailed debugging information
- `INFO`: General operational information
- `WARNING`: Warning messages
- `ERROR`: Error messages only

## Deployment

### Local Development
Use the Streamlit interface for development and testing.

### Production Deployment

#### Option 1: Simple Server
1. Set up a server (VPS, EC2, etc.)
2. Install dependencies and configure environment
3. Run the scheduler: `python main.py --scheduler`
4. Optionally run Streamlit UI: `streamlit run ui/streamlit_app.py`

#### Option 2: Docker (Future Enhancement)
Docker configuration can be added for containerized deployment.

#### Option 3: Cloud Platforms
- **Streamlit Cloud**: Deploy the UI component
- **Heroku/Railway**: Deploy the full application
- **AWS/GCP**: Use cloud services for scalable deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request


## Support

### Common Issues

**Configuration Errors**
- Ensure all required environment variables are set
- Verify Groq API key is valid
- Check email credentials and app password

**Email Delivery Issues**
- Verify Gmail app password is correct
- Check spam/junk folders
- Ensure 2-factor authentication is enabled

**Database Issues**
- Check file permissions for database directory
- Ensure SQLite is properly installed

### Getting Help
1. Check the logs for detailed error messages
2. Run `python main.py --test` to diagnose issues
3. Verify configuration with `python main.py --config`

## Future Enhancements

- **Real LeetCode Integration**: Connect to actual LeetCode API
- **OAuth Authentication**: Secure user login system
- **Cloud Database**: PostgreSQL/MongoDB for scalability
- **Webhook Notifications**: Alternative to email delivery
- **Admin Dashboard**: Enhanced monitoring and management
- **Mobile App**: Native mobile application
- **Social Features**: User communities and leaderboards

---

**Built with ❤️ using Python, Groq AI, and lots of coffee ☕**

*Making coding practice fun, one email at a time!* 🚀
