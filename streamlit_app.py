import streamlit as st
import zlib
import csv
import io
from datetime import datetime

st.set_page_config(
    page_title="Assignment Integrity Hub",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 1.5rem 1.7rem;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,.25);
    margin-bottom: 1.2rem;
}

.hero h1 {
    margin: 0 0 .3rem 0;
}

.hero p {
    margin: 0;
    opacity: .78;
}

.card {
    padding: 1rem 1.1rem;
    border-radius: 14px;
    border: 1px solid rgba(128,128,128,.25);
    min-height: 105px;
}

.card-label {
    font-size: .82rem;
    opacity: .7;
}

.card-value {
    font-size: 1.55rem;
    font-weight: 700;
    margin-top: .3rem;
}

.small-note {
    font-size: .88rem;
    opacity: .75;
}
</style>
""", unsafe_allow_html=True)


def crc_hex(data):
    return f"{zlib.crc32(data) & 0xffffffff:08X}"


def metric_card(label, value):
    st.markdown(
        f'<div class="card">'
        f'<div class="card-label">{label}</div>'
        f'<div class="card-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def csv_bytes(rows):
    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=[
            "Test ID",
            "Original File",
            "Received File",
            "Original CRC-32",
            "Received CRC-32",
            "Status",
            "Timestamp"
        ]
    )

    writer.writeheader()
    writer.writerows(rows)

    return output.getvalue().encode("utf-8")


# -------------------- SESSION STATE --------------------

defaults = {
    "student_reference_crc": None,
    "student_reference_data": None,
    "student_reference_name": None,
    "student_verified": False,
    "student_result": None,
    "student_corrupted": False,
    "lecturer_results": [],
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- HEADER --------------------

st.markdown("""
<div class="hero">
    <h1>🛡️ Assignment Integrity Hub</h1>
    <p>
        CRC-32 based assignment submission integrity verification
        and testing dashboard
    </p>
