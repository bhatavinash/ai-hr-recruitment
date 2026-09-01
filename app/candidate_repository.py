from database import get_connection


def save_candidate(candidate, resume_path):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        candidate_data = candidate.model_dump()

        name = candidate_data.get("name", "")
        email = candidate_data.get("email", "")
        phone = candidate_data.get("phone", "")
        location = candidate_data.get("location", "")
        experience_years = candidate_data.get("experience_years", 0)

        skills = candidate_data.get("skills", [])

        # Insert Candidate
        cursor.execute(
            """
            INSERT INTO candidates
            (
                name,
                email,
                phone,
                location,
                experience_years,
                resume_path
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email)
            DO UPDATE SET
                name = EXCLUDED.name,
                phone = EXCLUDED.phone,
                location = EXCLUDED.location,
                experience_years = EXCLUDED.experience_years,
                resume_path = EXCLUDED.resume_path
            RETURNING id;
            """,
            (name, email, phone, location, experience_years, resume_path),
        )

        candidate_id = cursor.fetchone()[0]

        # Remove old skills
        cursor.execute(
            """
            DELETE FROM candidate_skills
            WHERE candidate_id = %s
            """,
            (candidate_id,)
        )

        # Insert Skills
        for skill in skills:
            cursor.execute(
                """
                INSERT INTO candidate_skills (candidate_id, skill)
                VALUES (%s, %s)
                """,
                (candidate_id, skill),
            )

        connection.commit()

        print("Candidate saved successfully!")
        print(f"Candidate ID: {candidate_id}")

        return candidate_id

    except Exception as error:
        connection.rollback()
        print("Database save error:")
        print(error)
        return None

    finally:
        cursor.close()
        connection.close()
