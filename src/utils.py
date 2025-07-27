import re

# Check if a font name indicates bold style
def is_bold(font_name):
    return 'bold' in font_name.lower() or 'bd' in font_name.lower()

# Extract the base font family name (before '-' or ',')
def extract_font_family(font_name):
    return font_name.split("-")[0] if "-" in font_name else font_name.split(",")[0]

# Clean a line of text by trimming and removing trailing periods or ellipses
def clean_line_text(text):
    text = text.strip()
    if text.endswith('.') and not text.endswith('..'):
        return ""
    match = re.search(r"\.{3,}", text)
    if match:
        return text[:match.start()].strip()
    return text

# Split line into segments where horizontal gaps are larger than the threshold
def split_on_large_gaps(line_chars, gap_threshold=50):
    segments = []
    current_segment = []
    line_chars.sort(key=lambda c: c["x0"])
    for i in range(len(line_chars)):
        current_segment.append(line_chars[i])
        if i < len(line_chars) - 1:
            cur_end = line_chars[i]["x1"]
            next_start = line_chars[i + 1]["x0"]
            gap = next_start - cur_end
            if gap > gap_threshold:
                segments.append(current_segment)
                current_segment = []
    if current_segment:
        segments.append(current_segment)
    return segments

# Reconstruct text from character-level data, inserting spaces where needed
def reconstruct_text(chars, space_threshold=1.5):
    chars = sorted(chars, key=lambda c: c["x0"])
    text = ""
    for i, c in enumerate(chars):
        if i > 0:
            gap = c["x0"] - chars[i - 1]["x1"]
            if gap > space_threshold:
                text += " "
        text += c["text"]
    return text

# Merge lines with similar heading styles and nearby vertical positions
def merge_similar_headings(lines, y_gap=40):
    if not lines:
        return []
    lines.sort(key=lambda x: x["top"])
    merged = [lines[0]]
    for line in lines[1:]:
        last = merged[-1]
        if (
            abs(line["top"] - last["top"]) <= y_gap or abs(line["top"] - (last["top"] + last["height"])) <= y_gap
        ) and (
            line["font_size"] == last["font_size"] and
            line["style"] == last["style"] and
            line["font_family"] == last["font_family"] and
            line["font_size"] >= 15
        ):
            merged[-1]["text"] += " " + line["text"]
        else:
            merged.append(line)
    return merged

# Remove excessive character repetition and whitespace from text
def deduplicate_and_simplify(text):
    return re.sub(r'(\w)\1+', r'\1', text).strip()