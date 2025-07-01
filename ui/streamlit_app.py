"""
Streamlit UI for the Leetcode Email Agent.
This provides a user-friendly interface for subscription management.
"""

import streamlit as st
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.coordinator import LeetcodeEmailCoordinator
from src.config import Config

# Page configuration
st.set_page_config(
    page_title="LeetCode Email Agent",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        color: #0c5460;
        margin: 1rem 0;
    }
    .stat-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_coordinator():
    """Get the coordinator instance (cached for performance)."""
    try:
        return LeetcodeEmailCoordinator()
    except Exception as e:
        st.error(f"Failed to initialize system: {e}")
        return None

def show_header():
    """Display the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>LeetCode Email AI Agent</h1>
        <p>Daily coding challenges delivered to your inbox with humor!</p>
    </div>
    """, unsafe_allow_html=True)

def show_subscription_form():
    """Display the subscription form."""
    st.header("📧 Subscribe to Daily Challenges")

    with st.form("subscription_form"):
        col1, col2 = st.columns(2)

        with col1:
            email = st.text_input(
                "Email Address",
                placeholder="your.email@example.com",
                help="Enter your email address to receive daily coding challenges"
            )

            language = st.selectbox(
                "Preferred Programming Language",
                options=list(Config.SUPPORTED_LANGUAGES.keys()),
                format_func=lambda x: Config.SUPPORTED_LANGUAGES[x],
                help="Choose your preferred programming language for solutions"
            )

        with col2:
            difficulty = st.selectbox(
                "Preferred Difficulty",
                options=list(Config.DIFFICULTY_LEVELS.keys()),
                format_func=lambda x: Config.DIFFICULTY_LEVELS[x],
                help="Choose your preferred problem difficulty level"
            )

            st.markdown("### 🎯 What you'll get:")
            st.markdown("""
            - 📅 Daily coding problems
            - 💡 Detailed solutions with explanations
            - 😄 Humorous comments to make learning fun
            - 📊 Time and space complexity analysis
            """)

        submitted = st.form_submit_button("🚀 Subscribe Now!", use_container_width=True)

        if submitted:
            if not email:
                st.error("Please enter your email address")
            elif "@" not in email:
                st.error("Please enter a valid email address")
            else:
                coordinator = get_coordinator()
                if coordinator:
                    success = coordinator.add_user(email, language, difficulty)
                    if success:
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>🎉 Welcome aboard!</h4>
                            <p>You've successfully subscribed to daily LeetCode challenges!</p>
                            <ul>
                                <li><strong>Email:</strong> {email}</li>
                                <li><strong>Language:</strong> {Config.SUPPORTED_LANGUAGES[language]}</li>
                                <li><strong>Difficulty:</strong> {Config.DIFFICULTY_LEVELS[difficulty]}</li>
                            </ul>
                            <p>Your first challenge will arrive tomorrow morning. Get ready to code! 🚀</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="error-box">
                            <h4>❌ Subscription Failed</h4>
                            <p>You might already be subscribed or there was an error. Please try again or contact support.</p>
                        </div>
                        """, unsafe_allow_html=True)

def show_unsubscribe_form():
    """Display the unsubscribe form."""
    st.header("👋 Unsubscribe")

    with st.form("unsubscribe_form"):
        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            help="Enter the email address you want to unsubscribe"
        )

        submitted = st.form_submit_button("Unsubscribe", use_container_width=True)

        if submitted:
            if not email:
                st.error("Please enter your email address")
            elif "@" not in email:
                st.error("Please enter a valid email address")
            else:
                coordinator = get_coordinator()
                if coordinator:
                    success = coordinator.remove_user(email)
                    if success:
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>✅ Successfully Unsubscribed</h4>
                            <p>You have been unsubscribed from daily LeetCode challenges.</p>
                            <p>We're sorry to see you go! You can always resubscribe anytime.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="error-box">
                            <h4>❌ Unsubscribe Failed</h4>
                            <p>Email not found or already unsubscribed. Please check your email address.</p>
                        </div>
                        """, unsafe_allow_html=True)

