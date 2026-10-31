 
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def find_jobs(resume_text, csv_path="jobs.csv", top_n=5):
    """Recommend jobs based on resume and job description similarity."""

    jobs = pd.read_csv(csv_path)

    required_columns = [
        "Job_Title",
        "Required_Skills",
        "Job_Description"
    ]

    for column in required_columns:
        if column not in jobs.columns:
            raise ValueError(
                f"Missing column in jobs.csv: {column}"
            )

    jobs = jobs.dropna(subset=required_columns).copy()

    if jobs.empty:
        return []

    jobs["Job_Title"] = jobs["Job_Title"].astype(str)
    jobs["Required_Skills"] = jobs["Required_Skills"].astype(str)
    jobs["Job_Description"] = jobs["Job_Description"].astype(str)

    job_texts = (
        jobs["Required_Skills"] + " " +
        jobs["Job_Description"]
    ).tolist()

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    all_texts = [resume_text] + job_texts
    vectors = vectorizer.fit_transform(all_texts)

    resume_vector = vectors[0:1]
    job_vectors = vectors[1:]

    similarities = cosine_similarity(
        resume_vector,
        job_vectors
    )[0]

    jobs["Match_Percentage"] = similarities * 100

    jobs = jobs.sort_values(
        by="Match_Percentage",
        ascending=False
    )

    results = []

    for _, job in jobs.head(top_n).iterrows():
        results.append({
            "title": job["Job_Title"],
            "skills": job["Required_Skills"],
            "description": job["Job_Description"],
            "match": round(float(job["Match_Percentage"]), 2)
        })

    return results