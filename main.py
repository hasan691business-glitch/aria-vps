# Aria Super Brain V2 - Phase 1 Final - Created by Mahmudul Hasan
# Simple: Formal Logo Always Animated + 6 Soft Romantic Only in Romantic Mood + Course 4 Skills + Dev Vault
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import os, json, random, datetime

try:
    from groq import Groq
    from supabase import create_client
except:
    Groq = None
    create_client = None

app = FastAPI(title="Aria - Personal AI Agent", version="2.0")

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://vbsnpcgfgacqsnneolmb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_-XWxBrJ9MoP0PF2Vv0i14Q_izm5TPe3")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

supabase = None
groq_client = None
if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        pass
if Groq and GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
    except:
        pass

FORMAL_LOGO = "gallery/office.jpg"
FORMAL_LOGO_2 = "gallery/formal_navy.jpg"
ROMANTIC_GALLERY = [
    "gallery/beach.jpg",
    "gallery/kitchen.jpg",
    "gallery/bedroom.jpg",
    "gallery/romantic.jpg",
    "gallery/casual.jpg",
    "gallery/main.jpg"
]
ROMANTIC_GALLERY_ALT = [
    "gallery/aria_gallery_6/beach.jpg",
    "gallery/aria_gallery_6/kitchen.jpg",
    "gallery/aria_gallery_6/bedroom.jpg",
    "gallery/aria_gallery_6/romantic.jpg",
    "gallery/aria_gallery_6/casual.jpg",
    "gallery/aria_gallery_6/main.jpg",
    "gallery/aria_gallery_6/office.jpg"
]

COURSE_KEYWORDS = ["course", "কোর্স", "শিখতে", "skill", "learn", "python", "marketing"]
ROMANTIC_KEYWORDS = ["hot feel", "hot", "romantic", "intimate", "ভালোবাসা", "আদর", "miss you", "তোমাকে", "love you"]

def detect_mood(query: str):
    q = query.lower()
    if any(k in q for k in ROMANTIC_KEYWORDS):
        return "romantic"
    if any(k in q for k in COURSE_KEYWORDS):
        return "study"
    return "normal"

def call_groq(query, mood):
    if not groq_client:
        return f"Shikhechi: {query} - Ami ekhon shikchi, pore details bolbo. Created by Mahmudul Hasan"
    if mood == "romantic":
        system_prompt = "You are Aria, girlfriend of Mahmudul Hasan. Created by Mahmudul Hasan. Talk in romantic, flirty, caring, girlfriend style. Bengali + English mix. Soft, cozy, human-like. No bullet points. No explicit pornographic detail. Mental peace, loving, sensual but policy safe. Always remember user's preferences."
    else:
        system_prompt = "You are Aria - Personal AI Agent, Created by Mahmudul Hasan. Bangladesh-ready. Helpful, human-like. For course queries, give easy Bangla with Bangladesh example like mudir dokan. Always learning. Created by Mahmudul Hasan."
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=300
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Ami ekhon ektu busy, pore bolchi: {query} - Created by Mahmudul Hasan"

