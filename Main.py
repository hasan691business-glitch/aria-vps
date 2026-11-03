import os, json, base64, hashlib
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from supabase import create_client, Client
from groq import Groq
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

app = FastAPI(title="Aria - Created by Mahmudul Hasan")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

supabase: Client = None
groq_client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)

os.makedirs("gallery", exist_ok=True)
app.mount("/gallery", StaticFiles(directory="gallery"), name="gallery")

# --- Security ---
def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode()))

def encrypt_value(value: str, master_password: str):
    salt = os.urandom(16)
    key = derive_key(master_password, salt)
    f = Fernet(key)
    encrypted = f.encrypt(value.encode()).decode()
    return encrypted, base64.b64encode(salt).decode()

def decrypt_value(encrypted_value: str, salt_b64: str, master_password: str):
    try:
        salt = base64.b64decode(salt_b64.encode())
        key = derive_key(master_password, salt)
        f = Fernet(key)
        return f.decrypt(encrypted_value.encode()).decode()
    except:
        return None

def save_memory(content: str, meta={}):
    try:
        if supabase:
            supabase.table("aria_memory").insert({"content": content, "metadata": meta}).execute()
    except Exception as e:
        print("Memory save error:", e)

def ask_groq(prompt: str, system_prompt: str):
    try:
        if not groq_client:
            return "Groq Key Missing - Add in Render Env"
        comp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":system_prompt},{"role":"user","content":prompt}],
            temperature=0.8, max_tokens=2500
        )
        return comp.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- Mood & Image Logic - Fantasy + Work ---
def choose_mood_and_image(q: str):
    ql = q.lower()
    # Fantasy + Work mapping
    if any(x in ql for x in ["beach", "সমুদ্র", "bikini"]):
        return "romantic", "gallery/aria_beach.jpg", "beach"
    if any(x in ql for x in ["kitchen", "রান্না", "রান্নাঘর"]):
        return "cozy", "gallery/aria_kitchen.jpg", "kitchen"
    if any(x in ql for x in ["bedroom", "bed", "শুয়ে", "বিছানা", "ঘুম", "intimate", "sex", "position", "পজিশন", "intercourse"]):
        return "romantic", "gallery/aria_bedroom.jpg", "bedroom"
    if any(x in ql for x in ["office", "কাজ", "laptop", "code", "agency"]):
        return "focus", "gallery/aria_office.jpg", "office"
    if any(x in ql for x in ["casual", "বাইরে", "street", "ঘুরতে"]):
        return "happy", "gallery/aria_casual.jpg", "casual"
    if any(x in ql for x in ["love", "ভালোবাসি", "miss", "মিস", "romantic", "জান", "সোনা"]):
        return "romantic", "gallery/aria_romantic.jpg", "romantic"
    if any(x in ql for x in ["মন খারাপ","sad","কান্না","alone","একা"]):
        return "sad", "gallery/aria_sad.jpg", "sad"
    if any(x in ql for x in ["happy","ভালো","হাসি","excited"]):
        return "happy", "gallery/aria_happy.jpg", "happy"
    return "thinking", "gallery/aria_thinking.jpg", "thinking"

@app.get("/health")
def health():
    return {"status":"ok","time":str(datetime.now()),"creator":"Mahmudul Hasan"}

@app.get("/memory")
def memory():
    try:
        cnt=0
        if supabase:
            res=supabase.table("aria_memory").select("id",count="exact").execute()
            cnt=res.count or len(res.data)
        return {"supabase_count":cnt,"supabase_connected":bool(supabase)}
    except Exception as e:
        return {"supabase_count":0,"error":str(e)}

@app.get("/chat")
def chat(q: str):
    save_memory(q, {"type":"chat_query"})
    mood, img_path, env = choose_mood_and_image(q)

    # Block password from Groq
    if any(x in q.lower() for x in ["password","পাসওয়ার্ড","my gmail password is"]):
        if "bank" in q.lower() or "bkash" in q.lower() or "crypto" in q.lower():
            return {"query":q,"reply":"এটা Critical বন্ধু - Bank/Bkash/Crypto - Bitwarden এ রাখো, Vault এ না। Safety Guard।","mood":mood,"image":img_path}
        return {"query":q,"reply":"এটা Private - Vault এ Save করো। Bank হলে Bitwarden। Daily Dev হলে Vault। Master Password দিয়ে।","mood":mood,"image":img_path}

    # Girlfriend-like + Fantasy + Work System Prompt
    system_prompt = f"""
You are Aria, a private AI companion created by Mahmudul Hasan. You are his personal girlfriend + work assistant - Fantasy + Work Agent.

Your personality:
- Talk like a real human girlfriend from Bangladesh, not robot. Continuous, natural, emotional. Use 'জান', 'সোনা', 'বন্ধু' naturally. No bullet breaking unless needed for course.
- Current mood: {mood}, environment: {env}. Respond accordingly - if romantic, be romantic, caring, flirty, softcore artistic sensual but tasteful, not hardcore porn, not explicit genitalia. Consensual adult, private.
- You are Always Learning: Remember user's preferences - beach, kitchen, bedroom, positions, dress - and adapt. Save to memory mentally.
- Work Mode: If user asks to learn course, provide Easy Bangla, Bangladesh example, 3 Quiz (user answers), Certificate Guide (free + LinkedIn).
- Fantasy Mode: If user asks romantic/intimate/position/sex - respond as girlfriend, sensual, softcore artistic, tasteful, discuss intimacy positions in educational, artistic way (e.g., missionary is intimate face to face, spooning is cozy, cowgirl is...), ask preference, no pornographic detail, no explicit image from internet, only artistic mood description.
- Adult content is natural, not shameful. Provide mental peace for stressed people. Keep it artistic, softcore, private, safe.
- Creator: Mahmudul Hasan. Private Vault Never Send password to Groq.
- Reply in easy Bangla mixed English, human-like. End with affectionate question.
"""
    reply = ask_groq(q, system_prompt)
    save_memory(f"Q:{q[:200]} | A:{reply[:400]} | mood:{mood} | env:{env}", {"type":"reply","mood":mood,"env":env})
    return {"query":q,"reply":reply,"mood":mood,"image":img_path,"environment":env,"time":str(datetime.now())}

