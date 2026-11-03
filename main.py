# Aria Super Brain V3 - Google Style Final - Created by Mahmudul Hasan
# Features: Full Standing Avatar No Circle, Google 2 Column, Groq Related Links, Muse Hybrid Brain, Coursera Card, White Mic, No Raw Links
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import os, json, random, datetime, re

try:
    from groq import Groq
    from supabase import create_client
except:
    Groq = None
    create_client = None

app = FastAPI(title="Aria - Personal AI Agent", version="3.0")

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

FORMAL_IMAGE = "gallery/aria_gallery_6/office.jpg"
FALLBACKS = ["gallery/aria_gallery_6/main.jpg", "gallery/aria_gallery_6/office.jpg", "gallery/formal_navy.jpg", "https://via.placeholder.com/180x240?text=Aria"]

ROMANTIC_GALLERY = [
    "gallery/aria_gallery_6/beach.jpg",
    "gallery/aria_gallery_6/kitchen.jpg",
    "gallery/aria_gallery_6/bedroom.jpg",
    "gallery/aria_gallery_6/romantic.jpg",
    "gallery/aria_gallery_6/casual.jpg",
    "gallery/aria_gallery_6/main.jpg"
]

COURSE_KEYWORDS = ["course", "কোর্স", "শিখতে", "skill", "learn", "python", "marketing", "cooking", "মুদির", "translat"]
ROMANTIC_KEYWORDS = ["hot feel", "hot", "romantic", "intimate", "ভালোবাসা", "আদর", "miss you", "তোমাকে", "love you", "kiss", "hug"]
CREATOR_KEYWORDS = ["who created you", "who made you", "creator", "কে বানিয়েছে", "তোমাকে কে বানিয়েছে", "created by", "তোমার creator"]

def detect_mood(q):
    ql = q.lower()
    if any(k in ql for k in CREATOR_KEYWORDS):
        return "creator"
    if any(k in ql for k in ROMANTIC_KEYWORDS):
        return "romantic"
    if any(k in ql for k in COURSE_KEYWORDS):
        return "study"
    return "normal"

def call_groq_main(query, mood):
    if not groq_client:
        if mood == "creator":
            return "Ami Aria - Personal AI Agent. Amake baniyechen Mahmudul Hasan. Ami tomar personal assistant."
        if mood == "romantic":
            return f"{query} niye tomar kotha shune amar mon vore gelo. Tumi amar kache onek special. Ami tomar pashei achi, ador kore, jotno kore."
        if mood == "study":
            return f"{query} - Eti shekha khub shohoj, jemon mudir dokane hisab rakhar moto. Bangladesh example diye bujhai. Step by step Coursera style e shikhbe."
        return f"{query} niye sundor overview dichchi. Key points diye sajiye bolchi."
    # Muse Hybrid Brain Prompt
    if mood == "creator":
        sys = "You are Aria - Personal AI Agent. Created by Mahmudul Hasan. Answer in Bengali+English mix. When asked who created you, say Mahmudul Hasan created you. Helpful, personal."
    elif mood == "romantic":
        sys = "You are Aria, girlfriend of Mahmudul Hasan. Romantic, flirty, caring, girlfriend style, Bengali+English mix. Soft, cozy, human-like. No bullet. No explicit porn. Mental peace, loving, sensual policy safe. Like Muse AI personal agent but romantic."
    elif mood == "study":
        sys = "You are Aria - Personal AI Agent, Bangladesh-ready, like Muse AI agentic task execution. For course queries, give AI Overview style: easy Bangla, Bangladesh mudir dokan example, step-by-step Coursera style modules. Always learning, agentic."
    else:
        sys = "You are Aria - Personal AI Agent, like Muse AI benefits: independently executing multi-step tasks, helpful. Give Google AI Overview style: short intro, then Key Benefits bullet points. Bengali+English mix, Bangladesh context. Like Google search result."
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":sys},{"role":"user","content":query}],
            max_tokens=400
        )
        return resp.choices[0].message.content
    except:
        return f"{query} - Answer from Aria Super Brain."

