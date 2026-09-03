import streamlit as st
import zlib
import csv
import io
from datetime import datetime


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Assignment Integrity Hub",
    page_icon="🛡️",
    layout="wide"
)


# ============================================================
# FUNCTIONS
# ============================================================

def calculate_crc(data):
    """Calculate CRC-32 and return it as an 8-character HEX value."""
    return f"{zlib.crc32(data) & 0xffffffff:08X}"


def create_submission_id():
    """Create a simple submission ID."""
    return f"SUB-{len(st.session_state.submissions) + 1:03d}"


def generate_report():
    """Generate CSV verification report."""

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Submission ID",
        "Student Name",
        "Student ID",
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
            submission["file_name"],
            submission["original_crc"],
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
# HEADER
# ============================================================

st.title("🛡️ Assignment Integrity Hub")

st.caption(
    "CRC-32 based assignment submission and transmission integrity system"
)

st.divider()


# ============================================================
# TWO SIDES
# ============================================================

student_tab, lecturer_tab = st.tabs(
    ["🎓 Student Submission", "👨‍🏫 Lecturer Dashboard"]
)


# ============================================================
# STUDENT SIDE
# ============================================================

with student_tab:

    st.header("🎓 Submit Your Assignment")

    st.write(
        "Submit your assignment securely. "
        "You can also simulate transmission corruption for testing."
    )

    st.divider()

    # --------------------------------------------------------
    # SHOW SUCCESS SCREEN AFTER SUBMISSION
    # --------------------------------------------------------

    if st.session_state.student_submitted:

        last_submission = st.session_state.submissions[-1]

        st.success("✅ Assignment submitted successfully!")

        st.subheader("Submission Details")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Submission ID",
                last_submission["id"]
            )

        with col2:
            st.metric(
                "Status",
                "Submitted"
            )

        with col3:
            st.metric(
                "Integrity",
                "Ready for Lecturer"
            )

        st.write("")

        st.info(
            "Your assignment has been sent to the lecturer. "
            "The lecturer will perform the integrity check."
        )

        st.write("")

        st.write("### Assignment Information")

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.write(
                f"**Student:** {last_submission['student_name']}"
            )

            st.write(
                f"**Student ID:** {last_submission['student_id']}"
            )

        with info_col2:
            st.write(
                f"**File:** {last_submission['file_name']}"
            )

            st.write(
                f"**Submitted:** {last_submission['submitted_at']}"
            )

        st.divider()

        # ----------------------------------------------------
        # STUDENT CORRUPTION SIMULATION
        # ----------------------------------------------------

        st.subheader("🧪 Transmission Testing")

        st.write(
            "For demonstration purposes, you can simulate corruption "
            "of the submitted assignment."
        )

        if not last_submission["corrupted"]:

            if st.button(
                "🧪 Simulate Transmission Corruption",
                use_container_width=True
            ):

                original_data = last_submission["received_file_data"]

                if original_data:

                    corrupted_data = bytearray(original_data)

                    # Flip the first bit
                    corrupted_data[0] ^= 1

                    last_submission["received_file_data"] = bytes(
                        corrupted_data
                    )

                    last_submission["corrupted"] = True

                    # Reset lecturer verification
                    last_submission["received_crc"] = ""
                    last_submission["status"] = "PENDING"

                    st.success(
                        "🧪 Corruption simulated successfully!"
                    )

                    st.info(
                        "The assignment has been modified during "
                        "transmission. The lecturer will detect this "
                        "during CRC-32 verification."
                    )

                    st.rerun()

        else:

            st.warning(
                "⚠️ Transmission corruption has been simulated "
                "for this assignment."
            )

            st.write(
                "The lecturer will now receive a modified version "
                "of the assignment."
            )

        st.divider()

        if st.button(
            "📤 Submit Another Assignment",
            use_container_width=True
        ):

            st.session_state.student_submitted = False
            st.rerun()

    # --------------------------------------------------------
    # STUDENT SUBMISSION FORM
    # --------------------------------------------------------

    else:

        st.subheader("Student Details")

        student_name = st.text_input(
            "Student Name",
            placeholder="Enter your full name"
        )

        student_id = st.text_input(
            "Student ID",
            placeholder="Enter your Student ID"
        )

        st.write("")

        st.subheader("Assignment File")

        uploaded_file = st.file_uploader(
            "Upload your assignment",
            type=["pdf", "docx", "txt"],
            help="Supported formats: PDF, DOCX and TXT"
        )

        st.write("")

        if st.button(
            "📤 Submit Assignment",
            use_container_width=True,
            type="primary"
        ):

            if not student_name:

                st.error(
                    "Please enter your name."
                )

            elif not student_id:

                st.error(
                    "Please enter your Student ID."
                )

            elif uploaded_file is None:

                st.error(
                    "Please upload your assignment."
                )

            else:

                # Read uploaded file
                file_data = uploaded_file.getvalue()

                # Generate ORIGINAL CRC
                original_crc = calculate_crc(file_data)

                # Create submission ID
                submission_id = create_submission_id()

                # Submission timestamp
                submitted_at = datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                )

                # Store submission
                submission = {

                    "id": submission_id,

                    "student_name": student_name,

                    "student_id": student_id,

                    "file_name": uploaded_file.name,

                    # Original submitted file
                    "original_file_data": file_data,

                    # File lecturer currently receives
                    "received_file_data": file_data,

                    # CRC generated when student submits
                    "original_crc": original_crc,

                    # Lecturer calculates this later
                    "received_crc": "",

                    # Initial state
                    "status": "PENDING",

                    # Whether corruption was simulated
                    "corrupted": False,

                    "submitted_at": submitted_at
                }

                st.session_state.submissions.append(
                    submission
                )

                st.session_state.student_submitted = True

                st.rerun()


