import os
import psycopg2

from dotenv import load_dotenv

load_dotenv()


def get_connection():
    db_url = os.getenv("DB_URL")
    if not db_url:
        raise ValueError("DB_URL is missing from the .env file")

    connection = psycopg2.connect(db_url)
    return connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # Candidates Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        phone VARCHAR(50),
        location VARCHAR(255),
        experience_years FLOAT,
        resume_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Candidate Skills Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidate_skills (
        id SERIAL PRIMARY KEY,
        candidate_id INTEGER NOT NULL,
        skill VARCHAR(255) NOT NULL,
        FOREIGN KEY (candidate_id)
            REFERENCES candidates(id)
            ON DELETE CASCADE
    );
    """)
    cursor.execute("""

    CREATE TABLE IF NOT EXISTS jobs (

        id SERIAL PRIMARY KEY,

        title VARCHAR(255) NOT NULL,

        description TEXT,

        required_skills TEXT[],

        min_experience FLOAT DEFAULT 0,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
    );

    """)
    cursor.execute("""

    CREATE TABLE IF NOT EXISTS match_results (

        id SERIAL PRIMARY KEY,

        candidate_id INTEGER NOT NULL,

        job_id INTEGER NOT NULL,

        match_percentage FLOAT,

        matched_skills TEXT[],

        missing_skills TEXT[],

        experience_match BOOLEAN,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (candidate_id)
            REFERENCES candidates(id)
            ON DELETE CASCADE,

        FOREIGN KEY (job_id)
            REFERENCES jobs(id)
            ON DELETE CASCADE

    );

    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_emails (

        id SERIAL PRIMARY KEY,

        gmail_message_id VARCHAR(255) UNIQUE NOT NULL,

        sender_email VARCHAR(255),

        subject TEXT,

        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    );
    """)

    cursor.execute("""

 
 CREATE TABLE IF NOT EXISTS applications (

    id SERIAL PRIMARY KEY,

    candidate_id INTEGER NOT NULL,

    job_id INTEGER NOT NULL,

    match_percentage FLOAT DEFAULT 0,

    status VARCHAR(50) DEFAULT 'PENDING',

    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (candidate_id)
        REFERENCES candidates(id)
        ON DELETE CASCADE,

    FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE CASCADE,

    UNIQUE(candidate_id, job_id)

    );
    

    """)

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS email_history (

        id SERIAL PRIMARY KEY,

        application_id INTEGER NOT NULL,

        candidate_email VARCHAR(255),

        email_type VARCHAR(50),

        subject TEXT,

        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (application_id)
            REFERENCES applications(id)
            ON DELETE CASCADE

    );

    """)
    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    try:
        create_tables()
        print("Database tables created successfully!")
    except Exception as error:
        print("Database connection error:")
        print(error)
