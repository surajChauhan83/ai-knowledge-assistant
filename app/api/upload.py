# app/api/upload.py
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "app/local_storage/files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/")
async def upload_form():
    return HTMLResponse("""
    <html>
        <body>
            <h2>Upload Documents</h2>
            <form action="/upload/" method="post" enctype="multipart/form-data">
                <input type="file" name="files" multiple>
                <button type="submit">Upload</button>
            </form>
        </body>
    </html>
    """)

@router.post("/")
async def upload_files(files: list[UploadFile] = File(...)):
    for file in files:
        with open(os.path.join(UPLOAD_DIR, file.filename), "wb") as f:
            shutil.copyfileobj(file.file, f)
    return RedirectResponse(url="/chat/", status_code=303)