def show_update_preferences_form():
    """Display the update preferences form."""
    st.header("⚙️ Update Preferences")

    with st.form("update_preferences_form"):
        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            help="Enter your email address"
        )

        col1, col2 = st.columns(2)

        with col1:
            language = st.selectbox(
                "New Programming Language",
                options=[""] + list(Config.SUPPORTED_LANGUAGES.keys()),
                format_func=lambda x: "Keep current" if x == "" else Config.SUPPORTED_LANGUAGES[x],
                help="Choose new preferred programming language (leave as 'Keep current' to not change)"
            )

        with col2:
            difficulty = st.selectbox(
                "New Difficulty Level",
                options=[""] + list(Config.DIFFICULTY_LEVELS.keys()),
                format_func=lambda x: "Keep current" if x == "" else Config.DIFFICULTY_LEVELS[x],
                help="Choose new preferred difficulty level (leave as 'Keep current' to not change)"
            )

        submitted = st.form_submit_button("Update Preferences", use_container_width=True)

        if submitted:
            if not email:
                st.error("Please enter your email address")
            elif "@" not in email:
                st.error("Please enter a valid email address")
            elif not language and not difficulty:
                st.warning("Please select at least one preference to update")
            else:
                coordinator = get_coordinator()
                if coordinator:
                    # Convert empty strings to None
                    new_language = language if language else None
                    new_difficulty = difficulty if difficulty else None

                    success = coordinator.update_user_preferences(email, new_language, new_difficulty)
                    if success:
                        st.markdown(f"""
                        <div class="success-box">
                            <h4>✅ Preferences Updated</h4>
                            <p>Your preferences have been successfully updated!</p>
                            <p>Changes will take effect with your next daily challenge.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="error-box">
                            <h4>❌ Update Failed</h4>
                            <p>Email not found or there was an error. Please check your email address.</p>
                        </div>
                        """, unsafe_allow_html=True)

def show_user_stats():
    """Display user statistics lookup."""
    st.header("📊 User Statistics")

    with st.form("user_stats_form"):
        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            help="Enter your email address to view your statistics"
        )

        submitted = st.form_submit_button("Get My Stats", use_container_width=True)

        if submitted:
            if not email:
                st.error("Please enter your email address")
            elif "@" not in email:
                st.error("Please enter a valid email address")
            else:
                coordinator = get_coordinator()
                if coordinator:
                    stats = coordinator.get_user_stats(email)
                    if stats:
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"""
                            <div class="stat-card">
                                <h4>📧 Total Problems Sent</h4>
                                <h2>{stats.get('total_sent', 0)}</h2>
                            </div>
                            """, unsafe_allow_html=True)

                        with col2:
                            st.markdown(f"""
                            <div class="stat-card">
                                <h4>💻 Preferred Language</h4>
                                <h3>{Config.SUPPORTED_LANGUAGES.get(stats.get('preferred_language', 'python'), 'Python')}</h3>
                            </div>
                            """, unsafe_allow_html=True)

                        with col3:
                            st.markdown(f"""
                            <div class="stat-card">
                                <h4>🎯 Preferred Difficulty</h4>
                                <h3>{Config.DIFFICULTY_LEVELS.get(stats.get('preferred_difficulty', 'medium'), 'Medium')}</h3>
                            </div>
                            """, unsafe_allow_html=True)

                        # Difficulty breakdown
                        if stats.get('by_difficulty'):
                            st.subheader("📈 Problems by Difficulty")
                            difficulty_data = stats['by_difficulty']

                            for diff, count in difficulty_data.items():
                                st.metric(
                                    label=Config.DIFFICULTY_LEVELS.get(diff, diff.title()),
                                    value=count
                                )

                        # Account info
                        st.subheader("👤 Account Information")
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Email:** {stats.get('email', 'N/A')}")
                            st.write(f"**Status:** {'Active' if stats.get('is_active', False) else 'Inactive'}")

                        with col2:
                            created_at = stats.get('created_at')
                            if created_at:
                                try:
                                    created_date = datetime.fromisoformat(created_at).strftime("%B %d, %Y")
                                    st.write(f"**Member Since:** {created_date}")
                                except:
                                    st.write(f"**Member Since:** {created_at}")
                    else:
                        st.markdown("""
                        <div class="error-box">
                            <h4>❌ User Not Found</h4>
                            <p>No user found with that email address. Please check your email or subscribe first.</p>
                        </div>
                        """, unsafe_allow_html=True)

