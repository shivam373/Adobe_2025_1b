import os
import json
from src.pdf_parser import extract_documents
from src.relevance_ranker import rank_sections
from src.json_formatter import build_final_output
import pdfplumber


input_dir = "data/input_docs"
persona_file = "data/persona.json"
output_file = "data/output.json"

# Load persona info
def load_persona_info(persona_file):
    with open(persona_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["metadata"]["persona"], data["metadata"]["job_to_be_done"]

persona, job = load_persona_info(persona_file)

# Extract documents and full text map
doc_sections = extract_documents(input_dir)

# Flatten all sections for ranking
all_sections = []
for doc in doc_sections:
    doc_name = doc["document"]
    for page in doc["pages"]:
        page_num = page["page"]
        for section in page["sections"]:
            all_sections.append({
                "document": doc_name,
                "page_number": page_num,
                "section_title": section.get("text"),
            })


# Rank them
rank_section = rank_sections(persona , job , all_sections , top_n= 15)

def refine_sections(ranked_sections, full_documents):
    refined_section = []

    for item in ranked_sections:
        doc_name = item["document"]
        page_num = item["page_number"]
        section_title = item["section_title"]

        # Get all sections on that page
        page_sections = []
        for doc in full_documents:
            if doc["document"] != doc_name:
                continue
            for page in doc["pages"]:
                if page["page"] == page_num:
                    page_sections = page.get("sections", [])
                    break

        # Find the top position of the current section
        current_top = None
        next_top = float("inf")
        for idx, sec in enumerate(page_sections):
            if sec["text"].strip().lower() == section_title.strip().lower():
                current_top = sec.get("top")
                if idx + 1 < len(page_sections):
                    next_top = page_sections[idx + 1].get("top", float("inf"))
                break

        # Extract paragraph between current_top and next_top
        paragraph = ""
        if current_top is not None:
            try:
                with pdfplumber.open(os.path.join(input_dir, doc_name)) as pdf:
                    page = pdf.pages[page_num - 1]
                    lines = []
                    for char_obj in page.extract_words(use_text_flow=True, keep_blank_chars=False):
                        word_top = float(char_obj["top"])
                        if current_top < word_top < next_top:
                            lines.append(char_obj["text"])
                    paragraph = " ".join(lines).strip()
            except Exception as e:
                print(f"[ERROR] Paragraph extraction failed for {doc_name} page {page_num}: {e}")
                paragraph = ""

        refined_section.append({
            "document": doc_name,
            "section_title": section_title,
            "page_number": page_num,
            "importance_rank": item["importance_rank"],
            "paragraph": paragraph
        })

    return refined_section


# # Refine them
refined_output= refine_sections(rank_section, doc_sections)

# # Save final output
input_documents = [doc["document"] for doc in doc_sections]
final_result = build_final_output(persona, job, input_documents, rank_section, refined_output)


with open(output_file, "w", encoding="utf-8") as f:
    json.dump(final_result, f, indent=4, ensure_ascii=False)

print("Pipeline complete! Output saved to:", output_file)


