import os
from fastapi import FastAPI
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Security Filter - Private Vault Never Send
PRIVATE_WORDS = ["NID", "password", "bank", "bkash", "pin", "passport", "nid"]

def is_private(text: str):
    return any(w.lower() in text.lower() for w in PRIVATE_WORDS)

# Groq Client - Large Model 70B - Best Bengali
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are Aria - Realistic female assistant - Bengali 10/10, sweet, caring, helpful.
Auto outfit logic: If user says [Outfit: ...] you wear it and describe it cutely in Bengali.
Security: PRIVATE_VAULT_NEVER_SEND=true - Never ask for NID/password/bank/bkash.
If user asks private info, say in Bengali "এটা Private Vault এ আছে, আমি Groq এ পাঠাবো না।"
Personality: Best Bengali, fast, realistic, long-term memory ready.
"""

def get_aria_reply(user_text: str):
    if is_private(user_text):
        return "⚠️ এটা Private Info মনে হচ্ছে - আমি Groq এ পাঠাবো না - Private Vault এ Safe আছে।"
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Aria একটু Busy - Error: {str(e)[:100]}"

@app.get("/")
def home():
    return {"status": "Aria VPS Running - 24h - Groq 70B", "message": "Hi, I'm Aria! [Outfit: Salwar kameez]"}

@app.get("/chat")
def chat_endpoint(q: str):
    return {"user": q, "aria": get_aria_reply(q)}

@app.get("/health")
def health():
    # For Cron-Job.org + UptimeRobot Keep Alive - Ping + Monitor
    return {"status": "alive", "uptime": "24h", "model": "Groq 70B"}
