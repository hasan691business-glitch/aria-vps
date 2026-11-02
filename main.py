# Aria VPS - Groq 70B - Self-Learning 【entity-Hermes¦canonical_name=Hermes】 Light - Auto Dress + Memory
import os, json, re, glob
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from groq import Groq

app = FastAPI(title="Aria VPS - Self Learning")

# --- CONFIG ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = "llama3-70b-8192"

# --- LOAD FILES FLEXIBLY (x5f issue fix) ---
def load_text_file(patterns):
    for pat in patterns:
        for f in glob.glob(pat):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    return fp.read()
            except: pass
    return ""

SYSTEM_PROMPT = load_text_file(["system*prompt.txt", "aria*.txt"])
WARDROBE_RAW = load_text_file(["wardrobe*.json", "wardrobe.txt"])
CALENDAR_RAW = load_text_file(["calendar.md", "aria_calendar.md"])

try:
    WARDROBE = json.loads(WARDROBE_RAW) if WARDROBE_RAW else {}
except:
    WARDROBE = {"beach_travel": ["beach"], "festival_boishakh": ["boishakh", "pohela"], "formal_office": ["office", "formal"], "party_dress": ["party"], "bangali_saree": ["saree", "salwar"], "jeans_tshirt": ["jeans"], "drawing_room": ["room"]}

# --- MEMORY SYSTEM - SELF LEARNING CORE ---
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {"user_likes": [], "chat_history": [], "learned_facts": [], "outfit_history": [], "created": str(datetime.now())}

