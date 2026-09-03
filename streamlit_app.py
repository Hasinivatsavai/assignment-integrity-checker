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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- GENERAL ---------- */

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ---------- HERO ---------- */

    .hero {
        padding: 2.2rem 2.4rem;
        border-radius: 24px;
        border: 1px solid rgba(128,128,128,0.22);
        margin-bottom: 1.8rem;
    }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.35rem;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        opacity: 0.72;
        margin-bottom: 0;
    }

    /* ---------- SECTION TITLE ---------- */

    .section-title {
        font-size: 1.35rem;
        font-weight: 750;
        margin-top: 1rem;
        margin-bottom: 0.25rem;
    }

    .section-subtitle {
        opacity: 0.68;
        margin-bottom: 1.2rem;
    }

    /* ---------- CARDS ---------- */

    .info-card {
        border: 1px solid rgba(128,128,128,0.22);
        border-radius: 18px;
        padding: 1.25rem;
        min-height: 120px;
    }

    .info-label {
        font-size: 0.82rem;
        opacity: 0.65;
        margin-bottom: 0.45rem;
    }

    .info-value {
        font-size: 1.25rem;
        font-weight: 700;
        word-break: break-word;
    }

    /* ---------- SUBMISSION CARD ---------- */

    .submission-card {
        border: 1px solid rgba(128,128,128,0.22);
        border-radius: 20px;
        padding: 1.35rem;
        margin-bottom: 1rem;
    }

    .submission-name {
        font-size: 1.15rem;
        font-weight: 750;
    }

    .submission-meta {
        opacity: 0.68;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }

    /* ---------- STATUS ---------- */

    .status-box {
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(128,128,128,0.22);
        margin: 1rem 0;
    }

    .status-icon {
        font-size: 2.4rem;
    }

    .status-title {
        font-size: 1.45rem;
        font-weight: 800;
        margin-top: 0.35rem;
    }

    .status-description {
        opacity: 0.72;
        margin-top: 0.35rem;
    }

    /* ---------- CRC ---------- */

    .crc-box {
        border: 1px solid rgba(128,128,128,0.22);
        border-radius: 16px;
        padding: 1.2rem;
        text-align: center;
    }

    .crc-label {
        font-size: 0.8rem;
        opacity: 0.65;
    }

    .crc-value {
        font-family: monospace;
        font-size: 1.45rem;
        font-weight: 800;
        margin-top: 0.4rem;
        letter-spacing: 1px;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        opacity: 0.45;
        font-size: 0.82rem;
        margin-top: 3rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_crc(data):
    """Return CRC-32 as an 8-character hexadecimal value."""
    return f"{zlib.crc32(data) & 0xffffffff:08X}"


def info_card(label, value):
    """Display a small information card."""
    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-label">{label}</div>
            <div class="info-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def crc_card(label, value):
    """Display a CRC value card."""
    st.markdown(
        f"""
        <div class="crc-box">
            <div class="crc-label">{label}</div>
            <div class="crc-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def make_csv(submissions):
    """Create CSV report from submission records."""

    output = io.StringIO()

    fieldnames = [
        "Submission ID",
        "Student Name",
        "Student ID",
        "Course",
        "Assignment",
        "File Name",
        "Reference CRC-32",
        "Received CRC-32",
        "Integrity Status",
        "Submitted At"
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for submission in submissions:

        writer.writerow(
            {
                "Submission ID":
                    submission["submission_id"],

                "Student Name":
                    submission["student_name"],

                "Student ID":
                    submission["student_id"],

                "Course":
                    submission["course"],

                "Assignment":
                    submission["assignment"],

                "File Name":
                    submission["filename"],

                "Reference CRC-32":
                    submission["reference_crc"],

                "Received CRC-32":
                    submission["received_crc"],

                "Integrity Status":
                    submission["status"],

                "Submitted At":
                    submission["submitted_at"]
            }
        )

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

if "corruption_test" not in st.session_state:
    st.session_state.corruption_test = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🛡️ Integrity Hub")

    st.caption("Assignment submission & verification")

    st.divider()

    mode = st.radio(
        "Choose portal",
        [
            "👨‍🎓 Student",
            "👨‍🏫 Lecturer"
        ]
    )

    st.divider()

    st.caption("CRC-32")

    st.write(
        "A checksum used to detect whether "
        "file data has changed or become corrupted."
    )

    st.divider()

    st.caption(
        "Prototype • CRC-32 Assignment Integrity System"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-title">
            🛡️ Assignment Integrity Hub
        </div>

        <div class="hero-subtitle">
            Simple assignment submission with built-in
            CRC-32 integrity verification.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# STUDENT PORTAL
# ============================================================

if mode == "👨‍🎓 Student":

    st.markdown(
        '<div class="section-title">Submit Assignment</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Upload your assignment and submit it to the lecturer.'
        '</div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # STUDENT DETAILS
    # --------------------------------------------------------

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


    st.write("")


    # --------------------------------------------------------
    # FILE UPLOAD
    # --------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Upload Assignment",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX and TXT"
    )


    if uploaded_file:

        file_data = uploaded_file.getvalue()

        current_crc = calculate_crc(file_data)


        st.write("")


        # FILE INFORMATION

        a, b, c = st.columns(3)

        with a:

            info_card(
                "File",
                uploaded_file.name
            )

        with b:

            info_card(
                "File Size",
                f"{len(file_data):,} bytes"
            )

        with c:

            info_card(
                "Integrity Fingerprint",
                current_crc
            )


        st.write("")


        # ----------------------------------------------------
        # SUBMIT BUTTON
        # ----------------------------------------------------

        if st.button(
            "📤 Submit Assignment",
            use_container_width=True,
            type="primary"
        ):

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
                    "Please enter the course name."
                )

            elif not assignment.strip():

                st.error(
                    "Please enter the assignment name."
                )

            else:

                submission_number = (
                    len(st.session_state.submissions) + 1
                )

                submission_id = (
                    f"SUB-{submission_number:03d}"
                )

                submission = {

                    "submission_id":
                        submission_id,

                    "student_name":
                        student_name.strip(),

                    "student_id":
                        student_id.strip(),

                    "course":
                        course.strip(),

                    "assignment":
                        assignment.strip(),

                    "filename":
                        uploaded_file.name,

                    "file_data":
                        file_data,

                    "reference_crc":
                        current_crc,

                    "received_crc":
                        None,

                    "status":
                        "PENDING",

                    "submitted_at":
                        datetime.now().strftime(
                            "%d %b %Y • %I:%M %p"
                        )
                }


                st.session_state.submissions.append(
                    submission
                )

                st.session_state.student_submitted = True

                st.session_state.selected_submission = (
                    submission_id
                )


                st.success(
                    "Assignment submitted successfully."
                )


    # --------------------------------------------------------
    # SUBMISSION CONFIRMATION
    # --------------------------------------------------------

    if st.session_state.student_submitted:

        latest = (
            st.session_state.submissions[-1]
        )


        st.divider()


        st.markdown(
            "### ✅ Assignment Submitted"
        )

        st.write(
            "Your assignment has been added to the "
            "lecturer's submission inbox."
        )


        x1, x2, x3 = st.columns(3)

        with x1:

            info_card(
                "Submission ID",
                latest["submission_id"]
            )

        with x2:

            info_card(
                "Submitted File",
                latest["filename"]
            )

        with x3:

            info_card(
                "Status",
                "🟡 Submitted"
            )


        st.info(
            "Switch to Lecturer mode from the sidebar "
            "to see this submission in the lecturer inbox."
        )


# ============================================================
# LECTURER PORTAL
# ============================================================

else:

    st.markdown(
        '<div class="section-title">Lecturer Inbox</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Student submissions appear here automatically. '
        'No file upload is required.'
        '</div>',
        unsafe_allow_html=True
    )


    submissions = st.session_state.submissions


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total = len(submissions)

    verified = sum(
        1
        for s in submissions
        if s["status"] == "VERIFIED"
    )

    corrupted = sum(
        1
        for s in submissions
        if s["status"] == "CORRUPTED"
    )

    pending = sum(
        1
        for s in submissions
        if s["status"] == "PENDING"
    )


    s1, s2, s3, s4 = st.columns(4)

    with s1:

        info_card(
            "Total Submissions",
            total
        )

    with s2:

        info_card(
            "Verified",
            f"🟢 {verified}"
        )

    with s3:

        info_card(
            "Corrupted",
            f"🔴 {corrupted}"
        )

    with s4:

        info_card(
            "Pending",
            f"🟡 {pending}"
        )


    st.write("")


    # --------------------------------------------------------
    # EMPTY INBOX
    # --------------------------------------------------------

    if not submissions:

        st.info(
            "No assignments have been submitted yet."
        )

        st.write(
            "When a student submits an assignment, "
            "it will automatically appear here."
        )


    # --------------------------------------------------------
    # SUBMISSION LIST
    # --------------------------------------------------------

    else:

        st.markdown("### 📥 Recent Submissions")


        for submission in reversed(submissions):

            with st.container(border=True):

                left, middle, right = st.columns(
                    [2.2, 2.5, 1]
                )


                with left:

                    st.markdown(
                        f"### 📄 {submission['filename']}"
                    )

                    st.caption(
                        f"{submission['student_name']} "
                        f"• {submission['student_id']}"
                    )


                with middle:

                    st.write(
                        f"**{submission['assignment']}**"
                    )

                    st.caption(
                        f"{submission['course']} "
                        f"• {submission['submitted_at']}"
                    )


                with right:

                    if submission["status"] == "VERIFIED":

                        st.success(
                            "VERIFIED"
                        )

                    elif submission["status"] == "CORRUPTED":

                        st.error(
                            "CORRUPTED"
                        )

                    else:

                        st.warning(
                            "PENDING"
                        )


                    if st.button(
                        "View →",
                        key=(
                            "view_"
                            + submission["submission_id"]
                        ),
                        use_container_width=True
                    ):

                        st.session_state.selected_submission = (
                            submission["submission_id"]
                        )

                        st.session_state.corruption_test = False


    # --------------------------------------------------------
    # SELECTED SUBMISSION
    # --------------------------------------------------------

    selected_id = (
        st.session_state.selected_submission
    )


    selected = None


    if selected_id:

        for submission in submissions:

            if (
                submission["submission_id"]
                == selected_id
            ):

                selected = submission
                break


    if selected:

        st.divider()


        st.markdown(
            "## 🔍 Assignment Integrity Check"
        )


        st.caption(
            f"Submission {selected['submission_id']}"
        )


        # ----------------------------------------------------
        # ASSIGNMENT DETAILS
        # ----------------------------------------------------

        d1, d2, d3 = st.columns(3)

        with d1:

            info_card(
                "Student",
                selected["student_name"]
            )

        with d2:

            info_card(
                "Assignment",
                selected["assignment"]
            )

        with d3:

            info_card(
                "Submitted",
                selected["submitted_at"]
            )


        st.write("")


        d4, d5 = st.columns(2)

        with d4:

            info_card(
                "File",
                selected["filename"]
            )

        with d5:

            info_card(
                "Submission ID",
                selected["submission_id"]
            )


        st.write("")


        # ----------------------------------------------------
        # CHECK INTEGRITY
        # ----------------------------------------------------

        st.markdown(
            "### 🛡️ Integrity Verification"
        )

        st.write(
            "The lecturer does not need to upload the file. "
            "The submitted assignment is already stored "
            "in the submission record."
        )


        if st.button(
            "🔐 Check Assignment Integrity",
            use_container_width=True,
            type="primary",
            key=(
                "check_"
                + selected["submission_id"]
            )
        ):

            received_crc = calculate_crc(
                selected["file_data"]
            )

            selected["received_crc"] = (
                received_crc
            )


            if (
                selected["reference_crc"]
                == received_crc
            ):

                selected["status"] = (
                    "VERIFIED"
                )

            else:

                selected["status"] = (
                    "CORRUPTED"
                )


        # ----------------------------------------------------
        # SHOW CRC VALUES AFTER CHECK
        # ----------------------------------------------------

        if selected["received_crc"]:

            st.write("")


            crc1, crc2 = st.columns(2)


            with crc1:

                crc_card(
                    "Reference CRC-32",
                    selected["reference_crc"]
                )


            with crc2:

                crc_card(
                    "Received CRC-32",
                    selected["received_crc"]
                )


            st.write("")


            if selected["status"] == "VERIFIED":

                st.markdown(
                    """
                    <div class="status-box">

                        <div class="status-icon">
                            🟢
                        </div>

                        <div class="status-title">
                            INTEGRITY VERIFIED
                        </div>

                        <div class="status-description">
                            The received assignment matches
                            the reference submission data.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            elif selected["status"] == "CORRUPTED":

                st.markdown(
                    """
                    <div class="status-box">

                        <div class="status-icon">
                            🔴
                        </div>

                        <div class="status-title">
                            INTEGRITY CHECK FAILED
                        </div>

                        <div class="status-description">
                            The received assignment does not
                            match the reference submission data.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ----------------------------------------------------
        # TESTING / ERROR SIMULATION
        # ----------------------------------------------------

        st.divider()


        st.markdown(
            "### 🧪 Testing Tools"
        )

        st.caption(
            "For demonstration purposes, you can simulate "
            "a transmission error without changing the "
            "student's original submission."
        )


        if st.button(
            "⚡ Simulate Transmission Corruption",
            use_container_width=True,
            key=(
                "corrupt_"
                + selected["submission_id"]
            )
        ):

            st.session_state.corruption_test = True


        if st.session_state.corruption_test:

            original_data = bytearray(
                selected["file_data"]
            )


            if len(original_data) > 0:

                # Flip one bit in the first byte.
                original_data[0] ^= 1


            simulated_crc = calculate_crc(
                original_data
            )


            st.write("")


            c1, c2 = st.columns(2)


            with c1:

                crc_card(
                    "Original Reference CRC",
                    selected["reference_crc"]
                )


            with c2:

                crc_card(
                    "Simulated Received CRC",
                    simulated_crc
                )


            st.write("")


            if (
                simulated_crc
                != selected["reference_crc"]
            ):

                st.error(
                    "🔴 CORRUPTION DETECTED — "
                    "the simulated change produced "
                    "a different CRC-32 value."
                )

            else:

                st.warning(
                    "The CRC values matched in this simulation."
                )


        # ----------------------------------------------------
        # REPORT
        # ----------------------------------------------------

        st.divider()


        st.markdown(
            "### 📄 Submission Report"
        )


        report_data = [
            selected
        ]


        st.download_button(
            "⬇️ Download Verification Report",
            data=make_csv(report_data),
            file_name=(
                selected["submission_id"]
                + "_crc32_report.csv"
            ),
            mime="text/csv",
            use_container_width=True,
            key=(
                "download_"
                + selected["submission_id"]
            )
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Assignment Integrity Hub • CRC-32 based integrity detection
    </div>
    """,
    unsafe_allow_html=True
)