</div>
""", unsafe_allow_html=True)


# -------------------- SIDEBAR --------------------

with st.sidebar:

    st.header("Dashboard")

    role = st.radio(
        "Choose your view",
        ["Student", "Lecturer"]
    )

    st.divider()

    st.subheader("About CRC-32")

    st.write(
        "CRC-32 creates a checksum from the file's bytes. "
        "If the reference and received CRC values match, "
        "the tested data is unchanged with respect to this CRC check."
    )

    st.caption(
        "Note: CRC-32 detects accidental changes or corruption. "
        "It is not a plagiarism detector or proof of authorship."
    )


# ==========================================================
# STUDENT VIEW
# ==========================================================

if role == "Student":

    st.subheader("👨‍🎓 Student Verification")

    st.write(
        "Generate a reference CRC for your assignment, "
        "verify it, and test the error-simulation feature."
    )

    file = st.file_uploader(
        "Upload your assignment",
        type=["pdf", "docx", "txt"],
        key="student_file"
    )

    if file:

        data = file.getvalue()

        current_signature = (
            file.name,
            len(data),
            crc_hex(data)
        )

        previous_signature = st.session_state.get(
            "student_file_signature"
        )

        if previous_signature != current_signature:

            st.session_state.student_file_signature = current_signature

            st.session_state.student_reference_crc = None
            st.session_state.student_reference_data = None
            st.session_state.student_reference_name = None

            st.session_state.student_verified = False
            st.session_state.student_result = None
            st.session_state.student_corrupted = False


        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "File Name",
                file.name
            )

        with c2:
            metric_card(
                "File Size",
                f"{len(data):,} bytes"
            )

        with c3:
            metric_card(
                "Current CRC-32",
                crc_hex(data)
            )


        st.write("")

        b1, b2 = st.columns(2)


        with b1:

            if st.button(
                "🔐 Generate Reference CRC",
                use_container_width=True
            ):

                st.session_state.student_reference_crc = crc_hex(data)

                st.session_state.student_reference_data = data

                st.session_state.student_reference_name = file.name

                st.session_state.student_verified = False

                st.session_state.student_result = None

                st.session_state.student_corrupted = False


        with b2:

            if st.button(
                "🔍 Verify Current File",
                use_container_width=True
            ):

                if st.session_state.student_reference_crc is None:

                    st.warning(
                        "Generate the reference CRC first."
                    )

                else:

                    received_crc = crc_hex(data)

                    match = (
                        received_crc
                        == st.session_state.student_reference_crc
                    )

                    st.session_state.student_verified = True

                    st.session_state.student_result = {
                        "received_crc": received_crc,
                        "match": match,
                        "time": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    }


        if st.session_state.student_reference_crc:

            st.divider()

            st.subheader("CRC Verification")

            r1, r2 = st.columns(2)

            with r1:
                metric_card(
                    "Reference CRC-32",
                    st.session_state.student_reference_crc
                )

            with r2:
                metric_card(
                    "Current CRC-32",
                    crc_hex(data)
                )


            if (
                st.session_state.student_verified
                and st.session_state.student_result
            ):

                if st.session_state.student_result["match"]:

                    st.success(
                        "✅ VALID — CRC values match. "
                        "No change was detected in the tested file."
                    )

                else:

                    st.error(
                        "❌ CORRUPTED — CRC values do not match. "
                        "A change was detected."
                    )


            st.divider()

            st.subheader("🧪 Error Simulation")

            st.write(
                "This creates a temporary modified copy of the "
                "uploaded file. Your original upload is not changed."
            )


            if st.button(
                "⚡ Simulate Corruption",
                use_container_width=True
            ):

                st.session_state.student_corrupted = True


            if st.session_state.student_corrupted:

                corrupted_data = bytearray(data)

                if len(corrupted_data) > 0:

                    corrupted_data[0] ^= 1


                corrupted_crc = crc_hex(corrupted_data)


                s1, s2 = st.columns(2)

                with s1:

                    metric_card(
                        "Reference CRC-32",
                        st.session_state.student_reference_crc
                    )

                with s2:

                    metric_card(
                        "Simulated Corrupted CRC-32",
                        corrupted_crc
                    )


                if (
                    corrupted_crc
                    != st.session_state.student_reference_crc
                ):

                    st.error(
                        "❌ CORRUPTION DETECTED — "
                        "the simulated change produced a different "
                        "CRC-32 value."
                    )

                else:

                    st.warning(
                        "CRC values still match in this simulation."
                    )


            st.divider()

            st.subheader("📄 Student Verification Report")


            if (
                st.session_state.student_verified
                and st.session_state.student_result
            ):

                result = st.session_state.student_result

                student_row = [

                    {
                        "Test ID": "STUDENT-001",

                        "Original File":
                            st.session_state.student_reference_name,

                        "Received File":
                            file.name,

                        "Original CRC-32":
                            st.session_state.student_reference_crc,

                        "Received CRC-32":
                            result["received_crc"],

                        "Status":
                            "VALID"
                            if result["match"]
                            else "CORRUPTED",

                        "Timestamp":
                            result["time"]
                    }

                ]


                st.download_button(

                    "⬇️ Download Student CSV Report",

                    data=csv_bytes(student_row),

                    file_name="student_crc32_report.csv",

                    mime="text/csv",

                    use_container_width=True
                )

            else:

                st.info(
                    "Verify the current file first "
                    "to create a report."
                )


    else:

        st.info(
            "Upload a PDF, DOCX, or TXT assignment to begin."
        )


# ==========================================================
# LECTURER VIEW
# ==========================================================

else:

    st.subheader("👨‍🏫 Lecturer Integrity Console")

    st.write(
        "Compare original/reference assignments against "
        "received submissions and generate a verification report."
    )


    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            "### 📤 Original / Reference Files"
        )

        original_files = st.file_uploader(

            "Upload original files",

            type=["pdf", "docx", "txt"],

            accept_multiple_files=True,

            key="original_files"
        )


    with col2:

        st.markdown(
            "### 📥 Received / Submitted Files"
        )

        received_files = st.file_uploader(

            "Upload received files",

            type=["pdf", "docx", "txt"],

            accept_multiple_files=True,

            key="received_files"
        )


    original_count = (
        len(original_files)
        if original_files
        else 0
    )

    received_count = (
        len(received_files)
        if received_files
        else 0
    )

    pair_count = min(
        original_count,
        received_count
    )


    st.write("")


    m1, m2, m3 = st.columns(3)


    with m1:

        metric_card(
            "Original Files",
            original_count
        )


    with m2:

        metric_card(
            "Received Files",
            received_count
        )


    with m3:

        metric_card(
            "File Pairs",
            pair_count
        )


    if (
        original_count != received_count
        and (original_count > 0 or received_count > 0)
    ):

        st.warning(
            "The number of original and received files is different. "
            "Only files available in matching positions will be checked."
        )


    st.write("")


    if st.button(
        "🔍 Check CRC-32 Integrity",
        use_container_width=True
    ):

        if pair_count == 0:

            st.warning(
                "Upload at least one original file "
                "and one received file."
            )

        else:

            results = []


            for i in range(pair_count):

                original = original_files[i]

                received = received_files[i]


                original_data = original.getvalue()

                received_data = received.getvalue()


                original_crc = crc_hex(
                    original_data
                )

                received_crc = crc_hex(
                    received_data
                )


                match = (
                    original_crc
                    == received_crc
                )


                results.append(

                    {
                        "Test ID":
                            f"TEST-{i + 1:03d}",

                        "Original File":
                            original.name,

                        "Received File":
                            received.name,

                        "Original CRC-32":
                            original_crc,

                        "Received CRC-32":
                            received_crc,

                        "Status":
                            "VALID"
                            if match
                            else "CORRUPTED",

                        "Timestamp":
                            datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                    }

                )


            st.session_state.lecturer_results = results


    results = st.session_state.lecturer_results


    if results:

        valid_count = sum(

            1
            for row in results
            if row["Status"] == "VALID"

        )


        corrupted_count = (
            len(results)
            - valid_count
        )


        integrity_rate = (
            valid_count
            / len(results)
        ) * 100


        st.divider()

        st.subheader(
            "📊 Verification Summary"
        )


        a, b, c, d = st.columns(4)


        with a:

            metric_card(
                "Total Pairs",
                len(results)
            )


        with b:

            metric_card(
                "Valid Files",
                valid_count
            )


        with c:

            metric_card(
                "Corrupted Files",
                corrupted_count
            )


        with d:

            metric_card(
                "Integrity Rate",
                f"{integrity_rate:.1f}%"
            )


        if corrupted_count == 0:

            st.success(
                "🎉 All checked file pairs passed "
                "the CRC-32 integrity check."
            )

        else:

            st.error(
                f"⚠️ {corrupted_count} file pair(s) "
                "failed the CRC-32 integrity check."
            )


        st.divider()

        st.subheader(
            "📋 Detailed CRC-32 Results"
        )


        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True
        )


        st.divider()

        st.subheader(
            "📁 File-by-File Verification"
        )


        for row in results:

            if row["Status"] == "VALID":

                st.success(
                    f'{row["Test ID"]} — '
                    f'{row["Original File"]} → '
                    f'{row["Received File"]}: VALID'
                )

            else:

                st.error(
                    f'{row["Test ID"]} — '
                    f'{row["Original File"]} → '
                    f'{row["Received File"]}: CORRUPTED'
                )


        st.divider()

        st.subheader(
            "📄 Verification Report"
        )


        st.download_button(

            "⬇️ Download CRC-32 CSV Report",

            data=csv_bytes(results),

            file_name="crc32_verification_report.csv",

            mime="text/csv",

            use_container_width=True
        )


    else:

        st.info(
            "Upload your original/reference files "
            "and received files, then click "
            "Check CRC-32 Integrity."
        )
