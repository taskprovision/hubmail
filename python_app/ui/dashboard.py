import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "3001")
API_URL = f"http://{API_HOST}:{API_PORT}"

# Set page config
st.set_page_config(
    page_title="HubMail Dashboard",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.title("HubMail Dashboard")
st.sidebar.info("Email automation system with LLM processing")

# Functions to interact with API
@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_health():
    """Get API health status"""
    try:
        response = httpx.get(f"{API_URL}/health", timeout=5)
        return response.json()
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return {"status": "error", "version": "unknown", "timestamp": "unknown"}

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_recent_emails():
    """Get recent processed emails"""
    try:
        response = httpx.get(f"{API_URL}/api/emails", timeout=5)
        return response.json().get("emails", [])
    except Exception as e:
        st.error(f"Error fetching emails: {str(e)}")
        return []

def test_email_analysis(from_address, subject, body):
    """Test email analysis with the API"""
    try:
        response = httpx.post(
            f"{API_URL}/api/test-analysis",
            json={
                "from_address": from_address,
                "subject": subject,
                "body": body
            },
            timeout=10
        )
        return response.json()
    except Exception as e:
        st.error(f"Error testing email analysis: {str(e)}")
        return None

def trigger_email_check():
    """Trigger email check"""
    try:
        response = httpx.post(f"{API_URL}/api/check-emails", timeout=5)
        return response.json()
    except Exception as e:
        st.error(f"Error triggering email check: {str(e)}")
        return {"status": "error", "message": str(e)}

# Main content
def main():
    # Header
    st.title("📧 HubMail Dashboard")
    
    # Health status
    health = get_health()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_color = "green" if health["status"] == "ok" else "red"
        st.markdown(f"### Status: <span style='color:{status_color}'>{health['status'].upper()}</span>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### Version: {health['version']}")
    
    with col3:
        st.markdown(f"### Last Updated: {health['timestamp']}")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🧪 Test Analysis", "⚙️ Settings"])
    
    # Dashboard tab
    with tab1:
        st.header("Email Processing Dashboard")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.success("Data refreshed!")
        
        with col2:
            if st.button("📨 Check Emails Now"):
                result = trigger_email_check()
                st.success(f"Email check triggered: {result['message']}")
        
        # Recent emails
        st.subheader("Recent Processed Emails")
        emails = get_recent_emails()
        
        if not emails:
            st.info("No emails processed yet or unable to fetch data.")
        else:
            # Prepare data for display
            email_data = []
            for item in emails:
                email = item.get("email", {})
                analysis = item.get("analysis", {})
                
                email_data.append({
                    "ID": email.get("id", ""),
                    "From": email.get("from", ""),
                    "Subject": email.get("subject", ""),
                    "Date": email.get("date", ""),
                    "Classification": analysis.get("classification", ""),
                    "Confidence": analysis.get("confidence", 0),
                    "Suggested Action": analysis.get("suggested_action", "")
                })
            
            # Create DataFrame
            df = pd.DataFrame(email_data)
            
            # Display table
            st.dataframe(df)
            
            # Classification distribution chart
            st.subheader("Email Classification Distribution")
            
            if not df.empty:
                # Count classifications
                classification_counts = df["Classification"].value_counts().reset_index()
                classification_counts.columns = ["Classification", "Count"]
                
                # Create pie chart
                fig = px.pie(
                    classification_counts,
                    values="Count",
                    names="Classification",
                    color="Classification",
                    color_discrete_map={
                        "URGENT": "red",
                        "BUSINESS": "blue",
                        "SPAM": "gray",
                        "PERSONAL": "green"
                    }
                )
                
                st.plotly_chart(fig)
    
    # Test Analysis tab
    with tab2:
        st.header("Test Email Analysis")
        st.info("Use this form to test how an email would be classified by the system.")
        
        # Input form
        with st.form("test_analysis_form"):
            from_address = st.text_input("From Email", "test@example.com")
            subject = st.text_input("Subject", "Test Email Subject")
            body = st.text_area("Email Body", "This is a test email body. Please classify this email.")
            
            submitted = st.form_submit_button("Analyze Email")
            
            if submitted:
                with st.spinner("Analyzing email..."):
                    result = test_email_analysis(from_address, subject, body)
                
                if result:
                    # Display results
                    st.success("Analysis complete!")
                    
                    # Extract data
                    email = result.get("email", {})
                    analysis = result.get("analysis", {})
                    
                    # Create columns for display
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Email Details")
                        st.write(f"**From:** {email.get('from', '')}")
                        st.write(f"**Subject:** {email.get('subject', '')}")
                        st.write(f"**Body:**")
                        st.text(email.get("body", "")[:500] + ("..." if len(email.get("body", "")) > 500 else ""))
                    
                    with col2:
                        st.subheader("Analysis Results")
                        
                        # Classification with color
                        classification = analysis.get("classification", "UNKNOWN")
                        colors = {
                            "URGENT": "red",
                            "BUSINESS": "blue",
                            "SPAM": "gray",
                            "PERSONAL": "green",
                            "UNKNOWN": "orange"
                        }
                        color = colors.get(classification, "black")
                        
                        st.markdown(f"**Classification:** <span style='color:{color}'>{classification}</span>", unsafe_allow_html=True)
                        
                        # Confidence gauge
                        confidence = analysis.get("confidence", 0)
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=confidence * 100,
                            title={"text": "Confidence"},
                            gauge={
                                "axis": {"range": [0, 100]},
                                "bar": {"color": "darkblue"},
                                "steps": [
                                    {"range": [0, 50], "color": "lightgray"},
                                    {"range": [50, 75], "color": "gray"},
                                    {"range": [75, 100], "color": "darkgray"}
                                ]
                            }
                        ))
                        
                        st.plotly_chart(fig)
                        
                        st.write(f"**Reasoning:** {analysis.get('reasoning', '')}")
                        st.write(f"**Suggested Action:** {analysis.get('suggested_action', '')}")
    
    # Settings tab
    with tab3:
        st.header("System Settings")
        st.info("View and update system settings.")
        
        # Display current settings
        st.subheader("Current Configuration")
        
        settings = {
            "API URL": API_URL,
            "Email Check Interval": f"{os.getenv('EMAIL_CHECK_INTERVAL', '300')} seconds",
            "LLM Model": os.getenv("LLM_MODEL", "llama2:7b"),
            "Email Batch Size": os.getenv("EMAIL_BATCH_SIZE", "50")
        }
        
        # Display settings as a table
        settings_df = pd.DataFrame(list(settings.items()), columns=["Setting", "Value"])
        st.table(settings_df)
        
        # Note about changing settings
        st.info("To change settings, update the .env file and restart the application.")

# Run the app
if __name__ == "__main__":
    main()
