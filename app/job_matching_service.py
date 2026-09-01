from database import get_connection
from matching_engine import match_candidate_to_job
from application_repository import create_or_update_application


def get_all_candidate_ids():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM candidates")
    candidates = cursor.fetchall()

    cursor.close()
    connection.close()

    return [candidate[0] for candidate in candidates]


def match_all_candidates_with_job(job_id):
    candidate_ids = get_all_candidate_ids()

    if not candidate_ids:
        print("No candidates available.")
        return

    print(f"Matching all candidates with job {job_id}...")

    for candidate_id in candidate_ids:
        result = match_candidate_to_job(candidate_id, job_id)

        if result:
            match_percentage = result.get("final_match_percentage")
            create_or_update_application(candidate_id, job_id, match_percentage)

    print("Job matching completed!")
