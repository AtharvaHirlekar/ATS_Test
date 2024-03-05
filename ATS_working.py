import streamlit as st
from streamlit_option_menu import option_menu
import docx2txt
import os
import spacy
from spacy import displacy

from Base import BaseATS
from Preprocessing_Parsing import ResumeProcessor
from Matching import Match

Base_ATS = BaseATS()
Match_ATS = Match()

def main():
    # Get the absolute path of the currently executing Python script in Streamlit
    script_path = os.path.realpath(__file__)
    # Get the folder path from the script path
    folder_path = os.path.dirname(script_path)
    json_path = folder_path+"/JSON"

    if "choice" not in st.session_state:
        st.session_state.choice = "Home"

    if "missing_skills" not in st.session_state:
        st.session_state.missing_skills = ""

    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ['Home', 'Files', 'About'], index=['Home', 'Files', 'About'].index(st.session_state.choice))

    if choice=='Home':
        st.subheader('Welcome to the Applicant Tracking System (ATS)')
        st.title("Application Tracking System")

        intro = "Welcome to our Applicant Tracking System (ATS), a tool that makes hiring easier. Whether you're an employer or job seeker, our system simplifies the recruitment process. We use advanced natural language processing (NLP) to analyze resumes and job descriptions, offering valuable insights for better hiring decisions. Explore the features to streamline your recruitment journey."
        st.markdown(intro, unsafe_allow_html=True)

        st.subheader('Key Features')
        intro1 = 'File Upload: Easily upload resumes and job descriptions in various formats such as PDF, DOCX, and TXT. Text Processing: Extract and review the content of uploaded resumes and job descriptions with just a click. Analysis and Comparison: Identify common words between resumes and job descriptions, allowing for a quick match analysis.  ATS Functionality: Utilize advanced features such as keyword matching and scoring to efficiently assess candidate suitability.'
        st.markdown(intro1, unsafe_allow_html=True)

    elif choice =='Files':
        st.title('Resume And Job Description')
        # Initialize session_state
        if 'processed_resume' not in st.session_state:
            st.session_state.processed_resume = False
        if 'processed_job_description' not in st.session_state:
            st.session_state.processed_job_description = False
        # Upload Resume
        docx_file = st.file_uploader('Upload Resume', type=['pdf', 'docx', 'txt'])
        if st.button("Process Resume"):
            if docx_file is not None:
                file_details = {'filename': docx_file.name, 'filetype': docx_file.type, 'filesize': docx_file.size}
                st.write(file_details)
                if docx_file.type == 'text/plain':
                    st.session_state.raw_text = str(docx_file.read(), 'utf-8')
                    st.text(st.session_state.raw_text)
                elif docx_file.type == 'application/pdf':
                    save_path = Base_ATS.save_uploaded_file(docx_file, destination_path=folder_path)
                    st.session_state.raw_text = Base_ATS.read_pdf(docx_file)
                    st.text(st.session_state.raw_text)
                    st.session_state.resume_path = save_path
                    Base_ATS.delete_file(save_path)
                else:
                    st.session_state.raw_text = docx2txt.process(docx_file)
                    st.text(st.session_state.raw_text)

                st.session_state.processed_resume = True
                st.session_state.choice = "Home"

        # Upload Job Description
        docx_file1 = st.file_uploader('Upload Job Description', type=['pdf', 'docx', 'txt'])
        if st.button("Process Job Description"):
            if docx_file1 is not None:
                file_details = {'filename': docx_file1.name, 'filetype': docx_file1.type, 'filesize': docx_file1.size}
                st.write(file_details)
                if docx_file1.type == 'text/plain':
                    st.session_state.raw_text1 = str(docx_file1.read(), 'utf-8')
                    st.text(st.session_state.raw_text1)
                elif docx_file1.type == 'application/pdf':
                    save_path = Base_ATS.save_uploaded_file(docx_file1, destination_path=folder_path)
                    st.session_state.raw_text1 = Base_ATS.read_pdf(docx_file1)
                    st.text(st.session_state.raw_text1)
                    Base_ATS.delete_file(save_path)
                else:
                    st.session_state.raw_text1 = docx2txt.process(docx_file1)
                    st.text(st.session_state.raw_text1)

                st.session_state.processed_job_description = True
                st.session_state.choice = 'Home'

        st.header("Skill Relevance Overview")
        if st.button("Process"):
            # Check if both resume and job description are uploaded
            if st.session_state.processed_resume and st.session_state.processed_job_description:
                resume = st.session_state.raw_text
                jd = st.session_state.raw_text1
                resume_processor=ResumeProcessor()
                #resume_processor.load_skill_patterns("D:\Designing\Final_ATS\jz_skill_patterns.jsonl")
                resume_processor.load_skill_patterns("jz_skill_patterns.jsonl")
                remails = resume_processor.extract_emails(resume)
                rlinks = resume_processor.extract_links(resume)
                cleaned_resume = resume_processor.remove_links_and_emails(resume, rlinks, remails)
                cleaned_resume = resume_processor.preprocess_resume(cleaned_resume)
                jemails = resume_processor.extract_emails(jd)
                jlinks = resume_processor.extract_links(jd)
                cleaned_jd = resume_processor.remove_links_and_emails(jd, jlinks, jemails)
                cleaned_jd = resume_processor.preprocess_resume(cleaned_jd)
                st.subheader('Common Words between Resume and Job Description')
                common = Base_ATS.find_common_words_dict(cleaned_resume,cleaned_jd)  
                st.write(common)
                #skill_pattern="D:\\Designing\\Final_ATS\\jz_skill_patterns.jsonl"
                skill_pattern="jz_skill_patterns.jsonl"
                ner=spacy.load('en_core_web_lg')
                entity_ruler=ner.add_pipe("entity_ruler")
                entity_ruler.from_disk(skill_pattern)
                doc = ner(cleaned_resume)
                colors={
                        "SKILL": "linear-gradient(90deg, #9BE15D, #00E3AE)",
                        "ORG": "#ffd966",
                        "PERSON": "#e06666",
                        "GPE": "#9fc5e8",
                        "DATE": "#c27ba0",
                        "ORDINAL": "#674ea7"
                        }
                options={"ents": ["SKILL", "ORG", "PERSON", "GPE", "DATE", "ORDINAL"],"colors": colors,}
                html = displacy.render(doc, style="ent", options=options, page=False)
                st.subheader('Resume Analysis')
                st.markdown(html, unsafe_allow_html=True)
                labelled_entities=resume_processor.extracting_entities(doc)
                #st.markdown(json.dumps(labelled_entities,indent=2))
                #st.json(labelled_entities)
                resume_name = docx_file.name
                jd_name = docx_file1.name
                resume_name = resume_name.split('.')[0].strip()
                resume_name = resume_name + ".json"
                #st.write(resume_name)
                Base_ATS.save_json_file(labelled_entities, json_path, resume_name)
                st.write('')
                st.subheader('Skills in Job Description')
                jd_skills = Match_ATS.jd_skill(cleaned_jd)
                st.write(jd_skills)

                st.write('')
                resume_name = docx_file.name
                jd_name = docx_file1.name
                score, missing_skill = Match_ATS.cal_cosine_similarity(cleaned_resume, cleaned_jd)

                st.subheader('Match Results for Resume and Job Description')
                st.session_state.choice = 'Home'
                if score >= 50:  # Adjust threshold as needed
                    st.write(f"<h5><b><span style='color: #fd971f;'>{os.path.basename(resume_name)} is Recommended for {os.path.basename(jd_name)}</span></b></h5>", unsafe_allow_html=True)
                    st.write(f"<h5><b><span style='color: #fd971f;'>Score: {score}</span></b></h5>", unsafe_allow_html=True)
                else:
                    st.write(f"<h5><b><span style='color: #fd971f;'>{os.path.basename(resume_name)} is Not Recommended for {os.path.basename(jd_name)}</span></b></h5>", unsafe_allow_html=True)
                    st.write(f"<h5><b><span style='color: #fd971f;'>Score: {score}</span></b></h5>", unsafe_allow_html=True)
                if missing_skill:
                    st.subheader('Missing Skills')
                    st.write(missing_skill)
                    
                    st.session_state.missing_skills = missing_skill
                    st.session_state.show_go_to_feedback_button = True
                    
                    # if "show_go_to_feedback_button" in st.session_state and st.session_state.show_go_to_feedback_button:
                    #     if st.button("About"):
                    #         st.write("GG")
                    #         st.session_state.choice = 'About'
                    #         st.session_state.clicked_feedback_button = True
                    #         st.experimental_rerun()
                    
                    st.write("GG")
                    st.session_state.choice = 'About'
                    st.session_state.clicked_feedback_button = True
                    st.experimental_rerun()
            else:
                st.warning("Please upload both Resume and Job Description before using ATS")
        
    elif choice =='About':
        st.title("About")
        st.text('An NLP Project by ')
        st.subheader('Feedback')
        # Get user input
        recipient_email = st.text_input("Recipient Email:")
        subject = st.text_input("Subject:")
        if "clicked_feedback_button" in st.session_state and st.session_state.clicked_feedback_button:
            message = st.text_area("Message:",value=st.session_state.missing_skills)
        else:
            message = st.text_area("Message:")
        # Button to send email
        if st.button("Send Email"):
            if not recipient_email or not subject or not message:
                st.warning("Please fill in all the fields.")
            else:
                try:
                    Base_ATS.send_email(subject, message, recipient_email)
                    st.success(f"Email sent successfully to {recipient_email}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
