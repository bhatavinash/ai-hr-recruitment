from database import get_connection


def create_job(
    title,
    description,
    required_skills,
    min_experience
):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(
            """

            INSERT INTO jobs
            (
                title,
                description,
                required_skills,
                min_experience
            )

            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )

            RETURNING id;

            """,
            (
                title,
                description,
                required_skills,
                min_experience
            )
        )

        job_id = cursor.fetchone()[0]

        connection.commit()

        print(
            f"Job created successfully!"
        )

        print(
            f"Job ID: {job_id}"
        )

        return job_id

    except Exception as error:

        connection.rollback()

        print(
            "Job creation error:"
        )

        print(error)

        return None

    finally:

        cursor.close()
        connection.close()


def get_all_jobs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            required_skills,
            min_experience
        FROM jobs
        ORDER BY id DESC
        """
    )

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return jobs


def create_job_simple(title, required_skills, min_experience):
    """Wrapper to create a job without a description."""
    return create_job(title, "", required_skills, min_experience)