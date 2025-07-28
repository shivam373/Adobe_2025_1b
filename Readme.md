# CONNECTING THE DOTS 1b

This project extracts and ranks relevant sections from PDF documents based on a persona and a specific goal (job to be done). It uses semantic similarity and OCR to identify and refine relevant information.

---

## Prerequisites

Ensure you have the following:

- Docker (recommended) OR Python 3.11+ locally
- Git
- Internet (for downloading models and dependencies)
- Input PDF documents in the `data/` directory
- A `persona.json` file with `persona` and `job_to_be_done`


## Project Structure 

adobe_2025_1b/  
├── data/  
│   ├── input_docs/           # PDF input files  
│   ├── persona.json          # Persona & job spec  
│   └── output.json           # Final output JSON  
│  
├── src/  
│   ├── __init__.py  
│   ├── pdf_parser.py         # PDF + OCR based text extraction (reuse from 1A)  
 focus areas  
│   ├── relevance_ranker.py   # Rank document sections/subsections  
│   ├── json_formatter.py     # Output in required JSON format  
│   └── utils.py              # Any helper functions  
│  
├── models/                   # Lightweight model under 1GB (if needed)  
│  
├── Readme.md                 # Required explanation (300–500 words)  
├── run.py                    # Main entry point  
├── Dockerfile               # For deployment (CPU-only)  
└── requirements.txt         # Python dependencies  

---

## Setup Instructions

### Option 1: Using Docker (Recommended)

1. **Build Docker image:**

   ```bash
   docker build -t info-retrieval-app .

2. **Run**
   
   ```bash
   docker run --rm -v $(Get-Location)/data:/app/data info-retrieval-app
   
