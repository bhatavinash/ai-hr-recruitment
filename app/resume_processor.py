import os
import json

import fitz
from docx import Document

from gemini_parser import parse_resume
from candidate_repository import save_candidate

RESUME_FOLDER = "resumes"
JSON_FOLDER = "parsed"

# -----------------------------------------

# Create required folders

# -----------------------------------------

os.makedirs(
RESUME_FOLDER,
exist_ok=True
)

os.makedirs(
JSON_FOLDER,
exist_ok=True
)

# -----------------------------------------

# Extract PDF Text

# -----------------------------------------

def extract_pdf_text(file_path):
    document = fitz.open(file_path)
    text = ""
    for page in document:
        text += page.get_text()
        text += "\n"
    document.close()
    return text

# -----------------------------------------

# Extract DOCX Text

# -----------------------------------------

def extract_docx_text(file_path):
    document = Document(file_path)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text
        text += "\n"
    return text

# -----------------------------------------

# Process Resume

# -----------------------------------------

def process_resume(file_path):
    filename = os.path.basename(file_path)

    print("\n========================================")
    print("Processing:", filename)
    print("========================================")

    # Extract Resume Text
    if filename.lower().endswith(".pdf"):
        resume_text = extract_pdf_text(file_path)
    elif filename.lower().endswith(".docx"):
        resume_text = extract_docx_text(file_path)
    else:
        print("Unsupported resume format.")
        return

    # Validate Extracted Text
    if not resume_text.strip():
        print("Could not extract text from resume.")
        return

    print("Resume text extracted successfully.")

    # Gemini AI Parsing
    print("Sending resume to Gemini...")
    try:
        candidate = parse_resume(resume_text)
    except Exception as error:
        print("\nGemini error:")
        print(error)
        return

    # Convert Candidate to Dictionary
    candidate_data = candidate.model_dump()

    # Print Candidate JSON
    print("\nCandidate information:")
    print(json.dumps(candidate_data, indent=4, ensure_ascii=False))

    # Save JSON Locally
    json_filename = os.path.splitext(filename)[0] + ".json"
    json_path = os.path.join(JSON_FOLDER, json_filename)
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(candidate_data, file, indent=4, ensure_ascii=False)

    print("\nJSON saved successfully:")
    print(json_path)

    # -------------------------------------
    # Save Candidate to PostgreSQL
    # -------------------------------------

    print(
        "\nSaving candidate to PostgreSQL..."
    )

    try:

        candidate_id = save_candidate(
            candidate,
            file_path
        )

        if candidate_id:

            print(
                "\nCandidate successfully stored!"
            )

            print(
                "Candidate ID:",
                candidate_id
            )

        else:

            print(
                "\nCandidate could not be saved."
            )

            return None

    except Exception as error:

        print(
            "\nPostgreSQL save error:"
        )

        print(error)

        return None

    # -------------------------------------
    # Return Candidate Data and ID
    # -------------------------------------

    return {

        "candidate_data": candidate_data,

        "candidate_id": candidate_id

    }

# -----------------------------------------

# Process Existing Resumes

# -----------------------------------------

if __name__ == "__main__":
    files = os.listdir(RESUME_FOLDER)

    if not files:
        print("No resumes found in the resumes folder.")

    for filename in files:
        file_path = os.path.join(RESUME_FOLDER, filename)
        if filename.lower().endswith((".pdf", ".docx")):
            process_resume(file_path)
        else:
            print(f"Skipping unsupported file: {filename}")
