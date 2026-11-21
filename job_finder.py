import os

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from resume_analysis import detect_skills

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_FILE = os.path.join(BASE_DIR, "jobs.csv")


def find_jobs(resume_text, csv_path=JOBS_FILE, top_n=5):
    """Recommend jobs using skill overlap (70%) and text similarity (30%)."""

    jobs = pd.read_csv(csv_path, skip_blank_lines=True)
    jobs.columns = [c.strip() for c in jobs.columns]

    required_columns = ["Job_Title", "Required_Skills", "Job_Description"]

    for column in required_columns:
        if column not in jobs.columns:
            raise ValueError(f"Missing column in jobs.csv: {column}")

    jobs = jobs.dropna(subset=required_columns).reset_index(drop=True)

    if jobs.empty:
        return []

    for column in required_columns:
        jobs[column] = jobs[column].astype(str).str.strip()

    # --- Text similarity (TF-IDF) ---
    job_texts = (jobs["Required_Skills"] + " " + jobs["Job_Description"]).tolist()

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    vectors = vectorizer.fit_transform([resume_text] + job_texts)
    similarity = cosine_similarity(vectors[0:1], vectors[1:])[0] * 100

    # --- Skill overlap ---
    resume_skills = set(detect_skills(resume_text))

    results = []

    for i, job in jobs.iterrows():
        job_skills = detect_skills(job["Required_Skills"])
        matched = [s for s in job_skills if s in resume_skills]
        missing = [s for s in job_skills if s not in resume_skills]

        coverage = 100 * len(matched) / len(job_skills) if job_skills else 0
        score = 0.7 * coverage + 0.3 * min(100.0, float(similarity[i]) * 2)

        results.append({
            "title": job["Job_Title"],
            "skills": job["Required_Skills"],
            "description": job["Job_Description"],
            "matched": matched,
            "missing": missing,
            "match": round(score, 1),
        })

    results.sort(key=lambda r: r["match"], reverse=True)
    return results[:top_n]
