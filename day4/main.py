from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import shutil
import os
from resume_extractor import pdf_to_md, docx_to_md
from resume_analyzer import extract_info_from_llm

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r") as f:
        return f.read()

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    filename = file.filename
    extension = filename.split(".")[-1].lower()
    
    if extension not in ["pdf", "docx", "doc"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are supported.")
    
    # Save uploaded file temporarily
    temp_file_path = f"temp_{filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Extract text
        if extension == "pdf":
            md_content = pdf_to_md(temp_file_path)
        else:
            md_content = docx_to_md(temp_file_path)
            
        # Analyze
        analysis_result = extract_info_from_llm(md_content)
        
        return analysis_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
