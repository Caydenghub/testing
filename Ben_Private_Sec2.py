import streamlit as st
from datetime import datetime, time
import pytz
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os.path
import pickle

# Google Calendar Setup
SCOPES = ['https://www.googleapis.com/auth/calendar']


def authenticate_google():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


# Streamlit App
st.title("Audit Management System (UTC+8)")
st.sidebar.header("Schedule New Audit")

# Timezone Setup
UTC8 = pytz.timezone('Asia/Singapore')  # Singapore uses UTC+8

# Input Form
with st.sidebar.form("audit_form"):
    company = st.text_input("Company Name")
    auditor = st.text_input("Auditor Name")
    date = st.date_input("Meeting Date")

    # Manual time inputs
    start_time = st.time_input("Start Time (UTC+8)", value=time(9, 0))
    end_time = st.time_input("End Time (UTC+8)", value=time(10, 0))

    location = st.text_input("Location")
    notes = st.text_area("Notes")
    notification_time = st.selectbox("Notification Before", [5, 10, 15, 30, 60])

    submitted = st.form_submit_button("Schedule Audit")

# Handle Form Submission
if submitted:
    try:
        # Convert to UTC+8 datetime
        start_datetime = UTC8.localize(
            datetime.combine(date, start_time)
        )
        end_datetime = UTC8.localize(
            datetime.combine(date, end_time)
        )

        # Create Google Calendar event
        service = authenticate_google()
        event = {
            'summary': f"Audit: {company} - {auditor}",
            'location': location,
            'description': f"Auditor: {auditor}\nNotes: {notes}",
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Singapore',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Singapore',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': notification_time}
                ],
            },
        }

        # Send to Google Calendar
        service.events().insert(calendarId='primary', body=event).execute()
        st.success(f"Audit scheduled for {company} on {date} at {start_time.strftime('%H:%M')} UTC+8!")

    except Exception as e:
        st.error(f"Error: {str(e)}")

# Display Upcoming Audits
if st.button("Check Upcoming Audits"):
    try:
        service = authenticate_google()
        now = datetime.now(UTC8).isoformat()
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime',
            timeZone='Asia/Singapore'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            st.info("No upcoming audits found.")
        else:
            st.subheader("Upcoming Audits (UTC+8)")
            for event in events:
                start_str = event['start']['dateTime']
                start_time = datetime.fromisoformat(start_str).astimezone(UTC8)
                end_str = event['end']['dateTime']
                end_time = datetime.fromisoformat(end_str).astimezone(UTC8)

                st.write(f"""
                **{start_time.strftime('%Y-%m-%d %H:%M')}** to **{end_time.strftime('%H:%M')}**  
                **Company**: {event['summary']}  
                **Location**: {event.get('location', 'N/A')}
                """)
                st.write("---")

    except Exception as e:
        st.error(f"Error: {str(e)}")