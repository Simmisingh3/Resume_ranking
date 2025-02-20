from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import pdfplumber
import os

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

    return {"filename": file.filename, "text": extracted_text}


@app.post("/process-resume/")
async def process_resume(request: ResumeProcessRequest):
    """Processes the extracted resume text, matches skills, and calculates a resume score."""
    extracted_text = request.text

    matched_skills, resume_score = calculate_resume_score(extracted_text)

    return {
        "matched_skills": matched_skills,
        "resume_score": resume_score,
        "resume_text_preview": extracted_text[:500]  # Limit preview
    }


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

    return text.strip()


def calculate_resume_score(text: str):
    """Matches resume skills and calculates a score based on keyword weightage."""
    matched_skills = []
    total_score = 0

    for skill, weight in JOB_KEYWORDS.items():
        if skill.lower() in text.lower():
            matched_skills.append(skill)
            total_score += weight

    return matched_skills, total_score


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