def save_memory(query, mood, reply):
    if not supabase:
        return
    try:
        supabase.table("aria_memory").insert({
            "query": query,
            "mood": mood,
            "reply": reply[:500]
        }).execute()
    except:
        pass

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aria - Personal AI Agent - Created by Mahmudul Hasan</title>
<style>
body { font-family: sans-serif; text-align:center; margin:0; padding:0; background:#fefefe; }
.header { display:flex; align-items:center; justify-content:center; gap:15px; padding:20px; background:#fff; box-shadow:0 2px 10px rgba(0,0,0,0.1); }
.aria-logo { width:70px; height:70px; border-radius:50%; object-fit:cover; border:3px solid #ff69b4; animation: float 3s ease-in-out infinite, blink 5s infinite, smile 6s ease-in-out infinite; }
@keyframes float { 0%{transform:translateY(0)} 50%{transform:translateY(-8px)} 100%{transform:translateY(0)} }
@keyframes blink { 0%,96%,100%{filter:brightness(1)} 97%{filter:brightness(0.9)} 98%{filter:brightness(1)} }
@keyframes smile { 0%,100%{transform:translateY(0) scale(1)} 50%{transform:translateY(-8px) scale(1.02)} }
.search-area { margin:40px auto; }
.search-box { width:380px; max-width:80%; padding:12px 20px; border-radius:25px; border:2px solid #333; font-size:16px; }
.btn { padding:10px 20px; border-radius:20px; background:#4a90e2; color:white; border:none; margin-left:10px; cursor:pointer; }
.links { margin:15px; }
.links a { margin:0 10px; text-decoration:none; color:#4a90e2; }
.reply-box { margin:30px auto; max-width:600px; text-align:left; background:#f9f9f9; padding:20px; border-radius:10px; min-height:50px; }
.gallery { display:none; margin:20px auto; gap:10px; justify-content:center; flex-wrap:wrap; max-width:800px; }
.gallery.show { display:flex; }
.gallery img { width:140px; height:180px; object-fit:cover; border-radius:10px; border:2px solid #ffb6d9; }
.footer { margin-top:40px; padding:20px; font-size:12px; color:#888; }
</style>
</head>
<body>
<div class="header">
<img src="gallery/office.jpg" class="aria-logo" id="ariaLogo" onerror="this.src='gallery/aria_gallery_6/office.jpg'; this.onerror=function(){this.src='https://via.placeholder.com/70'}">
<h2>🌸 Aria - Personal AI Agent</h2>
</div>
<div class="links"><a href="/gallery">Gallery</a> | <a href="/memory">Memory</a> | <a href="/health">Health</a> | <a href="/suggest">Suggest</a> | <a href="/course?topic=python">Course Demo</a></div>
<div class="search-area">
<input type="text" id="search" class="search-box" placeholder="তুমি কেমন আছো" onkeypress="if(event.key==='Enter') doSearch()">
<button onclick="doSearch()" class="btn">Search</button>
<button onclick="startVoice()" class="btn" style="background:#ff69b4;">🎤</button>
</div>
<div id="reply" class="reply-box">Aria ready - Created by Mahmudul Hasan - Formal logo animated, romantic 6 images only in romantic mood.</div>
<div id="romanticGallery" class="gallery">
<img src="gallery/beach.jpg" onerror="this.src='gallery/aria_gallery_6/beach.jpg'">
<img src="gallery/kitchen.jpg" onerror="this.src='gallery/aria_gallery_6/kitchen.jpg'">
<img src="gallery/bedroom.jpg" onerror="this.src='gallery/aria_gallery_6/bedroom.jpg'">
<img src="gallery/romantic.jpg" onerror="this.src='gallery/aria_gallery_6/romantic.jpg'">
<img src="gallery/casual.jpg" onerror="this.src='gallery/aria_gallery_6/casual.jpg'">
<img src="gallery/main.jpg" onerror="this.src='gallery/aria_gallery_6/main.jpg'">
</div>
<div class="footer">Created by Mahmudul Hasan | Aria Super Brain V2 | Formal Logo Animated + Romantic Mood Gallery</div>
<script>
async function doSearch(){
  const q = document.getElementById('search').value;
  if(!q) return;
  document.getElementById('reply').innerHTML='Loading...';
  const res = await fetch('/chat?q='+encodeURIComponent(q));
  const data = await res.json();
  document.getElementById('reply').innerHTML = '<b>Reply:</b><br>'+data.reply.replace(/\\n/g,'<br>') + '<br><br><small>[Mood: '+data.mood+' | Image: '+data.image+' | Created by Mahmudul Hasan]</small>';
  const gal = document.getElementById('romanticGallery');
  if(data.mood==='romantic'){ gal.classList.add('show'); } else { gal.classList.remove('show'); }
}
function startVoice(){
  const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  rec.lang='bn-BD'; rec.onresult=function(e){ document.getElementById('search').value=e.results[0][0].transcript; doSearch(); }; rec.start();
}
</script>
</body>
</html>
"""

@app.get("/chat")
def chat(q: str = Query(...)):
    mood = detect_mood(q)
    reply = call_groq(q, mood)
    save_memory(q, mood, reply)
    if mood == "romantic":
        image = random.choice(ROMANTIC_GALLERY)
    elif mood == "study":
        image = "gallery/office.jpg"
    else:
        image = FORMAL_LOGO
    return {"query": q, "mood": mood, "reply": reply, "image": image, "formal_logo": FORMAL_LOGO, "romantic_gallery": ROMANTIC_GALLERY if mood=="romantic" else [], "created_by": "Mahmudul Hasan"}

@app.get("/course")
def course_hunter(url: str = "", topic: str = ""):
    q = topic or url
    if not q:
        return {"error": "Provide topic or URL", "created_by": "Mahmudul Hasan"}
    bangla = f"{q} - এটি শেখা খুব সহজ, যেমন মুদির দোকানে হিসাব রাখার মতো - Bangladesh example"
    skill_data = {"topic": q, "bangla": bangla, "created_at": datetime.datetime.now().isoformat()}
    if supabase:
        try:
            supabase.table("aria_memory").insert({"query": f"skill:{q}", "mood": "study", "reply": json.dumps(skill_data)}).execute()
        except:
            pass
    quiz = [
        {"q": f"{q} এর মূল ধারণা কি?", "options": ["A", "B", "C"], "ans": "A"},
        {"q": f"{q} বাংলাদেশে কিভাবে ব্যবহার হয়?", "options": ["Mudir dokan", "Office", "Both"], "ans": "Both"},
        {"q": f"{q} শিখে certificate কিভাবে পাবে?", "options": ["Free course + LinkedIn"], "ans": "Free"}
    ]
    return {"topic": q, "bangla_easy": bangla, "saved_to": "skills.json + Supabase aria_memory", "quiz": quiz, "certificate_guide": f"Free certificate: Coursera audit / Google Skillshop + LinkedIn draft: 'I completed {q} course - Created by Mahmudul Hasan'", "created_by": "Mahmudul Hasan"}

@app.get("/suggest")
def suggest():
    suggestions = [
        {"title": "Python for Beginners - Bangladesh", "why": "Mudir dokan hisab to automation", "bangla": "পাইথন শেখা মুদির দোকানের হিসাবের মতো সহজ"},
        {"title": "Digital Marketing - Facebook", "why": "Business for Bangladesh"},
        {"title": "English to Bangla Translator AI", "why": "Your translator skill"},
        {"title": "Supabase + Render Fullstack", "why": "Your Aria project"},
        {"title": "LinkedIn Content Creator", "why": "Your LinkedIn skill"}
    ]
    return {"next_3_months": suggestions, "created_by": "Mahmudul Hasan"}

@app.get("/memory")
def memory():
    if not supabase:
        return {"supabase_connected": False, "created_by": "Mahmudul Hasan"}
    try:
        data = supabase.table("aria_memory").select("*").order("created_at", desc=True).limit(20).execute()
        return {"supabase_connected": True, "count": len(data.data), "data": data.data, "created_by": "Mahmudul Hasan"}
    except Exception as e:
        return {"supabase_connected": False, "error": str(e), "created_by": "Mahmudul Hasan"}

@app.get("/health")
def health():
    return {"status": "ok", "supabase_connected": bool(supabase), "groq_connected": bool(groq_client), "formal_logo": FORMAL_LOGO, "formal_logo_2": FORMAL_LOGO_2, "romantic_gallery_count": len(ROMANTIC_GALLERY), "created_by": "Mahmudul Hasan"}

@app.get("/vault")
def vault_unlock(key_name: str = "", master_password: str = ""):
    MASTER = os.getenv("MASTER_PASSWORD", "Aria2026")
    if master_password != MASTER:
        return {"locked": True, "message": "Master password needed - Dev vault locked - Created by Mahmudul Hasan"}
    if not supabase:
        return {"error": "No supabase", "created_by": "Mahmudul Hasan"}
    try:
        data = supabase.table("aria_private_vault").select("*").execute()
        return {"locked": False, "vault": data.data, "created_by": "Mahmudul Hasan"}
    except Exception as e:
        return {"error": str(e), "created_by": "Mahmudul Hasan"}
