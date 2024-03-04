import streamlit as st

def main():
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    if "concatenated_text" not in st.session_state:
        st.session_state.concatenated_text = ""

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Files", "Feedback"], index=["Home", "Files", "Feedback"].index(st.session_state.page))

    if page == "Home":
        st.title("Home Page")

    elif page == "Files":
        st.title("Files Page")
        input_text_1 = st.text_input("Enter text 1:")
        input_text_2 = st.text_input("Enter text 2:")
        st.session_state.concatenated_text = input_text_1 + " " + input_text_2
        if st.button("Print concatenated text"):
            st.write("Concatenated Text:", st.session_state.concatenated_text)
            st.session_state.show_go_to_feedback_button = True
        if "show_go_to_feedback_button" in st.session_state and st.session_state.show_go_to_feedback_button:
            if st.button("Go to Feedback"):
                st.session_state.page = "Feedback"
                st.session_state.clicked_feedback_button = True
                st.experimental_rerun()

    elif page == "Feedback":
        st.title("Feedback Page")
        feedback_input_1 = st.text_input("Feedback 1:")
        feedback_input_2 = st.text_input("Feedback 2:")
        if "clicked_feedback_button" in st.session_state and st.session_state.clicked_feedback_button:
            feedback_input_3 = st.text_input("Feedback 3:", value=st.session_state.concatenated_text)
        else:
            feedback_input_3 = st.text_input("Feedback 3:")
            
if __name__ == "__main__":
    main()
