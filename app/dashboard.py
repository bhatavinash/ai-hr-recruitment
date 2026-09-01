import streamlit as st
import pandas as pd
import json

from database import get_connection
from application_repository import update_application_status
from email_service import send_email
from email_history_repository import save_email_history
from job_repository import create_job, get_all_jobs
from job_matching_service import match_all_candidates_with_job


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AI HR Recruitment",
    page_icon="🤖",
    layout="wide"
)


# =====================================================
# DATABASE FUNCTIONS
# =====================================================

def get_dashboard_data():

    connection = get_connection()

    query = """
        SELECT
            a.id AS application_id,

            c.id AS candidate_id,
            c.name AS candidate_name,
            c.email,
            c.phone,
            c.location,
            c.experience_years,
            c.resume_path,

            j.id AS job_id,
            j.title AS job_title,

            a.match_percentage,
            a.status,

            mr.matched_skills,
            mr.missing_skills,
            mr.experience_match,

            a.applied_at

        FROM applications a

        JOIN candidates c
            ON a.candidate_id = c.id

        JOIN jobs j
            ON a.job_id = j.id

        LEFT JOIN match_results mr
            ON mr.candidate_id = c.id
            AND mr.job_id = j.id

        ORDER BY a.match_percentage DESC
    """

    dataframe = pd.read_sql(
        query,
        connection
    )

    connection.close()

    return dataframe


# =====================================================
# TOTAL CANDIDATES
# =====================================================

def get_total_candidates():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM candidates
        """
    )

    total = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return total


# =====================================================
# TOTAL JOBS
# =====================================================

def get_total_jobs():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM jobs
        """
    )

    total = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return total


# =====================================================
# GET ALL CANDIDATES
# =====================================================

def get_all_candidates():

    connection = get_connection()

    query = """
        SELECT
            id,
            name,
            email,
            phone,
            location,
            experience_years,
            resume_path,
            created_at

        FROM candidates

        ORDER BY created_at DESC
    """

    dataframe = pd.read_sql(
        query,
        connection
    )

    connection.close()

    return dataframe


# =====================================================
# GET EMAIL HISTORY
# =====================================================

def get_email_history():

    connection = get_connection()

    query = """
        SELECT
            eh.id,

            c.name AS candidate_name,

            eh.candidate_email,

            eh.email_type,

            eh.subject,

            eh.sent_at

        FROM email_history eh

        LEFT JOIN applications a
            ON eh.application_id = a.id

        LEFT JOIN candidates c
            ON a.candidate_id = c.id

        ORDER BY eh.sent_at DESC
    """

    dataframe = pd.read_sql(
        query,
        connection
    )

    connection.close()

    return dataframe


# =====================================================
# CLEAN SKILLS
# =====================================================

def clean_skills(skills):

    if skills is None:
        return []

    if isinstance(skills, list):
        return skills

    if isinstance(skills, tuple):
        return list(skills)

    # PostgreSQL array sometimes comes as string
    if isinstance(skills, str):

        try:

            parsed = json.loads(skills)

            if isinstance(parsed, list):
                return parsed

        except Exception:
            pass

        # PostgreSQL array format
        skills = skills.strip(
            "{}"
        )

        if skills:

            return [
                skill.strip()
                for skill in skills.split(",")
                if skill.strip()
            ]

    return []


# =====================================================
# PROCESS BULK CANDIDATES
# =====================================================

