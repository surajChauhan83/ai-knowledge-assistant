# # FastAPI app entry point
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.api import upload, query, websocket

# app = FastAPI()

# # CORS middleware to allow requests from the frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins for development
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include the routers for different functionalities
# app.include_router(upload.router, prefix="/upload")
# app.include_router(query.router, prefix="/chat")  # Changed from "/query"

# app.include_router(websocket.router, prefix="/ws")

# @app.get("/")
# async def root():
#     return {"message": "Welcome to the FastAPI app AI assitant is running!"}

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import chat

app = FastAPI()

app.include_router(chat.router)  # ✅ No trailing slash
app.mount("/static", StaticFiles(directory="app/static"), name="static")
