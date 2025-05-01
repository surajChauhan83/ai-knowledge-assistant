from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
import os
from dotenv import load_dotenv
import requests
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()

router = APIRouter()

# Hugging Face API key
HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    raise ValueError("Hugging Face API key is not set in .env file.")

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
    all_text = ""
    for file in files:
        # Read PDF into memory
        pdf_bytes = await file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        full_text = "\n".join(page.get_text() for page in doc)
        all_text += full_text
    
    if not all_text:
        return JSONResponse({"status": "error", "message": "No text extracted from PDF."})
    
    # Store the embeddings in memory (using FAISS)
    vectorstore = get_vectorstore(all_text)
    
    return JSONResponse({"status": "success", "message": "Files uploaded and embeddings generated"})

@router.post("/chat/")
async def chat_with_docs(question: str = Form(...)):
    global vectorstore
    if vectorstore is None:
        return JSONResponse({"answer": "No documents uploaded. Please upload a file."}, status_code=400)
    
    retriever = vectorstore.as_retriever()
    
    # Use retrieval-based QA chain with Hugging Face model API
    qa = RetrievalQA.from_chain_type(llm=HuggingFaceRetrievalQA(HF_API_KEY), retriever=retriever)
    answer = qa.run(question)
    
    return JSONResponse({"answer": answer})

class HuggingFaceRetrievalQA:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def run(self, question: str):
        # API request to Hugging Face inference endpoint
        response = requests.post(
            "https://api-inference.huggingface.co/models/distilbert-base-uncased",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"inputs": question}
        )
        result = response.json()
        return result[0]['generated_text'] if 'generated_text' in result else "Sorry, I couldn't generate an answer."
