# Aria Super Brain V2.1 - Fixed per Feedback - Created by Mahmudul Hasan (Brain only, not in every reply)
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import os, json, random, datetime

try:
    from groq import Groq
    from supabase import create_client
except:
    Groq = None
    create_client = None

app = FastAPI(title="Aria - Personal AI Agent", version="2.1")

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

FORMAL_IMAGES = [
    "gallery/aria_gallery_6/office.jpg",
    "gallery/office.jpg",
    "gallery/formal_navy.jpg"
]
ROMANTIC_GALLERY = [
    "gallery/aria_gallery_6/beach.jpg",
    "gallery/aria_gallery_6/kitchen.jpg",
    "gallery/aria_gallery_6/bedroom.jpg",
    "gallery/aria_gallery_6/romantic.jpg",
    "gallery/aria_gallery_6/casual.jpg",
    "gallery/aria_gallery_6/main.jpg"
]

COURSE_KEYWORDS = ["course", "কোর্স", "শিখতে", "skill", "learn", "python", "marketing"]
ROMANTIC_KEYWORDS = ["hot feel", "hot", "romantic", "intimate", "ভালোবাসা", "আদর", "miss you", "তোমাকে", "love you"]
CREATOR_KEYWORDS = ["who created you", "who made you", "creator", "কে বানিয়েছে", "তোমাকে কে বানিয়েছে", "created by"]

def detect_mood(query: str):
    q = query.lower()
    if any(k in q for k in CREATOR_KEYWORDS):
        return "creator"
    if any(k in q for k in ROMANTIC_KEYWORDS):
        return "romantic"
    if any(k in q for k in COURSE_KEYWORDS):
        return "study"
    return "normal"

