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
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* ---------- GENERAL ---------- */

    .stApp {
        background: #0f1015;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        letter-spacing: -0.5px;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #24252d;
        border-right: 1px solid #343640;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    .brand {
        font-size: 25px;
        font-weight: 750;
        color: #f5f5f7;
        margin-bottom: 5px;
    }

    .brand-icon {
        color: #62a8ff;
    }

    .brand-subtitle {
        color: #a7a8b0;
        font-size: 14px;
        margin-bottom: 28px;
    }

    .side-divider {
        height: 1px;
        background: #44454e;
        margin: 22px 0;
    }

    .sidebar-info-title {
        color: #b6b7c0;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .sidebar-info {
        color: #eeeeef;
        font-size: 14px;
        line-height: 1.65;
    }

    .sidebar-footer {
        color: #898a94;
        font-size: 13px;
        line-height: 1.6;
        margin-top: 35px;
    }

    /* ---------- HERO ---------- */

    .hero {
        background: linear-gradient(
            135deg,
            #191a21 0%,
            #14151b 100%
        );
        border: 1px solid #30313a;
        border-radius: 22px;
        padding: 34px 38px;
        margin-bottom: 34px;
        box-shadow: 0 15px 45px rgba(0,0,0,0.20);
    }

    .hero-title {
        color: #f5f6f8;
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 9px;
    }

    .hero-subtitle {
        color: #aeb0ba;
        font-size: 16px;
        line-height: 1.6;
    }

    .hero-badge {
        display: inline-block;
        background: #1c2d43;
        color: #76b5ff;
        border: 1px solid #315277;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 650;
        margin-bottom: 15px;
    }

    /* ---------- SECTION HEADERS ---------- */

    .section-title {
        font-size: 27px;
        font-weight: 780;
        color: #f4f4f6;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #9fa1ab;
        font-size: 15px;
        margin-bottom: 24px;
    }

    /* ---------- CARDS ---------- */

    .info-card {
        background: #191a20;
        border: 1px solid #30313a;
        border-radius: 16px;
        padding: 21px;
        height: 100%;
    }

    .info-card-title {
        color: #f3f3f5;
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .info-card-text {
        color: #a6a7b0;
        font-size: 13px;
        line-height: 1.55;
    }

    /* ---------- SUBMISSION CARD ---------- */

    .submission-card {
        background: #191a20;
        border: 1px solid #30313a;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 12px;
    }

    .submission-id {
        color: #75b4ff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .submission-name {
        color: #f3f3f5;
        font-size: 18px;
        font-weight: 750;
        margin-top: 5px;
    }

    .submission-meta {
        color: #9ea0aa;
        font-size: 13px;
        margin-top: 5px;
    }

    /* ---------- STATUS ---------- */

    .status-pending {
        display: inline-block;
        background: #332c1b;
        color: #e9c76c;
        border: 1px solid #66572d;
        border-radius: 999px;
        padding: 5px 11px;
        font-size: 12px;
        font-weight: 700;
    }

    .status-verified {
        display: inline-block;
        background: #183222;
        color: #70d998;
        border: 1px solid #326945;
        border-radius: 999px;
        padding: 5px 11px;
        font-size: 12px;
        font-weight: 700;
    }

    .status-failed {
        display: inline-block;
        background: #371d20;
        color: #ff858d;
        border: 1px solid #71343a;
        border-radius: 999px;
        padding: 5px 11px;
        font-size: 12px;
        font-weight: 700;
    }

    /* ---------- CRC BOX ---------- */

    .crc-box {
        background: #15161b;
        border: 1px solid #343640;
        border-radius: 15px;
        padding: 20px;
        margin: 8px 0;
    }

    .crc-label {
        color: #9799a3;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 7px;
    }

    .crc-value {
        color: #f3f4f6;
        font-family: monospace;
        font-size: 23px;
        font-weight: 750;
        letter-spacing: 1px;
    }

    /* ---------- SUCCESS / ERROR ---------- */

    .success-panel {
        background: #14281c;
        border: 1px solid #326a45;
        border-radius: 18px;
        padding: 28px;
        text-align: center;
        margin: 20px 0;
    }

    .success-title {
        color: #73e19a;
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 7px;
    }

    .success-text {
        color: #b5d9c0;
        font-size: 14px;
    }

    .error-panel {
        background: #2c171a;
        border: 1px solid #71363c;
        border-radius: 18px;
        padding: 28px;
        text-align: center;
        margin: 20px 0;
    }

    .error-title {
        color: #ff858d;
        font-size: 25px;
        font-weight: 800;
        margin-bottom: 7px;
    }

    .error-text {
        color: #e0b5b9;
        font-size: 14px;
    }

    /* ---------- METRIC CARDS ---------- */

    .metric-card {
        background: #191a20;
        border: 1px solid #30313a;
        border-radius: 15px;
        padding: 18px;
        text-align: center;
    }

    .metric-number {
        color: #f4f4f6;
        font-size: 27px;
        font-weight: 800;
    }

    .metric-label {
        color: #9698a2;
        font-size: 12px;
        margin-top: 3px;
    }

    /* ---------- STREAMLIT INPUTS ---------- */

    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div {
        background-color: #25262e;
        border-color: #353640;
        border-radius: 10px;
    }

    input, textarea {
        color: #f1f1f3 !important;
    }

    label {
        color: #e4e4e7 !important;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 43px;
    }

    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 650;
    }

    /* ---------- FILE UPLOADER ---------- */

    section[data-testid="stFileUploaderDropzone"] {
        background: #191a20;
        border: 1px dashed #474955;
        border-radius: 14px;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #737580;
        font-size: 12px;
        margin-top: 55px;
        padding-top: 20px;
        border-top: 1px solid #292a31;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# FUNCTIONS
# ============================================================

def calculate_crc(data):
    """Calculate CRC-32 and return it as an 8-character hexadecimal value."""
    return f"{zlib.crc32(data) & 0xffffffff:08X}"


def create_submission_id():
    """Create a simple submission ID for the demo."""
    number = len(st.session_state.submissions) + 1
    return f"SUB-{number:03d}"


def status_badge(status):
    """Return HTML for submission status."""
    if status == "VERIFIED":
        return '<span class="status-verified">✓ VERIFIED</span>'
    elif status == "FAILED":
        return '<span class="status-failed">✕ FAILED</span>'
    else:
        return '<span class="status-pending">● PENDING</span>'


def generate_csv():
    """Generate CSV verification report."""
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
            submission.get("received_crc", ""),
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

if "corruption_test" not in st.session_state:
    st.session_state.corruption_test = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div class="brand">
        <span class="brand-icon">🛡️</span> Integrity Hub
    </div>

    <div class="brand-subtitle">
        Assignment submission & verification
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="sidebar-info-title">CHOOSE PORTAL</div>',
        unsafe_allow_html=True
    )

    role = st.radio(
        "Portal",
        ["🎓 Student", "👨‍🏫 Lecturer"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-info-title">CRC-32</div>

    <div class="sidebar-info">
        A checksum used to detect whether
        file data has changed or become
        corrupted during transmission.
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sidebar-footer">
        Prototype • CRC-32 Assignment Integrity System<br><br>
        Student submission → Lecturer verification
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# STUDENT PORTAL
# ============================================================

if role == "🎓 Student":

    # HERO
    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            CRC-32 INTEGRITY PROTECTION
        </div>

        <div class="hero-title">
            🛡️ Assignment Integrity Hub
        </div>

        <div class="hero-subtitle">
            Submit your assignment normally.
            The system automatically creates a CRC-32
            integrity reference for your submission.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # SUCCESS MESSAGE AFTER SUBMISSION

    if st.session_state.student_submitted:

        latest = st.session_state.submissions[-1]

        st.markdown("""
        <div class="success-panel">

            <div class="success-title">
                ✓ Assignment Submitted Successfully
            </div>

            <div class="success-text">
                Your assignment has been sent to the lecturer
                and its integrity reference has been generated.
            </div>

        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">{latest["id"]}</div>
                    <div class="metric-label">SUBMISSION ID</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">✓</div>
                    <div class="metric-label">SUBMISSION RECEIVED</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-number">CRC-32</div>
                    <div class="metric-label">INTEGRITY METHOD</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("")

        if st.button("Submit Another Assignment", use_container_width=False):
            st.session_state.student_submitted = False
            st.rerun()

    else:

        # SECTION TITLE

        st.markdown(
            '<div class="section-title">Submit Assignment</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Enter your details and upload your assignment.'
            '</div>',
            unsafe_allow_html=True
        )

        # STUDENT DETAILS

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

        st.markdown("")

        # FILE UPLOAD

        st.markdown(
            '<div class="section-title" style="font-size:20px;">'
            'Assignment File'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Upload your completed assignment.'
            '</div>',
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            "Choose your assignment file",
            type=["pdf", "docx", "txt"],
            help="Supported formats: PDF, DOCX and TXT"
        )

        st.markdown("")

        # SUBMIT BUTTON

        submit = st.button(
            "Submit Assignment →",
            type="primary",
            use_container_width=True
        )

        if submit:

            if not student_name.strip():
                st.error("Please enter your name.")

            elif not student_id.strip():
                st.error("Please enter your Student ID.")

            elif not course.strip():
                st.error("Please enter your course.")

            elif not assignment.strip():
                st.error("Please enter the assignment name.")

            elif uploaded_file is None:
                st.error("Please upload your assignment.")

            else:

                # Read uploaded file

                file_data = uploaded_file.getvalue()

                # Generate reference CRC

                reference_crc = calculate_crc(file_data)

                # Create submission record

                submission = {
                    "id": create_submission_id(),
                    "student_name": student_name.strip(),
                    "student_id": student_id.strip(),
                    "course": course.strip(),
                    "assignment": assignment.strip(),
                    "file_name": uploaded_file.name,
                    "file_data": file_data,
                    "reference_crc": reference_crc,
                    "received_crc": "",
                    "status": "PENDING",
                    "submitted_at": datetime.now().strftime(
                        "%d %b %Y, %I:%M %p"
                    )
                }

                # Store submission

                st.session_state.submissions.append(submission)

                st.session_state.student_submitted = True

                st.rerun()

    # INFORMATION CARDS

    st.markdown("")

    st.markdown(
        '<div class="section-title" style="font-size:22px;">'
        'How it works'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="info-card">

            <div class="info-card-title">
                01 · Submit
            </div>

            <div class="info-card-text">
                Upload your assignment and submit
                it to the lecturer.
            </div>

        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-card">

            <div class="info-card-title">
                02 · Protect
            </div>

            <div class="info-card-text">
                The system automatically generates
                a CRC-32 reference for the file.
            </div>

        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="info-card">

            <div class="info-card-title">
                03 · Verify
            </div>

            <div class="info-card-text">
                The lecturer can later check whether
                the assignment data has changed.
            </div>

        </div>
        """, unsafe_allow_html=True)


# ============================================================
# LECTURER PORTAL
# ============================================================

else:

    # HERO

    st.markdown("""
    <div class="hero">

        <div class="hero-badge">
            LECTURER PORTAL
        </div>

        <div class="hero-title">
            📥 Assignment Inbox
        </div>

        <div class="hero-subtitle">
            Student submissions appear here automatically.
            Open a submission to verify its file integrity
            using CRC-32.
        </div>

    </div>
    """, unsafe_allow_html=True)

    # ========================================================
    # SUMMARY METRICS
    # ========================================================

    total = len(st.session_state.submissions)

    verified = len([
        s for s in st.session_state.submissions
        if s["status"] == "VERIFIED"
    ])

    failed = len([
        s for s in st.session_state.submissions
        if s["status"] == "FAILED"
    ])

    pending = len([
        s for s in st.session_state.submissions
        if s["status"] == "PENDING"
    ])

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{total}</div>
                <div class="metric-label">TOTAL SUBMISSIONS</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{pending}</div>
                <div class="metric-label">PENDING CHECK</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{verified}</div>
                <div class="metric-label">VERIFIED</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{failed}</div>
                <div class="metric-label">FAILED</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("")

    # ========================================================
    # SELECTED SUBMISSION
    # ========================================================

    if st.session_state.selected_submission is not None:

        selected = None

        for submission in st.session_state.submissions:

            if submission["id"] == st.session_state.selected_submission:
                selected = submission
                break

        if selected is not None:

            st.markdown(
                '<div class="section-title">'
                'Submission Details'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="section-subtitle">'
                'Review the submission and perform an integrity check.'
                '</div>',
                unsafe_allow_html=True
            )

            # DETAILS CARD

            st.markdown(
                f"""
                <div class="submission-card">

                    <div class="submission-id">
                        {selected["id"]}
                    </div>

                    <div class="submission-name">
                        {selected["assignment"]}
                    </div>

                    <div class="submission-meta">
                        Student: {selected["student_name"]}
                        &nbsp; • &nbsp;
                        ID: {selected["student_id"]}
                        &nbsp; • &nbsp;
                        Course: {selected["course"]}
                    </div>

                    <div class="submission-meta">
                        File: {selected["file_name"]}
                        &nbsp; • &nbsp;
                        Submitted: {selected["submitted_at"]}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("")

            # CRC REFERENCE

            st.markdown(
                '<div class="section-title" style="font-size:20px;">'
                'Integrity Verification'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="section-subtitle">'
                'Compare the stored reference CRC-32 with the current file CRC-32.'
                '</div>',
                unsafe_allow_html=True
            )

            crc1, crc2 = st.columns(2)

            with crc1:

                st.markdown(
                    f"""
                    <div class="crc-box">

                        <div class="crc-label">
                            Reference CRC-32
                        </div>

                        <div class="crc-value">
                            {selected["reference_crc"]}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with crc2:

                current_crc = ""

                if selected["received_crc"]:
                    current_crc = selected["received_crc"]
                else:
                    current_crc = "Not checked"

                st.markdown(
                    f"""
                    <div class="crc-box">

                        <div class="crc-label">
                            Current / Received CRC-32
                        </div>

                        <div class="crc-value">
                            {current_crc}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("")

            # CHECK BUTTON

            if st.button(
                "🔍 Check Assignment Integrity",
                type="primary",
                use_container_width=True
            ):

                # Calculate CRC from the stored submission bytes

                received_crc = calculate_crc(selected["file_data"])

                selected["received_crc"] = received_crc

                if received_crc == selected["reference_crc"]:

                    selected["status"] = "VERIFIED"

                else:

                    selected["status"] = "FAILED"

                st.rerun()

            # RESULT

            if selected["status"] == "VERIFIED":

                st.markdown("""
                <div class="success-panel">

                    <div class="success-title">
                        ✓ INTEGRITY VERIFIED
                    </div>

                    <div class="success-text">
                        Reference CRC-32 and current CRC-32 match.
                        No change was detected in the assignment data.
                    </div>

                </div>
                """, unsafe_allow_html=True)

            elif selected["status"] == "FAILED":

                st.markdown("""
                <div class="error-panel">

                    <div class="error-title">
                        ✕ INTEGRITY CHECK FAILED
                    </div>

                    <div class="error-text">
                        The CRC-32 values are different.
                        The assignment data may have been changed
                        or corrupted.
                    </div>

                </div>
                """, unsafe_allow_html=True)

            # =================================================
            # CORRUPTION SIMULATION
            # =================================================

            st.markdown("")

            with st.expander("🧪 Testing Tools — Simulate Transmission Corruption"):

                st.write(
                    "This test intentionally changes one byte of the "
                    "assignment data to demonstrate how CRC-32 detects corruption."
                )

                if st.button(
                    "Simulate Corruption",
                    use_container_width=False
                ):

                    original_data = selected["file_data"]

                    if len(original_data) > 0:

                        corrupted_data = bytearray(original_data)

                        # Flip one bit in the first byte

                        corrupted_data[0] ^= 1

                        corrupted_crc = calculate_crc(
                            bytes(corrupted_data)
                        )

                        st.session_state.corruption_test = True

                        if corrupted_crc != selected["reference_crc"]:

                            st.error(
                                "CORRUPTION DETECTED — "
                                "The CRC-32 changed after the file data was modified."
                            )

                            st.code(
                                f"Reference CRC-32 : {selected['reference_crc']}\n"
                                f"Corrupted CRC-32 : {corrupted_crc}"
                            )

                        else:

                            st.warning(
                                "The CRC values matched in this simulation."
                            )

            st.markdown("")

            if st.button("← Back to Inbox"):

                st.session_state.selected_submission = None
                st.session_state.corruption_test = False
                st.rerun()

    # ========================================================
    # INBOX
    # ========================================================

    else:

        st.markdown(
            '<div class="section-title">'
            'Submissions'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Student assignments received by the lecturer.'
            '</div>',
            unsafe_allow_html=True
        )

        if len(st.session_state.submissions) == 0:

            st.markdown("""
            <div class="info-card">

                <div class="info-card-title">
                    📭 No submissions yet
                </div>

                <div class="info-card-text">
                    When a student submits an assignment,
                    it will automatically appear in this inbox.
                </div>

            </div>
            """, unsafe_allow_html=True)

        else:

            # Show newest submission first

            for submission in reversed(st.session_state.submissions):

                col1, col2 = st.columns([5, 1])

                with col1:

                    st.markdown(
                        f"""
                        <div class="submission-card">

                            <div class="submission-id">
                                {submission["id"]}
                            </div>

                            <div class="submission-name">
                                {submission["assignment"]}
                            </div>

                            <div class="submission-meta">
                                👤 {submission["student_name"]}
                                &nbsp; • &nbsp;
                                {submission["student_id"]}
                                &nbsp; • &nbsp;
                                {submission["course"]}
                            </div>

                            <div class="submission-meta">
                                📄 {submission["file_name"]}
                                &nbsp; • &nbsp;
                                {submission["submitted_at"]}
                            </div>

                            <div style="margin-top:12px;">
                                {status_badge(submission["status"])}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:

                    st.markdown("<br>", unsafe_allow_html=True)

                    if st.button(
                        "View →",
                        key=f"view_{submission['id']}",
                        use_container_width=True
                    ):

                        st.session_state.selected_submission = submission["id"]

                        st.session_state.corruption_test = False

                        st.rerun()


    # ========================================================
    # REPORT
    # ========================================================

    if len(st.session_state.submissions) > 0:

        st.markdown("")

        st.markdown(
            '<div class="section-title" style="font-size:22px;">'
            'Verification Report'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">'
            'Download a CSV record of all assignment integrity checks.'
            '</div>',
            unsafe_allow_html=True
        )

        csv_data = generate_csv()

        st.download_button(
            label="⬇ Download CSV Report",
            data=csv_data,
            file_name="assignment_integrity_report.csv",
            mime="text/csv",
            use_container_width=False
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
    Assignment Integrity Hub · CRC-32 Based File Integrity Verification
</div>
""", unsafe_allow_html=True)
