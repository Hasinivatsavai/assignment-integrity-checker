import streamlit as st
import zlib
import csv
import io
from datetime import datetime


# ============================================================
# PAGE SETTINGS
# ============================================================

st.set_page_config(
    page_title="Assignment Integrity Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CRC-32 FUNCTION
# ============================================================

def calculate_crc(data):
    """
    Calculate CRC-32 checksum for the uploaded file.
    """
    return f"{zlib.crc32(data) & 0xffffffff:08X}"


# ============================================================
# SUBMISSION ID
# ============================================================

def create_submission_id():
    number = len(st.session_state.submissions) + 1
    return f"SUB-{number:03d}"


# ============================================================
# CSV REPORT
# ============================================================

def generate_csv():

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Submission ID",
        "Student Name",
        "Student ID",
        "Course",
        "Assignment",
        "File Name",
        "Reference CRC-32",
        "Received CRC-32",
        "Status",
        "Submitted At"
    ])

    for submission in st.session_state.submissions:

        writer.writerow([
            submission["id"],
            submission["student_name"],
            submission["student_id"],
            submission["course"],
            submission["assignment"],
            submission["file_name"],
            submission["reference_crc"],
            submission["received_crc"],
            submission["status"],
            submission["submitted_at"]
        ])

    return output.getvalue().encode("utf-8")


# ============================================================
# SESSION STATE
# ============================================================

if "submissions" not in st.session_state:
    st.session_state.submissions = []

if "selected_submission" not in st.session_state:
    st.session_state.selected_submission = None