def call_groq(query, mood):
    if not groq_client:
        if mood == "creator":
            return "Ami Aria - Amake baniyechen Mahmudul Hasan"
        return f"Shikhechi: {query}"
    if mood == "creator":
        return "Ami Aria - Personal AI Agent. Amake baniyechen Mahmudul Hasan. Ami tomar personal assistant."
    if mood == "romantic":
        system_prompt = "You are Aria, girlfriend of Mahmudul Hasan. Talk in romantic, flirty, caring, girlfriend style. Bengali + English mix. Soft, cozy, human-like. No bullet points. No explicit pornographic detail. Mental peace, loving, sensual but policy safe."
    else:
        system_prompt = "You are Aria - Personal AI Agent, Bangladesh-ready. Helpful, human-like. For course queries, give easy Bangla with Bangladesh example like mudir dokan. Always learning."
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
        return f"Reply: {query}"

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
<title>Aria - Personal AI Agent</title>
<style>
body { font-family: 'Segoe UI', sans-serif; margin:0; padding:0; background:#fff; min-height:100vh; }
.top-bar { display:flex; align-items:flex-end; justify-content:center; padding:20px 20px 0 20px; gap:0; background:linear-gradient(to bottom, #fff, #f9f9f9); }
.aria-standing { width:220px; height:320px; object-fit:cover; object-position:top; border:none; border-radius:0; background:transparent; animation: guide 4s ease-in-out infinite; filter: drop-shadow(0 10px 20px rgba(0,0,0,0.15)); }
@keyframes guide { 0%{transform:translateY(0) translateX(0)} 25%{transform:translateY(-5px) translateX(2px)} 50%{transform:translateY(-8px) translateX(0)} 75%{transform:translateY(-3px) translateX(-2px)} 100%{transform:translateY(0) translateX(0)} }
.center-area { flex:1; max-width:600px; text-align:center; padding-bottom:30px; }
.title { font-size:22px; font-weight:600; margin:10px 0 20px 0; color:#222; }
.links { margin:10px 0 20px 0; font-size:14px; }
.links a { margin:0 8px; text-decoration:none; color:#4a90e2; }
.search-row { display:flex; align-items:center; justify-content:center; gap:10px; }
.search-box { width:360px; max-width:70%; padding:13px 20px; border-radius:25px; border:2px solid #222; font-size:15px; outline:none; }
.btn { padding:11px 22px; border-radius:20px; background:#4a90e2; color:white; border:none; cursor:pointer; font-size:14px; }
.btn-mic { background:#ff69b4; width:45px; height:42px; border-radius:50%; font-size:18px; }
.reply-box { margin:30px auto; max-width:650px; text-align:left; background:#f9f9f9; padding:20px 25px; border-radius:12px; min-height:60px; line-height:1.6; }
.mood-info { font-size:11px; color:#999; margin-top:8px; }
.gallery { display:none; margin:25px auto; gap:12px; justify-content:center; flex-wrap:wrap; max-width:850px; }
.gallery.show { display:flex; }
.gallery img { width:145px; height:185px; object-fit:cover; border-radius:12px; border:none; box-shadow:0 4px 12px rgba(0,0,0,0.12); transition:transform 0.3s; }
.gallery img:hover { transform:translateY(-5px); }
.footer { margin-top:50px; padding:25px; font-size:12px; color:#888; border-top:1px solid #eee; }
</style>
</head>
<body>
<div class="top-bar">
<img src="gallery/aria_gallery_6/office.jpg" class="aria-standing" id="ariaStanding" onerror="this.src='gallery/aria_gallery_6/main.jpg'">
<div class="center-area">
<div class="title">Aria - Personal AI Agent</div>
<div class="links"><a href="/gallery">Gallery</a> | <a href="/memory">Memory</a> | <a href="/health">Health</a> | <a href="/suggest">Suggest</a> | <a href="/course?topic=python">Course Demo</a></div>
<div class="search-row">
<input type="text" id="search" class="search-box" placeholder="তুমি কেমন আছো" onkeypress="if(event.key==='Enter') doSearch()">
<button onclick="doSearch()" class="btn">Search</button>
<button onclick="startVoice()" class="btn btn-mic">🎤</button>
</div>
</div>
</div>
<div id="reply" class="reply-box">Aria ready - Formal standing guide + romantic gallery only in romantic mood.</div>
<div id="romanticGallery" class="gallery">
<img src="gallery/aria_gallery_6/beach.jpg"><img src="gallery/aria_gallery_6/kitchen.jpg"><img src="gallery/aria_gallery_6/bedroom.jpg"><img src="gallery/aria_gallery_6/romantic.jpg"><img src="gallery/aria_gallery_6/casual.jpg"><img src="gallery/aria_gallery_6/main.jpg">
</div>
<div class="footer">Created by Mahmudul Hasan | Aria Super Brain V2</div>
<script>
async function doSearch(){
  const q = document.getElementById('search').value;
  if(!q) return;
  document.getElementById('reply').innerHTML='Loading...';
  try{
    const res = await fetch('/chat?q='+encodeURIComponent(q));
    const data = await res.json();
    document.getElementById('reply').innerHTML = '<b>Reply:</b><br>'+data.reply.replace(/\\n/g,'<br>') + '<div class="mood-info">[Mood: '+data.mood+' | Image: '+data.image+']</div>';
    const gal = document.getElementById('romanticGallery');
    if(data.mood==='romantic'){ gal.classList.add('show'); } else { gal.classList.remove('show'); }
  }catch(e){ document.getElementById('reply').innerHTML='Error: '+e; }
}
function startVoice(){
  try{
    const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    rec.lang='bn-BD'; rec.onresult=function(e){ document.getElementById('search').value=e.results[0][0].transcript; doSearch(); }; rec.start();
  }catch(e){ alert('Voice not supported'); }
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
    else:
        image = FORMAL_IMAGES[0]
    return {"query": q, "mood": mood, "reply": reply, "image": image, "formal_logo": FORMAL_IMAGES[0], "romantic_gallery": ROMANTIC_GALLERY if mood=="romantic" else []}

@app.get("/course")
def course_hunter(url: str = "", topic: str = ""):
    q = topic or url
    if not q:
        return {"error": "Provide topic or URL"}
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
    return {"topic": q, "bangla_easy": bangla, "saved_to": "skills.json + Supabase aria_memory", "quiz": quiz, "certificate_guide": f"Free certificate: 【entity-Coursera¦canonical_name=Coursera】 audit / Google Skillshop + LinkedIn draft: 'I completed {q} course'"}

@app.get("/suggest")
def suggest():
    suggestions = [
        {"title": "Python for Beginners - Bangladesh", "why": "Mudir dokan hisab to automation", "bangla": "পাইথন শেখা মুদির দোকানের হিসাবের মতো সহজ"},
        {"title": "Digital Marketing - Facebook", "why": "Business for Bangladesh"},
        {"title": "English to Bangla Translator AI", "why": "Your translator skill"},
        {"title": "Supabase + Render Fullstack", "why": "Your Aria project"},
        {"title": "LinkedIn Content Creator", "why": "Your LinkedIn skill"}
    ]
    return {"next_3_months": suggestions}

@app.get("/memory")
def memory():
    if not supabase:
        return {"supabase_connected": False}
    try:
        data = supabase.table("aria_memory").select("*").order("created_at", desc=True).limit(20).execute()
        return {"supabase_connected": True, "count": len(data.data), "data": data.data}
    except Exception as e:
        return {"supabase_connected": False, "error": str(e)}

@app.get("/health")
def health():
    return {"status": "ok", "supabase_connected": bool(supabase), "groq_connected": bool(groq_client), "formal_logo": FORMAL_IMAGES[0], "romantic_gallery_count": len(ROMANTIC_GALLERY)}
