import streamlit as st
import zlib
import csv
import io
from datetime import datetime


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Assignment Integrity Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# APPLICATION FUNCTIONS
# ============================================================

def calculate_crc(data):
    """
    Generate CRC-32 checksum for file data.
    """
    return f"{zlib.crc32(data) & 0xffffffff:08X}"


def create_submission_id():
    """
    Create a simple submission ID.
    """
    return f"SUB-{len(st.session_state.submissions) + 1:03d}"


def generate_report():
    """
    Generate CSV verification report.
    """

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Submission ID",
        "Student Name",
        "Student ID",
        "Course",
        "Assignment",
        "File Name",
        "Original CRC-32",
        "Received CRC-32",
        "Integrity Status",
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
            submission["original_crc"],
            submission["received_crc"],
            submission["status"],
            submission["submitted_at"]
        ])

    return output.getvalue().encode("utf-8")


def reset_student_form():
    """
    Reset student submission state.
    """
    st.session_state.student_submitted = False


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

    st.caption(
        "Secure assignment submission & integrity verification"
    )

    st.divider()

    st.subheader("Portal")

    role = st.radio(
        "Select portal",
        [
            "🎓 Student",
            "👨‍🏫 Lecturer"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.subheader("How it works")

    if role == "🎓 Student":

        st.write(
            "Submit your assignment. "
            "The system automatically generates "
            "an original CRC-32 reference."
        )

    else:

        st.write(
            "Open student submissions and compare "
            "the original CRC-32 with the received file."
        )

    st.divider()

    st.caption(
        "CRC-32 Based Assignment Integrity System"
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
        "Submit your assignment securely. "
        "Your file's integrity reference is generated "
        "automatically in the background."
    )

    st.divider()

    # --------------------------------------------------------
    # SUCCESS SCREEN
    # --------------------------------------------------------

    if st.session_state.student_submitted:

        latest = st.session_state.submissions[-1]

        st.success(
            "Assignment submitted successfully!"
        )

        st.header("Submission Confirmed")

        st.write(
            "Your assignment has been sent to the lecturer."
        )

        st.write("")

        # Summary

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
                "Integrity",
                "Protected"
            )

        st.write("")

        # Submission details

        with st.container(border=True):

            st.subheader("Submission Details")

            st.write(
                f"**Student:** {latest['student_name']}"
            )

            st.write(
                f"**Student ID:** {latest['student_id']}"
            )

            st.write(
                f"**Course:** {latest['course']}"
            )

            st.write(
                f"**Assignment:** {latest['assignment']}"
            )

            st.write(
                f"**File:** {latest['file_name']}"
            )

            st.write(
                f"**Submitted:** {latest['submitted_at']}"
            )

        st.write("")

        # Original CRC

        with st.expander("🔐 View Original CRC-32"):

            st.write(
                "This is the CRC-32 generated from your "
                "original submitted assignment."
            )

            st.code(
                latest["original_crc"],
                language="text"
            )

            st.caption(
                "The lecturer will use this reference "
                "during the integrity check."
            )

        st.write("")

        st.info(
            "You don't need to perform any CRC verification. "
            "The integrity check is handled by the lecturer."
        )

        st.write("")

        if st.button(
            "＋ Submit Another Assignment",
            use_container_width=True
        ):

            reset_student_form()

            st.rerun()

    # --------------------------------------------------------
    # STUDENT SUBMISSION FORM
    # --------------------------------------------------------

    else:

        st.header("Submit Assignment")

        st.write(
            "Fill in your details, upload your assignment, "
            "and submit it to the lecturer."
        )

        st.write("")

        # ----------------------------------------------------
        # STUDENT DETAILS
        # ----------------------------------------------------

        with st.container(border=True):

            st.subheader("Student Details")

            col1, col2 = st.columns(2)

            with col1:

                student_name = st.text_input(
                    "Student Name",
                    placeholder="Enter your full name"
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

        st.write("")

        # ----------------------------------------------------
        # FILE UPLOAD
        # ----------------------------------------------------

        with st.container(border=True):

            st.subheader("Assignment File")

            st.write(
                "Upload the completed assignment you want to submit."
            )

            uploaded_file = st.file_uploader(
                "Choose your assignment",
                type=[
                    "pdf",
                    "docx",
                    "txt"
                ],
                help="Supported formats: PDF, DOCX and TXT"
            )

        st.write("")

        # ----------------------------------------------------
        # SUBMIT
        # ----------------------------------------------------

        submit = st.button(
            "📤 Submit Assignment",
            type="primary",
            use_container_width=True
        )

        if submit:

            # Validate details

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
                    "Please upload your assignment file."
                )

            else:

                # ------------------------------------------------
                # READ FILE
                # ------------------------------------------------

                file_data = uploaded_file.getvalue()

                # ------------------------------------------------
                # GENERATE ORIGINAL CRC
                # ------------------------------------------------

                original_crc = calculate_crc(
                    file_data
                )

                # ------------------------------------------------
                # CREATE SUBMISSION
                # ------------------------------------------------

                submission = {

                    "id":
                        create_submission_id(),

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

                    # Original submitted file

                    "original_file_data":
                        file_data,

                    # File currently received
                    # by lecturer

                    "received_file_data":
                        file_data,

                    # CRC generated at submission

                    "original_crc":
                        original_crc,

                    # Lecturer calculates this later

                    "received_crc":
                        "",

                    # Initial state

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
        # SIMPLE EXPLANATION
        # ----------------------------------------------------

        st.divider()

        st.header("What happens after submission?")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.subheader("1️⃣ Submit")

            st.write(
                "Upload your assignment and submit it."
            )

        with col2:

            st.subheader("2️⃣ Reference Created")

            st.write(
                "The system automatically generates "
                "an original CRC-32."
            )

        with col3:

            st.subheader("3️⃣ Lecturer Checks")

            st.write(
                "The lecturer verifies the received "
                "assignment using the CRC reference."
            )


# ============================================================
# LECTURER PORTAL
# ============================================================

else:

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.title("📥 Lecturer Assignment Inbox")

    st.write(
        "Review student submissions and verify "
        "their file integrity using CRC-32."
    )

    st.divider()

    # --------------------------------------------------------
    # DASHBOARD NUMBERS
    # --------------------------------------------------------

    total = len(
        st.session_state.submissions
    )

    pending = sum(
        1
        for s in st.session_state.submissions
        if s["status"] == "PENDING"
    )

    verified = sum(
        1
        for s in st.session_state.submissions
        if s["status"] == "VERIFIED"
    )

    failed = sum(
        1
        for s in st.session_state.submissions
        if s["status"] == "FAILED"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Submissions",
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

    st.write("")

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

            # ------------------------------------------------
            # BACK
            # ------------------------------------------------

            if st.button("← Back to Inbox"):

                st.session_state.selected_submission = None

                st.rerun()

            st.divider()

            # ------------------------------------------------
            # SUBMISSION HEADER
            # ------------------------------------------------

            st.header(
                selected["assignment"]
            )

            st.caption(
                f"Submission ID: {selected['id']}"
            )

            # ------------------------------------------------
            # DETAILS
            # ------------------------------------------------

            col1, col2 = st.columns(2)

            with col1:

                with st.container(border=True):

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

                with st.container(border=True):

                    st.subheader("Assignment")

                    st.write(
                        f"**Assignment:** "
                        f"{selected['assignment']}"
                    )

                    st.write(
                        f"**File:** "
                        f"{selected['file_name']}"
                    )

                    st.write(
                        f"**Submitted:** "
                        f"{selected['submitted_at']}"
                    )

            st.write("")

            # ------------------------------------------------
            # FILE DOWNLOAD
            # ------------------------------------------------

            with st.container(border=True):

                st.subheader("📄 Submitted Assignment")

                st.write(
                    "The assignment submitted by the student "
                    "is available to the lecturer."
                )

                st.download_button(
                    "⬇️ Download Assignment",
                    data=selected["received_file_data"],
                    file_name=selected["file_name"],
                    key=f"download_{selected['id']}",
                    use_container_width=True
                )

            st.write("")

            # ------------------------------------------------
            # CRC VERIFICATION
            # ------------------------------------------------

            st.header("🔐 Assignment Integrity")

            st.write(
                "Compare the original CRC-32 reference "
                "with the CRC-32 calculated from the "
                "received assignment."
            )

            col1, col2 = st.columns(2)

            with col1:

                with st.container(border=True):

                    st.subheader(
                        "Original CRC-32"
                    )

                    st.code(
                        selected["original_crc"],
                        language="text"
                    )

                    st.caption(
                        "Generated when the student submitted "
                        "the assignment."
                    )

            with col2:

                with st.container(border=True):

                    st.subheader(
                        "Received CRC-32"
                    )

                    if selected["received_crc"]:

                        st.code(
                            selected["received_crc"],
                            language="text"
                        )

                        st.caption(
                            "Calculated from the received file."
                        )

                    else:

                        st.info(
                            "Not checked yet."
                        )

            st.write("")

            # ------------------------------------------------
            # CHECK BUTTON
            # ------------------------------------------------

            check = st.button(
                "🔍 Check Assignment Integrity",
                type="primary",
                use_container_width=True
            )

            if check:

                # Calculate CRC of received file

                received_crc = calculate_crc(
                    selected["received_file_data"]
                )

                selected["received_crc"] = received_crc

                # Compare

                if (
                    received_crc
                    ==
                    selected["original_crc"]
                ):

                    selected["status"] = "VERIFIED"

                else:

                    selected["status"] = "FAILED"

                st.rerun()

            st.write("")

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            if selected["status"] == "VERIFIED":

                st.success(
                    "✅ INTEGRITY VERIFIED"
                )

                st.write(
                    "The Original CRC-32 and Received CRC-32 "
                    "match. No change or corruption was detected "
                    "in the received assignment."
                )

            elif selected["status"] == "FAILED":

                st.error(
                    "❌ INTEGRITY CHECK FAILED"
                )

                st.write(
                    "The Original CRC-32 and Received CRC-32 "
                    "are different. The received assignment "
                    "may have been changed or corrupted."
                )

            else:

                st.info(
                    "Integrity verification has not been performed yet."
                )

            # =================================================
            # LECTURER TESTING AREA
            # =================================================

            st.divider()

            with st.expander(
                "🧪 Lecturer Testing Tools"
            ):

                st.write(
                    "Use this only for demonstration/testing. "
                    "It intentionally modifies the received "
                    "file to demonstrate CRC-32 corruption detection."
                )

                simulate = st.button(
                    "Simulate Transmission Corruption",
                    key=f"simulate_{selected['id']}"
                )

                if simulate:

                    original_data = (
                        selected["received_file_data"]
                    )

                    if len(original_data) == 0:

                        st.warning(
                            "The assignment file is empty."
                        )

                    else:

                        # Create corrupted copy

                        corrupted_data = bytearray(
                            original_data
                        )

                        # Flip one bit

                        corrupted_data[0] ^= 1

                        corrupted_data = bytes(
                            corrupted_data
                        )

                        # Calculate CRC

                        corrupted_crc = calculate_crc(
                            corrupted_data
                        )

                        st.error(
                            "⚠️ CORRUPTION DETECTED"
                        )

                        st.write(
                            "One bit of the received file was "
                            "intentionally changed."
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            st.write(
                                "**Original CRC-32**"
                            )

                            st.code(
                                selected["original_crc"]
                            )

                        with col2:

                            st.write(
                                "**Corrupted CRC-32**"
                            )

                            st.code(
                                corrupted_crc
                            )

                        if (
                            corrupted_crc
                            !=
                            selected["original_crc"]
                        ):

                            st.success(
                                "CRC-32 successfully detected "
                                "the simulated corruption."
                            )

            # ------------------------------------------------
            # END DETAILS
            # ------------------------------------------------

    # ========================================================
    # INBOX
    # ========================================================

    else:

        st.header("Student Submissions")

        if total == 0:

            st.info(
                "📭 No assignments have been submitted yet."
            )

            st.write(
                "Once a student submits an assignment, "
                "it will automatically appear in this inbox."
            )

        else:

            # Newest first

            for submission in reversed(
                st.session_state.submissions
            ):

                with st.container(border=True):

                    col1, col2, col3 = st.columns(
                        [4, 3, 1]
                    )

                    # ----------------------------------------
                    # STUDENT
                    # ----------------------------------------

                    with col1:

                        st.subheader(
                            submission["assignment"]
                        )

                        st.write(
                            f"👤 {submission['student_name']}"
                        )

                        st.caption(
                            f"Student ID: "
                            f"{submission['student_id']}"
                        )

                    # ----------------------------------------
                    # FILE / STATUS
                    # ----------------------------------------

                    with col2:

                        st.write(
                            f"📄 {submission['file_name']}"
                        )

                        st.caption(
                            submission["submitted_at"]
                        )

                        if submission["status"] == "PENDING":

                            st.warning(
                                "● Pending verification"
                            )

                        elif submission["status"] == "VERIFIED":

                            st.success(
                                "✓ Integrity verified"
                            )

                        else:

                            st.error(
                                "✕ Integrity failed"
                            )

                    # ----------------------------------------
                    # VIEW
                    # ----------------------------------------

                    with col3:

                        st.write("")

                        if st.button(
                            "View →",
                            key=f"view_{submission['id']}",
                            use_container_width=True
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

        st.header("📊 Verification Report")

        st.write(
            "Download the integrity verification history "
            "as a CSV file."
        )

        report = generate_report()

        st.download_button(
            "⬇️ Download CSV Report",
            data=report,
            file_name="assignment_integrity_report.csv",
            mime="text/csv"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Assignment Integrity Hub • CRC-32 File Integrity Verification"
)
