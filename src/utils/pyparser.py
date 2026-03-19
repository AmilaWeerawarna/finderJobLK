import spacy
from spacy.matcher import PhraseMatcher
import re
from dataclasses import dataclass
from typing import Iterable, List, Set

# Load the spaCy model (this may take a moment to load into memory)
nlp = spacy.load("en_core_web_md")

@dataclass
class ParsedProfile:
    skills: List[str]
    education: List[str]
    experience: List[str]

def extract_skills_spacy(doc, known_skills: Iterable[str]) -> List[str]:
    """Extract skills quickly and accurately using spaCy PhraseMatcher"""
    if not known_skills:
        return []
        
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    
    # Convert all skills from the database into spaCy patterns
    patterns = [nlp.make_doc(skill) for skill in known_skills if skill.strip()]
    matcher.add("SKILLS", patterns)

    matches = matcher(doc)
    extracted_skills = set()
    for match_id, start, end in matches:
        span = doc[start:end]
        extracted_skills.add(span.text.lower())
        
    return sorted(list(extracted_skills))

def extract_education_spacy(doc) -> List[str]:
    """Identify universities and institutions (ORG) using NER"""
    education = set()
    
    # Base keywords for degrees (improved version of the previous method)
    degree_keywords = ["bsc", "msc", "phd", "degree", "diploma", "bachelor", "master", "certificate", "hnd"]
    
    # Check sentence by sentence
    for sent in doc.sents:
        sent_text = sent.text.lower()
        if any(deg in sent_text for deg in degree_keywords):
            # Check if there is an organization (ORG) in this sentence
            orgs = [ent.text for ent in sent.ents if ent.label_ == "ORG"]
            if orgs:
                # Combine the degree and the university/institution
                clean_text = re.sub(r'\s+', ' ', sent.text).strip()
                education.add(clean_text)
                
    return sorted(list(education))

def extract_experience_spacy(doc) -> List[str]:
    """Extract experience by identifying dates (DATE) and organizations (ORG) using NER"""
    experience = set()
    exp_keywords = ["experience", "worked", "developer", "engineer", "manager", "intern", "role"]

    for sent in doc.sents:
        sent_text = sent.text.lower()
        
        # Check if the sentence contains experience-related keywords and dates (e.g., "2020", "Jan 2019 - Present")
        if any(kw in sent_text for kw in exp_keywords):
            has_date = any(ent.label_ == "DATE" for ent in sent.ents)
            if has_date:
                clean_text = re.sub(r'\s+', ' ', sent.text).strip()
                # Skip sentences related to education
                if not any(deg in sent_text for deg in ["university", "degree", "bsc"]):
                    experience.add(clean_text)

    return sorted(list(experience))

def parse_profile(cv_text: str, query_text: str, known_skills: Iterable[str]) -> ParsedProfile:
    combined_text = f"{cv_text}\n{query_text}"
    
    # Process the entire text through spaCy at once (efficient)
    doc = nlp(combined_text)

    skills = extract_skills_spacy(doc, known_skills)
    education = extract_education_spacy(doc)
    experience = extract_experience_spacy(doc)

    return ParsedProfile(skills=skills, education=education, experience=experience)