import os
import platform
import pdfplumber
from collections import defaultdict
from pdf2image import convert_from_path
import pytesseract
from src.utils import is_bold, extract_font_family, clean_line_text, split_on_large_gaps, reconstruct_text, merge_similar_headings

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"models\\Tesseract-OCR\\tesseract.exe"
    poppler_path = r"additional_requirements\\poppler-24.08.0\\Library\\bin"
else:
    poppler_path = None

def ocr_extract_headings(img, page_num):
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    words = []
    for i in range(len(ocr_data['text'])):
        text = ocr_data['text'][i].strip()
        if text:
            x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
            words.append({
                'text': text,
                'left': x,
                'top': y,
                'right': x + w,
                'bottom': y + h,
                'height': h,
                'font_size': h
            })

    def group_by_line(words, y_thresh=200, font_size_thresh=7):
        words.sort(key=lambda w: (w['top'], w['left']))
        lines, current = [], []
        for word in words:
            if not current:
                current.append(word)
            else:
                last = current[-1]
                same_line = abs(word['top'] - last['top']) <= y_thresh
                font_size_close = abs(word['font_size'] - last['font_size']) < font_size_thresh
                if same_line and font_size_close:
                    current.append(word)
                else:
                    lines.append(current)
                    current = [word]
        if current:
            lines.append(current)
        return lines

    headings = []
    lines = group_by_line(words)
    for line_words in lines:
        line_words.sort(key=lambda w: w['left'])
        line_text = " ".join(w['text'] for w in line_words)
        cleaned_text = clean_line_text(line_text)
        if not cleaned_text or len(cleaned_text.split()) > 12:
            continue
        avg_font_size = sum(w['font_size'] for w in line_words) / len(line_words)
        top = line_words[0]['top']
        height = line_words[0]['height']
        headings.append({
            'text': cleaned_text,
            'font_size': avg_font_size,
            'style': 'bold',
            'font_family': 'Unknown',
            'top': top,
            'height': height,
            'page': page_num,
            'source': 'ocr'
        })
    return headings


def extract_documents(path):
    document_data = []

    if os.path.isdir(path):
        pdf_files = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.pdf')]
    else:
        pdf_files = [path]

    for filepath in pdf_files:
        filename = os.path.basename(filepath)
        doc_info = {"document": filename, "pages": []}

        with pdfplumber.open(filepath) as pdf:
            images = convert_from_path(filepath, dpi=300, poppler_path=poppler_path)

            for page_num, page in enumerate(pdf.pages, start=1):
                line_map = defaultdict(list)
                has_text = bool(page.chars)
                chars_count = len(page.chars) if page.chars else 0

                if not has_text or chars_count < 10:
                    try:
                        ocr_headings = ocr_extract_headings(images[page_num - 1], page_num)
                        doc_info["pages"].append({"page": page_num, "sections": ocr_headings})
                    except Exception as e:
                        print(f"[ERROR] OCR failed for page {page_num} in {filename}: {e}")
                        doc_info["pages"].append({"page": page_num, "sections": []})
                    continue

                for char in page.chars:
                    text = char.get("text", "").strip()
                    if not text:
                        continue
                    font_size = round(char.get("size", 2), 2)
                    font_name = char.get("fontname", "")
                    font_family = extract_font_family(font_name)
                    weight = "bold" if is_bold(font_name) else "regular"
                    top = round(char["top"], 1)
                    height = round(char["height"], 1)
                    x0, x1 = char["x0"], char["x1"]
                    line_map[top].append({
                        "x0": x0, "x1": x1, "text": text,
                        "weight": weight, "font_size": font_size,
                        "font_family": font_family, "top": top, "height": height
                    })

                headings = []
                for line_chars in line_map.values():
                    segments = split_on_large_gaps(line_chars)
                    for segment in segments:
                        segment.sort(key=lambda c: c["x0"])
                        reconstructed_text = reconstruct_text(segment)
                        cleaned_text = clean_line_text(reconstructed_text)
                        if not cleaned_text or len(cleaned_text.split()) > 12:
                            continue
                        weights = {c["weight"] for c in segment}
                        families = {c["font_family"] for c in segment}
                        avg_size = round(sum(c["font_size"] for c in segment) / len(segment), 2)
                        top, height = segment[0]["top"], segment[0]["height"]
                        if len(weights) == 1:
                            style = weights.pop()
                            font_family = families.pop() if len(families) == 1 else "Mixed"
                            if (font_family.lower() == "arial" and avg_size > 9) or \
                               (style == "bold" and avg_size >= 11.5) or \
                               (style == "regular" and avg_size > 12.5):
                                headings.append({
                                    "text": cleaned_text, "font_size": avg_size,
                                    "style": style, "font_family": font_family,
                                    "top": top, "height": height, "page": page_num,
                                    "source": "text"
                                })
                merged_headings = merge_similar_headings(headings)
                doc_info["pages"].append({"page": page_num, "sections": merged_headings})

        document_data.append(doc_info)

    return document_data
