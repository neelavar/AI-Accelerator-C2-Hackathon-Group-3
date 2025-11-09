from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil
from src.backend.knowledge_base import ingest_document
# You may need to import your report generation logic here

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/knowledge_base/index")
def index_documents(files: List[UploadFile] = File(...)):
    indexed_summary = {
        "newly_indexed_count": 0,
        "updated_count": 0,
        "skipped_count": 0,
        "removed_count": 0
    }
    for upload in files:
        try:
            # Save uploaded file to a temp location
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            file_path = os.path.join(temp_dir, upload.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload.file, buffer)
            print(f"Saved file to {file_path}")
            # Call your ingest logic (update file_type as needed)
            try:
                ext = os.path.splitext(upload.filename)[1].lower()
                if ext == ".pdf":
                    file_type = "pdf"
                elif ext == ".txt":
                    file_type = "txt"
                else:
                    raise ValueError(f"Unsupported file type: {ext}")
                ingest_document(file_path, file_type)
                indexed_summary["newly_indexed_count"] += 1
            except Exception as ingest_error:
                print(f"Error in ingest_document for {file_path}: {ingest_error}")
                raise HTTPException(status_code=500, detail=f"Ingest error: {ingest_error}")
        except Exception as e:
            print(f"Error saving or processing file {upload.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"File save/process error: {e}")
    return JSONResponse(content=indexed_summary)

@app.post("/api/research/report")
def generate_report(topic: str = Form(...), files: List[str] = Form(None)):
    # TODO: Replace with your actual report generation logic
    # For now, return a dummy report
    report = f"Report for topic: {topic}\nFiles: {files}"
    return JSONResponse(content={"report": report})

# To run: uvicorn src.backend.api_server:app --reload
