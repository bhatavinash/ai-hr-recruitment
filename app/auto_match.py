from database import get_connection

from matching_engine import match_candidate_to_job
from application_repository import create_or_update_application


def get_all_jobs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, title
        FROM jobs
        """
    )

    jobs = cursor.fetchall()

    cursor.close()
    connection.close()

    return jobs


def match_candidate_with_all_jobs(candidate_id):
    jobs = get_all_jobs()

    if not jobs:
        print("No jobs available for matching.")
        return

    print(f"\nMatching candidate {candidate_id} with all jobs...")

    for job in jobs:
        job_id, job_title = job
        print(f"\nMatching with: {job_title}")

        result = match_candidate_to_job(candidate_id, job_id)

        if result:
            match_percentage = result.get("final_match_percentage")
            create_or_update_application(candidate_id, job_id, match_percentage)

    print("\nAll job matching completed!")


if __name__ == "__main__":
    candidate_id = 1
    match_candidate_with_all_jobs(candidate_id)
