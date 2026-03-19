from __future__ import annotations
import numpy as np

from src.repositories.job_post_repository import JobPostRepository
from src.utils.deep_embedder import DeepEmbedder
from src.utils.pdf_extractor import extract_text_from_pdf
from src.utils.pyparser import parse_profile
from src.services.skill_service import SkillService

import torch
import re
import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import util


nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

def cosine_scores(query_emb: np.ndarray, job_embs: np.ndarray) -> np.ndarray:
    return job_embs @ query_emb

class DeepMatchService:
    def __init__(self):
        self.repo = JobPostRepository()
        self.embedder = DeepEmbedder()
        self.skill_service = SkillService()

    def match(self, cv_pdf_path: str, top_k: int = 10):
        job_posts = self.repo.get_all_job_posts(limit=5000)
        if not job_posts:
            return {"skills": [], "education": [], "experience": []}, [], {"job_posts_fetched": 0}

        cv_text = extract_text_from_pdf(cv_pdf_path)
        
        known_skills = self.skill_service.get_all_skills()

        profile = parse_profile(cv_text=cv_text, query_text="", known_skills=known_skills)

        user_text = "\n".join([
            cv_text or "",
            "Skills: " + ", ".join(profile.skills),
            "Education: " + ", ".join(profile.education),
            "Experience: " + ", ".join(profile.experience) 
        ]).strip()

        user_emb = self.embedder.encode_long_text(user_text)  # shape (D,)

        usable_jobs = []
        job_embs = []

        for j in job_posts:
            emb = j.get("embedding")
            if isinstance(emb, list) and len(emb) > 0:
                usable_jobs.append(j)
                job_embs.append(emb)

        meta = {
            "job_posts_fetched": len(job_posts),
            "jobs_with_embeddings": len(usable_jobs),
            "cv_text_length": len(cv_text or "")
        }

        if not usable_jobs:
            return {"skills": profile.skills, "education": profile.education, "experience": profile.experience}, [], meta

        job_embs = np.array(job_embs, dtype=np.float32)

        sims = cosine_scores(user_emb, job_embs)
        top_idx = np.argsort(-sims)[:top_k]

        results = []
        for rank_i in top_idx:
            job = usable_jobs[int(rank_i)]
            score = float(sims[int(rank_i)])
            score_100 = round(((score + 1) / 2) * 100, 2)

            results.append({
                "job_id": str(job.get("_id", "")),
                "job_title": job.get("job_title") or "Untitled",
                "company_name": job.get("company_name") or "Unknown Company",
                "location": job.get("location") or "Not Specified",
                "salary": job.get("salary") or "Not Specified",
                "employment_type": job.get("employment_type") or "Not Specified",
                "category": job.get("category") or "",
                "end_date": job.get("end_date") or "",
                "job_image": job.get("job_image") or "", 
                "score": score_100,
            })


        return {
            "skills": profile.skills, 
            "education": profile.education, 
            "experience": profile.experience
        }, results, meta

    def analyze_cv_vs_job(self, job_dict, cv_text, extracted_skills, extracted_education, extracted_experience=None):
        
        if extracted_experience is None:
            extracted_experience = []


        qualifications = re.sub(r'<[^>]+>', '\n', str(job_dict.get('skills', '')))
        requirements = re.sub(r'<[^>]+>', '\n', str(job_dict.get('job_requirement', '')))
        

        experience_req = re.sub(r'<[^>]+>', '\n', str(job_dict.get('experience', ''))) 
        
        combined_text = qualifications + "\n" + requirements + "\n" + experience_req
        
        raw_skills = []
        for line in combined_text.split('\n'):
            cleaned_line = re.sub(r'^[-*•]\s*', '', line).strip()
            if len(cleaned_line) > 5 and cleaned_line.lower() != 'na':
                raw_skills.append(cleaned_line)
                
        required_skills = [s.lower() for s in raw_skills if s.strip()]
        
        if not required_skills:
            return {"match_percentage": 0, "matching_skills": [], "missing_skills": []}


        cv_chunks = []
        if cv_text:
            for line in cv_text.split('\n'):
                line = line.strip()
                if len(line) > 5:
                    cv_chunks.extend(sent_tokenize(line.lower()))
                    

        cv_chunks.extend([s.lower() for s in extracted_skills])
        cv_chunks.extend([e.lower() for e in extracted_education])
        cv_chunks.extend([exp.lower() for exp in extracted_experience]) # 🟢 නව වෙනස

        if not cv_chunks:
            return {"match_percentage": 0, "matching_skills": [], "missing_skills": []}

        cv_embeddings = self.embedder.model.encode(cv_chunks, convert_to_tensor=True)
        skill_embeddings = self.embedder.model.encode(required_skills, convert_to_tensor=True)


        cosine_scores = util.cos_sim(skill_embeddings, cv_embeddings)
        
        threshold = 0.50  
        matching_skills = []
        missing_skills = []

        for i, skill in enumerate(required_skills):
            max_score = torch.max(cosine_scores[i]).item()
            if max_score >= threshold:
                matching_skills.append(skill)
            else:
                missing_skills.append(skill)

        match_percentage = (len(matching_skills) / len(required_skills)) * 100 if required_skills else 0

        return {
            "match_percentage": round(match_percentage, 2),
            "matching_skills": matching_skills,
            "missing_skills": missing_skills
        }