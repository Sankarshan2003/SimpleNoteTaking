import streamlit as st
import requests

API_URL = "http://backend:8080"

st.title("📝 Note taking")

username = st.text_input("Enter your username:")

if username:
    response = requests.get(f"{API_URL}/notes/{username}")
    if response.status_code == 200:
        notes = response.json()["notes"]
    else:
        notes = []
        st.warning("No notes found for this user.")

    st.header("Your Notes")
    for note in notes:
        st.markdown(f"**Note {note['id']}:** {note['note']}")
        if st.button(f"Delete Note {note['id']}", key=f"delete_{note['id']}"):
            response = requests.delete(f"{API_URL}/notes/{username}/{note['id']}")
            if response.status_code == 200:
                st.success("Note deleted successfully!")
                st.rerun()

    st.sidebar.header("Add a New Note")
    new_note = st.sidebar.text_area("Write your note here:")
    if st.sidebar.button("Add Note"):
        if new_note.strip():
            response = requests.post(
                f"{API_URL}/notes",
                json={"username": username, "note": new_note.strip()},
            )
            print(response)
            if response.status_code == 200:
                st.sidebar.success("Note added successfully!")
                st.rerun()
            else:
                st.sidebar.error("Error adding note.")
        else:
            st.sidebar.error("Please write something before adding.")