def process_bulk_candidates(
    selected_candidates,
    action
):

    success_count = 0
    failed_count = 0

    total_candidates = len(
        selected_candidates
    )

    progress_bar = st.progress(0)

    status_text = st.empty()

    for index, (_, candidate_row) in enumerate(
        selected_candidates.iterrows(),
        start=1
    ):

        try:

            application_id = int(
                candidate_row["application_id"]
            )

            candidate_name = (
                candidate_row["candidate_name"]
            )

            candidate_email = (
                candidate_row["email"]
            )

            job_title = (
                candidate_row["job_title"]
            )

            status_text.info(
                f"Processing {index}/{total_candidates}: "
                f"{candidate_name}"
            )

            # ==========================================
            # SELECTED EMAIL
            # ==========================================

            if action == "SELECTED":

                subject = (
                    f"Congratulations! Your application "
                    f"for {job_title}"
                )

                body = f"""Hi {candidate_name},

Congratulations!

We are pleased to inform you that you have been selected for the next stage of the recruitment process for the {job_title} position.

Our HR team will contact you shortly with further details regarding the next steps.

Best regards,
HR Team
"""

            # ==========================================
            # REJECTED EMAIL
            # ==========================================

            else:

                subject = (
                    f"Update on your application "
                    f"for {job_title}"
                )

                body = f"""Hi {candidate_name},

Thank you for taking the time to apply for the {job_title} position.

After careful consideration, we have decided to move forward with other candidates whose profiles currently align more closely with our requirements.

We sincerely appreciate your interest in our organization and wish you the very best in your future career.

Best regards,
HR Team
"""

            # ==========================================
            # SEND EMAIL FIRST
            # ==========================================

            email_sent = send_email(
                candidate_email,
                subject,
                body
            )

            # ==========================================
            # UPDATE DATABASE ONLY AFTER EMAIL SUCCESS
            # ==========================================

            if email_sent:

                update_application_status(
                    application_id,
                    action
                )

                save_email_history(
                    application_id,
                    candidate_email,
                    action,
                    subject
                )

                success_count += 1

            else:

                failed_count += 1

        except Exception as error:

            print(
                f"Bulk {action} error:",
                error
            )

            failed_count += 1

        progress_bar.progress(
            index / total_candidates
        )

    status_text.empty()

    return (
        success_count,
        failed_count
    )


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.title("🤖 AI HR")

    st.caption(
        "Recruitment Automation"
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "👥 Candidates",
            "💼 Jobs",
            "📋 Applications",
            "📧 Email History"
        ]
    )

    st.divider()

    st.caption(
        "AI-Powered Recruitment Platform"
    )


# =====================================================
# DASHBOARD PAGE
# =====================================================

