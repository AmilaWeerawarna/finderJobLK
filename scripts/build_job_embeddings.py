import sys
import os
import re

# Add the project root to the PYTHONPATH to ensure absolute imports work correctly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from typing import Any, Dict, List
from src.database.mongo import db
from config import Config
from src.utils.deep_embedder import DeepEmbedder


def clean_html(raw_html: str) -> str:
    """Removes HTML tags and extra spaces from the provided text."""
    if not raw_html:
        return ""
        
    # Strip out HTML tags (e.g., <ul>, <li>, <p>)
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', str(raw_html))
    
    # Remove any excessive whitespace or newlines
    return re.sub(r'\s+', ' ', cleantext).strip()


def job_to_text(job: Dict[str, Any]) -> str:
    """Extracts and concatenates relevant fields from a job document into a single string."""
    # Using the correct keys based on the actual MongoDB document structure
    keys_to_extract = [
        "job_title",
        "company_name",
        "category",
        "location",
        "employment_type",
        "skills",
        "job_requirement",
        "job_duties"
    ]
    
    parts = []
    for k in keys_to_extract:
        v = job.get(k)
        if v:
            # Clean HTML tags and append the text
            parts.append(clean_html(v))
            
    # Join all extracted text parts with a single space
    return " ".join(parts).strip()


def main():
    # Access the job posts collection
    col = db[Config.JOB_POSTS_COLLECTION]
    jobs = list(col.find({}).limit(5000))  # Adjust the limit based on your requirement

    if not jobs:
        print("No job posts found in the collection.")
        return

    print("Loading AI Model...")
    embedder = DeepEmbedder()
    
    # Prepare the text for each job post
    texts = [job_to_text(j) for j in jobs]
    texts = [t if t.strip() else " " for t in texts]

    print(f"Generating embeddings for {len(jobs)} jobs...")
    
    # Generate the vector embeddings
    embs = embedder.encode(texts)

    print("Saving embeddings to the database...")
    
    # Update each job document in the database with its corresponding embedding array
    for job, emb in zip(jobs, embs):
        col.update_one(
            {"_id": job["_id"]},
            {"$set": {"embedding": emb.tolist()}}
        )

    print(f"Successfully updated {len(jobs)} job posts with embeddings.")

if __name__ == "__main__":
    main()