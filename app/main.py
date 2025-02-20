from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
import pdfplumber
import os
import pandas as pd
import re
from typing import List

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Define job-relevant skills with weights
JOB_KEYWORDS = {
    "Python": 10, "Machine Learning": 15, "AI": 20, "FastAPI": 10, "TensorFlow": 15,
    "PyTorch": 15, "NLP": 12, "Data Science": 18, "Deep Learning": 20, "Docker": 10
}

class ResumeProcessRequest(BaseModel):
    text: str  # Extracted text from resume

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    """Uploads a resume (PDF), extracts text, and returns the content."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    extracted_text = extract_text_from_pdf(file_path)
    candidate_name = extract_candidate_name(extracted_text)

    return {"filename": file.filename, "candidate_name": candidate_name, "text": extracted_text}


@app.post("/score-resumes/")
async def score_resumes(files: List[UploadFile] = File(...)):
    """Processes multiple resumes, scores them against ranking criteria, and returns an Excel file."""
    results = []

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        resume_text = extract_text_from_pdf(file_path)
        candidate_name = extract_candidate_name(resume_text)
        score_details = calculate_resume_score(candidate_name, resume_text)

        results.append(score_details)

    # Generate and return Excel output
    excel_path = generate_excel_output(results)
    return {"excel_file": excel_path}


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

    return text.strip()


def extract_candidate_name(text: str) -> str:
    """Attempts to extract the candidate's name from the first few lines of text."""
    lines = text.strip().split("\n")
    if lines:
        first_line = lines[0].strip()
        if len(first_line.split()) < 5:  # Assume names are short
            return first_line
    return "Unknown"


def calculate_resume_score(candidate_name: str, text: str):
    """Matches resume content with ranking criteria and calculates a structured score."""
    score_details = {"Candidate Name": candidate_name}
    total_score = 0

    for skill, weight in JOB_KEYWORDS.items():
        # Use regex for more accurate keyword matching
        if re.search(rf"\b{skill}\b", text, re.IGNORECASE):
            score_details[skill] = weight
            total_score += weight
        else:
            score_details[skill] = 0

    score_details["Total Score"] = total_score
    return score_details


def generate_excel_output(results: List[dict]) -> str:
    """Generates an Excel file from the scoring results."""
    df = pd.DataFrame(results)
    excel_filename = "resume_scores.xlsx"
    excel_path = os.path.join(UPLOAD_DIR, excel_filename)
    df.to_excel(excel_path, index=False)
    return excel_path


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
