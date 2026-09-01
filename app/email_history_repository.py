from database import get_connection


def save_email_history(application_id, candidate_email, email_type, subject):
    # Ensure native Python types for DB adapter
    try:
        application_id = int(application_id)
    except Exception:
        # fallback: leave as-is (DB adapter may still fail)
        pass

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO email_history
            (application_id, candidate_email, email_type, subject)
            VALUES (%s, %s, %s, %s)
            """,
            (application_id, candidate_email, email_type, subject),
        )

        connection.commit()

    except Exception as error:
        connection.rollback()
        print("Email history error:")
        print(error)

    finally:
        cursor.close()
        connection.close()
