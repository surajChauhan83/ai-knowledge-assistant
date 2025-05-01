from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
import io
import fitz  # PyMuPDF
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter

router = APIRouter()

# In-memory FAISS vector store
vectorstore = None

def get_vectorstore(text: str):
    """Generates vectorstore from text in-memory"""
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_texts(chunks, embedding=embeddings)

@router.get("/", response_class=HTMLResponse)
async def chat_interface():
    try:
        with open("app/static/chat.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>File not found</h1>", status_code=404)
    except UnicodeDecodeError:
        return HTMLResponse(content="<h1>Encoding error reading HTML file</h1>", status_code=500)

@router.post("/upload/")
async def upload_file(files: list[UploadFile] = File(...)):
    global vectorstore
    for file in files:
        # Read PDF into memory
        pdf_bytes = await file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = "\n".join(page.get_text() for page in doc)
        
        # Store the embeddings in memory (using FAISS)
        vectorstore = get_vectorstore(full_text)
    
    return JSONResponse({"status": "success", "message": "Files uploaded and embeddings generated"})

@router.post("/chat/")
async def chat_with_docs(question: str = Form(...)):
    global vectorstore
    if vectorstore is None:
        return JSONResponse({"answer": "No documents uploaded. Please upload a file."}, status_code=400)
    
    retriever = vectorstore.as_retriever()
    from langchain.chains import RetrievalQA
    from langchain.llms import OpenAI  # Or use HuggingFace models
    
    qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), retriever=retriever)
    answer = qa.run(question)
    
    return JSONResponse({"answer": answer})
