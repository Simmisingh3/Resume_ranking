# Resume Ranking API

## 📌 Overview
This FastAPI-based project provides two endpoints:
1. **Extract ranking criteria from job descriptions** (`/extract-criteria`)
2. **Score resumes based on extracted criteria** (`/score-resumes`)

## 🚀 Features
- Handles **PDF/DOCX** job descriptions & resumes
- Uses **LLMs** (GPT-4, Claude, Gemini) to analyze content
- Outputs structured **JSON responses** & **Excel score reports**
- **Swagger UI** for interactive API testing


A. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

B. Open **Swagger UI** at:
   ```
   http://127.0.0.1:8000/docs
   ```