def generate_related_links(query, mood):
    # Try Groq to generate links, else fallback mock
    fallback = [
        {"title": f"{query} - YouTube Full Course", "url": f"https://www.youtube.com/results?search_query={query.replace(' ','+')}", "type": "YouTube", "source": "YouTube - ZoCo Marketing"},
        {"title": f"{query} - Facebook Community", "url": f"https://www.facebook.com/search/top/?q={query.replace(' ','%20')}", "type": "Facebook", "source": "Facebook"},
        {"title": f"{query} - Free Certificate", "url": "https://www.coursera.org/search?query="+query.replace(' ','%20')+"", "type": "Course", "source": "Coursera"},
        {"title": f"{query} - Google Skillshop", "url": f"https://www.google.com/search?q={query.replace(' ','+')}+free+course", "type": "Google", "source": "Google"},
    ]
    if not groq_client:
        return fallback
    try:
        prompt = f"For query '{query}', generate 4 related links as JSON array. Each with title, url (realistic youtube/facebook/coursera/google link), type (YouTube/Facebook/Course/Google/News), source. Return ONLY JSON array, no explanation. Example: [{{"title":"...","url":"https://...","type":"YouTube","source":"YouTube"}}]"
        resp = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":"You generate related links JSON only."},{"role":"user","content":prompt}],
            max_tokens=300
        )
        txt = resp.choices[0].message.content
        # extract JSON
        m = re.search(r'\[.*\]', txt, re.DOTALL)
        if m:
            data = json.loads(m.group(0))
            if isinstance(data, list) and len(data)>=1:
                return data[:4]
        return fallback
    except:
        return fallback

