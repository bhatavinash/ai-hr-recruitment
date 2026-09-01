from job_repository import create_job


title = "Data Engineer"


description = """
We are looking for a Data Engineer with experience in
Python, SQL, ETL, PySpark, AWS and data pipelines.

The candidate should understand databases,
data warehouses and cloud technologies.
"""


required_skills = [

    "Python",
    "SQL",
    "ETL",
    "PySpark",
    "AWS",
    "Data Pipelines",
    "PostgreSQL"

]


min_experience = 1


create_job(
    title,
    description,
    required_skills,
    min_experience
)