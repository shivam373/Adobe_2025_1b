from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util

# Setup
# nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
model = SentenceTransformer('all-MiniLM-L6-v2')  # Efficient semantic model

def remove_stopwords(text):
    return ' '.join([word for word in text.split() if word.lower() not in stop_words])

def is_valid_title(title):
    # Filters out titles that are too short or generic
    return len(title.split()) > 2 and title.strip().lower() not in ["conclusion", "index", "references" , "introduction"]

def rank_sections(persona, job_to_be_done, sections, top_n=10, remove_stops=True):
    query = f"{persona}: {job_to_be_done}"
    if remove_stops:
        query = remove_stopwords(query)

    query_embedding = model.encode(query, convert_to_tensor=True)

    scored_sections = []
    seen_titles = set()

    for section in sections:
        raw_title = section.get("section_title")
        if not raw_title or not is_valid_title(raw_title):
            continue

        title_key = raw_title.strip().lower()
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)

        processed_title = remove_stopwords(raw_title) if remove_stops else raw_title
        title_embedding = model.encode(processed_title, convert_to_tensor=True)
        score = util.cos_sim(query_embedding, title_embedding).item()

        scored_sections.append({
            "document": section.get("document"),
            "section_title": raw_title,
            "page_number": section.get("page_number"),
            "score": score
        })

    scored_sections.sort(key=lambda x: x["score"], reverse=True)

    output = []
    for i, section in enumerate(scored_sections[:top_n]):
        output.append({
            "document": section["document"],
            "section_title": section["section_title"],
            "page_number": section["page_number"],
            "importance_rank": i + 1
        })

    return output