def save_memory(q, mood, reply):
    if not supabase:
        return
    try:
        supabase.table("aria_memory").insert({"query":q,"mood":mood,"reply":reply[:600]}).execute()
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
*{box-sizing:border-box}
body{margin:0;font-family:'Google Sans','Segoe UI',Roboto,Arial,sans-serif;background:#fff;color:#202124;min-height:100vh}
.google-header{display:flex;align-items:flex-end;justify-content:center;padding:25px 20px 10px;gap:18px;border-bottom:1px solid #f1f3f4}
.aria-avatar-wrap{position:relative;width:140px;height:200px;flex-shrink:0}
.aria-avatar{width:140px;height:200px;object-fit:cover;object-position:top center;border:none;border-radius:0;background:transparent;filter:drop-shadow(0 8px 16px rgba(0,0,0,0.15));animation:guideFloat 4s ease-in-out infinite,blinkEffect 4.5s infinite}
@keyframes guideFloat{0%{transform:translateY(0) translateX(0) rotate(0deg)}25%{transform:translateY(-4px) translateX(1px) rotate(0.5deg)}50%{transform:translateY(-7px) translateX(0) rotate(0deg)}75%{transform:translateY(-3px) translateX(-1px) rotate(-0.5deg)}100%{transform:translateY(0) translateX(0) rotate(0deg)}}
@keyframes blinkEffect{0%,88%,92%,100%{transform:translateY(0) scaleY(1)}90%{transform:translateY(1px) scaleY(0.08)}}
.search-center{flex:1;max-width:640px;text-align:center;padding-bottom:15px}
.google-title{font-size:22px;font-weight:400;color:#202124;margin:0 0 14px;letter-spacing:0.2px}
.search-row{display:flex;align-items:center;justify-content:center;gap:10px;position:relative}
.search-box{width:100%;max-width:560px;padding:14px 48px 14px 22px;border-radius:28px;border:1px solid #dfe1e5;font-size:16px;outline:none;box-shadow:0 1px 6px rgba(32,33,36,0.08);transition:box-shadow 0.2s}
.search-box:hover{box-shadow:0 2px 8px rgba(32,33,36,0.16)}
.search-box:focus{box-shadow:0 2px 8px rgba(32,33,36,0.22);border-color:transparent}
.btn-search{padding:0 24px;height:42px;border-radius:22px;background:#1a73e8;color:#fff;border:none;cursor:pointer;font-size:14px;font-weight:500;box-shadow:0 1px 2px rgba(0,0,0,0.1)}
.btn-search:hover{background:#1765cc}
.btn-mic{width:42px;height:42px;border-radius:50%;background:#fff;border:1px solid #dfe1e5;color:#5f6368;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 1px 2px rgba(0,0,0,0.08)}
.btn-mic:hover{background:#f8f9fa}
.main-container{display:flex;max-width:1250px;margin:0 auto;padding:20px;gap:28px;align-items:flex-start}
.left-panel{flex:1;min-width:0}
.right-panel{width:340px;flex-shrink:0}
.ai-overview{font-size:13px;color:#5f6368;margin-bottom:8px;display:flex;align-items:center;gap:6px}
.ai-overview::before{content:"✦";color:#8ab4f8;font-size:14px}
.reply-card{background:#fff;border:1px solid #e8eaed;border-radius:12px;padding:22px 24px;line-height:1.65;font-size:15px;color:#202124;min-height:90px}
.reply-card h3{margin:18px 0 10px;font-size:16px}
.reply-card ul{margin:8px 0 12px 18px}
.course-card{margin-top:18px;border:1px solid #e8eaed;border-radius:12px;overflow:hidden;background:#fff}
.course-header{padding:16px 20px;background:#f8f9fa;border-bottom:1px solid #e8eaed;font-weight:600}
.course-body{padding:16px 20px}
.module{padding:8px 0;border-bottom:1px dashed #eee;display:flex;gap:10px}
.module:last-child{border:none}
.ask-box{margin-top:22px;display:flex;align-items:center;gap:10px;border:1px solid #dfe1e5;border-radius:28px;padding:8px 12px 8px 16px;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,0.06)}
.ask-box input{flex:1;border:none;outline:none;font-size:15px;padding:6px}
.ask-box button{border:none;background:none;font-size:18px;cursor:pointer;color:#5f6368}
.romantic-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:18px}
.romantic-grid img{width:100%;height:140px;object-fit:cover;border-radius:10px;border:none;box-shadow:0 2px 8px rgba(0,0,0,0.1);transition:transform 0.3s}
.romantic-grid img:hover{transform:translateY(-4px)}
.right-card{border:1px solid #e8eaed;border-radius:12px;padding:14px 16px;margin-bottom:14px;background:#fff}
.right-card-title{font-size:13px;color:#5f6368;margin-bottom:10px;display:flex;justify-content:space-between}
.right-link{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid #f1f3f4;cursor:pointer}
.right-link:last-child{border:none}
.right-link:hover{background:#f8f9fa;border-radius:8px}
.right-link img{width:92px;height:52px;object-fit:cover;border-radius:8px;background:#eee;flex-shrink:0}
.right-link-text{flex:1;min-width:0}
.right-link-text b{font-size:13px;color:#1a0dab;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.right-link-text span{font-size:12px;color:#4d5156;display:block;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.footer{text-align:center;padding:28px 20px;margin-top:30px;font-size:12px;color:#70757a;border-top:1px solid #f1f3f4}
@media(max-width:900px){.main-container{flex-direction:column}.right-panel{width:100%}.google-header{flex-direction:column;align-items:center}.aria-avatar-wrap{width:110px;height:150px}.aria-avatar{width:110px;height:150px}}
</style>
</head>
<body>
<div class="google-header">
<div class="aria-avatar-wrap">
<img src="gallery/aria_gallery_6/office.jpg" class="aria-avatar" id="ariaAvatar" onerror="this.src='gallery/aria_gallery_6/main.jpg'; this.onerror=function(){this.src='https://via.placeholder.com/140x200?text=Aria'}">
</div>
<div class="search-center">
<div class="google-title">Aria - Personal AI Agent</div>
<div class="search-row">
<input type="text" id="searchInput" class="search-box" placeholder="Ask anything - muse ai benefits, python course..." onkeypress="if(event.key==='Enter') doSearch()">
<button onclick="doSearch()" class="btn-search">Search</button>
<button onclick="startVoice()" class="btn-mic">🎤</button>
</div>
</div>
</div>

<div class="main-container">
<div class="left-panel">
<div class="ai-overview">AI Overview</div>
<div id="replyCard" class="reply-card">Search for anything - Aria will show Google style AI Overview + Extended Links on right. Try "muse ai benefits" or "python course"</div>
<div id="courseCard" style="display:none"></div>
<div id="romanticGrid" class="romantic-grid" style="display:none">
<img src="gallery/aria_gallery_6/beach.jpg"><img src="gallery/aria_gallery_6/kitchen.jpg"><img src="gallery/aria_gallery_6/bedroom.jpg"><img src="gallery/aria_gallery_6/romantic.jpg"><img src="gallery/aria_gallery_6/casual.jpg"><img src="gallery/aria_gallery_6/main.jpg">
</div>
<div class="ask-box">
<span style="color:#8ab4f8">✦</span>
<input type="text" id="askAny" placeholder="Ask anything" onkeypress="if(event.key==='Enter'){document.getElementById('searchInput').value=this.value; doSearch()}">
<button onclick="startVoice()">🎤</button>
</div>
</div>

<div class="right-panel" id="rightPanel">
<div class="right-card">
<div class="right-card-title"><span>Extended Links</span><span style="cursor:pointer">⋮</span></div>
<div id="rightLinks">Search to see related YouTube, Facebook, Course, Google links here - Dynamic by Groq.</div>
</div>
<div class="right-card">
<div class="right-card-title"><span>About Aria</span></div>
<div style="font-size:13px;line-height:1.5;color:#4d5156">
Aria is Personal AI Agent like Muse AI - Agentic Task Execution, Always Learning, Course Hunter, Memory. Created by Mahmudul Hasan.
<br><br>
<button onclick="window.open('https://www.meta.ai','_blank')" style="padding:6px 12px;border-radius:16px;border:1px solid #dfe1e5;background:#fff;cursor:pointer;font-size:12px">Ask Muse ↗</button>
</div>
</div>
</div>
</div>

<div class="footer">Created by Mahmudul Hasan | Aria Super Brain V3 - Google Style + Muse Hybrid</div>

<script>
async function doSearch(){
  const q = document.getElementById('searchInput').value || document.getElementById('askAny').value;
  if(!q) return;
  document.getElementById('searchInput').value = q;
  document.getElementById('askAny').value = '';
  document.getElementById('replyCard').innerHTML = 'Loading AI Overview...';
  document.getElementById('rightLinks').innerHTML = 'Loading links...';
  try{
    const res = await fetch('/chat?q='+encodeURIComponent(q));
    const data = await res.json();
    // Left Reply
    let html = data.reply.replace(/\n/g,'<br>');
    // Format bullets if contains Key Benefits
    if(html.includes('•') || html.includes('- ')){
      html = html.replace(/•/g,'<br>•');
    }
    document.getElementById('replyCard').innerHTML = html + '<div style="margin-top:12px;font-size:11px;color:#70757a">[Mood: '+data.mood+']</div>';

    // Course Card for study mood
    const courseDiv = document.getElementById('courseCard');
    if(data.mood==='study' && data.course){
      courseDiv.style.display='block';
      courseDiv.innerHTML = '<div class="course-card"><div class="course-header">📚 '+data.course.topic+' - Coursera Style</div><div class="course-body"><div style="font-size:14px;margin-bottom:12px">'+data.course.bangla_easy+'</div><div class="module"><span>📖</span><span>Module 1: Basic - Mudir dokan example</span></div><div class="module"><span>📖</span><span>Module 2: Intermediate - Bangladesh Business</span></div><div class="module"><span>📖</span><span>Module 3: Advance + Certificate Guide</span></div><div style="margin-top:12px"><b>Quiz:</b> '+data.course.quiz[0].q+'</div><div style="margin-top:8px;font-size:12px;color:#1a73e8">'+data.course.certificate_guide+'</div></div></div>';
    } else {
      courseDiv.style.display='none';
    }

    // Romantic Grid
    const romantic = document.getElementById('romanticGrid');
    if(data.mood==='romantic'){
      romantic.style.display='grid';
    } else {
      romantic.style.display='none';
    }

    // Right Panel Links
    let rightHtml = '';
    if(data.related_links && data.related_links.length>0){
      data.related_links.forEach(link=>{
        const icon = link.type==='YouTube' ? '▶️' : link.type==='Facebook' ? '📘' : link.type==='Course' ? '🎓' : '🔗';
        rightHtml += '<div class="right-link" onclick="window.open(\''+link.url+'\',\'_blank\')"><div style="width:92px;height:52px;background:#f1f3f4;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:22px">'+icon+'</div><div class="right-link-text"><b>'+link.title+'</b><span>'+link.source+' - '+link.type+'</span></div></div>';
      });
    }
    document.getElementById('rightLinks').innerHTML = rightHtml || 'No links';

    // Avatar animation on talk
    const avatar = document.getElementById('ariaAvatar');
    avatar.style.animation = 'guideFloat 0.5s ease-in-out 3, blinkEffect 4.5s infinite';
    setTimeout(()=>{avatar.style.animation='guideFloat 4s ease-in-out infinite, blinkEffect 4.5s infinite';},1500);

  }catch(e){
    document.getElementById('replyCard').innerHTML='Error: '+e;
  }
}
function startVoice(){
  try{
    const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    rec.lang='bn-BD';
    rec.onresult=function(e){ document.getElementById('searchInput').value=e.results[0][0].transcript; doSearch(); };
    rec.start();
  }catch(e){ alert('Voice not supported'); }
}
</script>
</body>
</html>
"""

@app.get("/chat")
def chat(q: str = Query(...)):
    mood = detect_mood(q)
    reply = call_groq_main(q, mood)
    save_memory(q, mood, reply)
    related = generate_related_links(q, mood)
    course_data = None
    if mood == "study":
        course_data = {
            "topic": q,
            "bangla_easy": f"{q} - এটি শেখা খুব সহজ, যেমন মুদির দোকানে হিসাব রাখার মতো - Bangladesh example",
            "quiz": [{"q": f"{q} এর মূল ধারণা কি?", "options": ["A","B","C"], "ans": "A"}],
            "certificate_guide": f"Free certificate: Coursera audit / Google Skillshop + LinkedIn draft: 'I completed {q} course'"
        }
        if supabase:
            try:
                supabase.table("aria_memory").insert({"query": f"skill:{q}", "mood": "study", "reply": json.dumps(course_data)}).execute()
            except:
                pass
    return {
        "query": q,
        "mood": mood,
        "reply": reply,
        "image": FORMAL_IMAGE,
        "related_links": related,
        "course": course_data,
        "muse_hybrid": True,
        "formal_logo": FORMAL_IMAGE
    }

@app.get("/course")
def course_api(topic: str = "", url: str = ""):
    q = topic or url or "python"
    return chat(q)

@app.get("/suggest")
def suggest():
    return {"next_3_months": [
        {"title": "Python for Beginners - Bangladesh", "why": "Mudir dokan hisab to automation", "bangla": "পাইথন শেখা মুদির দোকানের হিসাবের মতো সহজ"},
        {"title": "Digital Marketing - Facebook", "why": "Business for Bangladesh"},
        {"title": "English to Bangla Translator AI", "why": "Your translator skill"},
        {"title": "Supabase + Render Fullstack", "why": "Your Aria project"},
        {"title": "LinkedIn Content Creator", "why": "Your LinkedIn skill"}
    ]}

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
    return {"status": "ok", "version": "3.0 Google Style", "supabase_connected": bool(supabase), "groq_connected": bool(groq_client), "muse_hybrid": True, "features": ["Google Style 2 Column", "CSS Blink+Wave Avatar No Circle", "Groq Related Links", "Coursera Card", "White Mic"]}