if page == "📊 Dashboard":

    st.title(
        "📊 HR Dashboard"
    )

    st.write(
        "AI-powered recruitment and candidate matching system."
    )

    dataframe = get_dashboard_data()

    total_candidates = get_total_candidates()

    total_jobs = get_total_jobs()

    if dataframe.empty:

        shortlisted_count = 0
        review_count = 0
        rejected_count = 0
        selected_count = 0

    else:

        shortlisted_count = len(
            dataframe[
                dataframe["status"] == "SHORTLISTED"
            ]
        )

        review_count = len(
            dataframe[
                dataframe["status"] == "REVIEW"
            ]
        )

        rejected_count = len(
            dataframe[
                dataframe["status"] == "REJECTED"
            ]
        )

        selected_count = len(
            dataframe[
                dataframe["status"] == "SELECTED"
            ]
        )

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:

        st.metric(
            "👥 Candidates",
            total_candidates
        )

    with col2:

        st.metric(
            "💼 Jobs",
            total_jobs
        )

    with col3:

        st.metric(
            "🟢 Shortlisted",
            shortlisted_count
        )

    with col4:

        st.metric(
            "🟡 Review",
            review_count
        )

    with col5:

        st.metric(
            "🔴 Rejected",
            rejected_count
        )

    with col6:

        st.metric(
            "🎉 Selected",
            selected_count
        )

    st.divider()

    st.subheader(
        "🏆 Top Candidates"
    )

    if dataframe.empty:

        st.info(
            "No applications available yet."
        )

    else:

        top_candidates = dataframe.head(10)

        st.dataframe(
            top_candidates[
                [
                    "candidate_name",
                    "job_title",
                    "experience_years",
                    "match_percentage",
                    "status"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


# =====================================================
# CANDIDATES PAGE
# =====================================================

elif page == "👥 Candidates":

    st.title(
        "👥 Candidates"
    )

    candidates = get_all_candidates()

    if candidates.empty:

        st.info(
            "No candidates found."
        )

    else:

        # ==============================================
        # SEARCH
        # ==============================================

        search_name = st.text_input(
            "🔍 Search Candidate"
        )

        filtered_candidates = candidates.copy()

        if search_name:

            filtered_candidates = filtered_candidates[
                filtered_candidates["name"]
                .astype(str)
                .str.contains(
                    search_name,
                    case=False,
                    na=False
                )
            ]

        # ==============================================
        # TABLE
        # ==============================================

        st.subheader(
            "📋 All Candidates"
        )

        st.dataframe(
            filtered_candidates,
            use_container_width=True,
            hide_index=True
        )

        if filtered_candidates.empty:

            st.warning(
                "No candidates found."
            )

        else:

            st.divider()

            # ==========================================
            # SELECT CANDIDATE
            # ==========================================

            candidate_options = []

            for _, row in filtered_candidates.iterrows():

                candidate_options.append(
                    f"{row['name']} | "
                    f"{row['email']}"
                )

            selected_option = st.selectbox(
                "👤 Select Candidate Name to View Full Profile",
                candidate_options
            )

            selected_index = candidate_options.index(
                selected_option
            )

            selected_candidate = (
                filtered_candidates.iloc[
                    selected_index
                ]
            )

            candidate_id = int(
                selected_candidate["id"]
            )

            # ==========================================
            # GET FULL CANDIDATE DETAILS
            # ==========================================

            connection = get_connection()

            cursor = connection.cursor()

            # ------------------------------------------
            # GET ALL CANDIDATE SKILLS
            # ------------------------------------------

            cursor.execute(
                """
                SELECT skill
                FROM candidate_skills
                WHERE candidate_id = %s
                ORDER BY skill
                """,
                (candidate_id,)
            )

            candidate_skills = [
                row[0]
                for row in cursor.fetchall()
            ]

            # ------------------------------------------
            # GET APPLICATION HISTORY
            # ------------------------------------------

            cursor.execute(
                """
                SELECT

                    j.title,

                    a.match_percentage,

                    a.status,

                    mr.matched_skills,

                    mr.missing_skills,

                    mr.experience_match

                FROM applications a

                JOIN jobs j
                    ON a.job_id = j.id

                LEFT JOIN match_results mr
                    ON mr.candidate_id = a.candidate_id
                    AND mr.job_id = a.job_id

                WHERE a.candidate_id = %s

                ORDER BY a.match_percentage DESC
                """,
                (candidate_id,)
            )

            applications = cursor.fetchall()

            cursor.close()

            connection.close()

            # ==========================================
            # PROFILE HEADER
            # ==========================================

            st.divider()

            st.header(
                f"👤 {selected_candidate['name']}"
            )

            # ==========================================
            # BASIC INFORMATION
            # ==========================================

            col1, col2, col3 = st.columns(3)

            with col1:

                st.subheader(
                    "📧 Contact"
                )

                st.write(
                    "**Email:**",
                    selected_candidate["email"]
                )

                st.write(
                    "**Phone:**",
                    selected_candidate["phone"]
                )

            with col2:

                st.subheader(
                    "📍 Experience"
                )

                st.write(
                    "**Location:**",
                    selected_candidate["location"]
                )

                st.write(
                    "**Experience:**",
                    selected_candidate[
                        "experience_years"
                    ],
                    "years"
                )

            with col3:

                st.subheader(
                    "📄 Resume"
                )

                resume_path = selected_candidate.get(
                    "resume_path"
                )

                if pd.notna(resume_path):

                    st.code(
                        resume_path
                    )

                else:

                    st.info(
                        "Resume path not available."
                    )

            # ==========================================
            # ALL SKILLS
            # ==========================================

            st.divider()

            st.subheader(
                f"🛠️ All Skills "
                f"({len(candidate_skills)})"
            )

            if candidate_skills:

                skill_columns = st.columns(4)

                for index, skill in enumerate(
                    candidate_skills
                ):

                    with skill_columns[index % 4]:

                        st.success(
                            f"✓ {skill}"
                        )

            else:

                st.warning(
                    "No skills found for this candidate."
                )

            # ==========================================
            # APPLICATION HISTORY
            # ==========================================

            st.divider()

            st.subheader(
                "💼 Job Applications"
            )

            if applications:

                for application in applications:

                    (
                        job_title,
                        match_percentage,
                        status,
                        matched_skills,
                        missing_skills,
                        experience_match

                    ) = application

                    with st.expander(
                        f"💼 {job_title} | "
                        f"🎯 {match_percentage}% | "
                        f"{status}"
                    ):

                        metric_col1, metric_col2, metric_col3 = (
                            st.columns(3)
                        )

                        with metric_col1:

                            st.metric(
                                "Match Score",
                                f"{match_percentage}%"
                            )

                        with metric_col2:

                            st.write(
                                "**Status:**",
                                status
                            )

                        with metric_col3:

                            if experience_match:

                                st.success(
                                    "Experience Matched"
                                )

                            else:

                                st.warning(
                                    "Experience Not Matched"
                                )

                        st.divider()

                        skill_col1, skill_col2 = (
                            st.columns(2)
                        )

                        with skill_col1:

                            st.success(
                                "✅ Matched Skills"
                            )

                            matched = clean_skills(
                                matched_skills
                            )

                            if matched:

                                for skill in matched:

                                    st.write(
                                        f"✅ {skill}"
                                    )

                            else:

                                st.info(
                                    "No matched skills."
                                )

                        with skill_col2:

                            st.error(
                                "❌ Missing Skills"
                            )

                            missing = clean_skills(
                                missing_skills
                            )

                            if missing:

                                for skill in missing:

                                    st.write(
                                        f"❌ {skill}"
                                    )

                            else:

                                st.success(
                                    "No missing skills!"
                                )

            else:

                st.info(
                    "This candidate has not been "
                    "matched with any job yet."
                )


# =====================================================
# JOBS PAGE
# =====================================================

elif page == "💼 Jobs":

    st.title(
        "💼 Job Management"
    )

    with st.expander(
        "➕ Create New Job",
        expanded=True
    ):

        with st.form(
            "create_job_form"
        ):

            job_title = st.text_input(
                "Job Title",
                placeholder="Example: Data Engineer"
            )

            skills_input = st.text_area(
                "Required Skills",
                placeholder=(
                    "Python, SQL, PySpark, AWS"
                )
            )

            min_experience = st.number_input(
                "Minimum Experience (Years)",
                min_value=0.0,
                value=0.0,
                step=0.5
            )

            submitted = st.form_submit_button(
                "🚀 Create Job"
            )

            if submitted:

                if not job_title.strip():

                    st.error(
                        "Please enter a job title."
                    )

                elif not skills_input.strip():

                    st.error(
                        "Please enter required skills."
                    )

                else:

                    required_skills = [

                        skill.strip()

                        for skill
                        in skills_input.split(",")

                        if skill.strip()

                    ]

                    job_id = create_job(
                        job_title,
                        required_skills,
                        min_experience
                    )

                    if job_id:

                        st.success(
                            f"Job created successfully! "
                            f"Job ID: {job_id}"
                        )

                        with st.spinner(
                            "Matching all existing candidates..."
                        ):

                            match_all_candidates_with_job(
                                job_id
                            )

                        st.success(
                            "Candidates matched successfully!"
                        )

                    else:

                        st.error(
                            "Could not create the job."
                        )

    st.divider()

    st.subheader(
        "📋 Existing Jobs"
    )

    jobs = get_all_jobs()

    if jobs:

        jobs_dataframe = pd.DataFrame(
            jobs,
            columns=[
                "ID",
                "Job Title",
                "Required Skills",
                "Minimum Experience"
            ]
        )

        st.dataframe(
            jobs_dataframe,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No jobs created yet."
        )


# =====================================================
# APPLICATIONS PAGE
# =====================================================

elif page == "📋 Applications":

    st.title(
        "📋 Candidate Applications"
    )

    dataframe = get_dashboard_data()

    if dataframe.empty:

        st.info(
            "No applications available yet."
        )

    else:

        # ==============================================
        # FILTER BY JOB
        # ==============================================

        job_options = (
            ["All Jobs"]
            +
            sorted(
                dataframe[
                    "job_title"
                ].dropna().unique()
            )
        )

        selected_job = st.selectbox(
            "💼 Select Job Role",
            job_options
        )

        filtered_data = dataframe.copy()

        if selected_job != "All Jobs":

            filtered_data = filtered_data[
                filtered_data[
                    "job_title"
                ] == selected_job
            ]

        # ==============================================
        # FILTER BY STATUS
        # ==============================================

        status_options = [
            "ALL",
            "SHORTLISTED",
            "REVIEW",
            "REJECTED",
            "SELECTED"
        ]

        selected_status = st.selectbox(
            "🎯 Filter by Status",
            status_options
        )

        if selected_status != "ALL":

            filtered_data = filtered_data[
                filtered_data[
                    "status"
                ] == selected_status
            ]

        # ==============================================
        # BULK SELECTION TABLE
        # ==============================================

        st.subheader(
            "🏆 Candidate Ranking"
        )

        editable_data = filtered_data[
            [
                "application_id",
                "candidate_name",
                "email",
                "experience_years",
                "job_title",
                "match_percentage",
                "status"
            ]
        ].copy()

        editable_data.insert(
            0,
            "Select",
            False
        )

        edited_data = st.data_editor(
            editable_data,
            column_config={

                "Select": st.column_config.CheckboxColumn(
                    "Select",
                    default=False
                ),

                "application_id": None

            },
            disabled=[

                column

                for column
                in editable_data.columns

                if column != "Select"

            ],
            hide_index=True,
            use_container_width=True,
            key="bulk_candidate_selection"
        )

        selected_candidates = edited_data[
            edited_data["Select"] == True
        ]

        st.info(
            f"👥 Selected Candidates: "
            f"{len(selected_candidates)}"
        )

        # ==============================================
        # BULK BUTTONS
        # ==============================================

        bulk_col1, bulk_col2 = st.columns(2)

        with bulk_col1:

            accept_clicked = st.button(
                "✅ Accept Selected Candidates",
                use_container_width=True,
                type="primary"
            )

        with bulk_col2:

            reject_clicked = st.button(
                "❌ Reject Selected Candidates",
                use_container_width=True
            )

        # ==============================================
        # BULK ACCEPT
        # ==============================================

        if accept_clicked:

            if selected_candidates.empty:

                st.warning(
                    "Please select at least one candidate."
                )

            else:

                with st.spinner(
                    "Sending acceptance emails..."
                ):

                    success_count, failed_count = (
                        process_bulk_candidates(
                            selected_candidates,
                            "SELECTED"
                        )
                    )

                st.success(
                    f"✅ {success_count} candidate(s) "
                    f"accepted successfully!"
                )

                if failed_count > 0:

                    st.warning(
                        f"⚠️ {failed_count} candidate(s) "
                        f"failed."
                    )

        # ==============================================
        # BULK REJECT
        # ==============================================

        if reject_clicked:

            if selected_candidates.empty:

                st.warning(
                    "Please select at least one candidate."
                )

            else:

                with st.spinner(
                    "Sending rejection emails..."
                ):

                    success_count, failed_count = (
                        process_bulk_candidates(
                            selected_candidates,
                            "REJECTED"
                        )
                    )

                st.success(
                    f"❌ {success_count} candidate(s) "
                    f"rejected successfully!"
                )

                if failed_count > 0:

                    st.warning(
                        f"⚠️ {failed_count} candidate(s) "
                        f"failed."
                    )

        st.divider()

        # ==============================================
        # INDIVIDUAL CANDIDATE DETAILS
        # ==============================================

        st.subheader(
            "👤 Candidate Details"
        )

        if filtered_data.empty:

            st.warning(
                "No candidates found."
            )

        else:

            candidate_options = [

                f"{row['candidate_name']} | "
                f"{row['job_title']} | "
                f"{row['match_percentage']}%"

                for _, row
                in filtered_data.iterrows()

            ]

            selected_candidate_option = st.selectbox(
                "Select Candidate",
                candidate_options
            )

            selected_index = candidate_options.index(
                selected_candidate_option
            )

            candidate = filtered_data.iloc[
                selected_index
            ]

            info_col1, info_col2 = st.columns(2)

            with info_col1:

                st.write(
                    "### 👤 Candidate Information"
                )

                st.write(
                    "**Name:**",
                    candidate["candidate_name"]
                )

                st.write(
                    "**Email:**",
                    candidate["email"]
                )

                st.write(
                    "**Phone:**",
                    candidate["phone"]
                )

                st.write(
                    "**Location:**",
                    candidate["location"]
                )

                st.write(
                    "**Experience:**",
                    candidate["experience_years"],
                    "years"
                )

            with info_col2:

                st.write(
                    "### 🎯 Application Result"
                )

                st.metric(
                    "Match Percentage",
                    f"{candidate['match_percentage']}%"
                )

                status = candidate["status"]

                if status == "SHORTLISTED":

                    st.success(
                        "🟢 SHORTLISTED"
                    )

                elif status == "REVIEW":

                    st.warning(
                        "🟡 REVIEW"
                    )

                elif status == "SELECTED":

                    st.success(
                        "🎉 SELECTED"
                    )

                elif status == "REJECTED":

                    st.error(
                        "🔴 REJECTED"
                    )

            # ==========================================
            # MATCHED / MISSING SKILLS
            # ==========================================

            st.divider()

            st.subheader(
                "🎯 Skills Matching Analysis"
            )

            skill_col1, skill_col2 = st.columns(2)

            with skill_col1:

                st.success(
                    "✅ Matched Skills"
                )

                matched_skills = clean_skills(
                    candidate.get(
                        "matched_skills"
                    )
                )

                if matched_skills:

                    for skill in matched_skills:

                        st.write(
                            f"✅ {skill}"
                        )

                else:

                    st.info(
                        "No matched skills."
                    )

            with skill_col2:

                st.error(
                    "❌ Missing Skills"
                )

                missing_skills = clean_skills(
                    candidate.get(
                        "missing_skills"
                    )
                )

                if missing_skills:

                    for skill in missing_skills:

                        st.write(
                            f"❌ {skill}"
                        )

                else:

                    st.success(
                        "No missing skills!"
                    )

            # ==========================================
            # EXPERIENCE MATCH
            # ==========================================

            experience_match = candidate.get(
                "experience_match"
            )

            if experience_match is True:

                st.success(
                    "🎓 Experience requirement matched."
                )

            elif experience_match is False:

                st.warning(
                    "⚠️ Experience requirement not matched."
                )

            # ==========================================
            # INDIVIDUAL DECISION
            # ==========================================

            st.divider()

            st.subheader(
                "⚡ Individual HR Decision"
            )

            application_id = int(
                candidate["application_id"]
            )

            candidate_name = candidate[
                "candidate_name"
            ]

            candidate_email = candidate[
                "email"
            ]

            job_title = candidate[
                "job_title"
            ]

            decision_col1, decision_col2 = (
                st.columns(2)
            )

            with decision_col1:

                select_clicked = st.button(
                    "✅ Select Candidate",
                    key=f"select_{application_id}"
                )

            with decision_col2:

                reject_clicked_individual = st.button(
                    "❌ Reject Candidate",
                    key=f"reject_{application_id}"
                )

            # ------------------------------------------
            # SELECT CANDIDATE
            # ------------------------------------------

            if select_clicked:

                subject = (
                    f"Congratulations! Your application "
                    f"for {job_title}"
                )

                body = f"""Hi {candidate_name},

Congratulations!

We are pleased to inform you that you have been selected for the next stage of the recruitment process for the {job_title} position.

Our HR team will contact you shortly with further details.

Best regards,
HR Team
"""

                email_sent = send_email(
                    candidate_email,
                    subject,
                    body
                )

                if email_sent:

                    update_application_status(
                        application_id,
                        "SELECTED"
                    )

                    save_email_history(
                        application_id,
                        candidate_email,
                        "SELECTED",
                        subject
                    )

                    st.success(
                        "Candidate selected and email sent!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Email failed. Status not changed."
                    )

            # ------------------------------------------
            # REJECT CANDIDATE
            # ------------------------------------------

            if reject_clicked_individual:

                subject = (
                    f"Update on your application "
                    f"for {job_title}"
                )

                body = f"""Hi {candidate_name},

Thank you for taking the time to apply for the {job_title} position.

After careful consideration, we have decided to move forward with other candidates whose profiles align more closely with our requirements.

We sincerely appreciate your interest and wish you success in your future career.

Best regards,
HR Team
"""

                email_sent = send_email(
                    candidate_email,
                    subject,
                    body
                )

                if email_sent:

                    update_application_status(
                        application_id,
                        "REJECTED"
                    )

                    save_email_history(
                        application_id,
                        candidate_email,
                        "REJECTED",
                        subject
                    )

                    st.success(
                        "Candidate rejected and email sent!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Email failed. Status not changed."
                    )


# =====================================================
# EMAIL HISTORY PAGE
# =====================================================

elif page == "📧 Email History":

    st.title(
        "📧 Email History"
    )

    email_history = get_email_history()

    if email_history.empty:

        st.info(
            "No emails have been sent yet."
        )

    else:

        st.dataframe(
            email_history,
            use_container_width=True,
            hide_index=True
        )