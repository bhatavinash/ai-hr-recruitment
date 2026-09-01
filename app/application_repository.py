from database import get_connection


def create_or_update_application(candidate_id, job_id, match_percentage):
    connection = get_connection()
    cursor = connection.cursor()

    status = get_application_status(match_percentage)

    try:
        cursor.execute(
            """
            INSERT INTO applications
            (
                candidate_id,
                job_id,
                match_percentage,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            ON CONFLICT (candidate_id, job_id) DO UPDATE SET
                match_percentage = EXCLUDED.match_percentage,
                status = EXCLUDED.status,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id;
            """,
            (candidate_id, job_id, match_percentage, status),
        )

        application_id = cursor.fetchone()[0]
        connection.commit()

        print("\nApplication saved successfully!")
        print("Application ID:", application_id)
        print("Match Score:", match_percentage, "%")
        print("Status:", status)

        return application_id

    except Exception as error:
        connection.rollback()
        print("Application save error:")
        print(error)
        return None

    finally:
        cursor.close()
        connection.close()
def update_application_status(application_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE applications
            SET
                status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (
                status.upper(),
                application_id,
            ),
        )

        connection.commit()
        print(f"Application status updated to: {status.upper()}")

    except Exception as error:
        connection.rollback()
        print(error)

    finally:
        cursor.close()
        connection.close()


def get_application_status(match_percentage):
    if match_percentage >= 80:
        return "SHORTLISTED"
    elif match_percentage >= 50:
        return "REVIEW"
    else:
        return "REJECTED"
