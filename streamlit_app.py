import streamlit as st
import zlib

st.title("Student Assignment Integrity Checker")

file = st.file_uploader(
    "Upload Assignment",
    type=["pdf", "docx", "txt"]
)

if file:
    data = file.getvalue()

    original_crc = zlib.crc32(data)

    st.write("File Name:", file.name)
    st.write("Original CRC-32:", hex(original_crc))

    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if "corrupted" not in st.session_state:
        st.session_state.corrupted = False

    if st.button("Submit Assignment"):
        st.session_state.submitted = True
        st.session_state.corrupted = False

    if st.session_state.submitted:

        received_crc = zlib.crc32(data)

        st.write("Received CRC-32:", hex(received_crc))

        if original_crc == received_crc:
            st.success("CRC MATCHED - Assignment is valid.")
        else:
            st.error("CRC MISMATCH - Corruption detected.")

        if st.button("Simulate Corruption"):
            st.session_state.corrupted = True

        if st.session_state.corrupted:

            corrupted_data = bytearray(data)

            if len(corrupted_data) > 0:
                corrupted_data[0] ^= 1

            corrupted_crc = zlib.crc32(corrupted_data)

            st.write("Original CRC-32:", hex(original_crc))
            st.write("Corrupted CRC-32:", hex(corrupted_crc))

            if original_crc == corrupted_crc:
                st.success("CRC MATCHED")
            else:
                st.error("CRC MISMATCH - Corruption detected.")