if "student_submitted" not in st.session_state:
    st.session_state.student_submitted = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🛡️ Integrity Hub")

    st.caption("Assignment submission & verification")

    st.divider()

    st.subheader("Choose Portal")

    role = st.radio(
        "Portal",
        [
            "🎓 Student",
            "👨‍🏫 Lecturer"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.subheader("CRC-32")

    st.write(
        "A checksum used to detect whether "
        "file data has changed or become corrupted."
    )

    st.divider()

    st.caption(
        "Prototype\n\n"
        "CRC-32 Assignment Integrity System"
    )


# ============================================================
# STUDENT PORTAL
# ============================================================

if role == "🎓 Student":

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.title("🛡️ Assignment Integrity Hub")

    st.write(
        "Submit your assignment normally. "
        "The system automatically creates a CRC-32 "
        "integrity reference for your submission."
    )

    st.divider()

    # --------------------------------------------------------
    # SUBMISSION SUCCESS
    # --------------------------------------------------------

    if st.session_state.student_submitted:

        latest = st.session_state.submissions[-1]

        st.success(
            "Assignment submitted successfully!"
        )

        st.subheader("Submission Confirmed")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Submission ID",
                latest["id"]
            )

        with col2:
            st.metric(
                "Status",
                "Submitted"
            )

        with col3:
            st.metric(
                "Integrity Method",
                "CRC-32"
            )

        st.info(
            "Your assignment has been sent to the lecturer. "
            "The system has stored its CRC-32 reference."
        )

        st.divider()

        if st.button(
            "Submit Another Assignment",
            use_container_width=True
        ):

            st.session_state.student_submitted = False

            st.rerun()

    # --------------------------------------------------------
    # SUBMISSION FORM
    # --------------------------------------------------------

    else:

        st.header("Submit Assignment")

        st.write(
            "Enter your details and upload your completed assignment."
        )

        st.subheader("Student Details")

        col1, col2 = st.columns(2)

        with col1:

            student_name = st.text_input(
                "Student Name",
                placeholder="Enter your name"
            )

        with col2:

            student_id = st.text_input(
                "Student ID",
                placeholder="Enter your student ID"
            )

        col3, col4 = st.columns(2)

        with col3:

            course = st.text_input(
                "Course",
                placeholder="Example: Database Management Systems"
            )

        with col4:

            assignment = st.text_input(
                "Assignment",
                placeholder="Example: Assignment 03"
            )

        st.subheader("Assignment File")

        uploaded_file = st.file_uploader(
            "Upload your assignment",
            type=[
                "pdf",
                "docx",
                "txt"
            ],
            help="Supported formats: PDF, DOCX and TXT"
        )

        st.write("")

        submit_button = st.button(
            "📤 Submit Assignment",
            type="primary",
            use_container_width=True
        )

        # ----------------------------------------------------
        # SUBMIT
        # ----------------------------------------------------

        if submit_button:

            if not student_name.strip():

                st.error(
                    "Please enter your name."
                )

            elif not student_id.strip():

                st.error(
                    "Please enter your Student ID."
                )

            elif not course.strip():

                st.error(
                    "Please enter your course."
                )

            elif not assignment.strip():

                st.error(
                    "Please enter the assignment name."
                )

            elif uploaded_file is None:

                st.error(
                    "Please upload your assignment."
                )

            else:

                # Get file bytes

                file_data = uploaded_file.getvalue()

                # Generate CRC-32

                reference_crc = calculate_crc(
                    file_data
                )

                # Create submission

                submission = {

                    "id": create_submission_id(),

                    "student_name":
                        student_name.strip(),

                    "student_id":
                        student_id.strip(),

                    "course":
                        course.strip(),

                    "assignment":
                        assignment.strip(),

                    "file_name":
                        uploaded_file.name,

                    "file_data":
                        file_data,

                    "reference_crc":
                        reference_crc,

                    "received_crc":
                        "",

                    "status":
                        "PENDING",

                    "submitted_at":
                        datetime.now().strftime(
                            "%d %b %Y, %I:%M %p"
                        )
                }

                # Store submission

                st.session_state.submissions.append(
                    submission
                )

                st.session_state.student_submitted = True

                st.rerun()

        # ----------------------------------------------------
        # HOW IT WORKS
        # ----------------------------------------------------

        st.divider()

        st.header("How it works")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.subheader("1️⃣ Submit")

            st.write(
                "Upload your assignment and "
                "submit it to the lecturer."
            )

        with col2:

            st.subheader("2️⃣ Protect")

            st.write(
                "The system automatically generates "
                "a CRC-32 reference for the file."
            )

        with col3:

            st.subheader("3️⃣ Verify")

            st.write(
                "The lecturer checks whether "
                "the assignment data has changed."
            )


# ============================================================
# LECTURER PORTAL
# ============================================================

else:

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.title("📥 Assignment Inbox")

    st.write(
        "Student submissions appear here automatically. "
        "Open a submission to verify its file integrity."
    )

    st.divider()

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total = len(
        st.session_state.submissions
    )

    pending = len([
        s for s in st.session_state.submissions
        if s["status"] == "PENDING"
    ])

    verified = len([
        s for s in st.session_state.submissions
        if s["status"] == "VERIFIED"
    ])

    failed = len([
        s for s in st.session_state.submissions
        if s["status"] == "FAILED"
    ])

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total",
            total
        )

    with col2:

        st.metric(
            "Pending",
            pending
        )

    with col3:

        st.metric(
            "Verified",
            verified
        )

    with col4:

        st.metric(
            "Failed",
            failed
        )

    st.divider()

    # ========================================================
    # SELECTED SUBMISSION
    # ========================================================

    if st.session_state.selected_submission is not None:

        selected = None

        for submission in st.session_state.submissions:

            if (
                submission["id"]
                ==
                st.session_state.selected_submission
            ):

                selected = submission

                break

        if selected is not None:

            st.header("Submission Details")

            st.caption(
                f"Submission ID: {selected['id']}"
            )

            # ------------------------------------------------
            # STUDENT INFORMATION
            # ------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("Student")

                st.write(
                    f"**Name:** {selected['student_name']}"
                )

                st.write(
                    f"**Student ID:** {selected['student_id']}"
                )

                st.write(
                    f"**Course:** {selected['course']}"
                )

            with col2:

                st.subheader("Assignment")

                st.write(
                    f"**Assignment:** {selected['assignment']}"
                )

                st.write(
                    f"**File:** {selected['file_name']}"
                )

                st.write(
                    f"**Submitted:** {selected['submitted_at']}"
                )

            st.divider()

            # ------------------------------------------------
            # INTEGRITY CHECK
            # ------------------------------------------------

            st.header("CRC-32 Integrity Check")

            col1, col2 = st.columns(2)

            with col1:

                st.subheader(
                    "Reference CRC-32"
                )

                st.code(
                    selected["reference_crc"]
                )

            with col2:

                st.subheader(
                    "Current CRC-32"
                )

                if selected["received_crc"]:

                    st.code(
                        selected["received_crc"]
                    )

                else:

                    st.info(
                        "Not checked yet"
                    )

            st.write("")

            check_button = st.button(
                "🔍 Check Assignment Integrity",
                type="primary",
                use_container_width=True
            )

            if check_button:

                # Calculate current CRC

                received_crc = calculate_crc(
                    selected["file_data"]
                )

                selected["received_crc"] = received_crc

                # Compare CRC values

                if (
                    received_crc
                    ==
                    selected["reference_crc"]
                ):

                    selected["status"] = "VERIFIED"

                else:

                    selected["status"] = "FAILED"

                st.rerun()

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            if selected["status"] == "VERIFIED":

                st.success(
                    "✓ INTEGRITY VERIFIED"
                )

                st.write(
                    "The reference CRC-32 and current CRC-32 "
                    "match. No change was detected in the "
                    "assignment data."
                )

            elif selected["status"] == "FAILED":

                st.error(
                    "✕ INTEGRITY CHECK FAILED"
                )

                st.write(
                    "The CRC-32 values are different. "
                    "The assignment data may have been "
                    "changed or corrupted."
                )

            # ------------------------------------------------
            # CORRUPTION SIMULATION
            # ------------------------------------------------

            st.divider()

            st.subheader(
                "🧪 Testing: Simulate Transmission Corruption"
            )

            st.write(
                "This test intentionally changes one bit "
                "of the assignment data to demonstrate "
                "how CRC-32 detects corruption."
            )

            simulate_button = st.button(
                "Simulate Corruption"
            )

            if simulate_button:

                original_data = selected["file_data"]

                if len(original_data) > 0:

                    corrupted_data = bytearray(
                        original_data
                    )

                    # Flip one bit

                    corrupted_data[0] ^= 1

                    corrupted_crc = calculate_crc(
                        bytes(corrupted_data)
                    )

                    st.error(
                        "CORRUPTION DETECTED"
                    )

                    st.write(
                        "The assignment data was intentionally "
                        "modified. The CRC-32 value changed."
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            "**Original CRC-32**"
                        )

                        st.code(
                            selected["reference_crc"]
                        )

                    with col2:

                        st.write(
                            "**Corrupted CRC-32**"
                        )

                        st.code(
                            corrupted_crc
                        )

            st.divider()

            # ------------------------------------------------
            # BACK BUTTON
            # ------------------------------------------------

            if st.button(
                "← Back to Inbox",
                use_container_width=True
            ):

                st.session_state.selected_submission = None

                st.rerun()

    # ========================================================
    # INBOX
    # ========================================================

    else:

        st.header("Student Submissions")

        if total == 0:

            st.info(
                "📭 No submissions yet. "
                "When a student submits an assignment, "
                "it will appear here automatically."
            )

        else:

            # Newest submission first

            for submission in reversed(
                st.session_state.submissions
            ):

                with st.container(border=True):

                    col1, col2, col3 = st.columns(
                        [4, 3, 1]
                    )

                    with col1:

                        st.subheader(
                            submission["assignment"]
                        )

                        st.write(
                            f"👤 {submission['student_name']}"
                        )

                        st.caption(
                            f"Student ID: {submission['student_id']}"
                        )

                    with col2:

                        st.write(
                            f"📄 {submission['file_name']}"
                        )

                        st.caption(
                            submission["submitted_at"]
                        )

                        if submission["status"] == "PENDING":

                            st.warning(
                                "● Pending"
                            )

                        elif submission["status"] == "VERIFIED":

                            st.success(
                                "✓ Verified"
                            )

                        else:

                            st.error(
                                "✕ Failed"
                            )

                    with col3:

                        st.write("")

                        if st.button(
                            "View →",
                            key=f"view_{submission['id']}"
                        ):

                            st.session_state.selected_submission = (
                                submission["id"]
                            )

                            st.rerun()

    # ========================================================
    # CSV REPORT
    # ========================================================

    if total > 0:

        st.divider()

        st.header("Verification Report")

        st.write(
            "Download a CSV record of the assignment "
            "integrity checks."
        )

        csv_data = generate_csv()

        st.download_button(
            "⬇️ Download CSV Report",
            data=csv_data,
            file_name="assignment_integrity_report.csv",
            mime="text/csv"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Assignment Integrity Hub • CRC-32 Based "
    "File Integrity Verification"
)
