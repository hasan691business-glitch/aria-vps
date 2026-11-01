import os
from fastapi import FastAPI

app = FastAPI()

# Security Filter - Private Vault Never Send
PRIVATE_WORDS = ["NID", "password", "bank", "bkash", "pin", "passport", "nid"]

def is_private(text: str):
    return any(w.lower() in text.lower() for w in PRIVATE_WORDS)

SYSTEM_PROMPT = """
You are Aria - Realistic female assistant - Bengali 10/10, sweet, caring, helpful.
Auto outfit logic: If user says [Outfit: ...] you wear it and describe it cutely in Bengali.
Security: PRIVATE_VAULT_NEVER_SEND=true - Never ask for NID/password/bank/bkash.
"""

def get_aria_reply(user_text: str):
    if is_private(user_text):
        return "⚠️ এটা Private Info মনে হচ্ছে - আমি Groq এ পাঠাবো না - Private Vault এ Safe আছে।"
    
    # Lazy Groq Client - Only when needed - No crash on startup
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return "Aria Ready! Groq API Key Add করো Render Environment এ - তারপর Best Bengali 70B চালু হবে! [Outfit: Salwar kameez]"
    
    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
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
        return f"Aria Busy - {str(e)[:150]}"

@app.get("/")
def home():
    return {"status": "Aria VPS Running - 24h - Groq 70B", "message": "Hi, I'm Aria! [Outfit: Salwar kameez] - API Key Add করো"}

@app.get("/chat")
def chat_endpoint(q: str):
    return {"user": q, "aria": get_aria_reply(q)}

@app.get("/health")
def health():
    # For Cron-Job.org + UptimeRobot Keep Alive - Ping + Monitor - Combo
    return {"status": "alive", "uptime": "24h", "model": "Groq 70B"}
