import os
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from resume_processor import process_resume


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

creds = None


if os.path.exists(TOKEN_FILE):

    creds = Credentials.from_authorized_user_file(
        TOKEN_FILE,
        SCOPES
    )


if not creds or not creds.valid:

    if (
        creds
        and creds.expired
        and creds.refresh_token
    ):

        creds.refresh(
            Request()
        )

    else:

        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE,
            SCOPES
        )

        creds = flow.run_local_server(
            port=0
        )


    with open(
        TOKEN_FILE,
        "w"
    ) as token:

        token.write(
            creds.to_json()
        )


gmail = build(
    "gmail",
    "v1",
    credentials=creds
)


# -----------------------------------------
# Get Emails
# -----------------------------------------

results = gmail.users().messages().list(

    userId="me",

    q="has:attachment"
).execute()


messages = results.get(
    "messages",
    []
)


print(
    f"\nFound {len(messages)} emails with attachments."
)


# -----------------------------------------
# Process Emails
# -----------------------------------------

for message in messages:

    message_id = message["id"]


    msg = gmail.users().messages().get(

        userId="me",

        id=message_id
    ).execute()


    payload = msg.get(
        "payload",
        {}
    )


    headers = payload.get(
        "headers",
        []
    )


    sender = ""

    subject = ""


    for header in headers:

        name = header[
            "name"
        ].lower()


        if name == "from":

            sender = header[
                "value"
            ]


        elif name == "subject":

            subject = header[
                "value"
            ]


    print(
        "\n-----------------------------------"
    )

    print(
        "From:",
        sender
    )

    print(
        "Subject:",
        subject
    )


    # -----------------------------------------
    # Find Attachments
    # -----------------------------------------

    parts = payload.get(
        "parts",
        []
    )


    for part in parts:

        filename = part.get(
            "filename",
            ""
        )


        if not filename:

            continue


        if not filename.lower().endswith(
            (
                ".pdf",
                ".docx"
            )
        ):

            continue


        body = part.get(
            "body",
            {}
        )


        attachment_id = body.get(
            "attachmentId"
        )


        if not attachment_id:

            continue


        # -----------------------------------------
        # Download Attachment
        # -----------------------------------------

        attachment = (
            gmail
            .users()
            .messages()
            .attachments()
            .get(
                userId="me",
                messageId=message_id,
                id=attachment_id
            )
            .execute()
        )


        file_data = attachment.get(
            "data"
        )


        if not file_data:

            continue


        file_data = base64.urlsafe_b64decode(
            file_data.encode(
                "UTF-8"
            )
        )


        file_path = os.path.join(
            RESUME_FOLDER,
            filename
        )


        with open(
            file_path,
            "wb"
        ) as file:

            file.write(
                file_data
            )


        print(
            "Resume saved:",
            file_path
        )


        # -----------------------------------------
        # Send Resume to AI
        # -----------------------------------------

        print(
            "Starting AI resume processing..."
        )


        process_resume(
            file_path
        )