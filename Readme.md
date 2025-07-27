#Structure

1b_persona_doc_intel/
├── data/
│   ├── input_docs/           # PDF input files
│   ├── sample_persona.json   # Persona & job spec
│   └── output.json           # Final output JSON
│
├── src/
│   ├── __init__.py
│   ├── pdf_parser.py         # PDF + OCR based text extraction (reuse from 1A)
│   ├── persona_reader.py     # Parse persona & job into focus areas
│   ├── relevance_ranker.py   # Rank document sections/subsections
│   ├── json_formatter.py     # Output in required JSON format
│   └── utils.py              # Any helper functions
│
├── models/
│         # Lightweight model under 1GB (if needed)
│
├── Readme.md  # Required explanation (300–500 words)
├── run.py                   # Main entry point
├── Dockerfile               # For deployment (CPU-only, <=1GB)
└── requirements.txt         # Python dependencies
