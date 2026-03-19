import os
import sys
from pymongo import UpdateOne


sys.path.append(os.path.dirname(os.path.abspath(__file__)))


try:
    from src.database.mongo import db
except ImportError:
    print("Error: 'src.database.mongo' not found.")
    db = None


SKILLS_BY_CATEGORY = {
    "IT & Software": [
        "python", "java", "javascript", "typescript", "c#", "php", "go", "rust", "kotlin", "swift",
        "react", "angular", "vue.js", "node.js", "next.js", "django", "laravel", "spring boot",
        "mysql", "postgresql", "mongodb", "redis", "docker", "kubernetes", "aws", "azure", "gcp",
        "html5", "css3", "tailwind css", "rest api", "graphql", "microservices", "unit testing",
        "git", "ci/cd", "agile", "scrum", "ui/ux design", "figma", "adobe xd", "cybersecurity",
        "machine learning", "data science", "nlp", "flutter", "react native", "software architecture"
    ],
    "Education & Teaching": [
        "lesson planning", "classroom management", "curriculum development", "student assessment",
        "educational technology", "online teaching", "child psychology", "special education",
        "subject expertise", "lecturing", "mentoring", "academic research", "public speaking",
        "creative teaching", "early childhood education", "stem education", "tefl", "tesl",
        "educational leadership", "parent-teacher communication", "google classroom", "moodle",
        "zoom for teaching", "vocational training", "exam preparation", "student counseling",
        "record keeping", "time management", "adaptability", "collaborative learning", "literacy instruction"
    ],
    "Banking & Finance": [
        "financial analysis", "risk management", "investment banking", "wealth management",
        "corporate finance", "credit analysis", "banking operations", "retail banking", "aml", "kyc",
        "financial modeling", "derivatives", "portfolio management", "treasury management", "fintech",
        "digital banking", "loan processing", "debt recovery", "insurance", "actuarial science",
        "capital markets", "asset management", "swift transfers", "core banking systems",
        "regulatory compliance", "financial reporting", "crm", "business development", "auditing"
    ],
    "Healthcare & Medical": [
        "clinical expertise", "patient care", "medical diagnosis", "nursing care", "first aid", "cpr",
        "medical records management", "pharmacology", "surgery", "radiography", "laboratory testing",
        "phlebotomy", "emergency care", "critical care", "public health", "telehealth", "anatomy",
        "medical ethics", "patient education", "infection control", "ehr software", "medical equipment",
        "dentistry", "physiotherapy", "nutrition", "mental health support", "midwifery", "pediatric care"
    ],
    "Engineering": [
        "civil engineering", "mechanical engineering", "electrical engineering", "electronic engineering",
        "structural analysis", "autocad", "solidworks", "project engineering", "site management",
        "hvac", "quantity surveying", "bridge construction", "road construction", "telecommunications",
        "robotics", "automation", "quality control", "safety management", "renewable energy",
        "power systems", "fluid mechanics", "thermodynamics", "surveying", "estimation", "troubleshooting"
    ],
    "Sales & Marketing": [
        "digital marketing", "seo", "sem", "social media marketing", "content marketing", "email marketing",
        "brand management", "market research", "public relations", "event planning", "sales strategy",
        "b2b sales", "b2c sales", "lead generation", "customer acquisition", "salesforce", "hubspot",
        "negotiation", "networking", "telemarketing", "copywriting", "graphic design", "influencer marketing",
        "data-driven marketing", "pricing strategy", "e-commerce", "presentation skills", "closing deals"
    ],
    "Accounting & Audit": [
        "bookkeeping", "financial accounting", "management accounting", "cost accounting", "auditing",
        "taxation", "vat compliance", "tax returns", "financial statements", "payroll management",
        "reconciliations", "accounts payable", "accounts receivable", "fixed assets", "budgeting",
        "forecasting", "ifrs", "slfrs", "quickbooks", "tally", "sage", "xero", "erp sap", "internal controls",
        "risk assessment", "excel for finance", "statutory audit", "compliance"
    ],
    "Tourism & Hospitality": [
        "hotel management", "front office", "housekeeping", "food and beverage", "culinary arts", "chef",
        "waiter service", "tourism management", "tour guiding", "ticketing", "amadeus", "travel planning",
        "event management", "concierge", "guest relations", "ecotourism", "sustainable tourism",
        "barista skills", "mixology", "food safety haccp", "resort management", "spa management",
        "multilingualism", "customer experience", "hospitality software"
    ],
    "Manufacturing & Operations": [
        "production planning", "lean manufacturing", "six sigma", "quality assurance", "supply chain",
        "inventory control", "factory management", "process optimization", "health and safety",
        "machinery maintenance", "warehouse management", "procurement", "operational excellence",
        "assembly line", "logistics coordination", "iso standards", "industrial engineering",
        "vendor management", "cost reduction", "troubleshooting", "erp systems", "change management"
    ],
    "Apparel & Textiles": [
        "garment construction", "pattern making", "sewing", "cutting room management", "textile science",
        "fashion design", "merchandising", "fabric sourcing", "quality control apparel", "lean apparel",
        "production tracking", "industrial engineering apparel", "fashion illustration", "cad for textiles",
        "embroidery", "printing screen digital", "dyeing", "finishing", "smv calculation",
        "compliance wrap bsci", "export procedures", "gsd", "sampling", "trims and accessories"
    ],
    "Admin & Secretarial": [
        "office management", "secretarial duties", "receptionist skills", "typing", "transcription",
        "document control", "filing systems", "data entry", "correspondence", "scheduling",
        "meeting coordination", "travel arrangements", "calendar management", "office equipment",
        "minute taking", "procurement admin", "facility management", "ms office", "front desk",
        "professionalism", "confidentiality"
    ],
    "Human Resources": [
        "recruitment", "talent acquisition", "employee onboarding", "payroll administration",
        "hr policy development", "employee relations", "performance management", "training development",
        "compensation benefits", "labor law sri lanka", "epf etf handling", "conflict resolution",
        "employee engagement", "succession planning", "hris", "workforce planning", "interviewing skills",
        "grievance handling", "organizational culture", "disciplinary procedures", "staff welfare"
    ],
    "Logistics & Supply Chain": [
        "shipping freight forwarding", "warehouse operations", "inventory management", "supply chain optimization",
        "procurement", "sourcing", "import export documentation", "customs clearance", "transport management",
        "fleet management", "3pl 4pl", "route planning", "cold chain logistics", "distribution management",
        "demand forecasting", "supplier relationship management", "logistical analysis", "contract negotiation"
    ],
    "Construction & Architecture": [
        "architectural design", "urban planning", "landscape architecture", "interior design", "bim",
        "revit", "autocad 3d", "3d rendering", "sketchup", "construction management", "site supervision",
        "structural engineering construction", "quantity surveying qs", "cost estimation construction",
        "contract management fidic", "safety supervision", "civil works", "plumbing design", "electrical layouts"
    ],
    "Freelance & Creative": [
        "graphic design", "logo design", "content writing", "copywriting", "creative writing",
        "blog writing", "translation sinhala tamil english", "video editing", "adobe premiere pro",
        "after effects", "motion graphics", "illustration", "photoshop", "illustrator", "indesign",
        "figma creative", "photography", "videography", "voiceover", "social media management freelance",
        "ghostwriting", "proofreading", "brand identity", "portfolio management creative"
    ],
    "Customer Service / BPO": [
        "call center operations", "inbound outbound sales", "customer support", "tech support",
        "data entry bpo", "back office support", "chat support", "email support", "complaint handling",
        "telemarketing bpo", "crm proficiency", "empathy", "active listening", "conflict management bpo",
        "typing speed", "language proficiency", "time management bpo", "quality monitoring",
        "escalation handling"
    ],
    "Agriculture & Plantation": [
        "crop management", "soil science", "irrigation management", "pest control", "fertilizer application",
        "tea plantation management", "rubber harvesting", "coconut cultivation", "modern farming",
        "hydroponics", "greenhouse management", "agricultural machinery", "farm management",
        "livestock management", "poultry farming", "organic farming", "agribusiness", "food processing",
        "sustainable agriculture", "harvest planning", "plantation labor management"
    ],
    "Media & Communication": [
        "journalism", "news reporting", "scriptwriting", "broadcasting", "radio hosting", "tv production",
        "public relations pr", "mass communication", "media ethics", "photojournalism",
        "social media strategy media", "media planning", "interviewing media", "press release writing",
        "multimedia storytelling", "podcasting", "anchoring", "sub editing", "investigative journalism"
    ],
    "Legal": [
        "legal research", "litigation", "corporate law", "drafting contracts", "conveyancing",
        "intellectual property", "criminal law", "civil law", "family law", "employment law",
        "notarial work", "court procedures", "legal advice", "client counseling", "mediation",
        "arbitration", "compliance legal", "document review", "case management", "commercial law"
    ],
    "Government Sector": [
        "public administration", "policy analysis", "governance", "public finance", "community development",
        "local government", "regulatory affairs", "public relations government", "record management govt",
        "statistical analysis", "crisis management govt", "project coordination state", "protocol etiquette",
        "state budgeting", "procurement government", "public welfare", "legislative support"
    ]
}

def seed_skills_to_db():
    if db is None:
        print("❌ Error: MongoDB connection failed.")
        return

    collection = db["skills"]
    all_skills = []
    
    for category, skills in SKILLS_BY_CATEGORY.items():
        all_skills.extend(skills)

    unique_skills = list(set([s.lower().strip() for s in all_skills]))
    
    operations = []
    print(f"Preparing to seed {len(unique_skills)} unique skills...")

    for skill in unique_skills:
        operations.append(
            UpdateOne(
                {"name": skill},
                {"$set": {"name": skill}},
                upsert=True
            )
        )

    if operations:
        try:
            result = collection.bulk_write(operations)
            print("Database Seeding Completed Successfully!")
            print(f"   - Total Skills Processed: {len(unique_skills)}")
            print(f"   - Newly Inserted: {result.upserted_count}")
            print(f"   - Already Existed: {result.matched_count}")
        except Exception as e:
            print(f"Error while writing to DB: {e}")

if __name__ == "__main__":
    seed_skills_to_db()