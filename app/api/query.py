# app/api/query.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/")
async def chat_page():
    return HTMLResponse("""
    <html>
        <body>
            <h2>Ask Questions</h2>
            <form action="/query/" method="post">
                <input type="text" name="question" placeholder="Ask a question" />
                <button type="submit">Ask</button>
            </form>
        </body>
    </html>
    """)

@router.post("/")
async def chat_answer(question: str = Form(...)):
    # Later you will add RAG logic here
    return HTMLResponse(f"""
    <html>
        <body>
            <h2>Ask Questions</h2>
            <form action="/query/" method="post">
                <input type="text" name="question" placeholder="Ask a question" />
                <button type="submit">Ask</button>
            </form>
            <hr>
            <h3>You asked:</h3>
            <p>{question}</p>
            <h3>Answer (placeholder):</h3>
            <p>This will show the answer using RAG logic soon.</p>
        </body>
    </html>
    """)