def show_system_stats():
    """Display system statistics."""
    st.header("🔧 System Statistics")

    coordinator = get_coordinator()
    if coordinator:
        stats = coordinator.get_system_stats()
        health = coordinator.test_system_health()

        # System health
        st.subheader("🏥 System Health")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            status = "✅ Healthy" if health.get('database', False) else "❌ Error"
            st.metric("Database", status)

        with col2:
            status = "✅ Connected" if health.get('groq_api', False) else "❌ Error"
            st.metric("Groq API", status)

        with col3:
            status = "✅ Working" if health.get('email', False) else "❌ Error"
            st.metric("Email Service", status)

        with col4:
            status = "✅ Ready" if health.get('fetch_agent', False) else "❌ Error"
            st.metric("Problem Fetcher", status)

        # Overall system status
        overall_status = "🟢 All Systems Operational" if health.get('overall', False) else "🔴 System Issues Detected"
        st.markdown(f"**Overall Status:** {overall_status}")

        # System statistics
        st.subheader("📊 Usage Statistics")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Active Users", stats.get('total_active_users', 0))
            st.metric("Total Problems", stats.get('total_problems', 0))

        with col2:
            # Problems by difficulty
            problems_by_diff = stats.get('problems_by_difficulty', {})
            for diff, count in problems_by_diff.items():
                st.metric(f"{diff.title()} Problems", count)

        # Supported features
        st.subheader("🛠️ Supported Features")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Programming Languages:**")
            for lang_key, lang_name in Config.SUPPORTED_LANGUAGES.items():
                st.write(f"• {lang_name}")

        with col2:
            st.write("**Difficulty Levels:**")
            for diff_key, diff_name in Config.DIFFICULTY_LEVELS.items():
                st.write(f"• {diff_name}")

def show_admin_panel():
    """Display admin panel for testing."""
    st.header("🔧 Admin Panel")

    coordinator = get_coordinator()
    if not coordinator:
        st.error("System not available")
        return

    # Manual job execution
    st.subheader("🚀 Manual Operations")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Send Test Emails Now", use_container_width=True):
            with st.spinner("Processing emails..."):
                result = coordinator.process_daily_emails()

                if result.get('emails_sent', 0) > 0:
                    st.success(f"✅ Successfully sent {result['emails_sent']} emails!")
                elif result.get('total_users', 0) == 0:
                    st.info("ℹ️ No active users found")
                else:
                    st.error(f"❌ Failed to send emails. {result.get('emails_failed', 0)} failures.")

                # Show detailed results
                with st.expander("View Detailed Results"):
                    st.json(result)

    with col2:
        if st.button("Initialize Sample Data", use_container_width=True):
            with st.spinner("Loading sample problems..."):
                success = coordinator.initialize_sample_data()

                if success:
                    st.success("✅ Sample data initialized successfully!")
                else:
                    st.error("❌ Failed to initialize sample data")

def main():
    """Main application function."""
    show_header()

    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        [
            "🏠 Home & Subscribe",
            "👋 Unsubscribe",
            "⚙️ Update Preferences",
            "📊 My Statistics",
            "🔧 System Status",
            "🛠️ Admin Panel"
        ]
    )

    # Show configuration status in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Configuration")

    config_valid = Config.validate_config()
    if config_valid:
        st.sidebar.success("✅ Configuration Valid")
    else:
        st.sidebar.error("❌ Configuration Issues")
        st.sidebar.markdown("""
        <div class="error-box">
            <p><strong>Setup Required:</strong></p>
            <ol>
                <li>Copy .env.example to .env</li>
                <li>Add your Groq API key</li>
                <li>Configure email settings</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    # Display selected page
    if page == "🏠 Home & Subscribe":
        show_subscription_form()

        # Show some info about the service
        st.markdown("---")
        st.subheader("🎯 How It Works")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            ### 📧 Subscribe
            Enter your email and preferences to start receiving daily coding challenges.
            """)

        with col2:
            st.markdown("""
            ### 🧠 Solve
            Each morning, get a new problem with detailed solutions and funny comments.
            """)

        with col3:
            st.markdown("""
            ### 🚀 Improve
            Build your coding skills one problem at a time with consistent practice.
            """)

    elif page == "👋 Unsubscribe":
        show_unsubscribe_form()

    elif page == "⚙️ Update Preferences":
        show_update_preferences_form()

    elif page == "📊 My Statistics":
        show_user_stats()

    elif page == "🔧 System Status":
        show_system_stats()

    elif page == "🛠️ Admin Panel":
        show_admin_panel()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🚀 LeetCode Email Agent - Making coding practice fun, one email at a time!</p>
        <p><small>Built with ❤️ using Streamlit, Groq, and lots of coffee ☕</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
