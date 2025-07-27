import json
import re
from datetime import datetime

# Load persona and job-to-be-done from a JSON file
def load_persona_info(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("persona", ""), data.get("job_to_be_done", "")

# Extract keywords and focus areas from persona and job description
def extract_focus_areas(persona, job):
    combined = f"{persona} {job}".lower()

    # Simple keyword extraction using regex and basic heuristics
    keywords = re.findall(r"\b[a-zA-Z]{4,}\b", combined)
    
    # Remove common stopwords (can be extended)
    stopwords = set([
        "with", "from", "that", "this", "these", "those", "their", "will",
        "need", "needs", "task", "focus", "given", "prepare", "summary", "review",
        "based", "provide", "identify", "should", "which", "about", "what",
    ])
    filtered = [word for word in keywords if word not in stopwords]

    return list(set(filtered))  # remove duplicates

# Add a timestamp for metadata
def get_timestamp():
    return datetime.utcnow().isoformat() + "Z"

if __name__ == "__main__":
    persona, job = load_persona_info("data/persona.json")
    focus_terms = extract_focus_areas(persona, job)
    print("Persona:", persona)
    print("Job:", job)
    print("Focus terms:", focus_terms)
