from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
import os
load_dotenv()

import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

# 🔹 Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 🔹 Load FAISS index
INDEX_PATH = "data/wpi_corpus_index.faiss"
MAPPING_PATH = "data/wpi_corpus_mapping.json"

index = faiss.read_index(INDEX_PATH)

with open(MAPPING_PATH, "r", encoding="utf-8") as f:
    corpus_mapping = json.load(f)


app = FastAPI()

# Allow your Vite dev server origins (5173 and fallback 5174)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"message": "Backend is running"}

def retrieve_wpi_context(query: str, k: int = 3) -> str:
    query_embedding = embedding_model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, k)

    chunks = []
    for idx in indices[0]:
        if str(idx) in corpus_mapping:
            chunks.append(corpus_mapping[str(idx)])

    return "\n\n".join(chunks)
def format_prompt(query, context):
    return f"""
You are WPIBot — an expert assistant built for Worcester Polytechnic Institute (WPI) students.
Use ONLY the information provided in the context below.
If the answer is not present in the context, say: "I couldn't find that information."

Context:
{context}

Question: {query}
Answer:
"""


@app.post("/chat")
def chat(req: ChatRequest):
    context = retrieve_wpi_context(req.question)
    prompt = format_prompt(req.question, context)

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 400,
    }

    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=30,
    )

    if r.status_code != 200:
        return {"answer": f"Groq error {r.status_code}: {r.text}"}

    return {"answer": r.json()["choices"][0]["message"]["content"]}