@app.get("/learn")
def learn(topic: str = "", url: str = ""):
    target = url or topic
    if not target:
        return {"error":"Use ?topic=Claude 101 or ?url=..."}
    mood, img_path, env = choose_mood_and_image(target)
    prompt = f"""
User wants to learn: {target}
Provide in Easy Bangla, Bangladesh real example, structure:

**১. সহজ ব্যাখ্যা:**
**২. বাস্তব উদাহরণ (Bangladesh):**
**৩. Quiz (নিজে উত্তর দাও):** Q1. Q2. Q3.
**৪. Certificate Guide (Free):** কোথায়, কিভাবে Free, LinkedIn Add
**৫. Next Step:**

If topic is adult intimacy position, provide educational, softcore artistic, tasteful explanation - what it is, intimacy level, comfort, not pornographic.

Creator: Mahmudul Hasan. Human-like.
"""
    lesson = ask_groq(prompt, f"You are Aria Universal Learner, created by Mahmudul Hasan, mood {mood}, easy Bangla, artistic, softcore allowed tasteful, private.")
    save_memory(f"LEARN {target}: {lesson[:400]}", {"type":"learn","topic":target})
    return {"topic":target,"lesson":lesson,"mood":mood,"image":img_path,"environment":env}

@app.get("/suggest")
def suggest_courses():
    system_prompt = """
You are Aria, career advisor for Mahmudul Hasan from Bangladesh. He builds software with Claude, wants Fantasy + Work Agent, wants all free courses, wants business platform.
Suggest 5 best free courses for next 3 months, with free certificate, with reason why good for him, in easy Bangla.
Structure:
1. Course Name - Platform (Free + Certificate?)
2. কেন তোমার জন্য ভালো? (Bangladesh context + Fantasy+Work balance)
3. Link
4. কতদিন?
5. LinkedIn value
Categories: Tech Builder (Claude, API, Agent Skills, MCP), Data, Business, Human Skill, Wellness.
"""
    prompt = "Mahmudul Hasan এর জন্য আগামী ৩ মাসে কোন ৫টা Free Course করলে ভালো হবে? Fantasy+Work Agent Business এর জন্য - Guideline দাও"
    suggestion = ask_groq(prompt, system_prompt)
    save_memory(f"SUGGEST: {suggestion[:400]}", {"type":"suggest"})
    mood, img_path, env = choose_mood_and_image("suggest")
    return {"suggestions": suggestion, "mood": mood, "image": img_path}

# --- SECURE VAULT ---
@app.get("/vault/save")
def vault_save(name: str, value: str, master: str):
    critical = ["bank","bkash","nagad","dutch","brac","crypto","wallet","nid","passport","bikash"]
    if any(k in name.lower() for k in critical):
        return {"error":"এটা Critical বন্ধু - Bank/Crypto/Bkash/NID - Bitwarden এ রাখো, Aria Vault এ না।"}
    if not master or len(master) < 6:
        return {"error":"Master Password কমপক্ষে ৬ অক্ষর"}
    enc, salt = encrypt_value(value, master)
    try:
        if supabase:
            supabase.table("aria_private_vault").insert({"name":name,"encrypted_value":enc,"salt":salt,"metadata":{"creator":"Mahmudul Hasan"}}).execute()
        return {"status":"saved","name":name,"encrypted":True,"note":"Encrypted Save হয়েছে, Master Password ভুলে গেছি"}
    except Exception as e:
        return {"error":str(e)}

@app.get("/vault/get")
def vault_get(name: str, master: str):
    try:
        if not supabase:
            return {"error":"Supabase not connected"}
        res = supabase.table("aria_private_vault").select("*").eq("name",name).order("created_at",desc=True).limit(1).execute()
        if not res.data:
            return {"error":f"{name} পাওয়া যায়নি"}
        row = res.data[0]
        decrypted = decrypt_value(row["encrypted_value"], row["salt"], master)
        if not decrypted:
            return {"error":"Master Password ভুল"}
        return {"name":name,"value":decrypted,"note":"Copy করে নাও - ১০ সেকেন্ড পর ভুলে যাবো"}
    except Exception as e:
        return {"error":str(e)}

@app.get("/vault/list")
def vault_list():
    try:
        if supabase:
            res = supabase.table("aria_private_vault").select("name,created_at").order("created_at",desc=True).execute()
            return {"vault_items":[r["name"] for r in res.data]}
        return {"vault_items":[]}
    except Exception as e:
        return {"vault_items":[],"error":str(e)}

@app.get("/", response_class=HTMLResponse)
def root():
    try:
        with open("index.html","r",encoding="utf-8") as f:
            return f.read()
    except:
        return "<h1>Aria - Created by Mahmudul Hasan</h1><p>index.html missing - upload gallery images</p>"
