from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
import os
import fitz
from dotenv import load_dotenv
import requests
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEndpoint

from langchain_community.llms import HuggingFaceHub 
import traceback
from fastapi import HTTPException

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
    print("Extracted text from PDF:", all_text)  # Print first 100 characters for debugging
    if not all_text:
        return JSONResponse({"status": "error", "message": "No text extracted from PDF."})
    
    # Store the embeddings in memory (using FAISS)
    vectorstore = get_vectorstore(all_text)
    print("Vectore",vectorstore)
    
    return JSONResponse({"status": "success", "message": "Files uploaded and embeddings generated"})


@router.post("/chat/")
async def chat_with_docs(question: str = Form(...)):
    global vectorstore

    # Check if vectorstore is initialized
    if vectorstore is None:
        return JSONResponse({"answer": "No documents uploaded."}, status_code=400)

    # Check if question is provided
    if not question:
        return JSONResponse({"error": "Question field is missing or empty."}, status_code=400)

    try:
        # Set up the retriever to fetch relevant documents
        retriever = vectorstore.as_retriever()

        # Initialize the QA chain with a Hugging Face model
        llm = HuggingFaceEndpoint(
            repo_id="google/flan-t5-base",
            task="text2text-generation",
            huggingfacehub_api_token=HF_API_KEY
        )

        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever()
        )

        # Get the answer from the model
        answer = qa.run(question)
        return JSONResponse({"answer": answer})

    except Exception as e:
        # Log the exception and return error message
        error_message = f"Error processing question: {question}. Error: {str(e)}"
        traceback.print_exc()  # Print the full stack trace for debugging
        return JSONResponse({"error": error_message}, status_code=500)
