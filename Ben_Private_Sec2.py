import streamlit as st
from datetime import datetime, time
import pytz
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow  # Import Flow
import os.path
import pickle


# ... (rest of your imports)

# Google Calendar Authentication (Modified)
def authenticate_google():
    creds = None
    if st.secrets.get("token"):  # Check in secrets if token is available
        creds = pickle.loads(st.secrets["token"])  # Load from secrets

    if not creds or not creds.valid:
        flow = Flow.from_client_secrets_info(
            st.secrets["credentials"], SCOPES)  # Use client secrets from secrets
        creds = flow.run_local_server(port=0)  # Run local server flow

        # Store token in secrets - convert to bytes first
        st.secrets["token"] = pickle.dumps(creds)  # Store in secrets

    return build('calendar', 'v3', credentials=creds)

# ... (rest of your Streamlit code)