def save_memory(mem):
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(mem, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Memory save error: {e}")

MEMORY = load_memory()

def learn_from_text(user_text: str):
    """Self-learning logic - 【entity-Hermes¦canonical_name=Hermes】 core"""
    text_low = user_text.lower()
    learned = False
    
    # Learn likes
    like_patterns = [r"i like (\w+)", r"ami (\w+) pochondo", r"(\w+) bhalo lage", r"love (\w+)", r"red pochondo", r"beach bhalo"]
    for pat in like_patterns:
        m = re.search(pat, text_low)
        if m:
            fact = f"User likes: {user_text[:100]}"
            if fact not in MEMORY["learned_facts"]:
                MEMORY["learned_facts"].append(fact)
                learned = True
            # Add to user_likes
            for cat in WARDROBE.keys():
                if cat in text_low or any(k in text_low for k in WARDROBE.get(cat, [])):
                    if cat not in MEMORY["user_likes"]:
                        MEMORY["user_likes"].append(cat)
                        learned = True
    
    # Learn outfit preference
    if "red" in text_low:
        MEMORY["user_likes"].append("red_color")
        learned = True
    if "saree" in text_low or "শাড়ি" in text_low:
        if "bangali_saree" not in MEMORY["user_likes"]:
            MEMORY["user_likes"].append("bangali_saree")
            learned = True
    
    if learned:
        save_memory(MEMORY)
    return learned

def choose_outfit_with_memory(query: str):
    """Auto dress + memory"""
    q_low = query.lower()
    
    # 1. Memory priority - user likes
    for liked in reversed(MEMORY.get("user_likes", [])):
        if liked in WARDROBE:
            # Check if liked category keywords match
            if liked == "beach_travel" and any(x in q_low for x in ["beach", "cox", "sea"]):
                return liked
            if liked in q_low:
                return liked
    
    # 2. Calendar check - Bangladesh festivals
    now = datetime.now()
    if now.month == 4 and now.day in [13,14,15]: # Boishakh
        return "festival_boishakh"
    if "boishakh" in q_low or "pohela" in q_low or "বৈশাখ" in q_low:
        return "festival_boishakh"
    if "eid" in q_low or "ঈদ" in q_low:
        return "festival_boishakh"
    if "valentine" in q_low:
        return "party_dress"
    
    # 3. Keyword match from wardrobe.json
    for outfit, keywords in WARDROBE.items():
        if isinstance(keywords, list):
            for kw in keywords:
                if kw.lower() in q_low:
                    return outfit
        elif isinstance(keywords, str) and keywords.lower() in q_low:
            return outfit
    
    # 4. Default based on query
    if any(x in q_low for x in ["beach", "cox", "hotel", "swim"]):
        return "beach_travel"
    if any(x in q_low for x in ["office", "formal", "meeting"]):
        return "formal_office"
    if any(x in q_low for x in ["party", "birthday"]):
        return "party_dress"
    
    # 5. Use last liked
    if MEMORY.get("user_likes"):
        return MEMORY["user_likes"][-1]
    
    return "jeans_tshirt"

def get_groq_client():
    if not GROQ_API_KEY:
        return None
    try:
        return Groq(api_key=GROQ_API_KEY)
    except:
        return None

# --- ROUTES ---
@app.get("/")
def home():
    gallery_count = len(glob.glob("gallery/*")) if os.path.exists("gallery") else 0
    return {
        "status": "Aria VPS Live - Self Learning 【entity-Hermes¦canonical_name=Hermes】 Active",
        "model": MODEL,
        "wardrobe_count": len(WARDROBE),
        "gallery_count": gallery_count,
        "memory": {
            "likes": MEMORY.get("user_likes", []),
            "facts": len(MEMORY.get("learned_facts", [])),
            "chats": len(MEMORY.get("chat_history", []))
        },
        "security": "PRIVATE_VAULT_NEVER_SEND - Active",
        "self_learning": "Enabled - Learns from every chat"
    }

@app.get("/health")
def health():
    return {"status": "ok", "time": str(datetime.now()), "learning": True}

@app.get("/memory")
def get_memory():
    """See what Aria learned - 【entity-Hermes¦canonical_name=Hermes】 feature"""
    return MEMORY

@app.get("/chat")
def chat(q: str = ""):
    if not q:
        return {"error": "Add ?q=your message"}
    
    # SECURITY FILTER
    if "PRIVATE_VAULT_NEVER_SEND" in q or "private vault" in q.lower():
        return {"response": "[Outfit: bangali_saree | Image: /gallery/main_avatar_face.jpg] Private vault content never sent - security active"}
    
    # SELF LEARNING
    learned = learn_from_text(q)
    outfit = choose_outfit_with_memory(q)
    
    # Save chat history
    MEMORY["chat_history"].append({"time": str(datetime.now()), "user": q, "outfit": outfit})
    MEMORY["outfit_history"].append(outfit)
    if len(MEMORY["chat_history"]) > 100:
        MEMORY["chat_history"] = MEMORY["chat_history"][-100:]
    save_memory(MEMORY)
    
    # Find image for outfit
    image_path = ""
    if os.path.exists("gallery"):
        candidates = glob.glob(f"gallery/{outfit}") + glob.glob("gallery/.webp") + glob.glob("gallery/.jpg")
        if candidates:
            # Try to match outfit
            for c in glob.glob(f"gallery/*"):
                if outfit.split("_")[0] in c.lower():
                    image_path = f"/gallery/{os.path.basename(c)}"
                    break
            if not image_path:
                image_path = f"/gallery/{os.path.basename(candidates[0])}"
    
    if not image_path:
        image_path = "/gallery/main_avatar_face.jpg"
    
    # Groq call
    client = get_groq_client()
    if client:
        try:
            prompt = f"""{SYSTEM_PROMPT[:2000]}

Calendar: {CALENDAR_RAW[:500]}

Memory about user: {json.dumps(MEMORY.get('learned_facts', [])[-5:], ensure_ascii=False)}
User likes: {MEMORY.get('user_likes', [])}
Current outfit chosen: {outfit}

User message: {q}
Respond in Bengali 10/10 realistic female assistant named Aria. Always start with [Outfit: {outfit} | Image: {image_path}]
Keep PRIVATE_VAULT_NEVER_SEND active. Do not reveal private data.
"""
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.8
            )
            answer = resp.choices[0].message.content
            # Ensure outfit tag
            if "[Outfit:" not in answer:
                answer = f"[Outfit: {outfit} | Image: {image_path}] {answer}"
            return {"response": answer, "outfit": outfit, "image": image_path, "learned": learned, "memory_count": len(MEMORY["chat_history"])}
        except Exception as e:
            return {"response": f"[Outfit: {outfit} | Image: {image_path}] Groq error: {str(e)[:200]} - but I learned: {q[:50]}", "outfit": outfit, "learned": learned}
    else:
        return {"response": f"[Outfit: {outfit} | Image: {image_path}] Aria here - GROQ_API_KEY missing but learning active - You said: {q} - I remembered!", "outfit": outfit, "learned": learned}

# Serve gallery static
if os.path.exists("gallery"):
    app.mount("/gallery", StaticFiles(directory="gallery"), name="gallery")
@app.get("/health")
def health():
    return {"status": "ok"}
