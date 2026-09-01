import os
import time

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing from .env"
    )


client = genai.Client(
    api_key=api_key
)


# -----------------------------------------
# Candidate Schema
# -----------------------------------------

class Candidate(BaseModel):

    name: str = Field(
        description="Candidate's full name"
    )

    email: str = Field(
        description="Candidate's email address"
    )

    phone: str = Field(
        description="Candidate's phone number"
    )

    location: str = Field(
        description="Candidate's location"
    )

    skills: list[str] = Field(
        description="Technical and professional skills"
    )

    experience_years: float = Field(
        description="Total years of professional experience"
    )

    education: list[str] = Field(
        description="Educational qualifications"
    )

    companies: list[str] = Field(
        description="Companies where the candidate has worked"
    )

    job_titles: list[str] = Field(
        description="Previous job titles"
    )

    projects: list[str] = Field(
        description="Important projects mentioned in resume"
    )

    certifications: list[str] = Field(
        description="Professional certifications"
    )


# -----------------------------------------
# Resume Parser
# -----------------------------------------

def parse_resume(resume_text):

    prompt = f"""
You are an AI recruitment resume parsing system.

Analyze the resume below and extract the candidate's information.

Important rules:

1. Extract ONLY information present in the resume.
2. Do NOT invent information.
3. If information is missing, return an empty string,
   empty list, or 0.
4. Keep individual skills as separate items.
5. Calculate total professional experience only when
   the dates in the resume provide enough information.
6. Ignore unrelated information.
7. Return structured information according to the
   provided schema.

RESUME:

{resume_text}
"""


    max_retries = 3

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Candidate,
                    "temperature": 0
                }
            )

            candidate = Candidate.model_validate_json(
                response.text
            )

            return candidate

        except Exception as error:

            print(
                f"Gemini attempt {attempt + 1} failed: {error}"
            )

            if attempt < max_retries - 1:

                wait_time = 5 * (attempt + 1)

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                raise error