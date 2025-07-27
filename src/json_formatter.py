from datetime import datetime
import datetime

def build_final_output(persona, job_to_be_done, input_documents, ranked_sections, paragraph_results):
    # Get timestamp
    timestamp = datetime.datetime.now().isoformat()

    # Build extracted_sections
    extracted_sections = []
    seen_titles = set()
    for section in ranked_sections:
        key = (section["document"], section["section_title"])
        if key in seen_titles:
            continue
        seen_titles.add(key)

        extracted_sections.append({
            "document": section["document"],
            "section_title": section["section_title"],
            "importance_rank": section["importance_rank"],
            "page_number": section["page_number"]
        })

    # Build subsection_analysis
    subsection_analysis = []
    for para in paragraph_results:
        subsection_analysis.append({
            "document": para["document"],
            "refined_text": para["paragraph"],
            "page_number": para["page_number"]
        })

    # Build metadata
    metadata = {
        "input_documents": input_documents,
        "persona": persona,
        "job_to_be_done": job_to_be_done,
        "processing_timestamp": timestamp
    }

    return {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }
