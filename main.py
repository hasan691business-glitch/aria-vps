import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from datetime import datetime
import json

try:
    from groq import Groq
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except:
    groq_client = None

try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    else:
        supabase = None
except Exception as e:
    print(f"Supabase init error: {e}")
    supabase = None

app = FastAPI()

if os.path.exists("gallery"):
    app.mount("/gallery", StaticFiles(directory="gallery"), name="gallery")

def load_memory():
    if os.path.exists("memory.json"):
        try:
            with open("memory.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"user_likes": [], "chat_history": [], "learned_facts": []}
    return {"user_likes": [], "chat_history": [], "learned_facts": []}

def save_memory(data):
    try:
        with open("memory.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if supabase:
            try:
                supabase.table("aria_memory").insert({
                    "content": json.dumps(data, ensure_ascii=False)[:1000],
                    "embedding": "local_backup",
                    "metadata": {"type": "backup", "time": str(datetime.now())}
                }).execute()
            except:
                pass
    except:
        pass

def learn_from_text(text, memory):
    tl = text.lower()
    if "pochondo" in tl or "like" in tl or "valobasi" in tl:
        memory["user_likes"].append(text)
        memory["learned_facts"].append(f"Likes: {text}")
    return memory

def choose_outfit():
    try:
        with open("wardrobe.json", "r", encoding="utf-8") as f:
            wardrobe = json.load(f)
        if wardrobe:
            k = list(wardrobe.keys())[0]
            v = wardrobe[k]
            img = v.get("image", "gallery/default.jpg") if isinstance(v, dict) else "gallery/default.jpg"
            return f"[Outfit: {k} | Image: {img}]"
    except:
        pass
    return "[Outfit: casual | Image: gallery/default.jpg]"

@app.get("/", response_class=HTMLResponse)
def root():
    if os.path.exists("index.html"):
        try:
            with open("index.html", "r", encoding="utf-8") as f:
                return f.read()
        except:
            pass
    return "<html><body><h1>Aria VPS Running - Vector Ready</h1><p>Please add index.html for Dashboard</p><p><a href='/memory'>Memory</a> | <a href='/health'>Health</a> | <a href='/gallery/'>Gallery</a></p></body></html>"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/memory")
def get_memory():
    mem = load_memory()
    count = 0
    if supabase:
        try:
            r = supabase.table("aria_memory").select("id", count="exact").execute()
            count = r.count if hasattr(r, 'count') else len(r.data)
        except:
            count = 0
    return {"local": mem, "supabase_count": count, "supabase_connected": bool(supabase)}

@app.get("/chat")
def chat(q: str = ""):
    memory = load_memory()
    memory = learn_from_text(q, memory)
    memory["chat_history"].append({"q": q, "time": str(datetime.now())})
    save_memory(memory)
    reply = f"Bujhechi: {q}"
    if groq_client and q:
        try:
            sys_prompt = "You are Aria, personal AI for Hasan Reza from Bangladesh. Reply in simple Bengali, with example, as user likes. If user asks to learn course, explain in Bangla easy, step by step."
            comp = groq_client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": q}],
                model="llama-3.3-70b-versatile",
            )
            reply = comp.choices[0].message.content
        except Exception as e:
            reply = f"Shikhechi: {q} - Ami ekhon shikchi"
    return {"reply": reply, "outfit": choose_outfit(), "supabase": bool(supabase)}

@app.get("/learn")
def learn_anything(topic: str, url: str = ""):
    content = f"Learning {topic} url {url}"
    if supabase:
        try:
            supabase.table("aria_memory").insert({
                "content": content,
                "embedding": topic,
                "metadata": {"type": "course", "topic": topic, "url": url, "lang": "bn"}
            }).execute()
            return {"status": "saved_to_vector", "topic": topic}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    return {"status": "supabase_not_connected"}
