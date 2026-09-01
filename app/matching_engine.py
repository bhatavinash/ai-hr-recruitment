from database import get_connection


def normalize_skill(skill):
    return skill.strip().lower()


def calculate_match(candidate_skills, candidate_experience, job_skills, min_experience):
    # Normalize Skills
    candidate_skills = {normalize_skill(skill) for skill in candidate_skills}
    job_skills = {normalize_skill(skill) for skill in job_skills}

    # Find Matched and Missing Skills
    matched_skills = candidate_skills.intersection(job_skills)
    missing_skills = job_skills.difference(candidate_skills)

    # Skill Match Percentage
    if job_skills:
        skill_match_percentage = (len(matched_skills) / len(job_skills)) * 100
    else:
        skill_match_percentage = 0

    # Experience Match
    experience_match = candidate_experience >= min_experience
    experience_score = 100 if experience_match else 0

    # Final Match Score (Skills 80%, Experience 20%)
    final_match_percentage = skill_match_percentage * 0.8 + experience_score * 0.2

    return {
        "skill_match_percentage": round(skill_match_percentage, 2),
        "final_match_percentage": round(final_match_percentage, 2),
        "matched_skills": list(matched_skills),
        "missing_skills": list(missing_skills),
        "experience_match": experience_match,
    }


def get_candidate(candidate_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, experience_years
        FROM candidates
        WHERE id = %s
        """,
        (candidate_id,)
    )

    candidate = cursor.fetchone()
    if not candidate:
        cursor.close()
        connection.close()
        return None

    cursor.execute(
        """
        SELECT skill
        FROM candidate_skills
        WHERE candidate_id = %s
        """,
        (candidate_id,)
    )

    skills = [row[0] for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    return {
        "id": candidate[0],
        "name": candidate[1],
        "experience_years": (candidate[2] or 0),
        "skills": skills,
    }


def get_job(job_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, title, required_skills, min_experience
        FROM jobs
        WHERE id = %s
        """,
        (job_id,)
    )

    job = cursor.fetchone()
    cursor.close()
    connection.close()

    if not job:
        return None

    return {
        "id": job[0],
        "title": job[1],
        "required_skills": (job[2] or []),
        "min_experience": (job[3] or 0),
    }


def save_match_result(candidate_id, job_id, result):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO match_results
            (candidate_id, job_id, match_percentage, matched_skills, missing_skills, experience_match)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                candidate_id,
                job_id,
                result["final_match_percentage"],
                result["matched_skills"],
                result["missing_skills"],
                result["experience_match"],
            ),
        )

        connection.commit()

    except Exception as error:
        connection.rollback()
        print("Error saving match result:")
        print(error)

    finally:
        cursor.close()
        connection.close()


def match_candidate_to_job(candidate_id, job_id):
    candidate = get_candidate(candidate_id)
    job = get_job(job_id)

    if not candidate:
        print("Candidate not found.")
        return None

    if not job:
        print("Job not found.")
        return None

    result = calculate_match(
        candidate.get("skills", []),
        candidate.get("experience_years", 0),
        job.get("required_skills", []),
        job.get("min_experience", 0),
    )

    try:
        save_match_result(candidate_id, job_id, result)
    except Exception:
        # save_match_result already prints errors
        pass

    return result


if __name__ == "__main__":
    candidate_id = 1
    job_id = 1

    result = match_candidate_to_job(candidate_id, job_id)

    if result:
        print("\n====================================")
        print("CANDIDATE JOB MATCH RESULT")
        print("====================================")

        candidate = get_candidate(candidate_id)
        job = get_job(job_id)

        print("\nCandidate:", candidate["name"])
        print("Job:", job["title"])

        print("\nMatched Skills:", ", ".join(result["matched_skills"]))

        print("Missing Skills:", ", ".join(result["missing_skills"]))

        print("\nSkill Match:", result["skill_match_percentage"], "%")
        print("Experience Match:", result["experience_match"])

        print("\nFINAL MATCH SCORE:", result["final_match_percentage"], "%")

