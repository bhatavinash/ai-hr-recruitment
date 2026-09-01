import os
import time
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from auto_match import match_candidate_with_all_jobs
from resume_processor import process_resume
from matching_engine import match_candidate_to_job
from email_repository import (
is_email_processed,
mark_email_processed
)

SCOPES = [
"https://www.googleapis.com/auth/gmail.readonly"
]

CREDENTIALS_FILE = (
"credentials/credentials.json"
)

TOKEN_FILE = (
"credentials/token.json"
)

RESUME_FOLDER = "resumes"

os.makedirs(
RESUME_FOLDER,
exist_ok=True
)

# -----------------------------------------

# Gmail Authentication

# -----------------------------------------

def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

# -----------------------------------------

# Get Gmail Header

# -----------------------------------------

def get_header(
headers,
header_name
):
    for header in headers:
        if header["name"].lower() == header_name.lower():
            return header["value"]
    return ""

# -----------------------------------------

# Find Resume Attachments

# -----------------------------------------

def get_resume_attachments(
gmail,
message_id,
payload
):

    attachments = []

    # Resume-related keywords and extension check
    resume_keywords = ["resume", "cv", "curriculum vitae", "candidate profile"]

    def is_resume_file(filename: str) -> bool:
        filename_lower = (filename or "").lower()
        # Extension check
        # require a recognized extension
        if not (filename_lower.endswith(".pdf") or filename_lower.endswith(".docx")):
            return False
        # require at least one resume keyword in the filename
        for keyword in resume_keywords:
            if keyword in filename_lower:
                return True
        return False

    def process_parts(parts):
        for part in parts:
            filename = part.get("filename", "")
            if is_resume_file(filename):
                body = part.get("body", {})
                attachment_id = body.get("attachmentId")
                if attachment_id:
                    attachments.append((filename, attachment_id))

            # Recurse into nested parts
            if "parts" in part:
                process_parts(part["parts"])

    process_parts(payload.get("parts", []))
    return attachments

# -----------------------------------------
# Process New Emails
# -----------------------------------------

def check_new_emails():
    gmail = get_gmail_service()

    results = gmail.users().messages().list(userId="me", q="has:attachment").execute()
    messages = results.get("messages", [])

    for message in messages:
        message_id = message["id"]

        # Skip already processed emails
        if is_email_processed(message_id):
            continue

        msg = gmail.users().messages().get(userId="me", id=message_id, format="full").execute()

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])

        sender = get_header(headers, "From")
        subject = get_header(headers, "Subject")

        attachments = get_resume_attachments(gmail, message_id, payload)
        if not attachments:
            continue

        print("\n========================================")
        print("NEW RESUME EMAIL")
        print("From:", sender)
        print("Subject:", subject)

        all_success = True

        for (filename, attachment_id) in attachments:
            try:
                attachment = (
                    gmail.users()
                    .messages()
                    .attachments()
                    .get(userId="me", messageId=message_id, id=attachment_id)
                    .execute()
                )

                file_data = attachment["data"]
                file_data = base64.urlsafe_b64decode(file_data)

                safe_filename = f"{message_id}_{filename}"
                file_path = os.path.join(RESUME_FOLDER, safe_filename)

                with open(file_path, "wb") as file:
                    file.write(file_data)

                print("\nResume downloaded:", safe_filename)

                # Process Resume

                process_result = process_resume(file_path)

                if not process_result:
                    all_success = False
                    continue

                candidate_id = process_result.get("candidate_id")

                if not candidate_id:
                    print("Candidate ID was not returned.")
                    all_success = False
                    continue

                print("\nResume processed successfully!")

                # ---------------------------------
                # Automatically Match All Jobs
                # ---------------------------------
                print("\nStarting automatic job matching...")
                match_candidate_with_all_jobs(candidate_id)
                print("\nAutomatic job matching completed!")
            except Exception as error:
                all_success = False
                print("\nError processing attachment:")
                print(error)

        # Mark email only after processing succeeds
        if all_success:
            mark_email_processed(message_id, sender, subject)
            print("\nEmail marked as processed.")

# Main Watcher

# -----------------------------------------

if __name__ == "__main__":
    print("\n🤖 AI HR Recruitment Automation Started")
    print("Checking Gmail every 30 seconds...")

    while True:
        try:
            check_new_emails()
        except Exception as error:
            print("\nPipeline Error:")
            print(error)

        print("\nWaiting for new emails...")
        time.sleep(30)
