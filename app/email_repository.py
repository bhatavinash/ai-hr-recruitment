from database import get_connection

def is_email_processed(message_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM processed_emails
        WHERE gmail_message_id = %s
        """,
        (message_id,)
    )

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result is not None

def mark_email_processed(
message_id,
sender,
subject
):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO processed_emails
            (gmail_message_id, sender_email, subject)
            VALUES (%s, %s, %s)
            ON CONFLICT (gmail_message_id) DO NOTHING
            """,
            (message_id, sender, subject),
        )

        connection.commit()

    except Exception as error:
        connection.rollback()
        print("Error marking email as processed:")
        print(error)

    finally:
        cursor.close()
        connection.close()
