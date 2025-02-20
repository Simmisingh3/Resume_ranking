import pdfplumber
import docx2txt
import openai
from app.config import OPENAI_API_KEY


def extract_text(file):
    """
    Extracts text from a PDF or DOCX file.
    """
    if file.filename.endswith(".pdf"):
        text = []
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)
    
    elif file.filename.endswith(".docx"):
        return docx2txt.process(file.file)

    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")


def extract_criteria(text):
    """
    Uses OpenAI LLM to extract key ranking criteria from job description text.
    """
    prompt = f"Extract key ranking criteria (skills, experience, certifications) from the following job description:\n{text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY  # Securely pass API key
    )
    
    criteria = response["choices"][0]["message"]["content"].split("\n")
    return [c.strip() for c in criteria if c.strip()]


def score_resumes(resume_text, criteria):
    """
    Scores a resume against ranking criteria using LLM-based keyword matching.
    """
    score_details = {}
    total_score = 0

    for criterion in criteria:
        prompt = f"Rate the resume (0-5) based on relevance to: '{criterion}'. Resume content:\n{resume_text}"

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                api_key=OPENAI_API_KEY
            )
            
            score_text = response["choices"][0]["message"]["content"].strip()
            score = int(score_text) if score_text.isdigit() else 0  # Ensure integer score

        except Exception as e:
            print(f"Error scoring resume for criterion '{criterion}': {e}")
            score = 0  # Default to 0 if error occurs

        score_details[criterion] = score
        total_score += score

    return {"Candidate Name": "Unknown", **score_details, "Total Score": total_score}
