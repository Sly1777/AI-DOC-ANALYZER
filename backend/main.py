from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from document_service import document_service
import uvicorn

app = FastAPI(title="SmartDoc AI Python Backend")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'rtf', 'xlsx', 'xls'}

@app.post("/api/documents/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    tone: str = Form("executive")
):
    try:
        filename = file.filename
        extension = filename.split('.')[-1].lower() if '.' in filename else ''
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Invalid file type: {extension}")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

        return document_service.analyze_document(content, file.filename, tone)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis Error: {str(e)}")

@app.post("/api/documents/ask")
async def ask_question(request: dict):
    text = request.get("text")
    question = request.get("question")
    if not text or not question:
        raise HTTPException(status_code=400, detail="Missing text or question")
    
    answer = document_service.answer_question(text, question)
    return {"answer": answer}

@app.post("/api/documents/summarize")
async def summarize(request: dict):
    text = request.get("text")
    tone = request.get("tone", "executive")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")
    
    summary = document_service.generate_ai_summary(text, tone)
    takeaways = document_service.extract_key_takeaways(text)
    return {"summary": summary, "takeaways": takeaways}

@app.get("/api/documents/test")
async def test():
    return {"status": "Backend is working!", "message": "Ready to analyze!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
