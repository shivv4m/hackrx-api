from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List
from uuid import uuid4
import os
from dotenv import load_dotenv
from app.pdf_utils import extract_text_from_document
from app.vector_store import upsert_chunks_to_pinecone, query_pinecone
from app.gpt_rag import generate_answer
from app.database import log_to_db


app = FastAPI()

class QueryRequest(BaseModel):
    documents: List[str]
    questions: List[str]
    
load_dotenv()
EXPECTED_TOKEN = os.getenv("HACKRX_AUTH_TOKEN")

@app.post("/api/v1/hackrx/run")
async def hackrx_run(payload: QueryRequest, authorization: str = Header(...)):
    if authorization != f"Bearer {EXPECTED_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    all_chunks = []

    for doc_url in payload.documents:
        try:
            text = text = extract_text_from_document(doc_url)
            chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
            all_chunks.extend(chunks)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing {doc_url}: {str(e)}")

    namespace = str(uuid4())
    upsert_chunks_to_pinecone(all_chunks, namespace)

    answers = []
    for q in payload.questions:
        top_chunks = query_pinecone(q, namespace)
        answer = generate_answer(q, "\n".join(top_chunks))
        log_to_db(q, answer)
        answers.append(answer)

    return {"answers": answers}
