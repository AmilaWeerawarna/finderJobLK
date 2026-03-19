from src.database.mongo import db

# Database එක fail වුනොත් හෝ හිස් නම් පාවිච්චි වෙන Fallback List එක
FALLBACK_SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript",
    "sql", "mysql", "postgresql", "mongodb", "react", "angular", "vue",
    "node.js", "express", "spring boot", "django", "flask", "fastapi",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "git",
    "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "excel", "power bi", "tableau", "accounting", "finance", "auditing",
    "communication", "leadership", "teamwork", "problem solving",
    "html", "css", "bootstrap", "tailwind"
]

class SkillService:
    def __init__(self):
        self.col = db["skills"] if db is not None else None

    def get_all_skills(self) -> list:
        skills = set(FALLBACK_SKILLS)
        try:
            if self.col is not None:
                db_skills = self.col.find({}, {"name": 1})
                for doc in db_skills:
                    if "name" in doc:
                        skills.add(doc["name"].lower().strip())
        except Exception as e:
            print(f"Error fetching skills from DB: {e}")
        
        return list(skills)