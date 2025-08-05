import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_answer(question, context):
    prompt = f"""
You are a concise and factual assistant.

Using only the relevant parts of the context, answer the following question in 2-3 lines. Be direct, avoid repetition, and skip unnecessary details.

Context:
{context}

Question:
{question}

Answer (in 2-3 lines):
"""
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 100  # This limits the length of the answer
        }
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()
