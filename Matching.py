
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Preprocessing_Parsing import ResumeProcessor

class Match:
    def jd_skill(self,jd):
        resume_processor = ResumeProcessor()
        resume_processor.load_skill_patterns("jz_skill_patterns.jsonl")
        jd_skills = resume_processor.extracting_entities(jd)["SKILL"]
        return jd_skills

    def find_not_in_resume(self,resume, jd):
        resume_processor = ResumeProcessor()
        resume_processor.load_skill_patterns("jz_skill_patterns.jsonl")
        # Extract Resume Skills
        resume_skills = resume_processor.extracting_entities(resume)["SKILL"]
        # Extracting Job Description Skills
        jd_skills = resume_processor.extracting_entities(jd)["SKILL"]
        return [skill for skill in jd_skills if skill not in resume_skills]

    def cal_cosine_similarity(self,resume, job_description, threshold=15):
        resume_processor = ResumeProcessor()  # Shrawani's Function
        resume_processor.load_skill_patterns("jz_skill_patterns.jsonl")
        resume_skills = resume_processor.extracting_entities(resume)["SKILL"]
        job_description_skills = resume_processor.extracting_entities(job_description)["SKILL"]
        # Combining resume_skills and job_description skills
        corpus = resume_skills + job_description_skills
        corpus = [word.replace(" ", "") for word in corpus]
        corpus = [" ".join(resume_skills), " ".join(job_description_skills)]
        # If job description skills not present in resume
        skills_not_in_resume = self.find_not_in_resume(resume, job_description)
        missing_skills = ", ".join(skills_not_in_resume)
        # creating a vectorizer
        vectorizer = TfidfVectorizer()
        vectorizer.fit_transform(corpus)
        # calculating cosine similarity
        resume_text, job_description_text = ", ".join(resume_skills), " ".join(job_description_skills)
        similarity = cosine_similarity(vectorizer.fit_transform([resume_text, job_description_text]))
        score = round(similarity[0][1] * 100, 2)
        missing_skill = dict(enumerate(skills_not_in_resume))
        return score, missing_skill