# ============================================================
# LECTURER SIDE
# ============================================================

with lecturer_tab:

    st.header("👨‍🏫 Lecturer Dashboard")

    st.write(
        "View student submissions and verify assignment integrity "
        "using CRC-32."
    )

    st.divider()

    # ========================================================
    # DASHBOARD METRICS
    # ========================================================

    total = len(st.session_state.submissions)

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
            "Integrity Failed",
            failed
        )

    st.divider()


    # ========================================================
    # SUBMISSION INBOX
    # ========================================================

    if st.session_state.selected_submission is None:

        st.subheader("📥 Submission Inbox")

        if not st.session_state.submissions:

            st.info(
                "No assignments have been submitted yet."
            )

        else:

            for index, submission in enumerate(
                st.session_state.submissions
            ):

                with st.container(border=True):

                    left, middle, right = st.columns(
                        [3, 3, 1]
                    )

                    with left:

                        st.write(
                            f"### {submission['file_name']}"
                        )

                        st.write(
                            f"👤 **{submission['student_name']}**"
                        )

                        st.write(
                            f"🆔 {submission['student_id']}"
                        )

                    with middle:

                        st.write(
                            f"📄 **{submission['file_name']}**"
                        )

                        st.write(
                            f"🕒 {submission['submitted_at']}"
                        )

                    with right:

                        if submission["status"] == "VERIFIED":

                            st.success("VERIFIED")

                        elif submission["status"] == "FAILED":

                            st.error("CORRUPTED")

                        else:

                            st.warning("PENDING")

                        if st.button(
                            "View →",
                            key=f"view_{index}"
                        ):

                            st.session_state.selected_submission = index

                            st.rerun()


    # ========================================================
    # SELECTED SUBMISSION
    # ========================================================

    else:

        index = st.session_state.selected_submission

        submission = st.session_state.submissions[index]

        if st.button(
            "← Back to Submission Inbox"
        ):

            st.session_state.selected_submission = None

            st.rerun()

        st.divider()

        st.header("📄 Assignment Submission")

        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Student Name:** {submission['student_name']}"
            )

            st.write(
                f"**Student ID:** {submission['student_id']}"
            )

        with col2:

            st.write(
                f"**File Name:** {submission['file_name']}"
            )

            st.write(
                f"**Submission ID:** {submission['id']}"
            )

        st.divider()


        # ====================================================
        # DOWNLOAD ASSIGNMENT
        # ====================================================

        st.subheader("📥 Assignment File")

        st.download_button(
            label="⬇️ Download Assignment",
            data=submission["received_file_data"],
            file_name=submission["file_name"],
            use_container_width=True
        )

        st.divider()


        # ====================================================
        # INTEGRITY CHECK
        # ====================================================

        st.subheader("🔐 Assignment Integrity")

        st.write(
            "CRC-32 is used to compare the original submitted "
            "assignment with the assignment received by the lecturer."
        )

        crc_col1, crc_col2 = st.columns(2)

        with crc_col1:

            st.metric(
                "Original CRC-32",
                submission["original_crc"]
            )

        with crc_col2:

            if submission["received_crc"]:

                st.metric(
                    "Received CRC-32",
                    submission["received_crc"]
                )

            else:

                st.metric(
                    "Received CRC-32",
                    "Not Checked"
                )

        st.write("")

        # ----------------------------------------------------
        # CHECK BUTTON
        # ----------------------------------------------------

        if st.button(
            "🔍 Check Assignment Integrity",
            use_container_width=True,
            type="primary"
        ):

            received_crc = calculate_crc(
                submission["received_file_data"]
            )

            submission["received_crc"] = received_crc

            # Compare CRC values
            if received_crc == submission["original_crc"]:

                submission["status"] = "VERIFIED"

            else:

                submission["status"] = "FAILED"

            st.rerun()


        # ====================================================
        # RESULT
        # ====================================================

        if submission["status"] == "VERIFIED":

            st.success(
                "🟢 INTEGRITY VERIFIED"
            )

            st.write(
                "The received assignment matches the original "
                "submitted assignment."
            )

            st.info(
                "CRC-32 values are identical."
            )

        elif submission["status"] == "FAILED":

            st.error(
                "🔴 INTEGRITY CHECK FAILED"
            )

            st.write(
                "The received assignment has been modified or "
                "corrupted during transmission."
            )

            st.warning(
                "CRC-32 values do not match."
            )

        else:

            st.info(
                "Integrity has not been checked yet."
            )


        st.divider()


        # ====================================================
        # TRANSMISSION STATUS
        # ====================================================

        st.subheader("🧪 Transmission Status")

        if submission["corrupted"]:

            st.warning(
                "⚠️ This submission has been intentionally "
                "corrupted for testing."
            )

            st.write(
                "The student simulated a transmission error. "
                "The lecturer's CRC-32 verification should detect it."
            )

        else:

            st.success(
                "No simulated transmission corruption."
            )


    # ========================================================
    # CSV REPORT
    # ========================================================

    if st.session_state.submissions:

        st.divider()

        st.subheader("📊 Verification Report")

        st.write(
            "Download a CSV report containing all assignment "
            "integrity verification results."
        )

        st.download_button(
            label="📥 Download CSV Report",
            data=generate_report(),
            file_name="assignment_integrity_report.csv",
            mime="text/csv",
            use_container_width=True
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Assignment Integrity Hub • CRC-32 Based Submission Integrity System"
)
