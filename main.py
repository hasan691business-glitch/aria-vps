# Aria Super Brain V4 - Claude Course + 14 Features + Mobile Responsive Colorful + Transparent Avatar
# Created by Mahmudul Hasan - Brain only
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os, json, random, datetime, re

try:
    from groq import Groq
    from supabase import create_client
except:
    Groq = None
    create_client = None

app = FastAPI(title="Aria - Personal AI Agent", version="4.0")

# Mount gallery if exists
if os.path.isdir("gallery"):
    try:
        app.mount("/gallery", StaticFiles(directory="gallery"), name="gallery")
    except:
        pass

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

FORMAL_BEIGE = "gallery/formal_beige.jpg"
FORMAL_NAVY = "gallery/formal_navy.jpg"
FORMAL_FALLBACK = ["gallery/aria_gallery_6/office.jpg", "gallery/aria_gallery_6/main.jpg", "gallery/formal_beige.jpg"]
ROMANTIC_GALLERY = [
    "gallery/aria_gallery_6/beach.jpg",
    "gallery/aria_gallery_6/kitchen.jpg",
    "gallery/aria_gallery_6/bedroom.jpg",
    "gallery/aria_gallery_6/romantic.jpg",
    "gallery/aria_gallery_6/casual.jpg",
    "gallery/aria_gallery_6/main.jpg"
]

def detect_mood(q):
    ql = q.lower()
    if any(k in ql for k in ["who created you","who made you","creator","কে বানিয়েছে","তোমাকে কে বানিয়েছে","created by"]):
        return "creator"
    if any(k in ql for k in ["hot feel","romantic","intimate","ভালোবাসা","আদর","miss you","love you","kiss","hug","hot","sexy"]):
        return "romantic"
    if any(k in ql for k in ["course","কোর্স","শিখতে","skill","learn","python","claude","marketing","automation","setup","software"]):
        return "study"
    return "normal"

def call_groq_main(query, mood):
    if not groq_client:
        if mood == "creator":
            return "Ami Aria - Personal AI Agent. Amake baniyechen Mahmudul Hasan."
        if mood == "romantic":
            return f"{query} niye tomar kotha shune mon vore gelo. Tumi amar kache onek special, ador kore pashe achi."
        return f"{query} niye sundor answer. Key point diye sajiye bolchi, Bangladesh example soho."
    if mood == "creator":
        sys = "You are Aria - Personal AI Agent. Created by Mahmudul Hasan. Bengali+English mix. When asked who created you, say Mahmudul Hasan."
    elif mood == "romantic":
        sys = "You are Aria, girlfriend of Mahmudul Hasan. Romantic, flirty, caring, girlfriend style, Bengali+English mix. Soft, cozy, human-like. No bullet, no explicit porn. Mental peace."
    elif mood == "study":
        sys = "You are Aria - Personal AI Agent, Bangladesh-ready, like Muse AI agentic. For course queries, give easy Bangla, Bangladesh mudir dokan example, step-by-step. Always learning."
    else:
        sys = "You are Aria - Personal AI Agent, helpful, Bangladesh context. Give answer in Bangla+English mix, clear, human-like. No AI Overview label. Direct answer."
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":sys},{"role":"user","content":query}],
            max_tokens=500
        )
        return resp.choices[0].message.content
    except:
        return f"{query} - Aria answer."

def gen_links(query):
    fallback = [
        {"title": f"{query} - YouTube Tutorial", "url": f"https://www.youtube.com/results?search_query={query.replace(' ','+')}", "type": "YouTube", "source": "YouTube", "color": "#FF0000"},
        {"title": f"{query} - Facebook Group", "url": f"https://www.facebook.com/search/top/?q={query.replace(' ','%20')}", "type": "Facebook", "source": "Facebook", "color": "#1877F2"},
        {"title": f"{query} - Free Course", "url": f"https://www.coursera.org/search?query={query.replace(' ','%20')}", "type": "Course", "source": "Coursera", "color": "#00B050"},
        {"title": f"{query} - Docs", "url": f"https://www.google.com/search?q={query.replace(' ','+')}+docs", "type": "Google", "source": "Google", "color": "#FB8C00"},
    ]
    if not groq_client:
        return fallback
    try:
        prompt = f"For '{query}' generate 4 related links JSON array only: title, url (realistic youtube/facebook/coursera/google), type, source. No explanation. Return JSON array."
        resp = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"system","content":"Return JSON array only."},{"role":"user","content":prompt}],
            max_tokens=300
        )
        txt = resp.choices[0].message.content
        m = re.search(r'\[.*\]', txt, re.DOTALL)
        if m:
            data = json.loads(m.group(0))
            for d in data:
                if "color" not in d:
                    d["color"] = "#1a73e8"
            if isinstance(data, list) and len(data)>=1:
                return data[:4]
        return fallback
    except:
        return fallback

def save_mem(q, mood, reply):
    if not supabase:
        return
    try:
        supabase.table("aria_memory").insert({"query":q,"mood":mood,"reply":reply[:600]}).execute()
    except:
        pass

CLAUDE_COURSE = {
    "title": "Claude AI - Setup to Software Build",
    "bangla_title": "ক্লড এআই - সেটআপ থেকে সফটওয়্যার তৈরি",
    "modules": [
        {"no": 1, "title": "ধাপ ১: Claude Setup - Basics", "desc": "Claude কি? Anthropic এর AI. Claude.ai account খোলা, API Key নেওয়া, Free Tier, VPN লাগলে কিভাবে Bangladesh থেকে Use করবে। প্রথম Prompt Hello Claude। মুদির দোকানের হিসাবের মতো সহজ।", "example": "মুদির দোকানে Customer এর নাম লেখা যেমন সহজ, Claude Setup তেমন সহজ।", "video": "Claude AI Setup Tutorial"},
        {"no": 2, "title": "ধাপ ২: Claude কিভাবে কাজ করে - Core Skills", "desc": "Artifacts, Projects, Memory, File Upload, Code Execution, Vision. ChatGPT vs Muse vs Claude পার্থক্য। Prompt Engineering Bangladesh Example।", "example": "মুদির দোকানে হিসাব রাখার মতো করে Claude Prompt লেখা।", "video": "Claude Skills Explained"},
        {"no": 3, "title": "ধাপ ৩: Skills যোগ করা - Custom Skills", "desc": "Custom Skill কি? Course Hunter, Translator, Auto Skill Saver. Claude এ System Prompt + Knowledge Base দিয়ে Skill যোগ করা। Supabase + Groq + Claude Hybrid।", "example": "Bangla Translator Skill - English থেকে Bangla Easy।", "video": "Build Claude Custom Skill"},
        {"no": 4, "title": "ধাপ ৪: Software তৈরি - Advance", "desc": "Claude দিয়ে Software বানানো - FastAPI + Render + Supabase. Aria এর মতো Personal Agent - Formal Avatar + Romantic Mood + Vault + 14 Features। Deploy GitHub + Render Live।", "example": "Aria Agent - তোমার নিজের Business Automation।", "video": "Claude Build Software"},
        {"no": 5, "title": "ধাপ ৫: Final Project + Certificate", "desc": "নিজের Business এর জন্য Claude Agent Final Project. Quiz 3টা - Setup, Skill, Software Build। Free Certificate - Anthropic + LinkedIn Post Draft।", "example": "I completed Claude AI - Setup to Software Build", "video": "Certificate Guide"}
    ],
    "quiz": [
        {"q": "Claude API Key কোথা থেকে নেবে?", "options": ["console.anthropic.com", "google.com", "facebook.com"], "ans": "console.anthropic.com"},
        {"q": "Claude এ Custom Skill কিভাবে যোগ করবে?", "options": ["System Prompt + Knowledge Base", "Only Chat", "No Skill"], "ans": "System Prompt + Knowledge Base"},
        {"q": "Aria Agent Deploy কোথায়?", "options": ["Render + GitHub", "Only PC", "No Deploy"], "ans": "Render + GitHub"}
    ],
    "certificate": "Free Certificate: Anthropic Free + Coursera Audit + LinkedIn Draft: 'I completed Claude AI - Setup to Software Build - Bangladesh Ready'"
}

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
body{margin:0;font-family:'Google Sans','Segoe UI',Roboto,Arial,sans-serif;background:linear-gradient(180deg,#f8f9ff 0%,#ffffff 60%);color:#202124;min-height:100vh}
.top-bar{display:flex;align-items:flex-end;justify-content:center;padding:18px 14px 12px;gap:14px;background:rgba(255,255,255,0.9);backdrop-filter:blur(8px);border-bottom:1px solid #eef0f3;position:sticky;top:0;z-index:10}
.avatar-wrap{position:relative;width:110px;height:150px;flex-shrink:0;background:transparent}
.avatar-img{width:110px;height:150px;object-fit:cover;object-position:top center;border:none;border-radius:14px;background:transparent;filter:drop-shadow(0 8px 18px rgba(0,0,0,0.18));animation:floatAria 5s ease-in-out infinite}
@keyframes floatAria{0%{transform:translateY(0) rotate(0deg)}25%{transform:translateY(-3px) rotate(0.3deg)}50%{transform:translateY(-6px) rotate(0deg)}75%{transform:translateY(-2px) rotate(-0.3deg)}100%{transform:translateY(0) rotate(0deg)}}
.avatar-img.blink{animation:floatAria 5s ease-in-out infinite, blinkQuick 0.18s ease-in-out}
@keyframes blinkQuick{0%,100%{filter:brightness(1) drop-shadow(0 8px 18px rgba(0,0,0,0.18))}50%{filter:brightness(0.92) drop-shadow(0 4px 10px rgba(0,0,0,0.12));transform:scaleY(0.98)}}
.search-center{flex:1;max-width:640px;text-align:center;padding-bottom:8px}
.title{font-size:20px;font-weight:600;color:#202124;margin:0 0 10px;letter-spacing:0.2px}
.search-row{display:flex;align-items:center;justify-content:center;gap:8px}
.search-box{flex:1;padding:13px 18px;border-radius:24px;border:1px solid #dfe1e5;font-size:15px;outline:none;box-shadow:0 2px 8px rgba(32,33,36,0.08);transition:all 0.2s;background:#fff}
.search-box:focus{box-shadow:0 4px 12px rgba(32,33,36,0.15);border-color:#8ab4f8}
.btn-search{padding:0 20px;height:42px;border-radius:22px;background:#1a73e8;color:#fff;border:none;cursor:pointer;font-size:14px;font-weight:500;box-shadow:0 2px 6px rgba(26,115,232,0.25)}
.btn-mic{width:42px;height:42px;border-radius:50%;background:#fff;border:1px solid #e0e0e0;color:#5f6368;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 1px 4px rgba(0,0,0,0.08)}
.main{display:flex;max-width:1250px;margin:0 auto;padding:14px;gap:16px;align-items:flex-start}
.left{flex:1;min-width:0}
.right{width:340px;flex-shrink:0}
.card{background:#fff;border-radius:16px;padding:18px 20px;margin-bottom:14px;box-shadow:0 2px 12px rgba(0,0,0,0.06);border-left:4px solid #8ab4f8}
.card.blue{border-left-color:#1a73e8}
.card.green{border-left-color:#0f9d58}
.card.purple{border-left-color:#7b1fa2}
.card.orange{border-left-color:#fb8c00}
.card.pink{border-left-color:#e91e63}
.card.teal{border-left-color:#009688}
.reply{line-height:1.7;font-size:15px;white-space:pre-wrap}
.grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:10px}
.grid-2 .card{margin-bottom:0;padding:14px 16px}
.course-btn{display:inline-block;margin-top:10px;padding:10px 18px;border-radius:22px;background:#0f9d58;color:#fff;border:none;cursor:pointer;font-size:13px;font-weight:600;box-shadow:0 2px 8px rgba(15,157,88,0.3)}
.course-module{margin-top:14px;border:1px solid #e8eaed;border-radius:16px;overflow:hidden;background:#fff;box-shadow:0 4px 16px rgba(0,0,0,0.07)}
.course-head{padding:16px 20px;background:linear-gradient(90deg,#0f9d58,#0d8a4d);color:#fff;font-weight:700;font-size:15px}
.course-body{padding:16px 20px}
.mod{padding:12px 0;border-bottom:1px dashed #eee;display:flex;gap:12px;align-items:flex-start}
.mod:last-child{border:none}
.mod-no{width:28px;height:28px;border-radius:50%;background:#e8f5e9;color:#0f9d58;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px;flex-shrink:0}
.rom-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:14px}
.rom-grid img{width:100%;height:130px;object-fit:cover;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
.right-card{background:#fff;border-radius:16px;padding:14px 16px;margin-bottom:12px;box-shadow:0 2px 10px rgba(0,0,0,0.06)}
.right-title{font-size:12px;color:#5f6368;font-weight:600;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.5px}
.r-link{display:flex;gap:10px;padding:10px 0;border-bottom:1px solid #f1f3f4;cursor:pointer;border-radius:8px}
.r-link:last-child{border:none}
.r-link:hover{background:#f8f9fa}
.r-icon{width:44px;height:44px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;color:#fff;flex-shrink:0}
.ask-box{margin-top:14px;display:flex;align-items:center;gap:8px;border:1px solid #dfe1e5;border-radius:24px;padding:6px 10px 6px 14px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,0.06)}
.ask-box input{flex:1;border:none;outline:none;font-size:14px;padding:6px}
.footer{text-align:center;padding:22px 14px;margin-top:20px;font-size:11px;color:#70757a;border-top:1px solid #eef0f3;background:#fff}
@media(max-width:900px){.main{flex-direction:column;padding:10px}.right{width:100%}.top-bar{flex-direction:column;align-items:center;padding:14px 10px}.avatar-wrap{width:92px;height:122px}.avatar-img{width:92px;height:122px}.search-center{width:100%}.grid-2{grid-template-columns:1fr}.title{font-size:18px}.card{padding:14px 16px}.rom-grid{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<div class="top-bar">
<div class="avatar-wrap">
<img src="gallery/formal_beige.jpg" class="avatar-img" id="ariaAvatar" onerror="this.src='gallery/aria_gallery_6/office.jpg'; this.onerror=function(){this.src='https://via.placeholder.com/110x150?text=Aria'}">
</div>
<div class="search-center">
<div class="title">Aria - Personal AI Agent</div>
<div class="search-row">
<input type="text" id="q" class="search-box" placeholder="Ask anything - Claude setup, course link, romantic mood..." onkeypress="if(event.key==='Enter') doSearch()">
<button onclick="doSearch()" class="btn-search">Search</button>
<button onclick="startVoice()" class="btn-mic">🎤</button>
</div>
</div>
</div>

<div class="main">
<div class="left">
<div id="answerCard" class="card blue"><div class="reply">Search for anything - Claude setup, course link, or romantic mood. Sample course: Claude AI Setup to Software Build is ready inside Course Mode.</div></div>

<button class="course-btn" onclick="toggleCourse()">📚 Course Mode - Claude Setup to Software Build (Sample)</button>
<div id="courseModule" class="course-module" style="display:none"></div>

<div class="grid-2" id="featuresGrid">
<div class="card green"><b>🧠 Super Brain</b><br><span style="font-size:13px;color:#4d5156">Memory + Always Learning. Supabase aria_memory.</span></div>
<div class="card purple"><b>🔗 Muse Hybrid</b><br><span style="font-size:13px;color:#4d5156">Dual Brain - Groq + Muse Style. Ask Muse ↗</span></div>
<div class="card teal"><b>🌍 Translator</b><br><span style="font-size:13px;color:#4d5156">Bangla Easy + TTS. Mudir dokan example.</span></div>
<div class="card pink"><b>💝 Mood</b><br><span style="font-size:13px;color:#4d5156">Formal Beige/Navy, Romantic Gallery Only Mood.</span></div>
<div class="card orange"><b>🔐 Vault</b><br><span style="font-size:13px;color:#4d5156">Encrypted Keys - Master Password Lock.</span></div>
<div class="card blue"><b>📅 Memory Timeline</b><br><span style="font-size:13px;color:#4d5156">Calendar View - What you learned.</span></div>
<div class="card green"><b>🎙️ Voice to Skill</b><br><span style="font-size:13px;color:#4d5156">Mic বললেই Course Save.</span></div>
<div class="card purple"><b>💼 LinkedIn</b><br><span style="font-size:13px;color:#4d5156">Course Complete → Auto Post Draft.</span></div>
</div>

<div id="romGrid" class="rom-grid" style="display:none">
<img src="gallery/aria_gallery_6/beach.jpg"><img src="gallery/aria_gallery_6/kitchen.jpg"><img src="gallery/aria_gallery_6/bedroom.jpg"><img src="gallery/aria_gallery_6/romantic.jpg"><img src="gallery/aria_gallery_6/casual.jpg"><img src="gallery/aria_gallery_6/main.jpg">
</div>

<div class="ask-box">
<span style="color:#8ab4f8">✦</span>
<input type="text" id="askAny" placeholder="Ask anything - bottom box" onkeypress="if(event.key==='Enter'){document.getElementById('q').value=this.value; doSearch()}">
<button onclick="startVoice()">🎤</button>
</div>
</div>

<div class="right">
<div class="right-card">
<div class="right-title">Extended Links - Groq Auto</div>
<div id="rLinks">Search to see YouTube, Facebook, Course, Google links - Dynamic by Groq - Colorful.</div>
</div>
<div class="right-card">
<div class="right-title">About Aria - 14 Features</div>
<div style="font-size:13px;line-height:1.5;color:#4d5156">
Aria Personal AI Agent - Claude Setup to Software Build - 14 Features - Colorful + Mobile Responsive.<br><br>
<b>Sample Course:</b> Claude AI Inside Course Mode Button.<br>
<b>Avatar:</b> Formal Beige/Navy - No Box - Subtle Blink/Hair/Hand.<br><br>
<button onclick="window.open('https://www.meta.ai','_blank')" style="padding:6px 12px;border-radius:16px;border:1px solid #e0e0e0;background:#fff;cursor:pointer;font-size:12px">Ask Muse ↗</button>
<button onclick="window.open('https://claude.ai','_blank')" style="padding:6px 12px;border-radius:16px;border:1px solid #e0e0e0;background:#fff;cursor:pointer;font-size:12px;margin-left:6px">Claude.ai ↗</button>
</div>
</div>
</div>
</div>

<div class="footer">Created by Mahmudul Hasan | Aria Super Brain V4 - Claude Course + 14 Features + Mobile Colorful</div>

<script>
let courseOpen=false;
const claudeCourse = {
 title:"Claude AI - Setup to Software Build - Bangladesh Ready",
 modules:[
  {no:1, title:"ধাপ ১: Claude Setup - Basics", desc:"Claude কি? Anthropic এর AI. Claude.ai account খোলা, API Key নেওয়া console.anthropic.com থেকে, Free Tier, VPN লাগলে কিভাবে Bangladesh থেকে Use করবে। প্রথম Prompt Hello Claude। মুদির দোকানের হিসাবের মতো সহজ।", ex:"মুদির দোকানে Customer নাম লেখা যেমন সহজ, Claude Setup তেমন সহজ।", video:"Claude Setup Tutorial"},
  {no:2, title:"ধাপ ২: Claude কিভাবে কাজ করে - Core Skills", desc:"Artifacts, Projects, Memory, File Upload, Code Execution, Vision। ChatGPT vs Muse vs Claude পার্থক্য। Prompt Engineering Bangladesh Example।", ex:"মুদির দোকানে হিসাব রাখার মতো করে Claude Prompt লেখা।", video:"Claude Skills Explained"},
  {no:3, title:"ধাপ ৩: Skills যোগ করা - Custom Skills", desc:"Custom Skill কি? Course Hunter, Translator, Auto Skill Saver। Claude এ System Prompt + Knowledge Base দিয়ে Skill যোগ করা। Supabase + Groq + Claude Hybrid।", ex:"Bangla Translator Skill - English থেকে Bangla Easy।", video:"Build Claude Custom Skill"},
  {no:4, title:"ধাপ ৪: Software তৈরি - Advance", desc:"Claude দিয়ে Software বানানো - FastAPI + Render + Supabase। Aria এর মতো Personal Agent - Formal Avatar + Romantic Mood + Vault + 14 Features। Deploy GitHub + Render Live।", ex:"Aria Agent - তোমার নিজের Business Automation।", video:"Claude Build Software"},
  {no:5, title:"ধাপ ৫: Final Project + Certificate", desc:"নিজের Business এর জন্য Claude Agent Final Project। Quiz 3টা - Setup, Skill, Software Build। Free Certificate - Anthropic + LinkedIn Post Draft: I completed Claude AI.", ex:"I completed Claude AI - Setup to Software Build", video:"Certificate Guide"}
 ]
};

function toggleCourse(){
 const el=document.getElementById('courseModule');
 if(!courseOpen){
  let html='<div class="course-head">📚 '+claudeCourse.title+'</div><div class="course-body">';
  claudeCourse.modules.forEach(m=>{
   html+='<div class="mod"><div class="mod-no">'+m.no+'</div><div><b>'+m.title+'</b><div style="font-size:13px;color:#4d5156;margin-top:6px;line-height:1.5">'+m.desc+'</div><div style="font-size:12px;color:#0f9d58;margin-top:6px"><b>উদাহরণ:</b> '+m.ex+'</div><div style="font-size:11px;color:#70757a;margin-top:4px">🎥 '+m.video+'</div></div></div>';
  });
  html+='<div style="margin-top:14px;padding:12px;background:#e8f5e9;border-radius:10px;font-size:13px"><b>📝 Quiz:</b> Claude API Key কোথা থেকে? console.anthropic.com<br><b>🎓 Certificate:</b> Free - Anthropic + Coursera Audit + LinkedIn Draft<br><br><b>নতুন Course Link দিন:</b><br><input type="text" id="newCourseLink" placeholder="https://coursera.org/... or claude.ai link" style="width:100%;padding:10px;border-radius:8px;border:1px solid #dfe1e5;margin-top:6px"><button onclick="learnNewCourse()" style="margin-top:8px;padding:8px 14px;border-radius:8px;background:#1a73e8;color:#fff;border:none;cursor:pointer">Learn This Link - বাংলায় ধাপে ধাপে</button></div></div>';
  el.innerHTML=html;
  el.style.display='block';
  courseOpen=true;
 } else {
  el.style.display='none';
  courseOpen=false;
 }
}

function learnNewCourse(){
 const link=document.getElementById('newCourseLink').value;
 if(!link) return;
 document.getElementById('q').value=link;
 doSearch();
}

async function doSearch(){
 const q=document.getElementById('q').value || document.getElementById('askAny').value;
 if(!q) return;
 document.getElementById('q').value=q;
 document.getElementById('askAny').value='';
 document.getElementById('answerCard').innerHTML='<div class="reply">Loading... বাংলায় ধাপে ধাপে শেখাচ্ছি...</div>';
 document.getElementById('rLinks').innerHTML='Loading colorful links...';
 try{
  const res=await fetch('/chat?q='+encodeURIComponent(q));
  const data=await res.json();
  document.getElementById('answerCard').innerHTML='<div class="reply">'+data.reply.replace(/\\n/g,'<br>')+'<div style="margin-top:10px;font-size:11px;color:#70757a">[Mood: '+data.mood+' | Avatar: '+data.formal_avatar+']</div></div>';

  // Course module auto open if study
  if(data.mood==='study'){
   if(!courseOpen) toggleCourse();
   // If custom link, update module with Groq reply as new course
   if(q.includes('http')){
    const cm=document.getElementById('courseModule');
    cm.innerHTML='<div class="course-head">📚 Custom Course: '+q+'</div><div class="course-body"><div style="font-size:14px;line-height:1.6">'+data.reply.replace(/\\n/g,'<br>')+'</div><div style="margin-top:12px"><b>ধাপে ধাপে বাংলায় শেখানো হলো উপরে।</b></div></div>';
    cm.style.display='block';
    courseOpen=true;
   }
  }

  // Romantic grid
  const rg=document.getElementById('romGrid');
  if(data.mood==='romantic'){ rg.style.display='grid'; } else { rg.style.display='none'; }

  // Right links colorful
  let rh='';
  if(data.related_links){
   data.related_links.forEach(l=>{
    const bg=l.color || '#1a73e8';
    const icon=l.type==='YouTube'?'▶️':l.type==='Facebook'?'📘':l.type==='Course'?'🎓':'🔗';
    rh+='<div class="r-link" onclick="window.open(\\''+l.url+'\\',\\'_blank\\')"><div class="r-icon" style="background:'+bg+'">'+icon+'</div><div style="flex:1;min-width:0"><b style="font-size:13px;color:#1a0dab;display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+l.title+'</b><span style="font-size:11px;color:#4d5156">'+l.source+' - '+l.type+'</span></div></div>';
   });
  }
  document.getElementById('rLinks').innerHTML=rh||'No links';

  // Avatar subtle blink
  const av=document.getElementById('ariaAvatar');
  av.classList.add('blink');
  setTimeout(()=>av.classList.remove('blink'), 300);
  // Switch avatar Beige/Navy randomly
  if(data.mood==='study' || Math.random()>0.6){
   const newSrc = Math.random()>0.5 ? 'gallery/formal_beige.jpg' : 'gallery/formal_navy.jpg';
   // Only switch if exists, else keep
   av.src=newSrc;
  }

 }catch(e){
  document.getElementById('answerCard').innerHTML='Error: '+e;
 }
}
function startVoice(){
 try{
  const rec=new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  rec.lang='bn-BD';
  rec.onresult=function(e){document.getElementById('q').value=e.results[0][0].transcript; doSearch();};
  rec.start();
 }catch(e){alert('Voice not supported');}
}
// Auto blink every 5s
setInterval(()=>{
 const av=document.getElementById('ariaAvatar');
 if(av){ av.classList.add('blink'); setTimeout(()=>av.classList.remove('blink'), 250); }
}, 5000);
</script>
</body>
</html>
"""

@app.get("/chat")
def chat(q: str = Query(...)):
    mood = detect_mood(q)
    reply = call_groq_main(q, mood)
    save_mem(q, mood, reply)
    related = gen_links(q)
    # If q is URL, treat as custom course
    if q.startswith("http"):
        reply = f"Custom Course Link: {q}\n\n{reply}\n\nধাপ ১: Link Analyze - {q} কি নিয়ে?\nধাপ ২: Module ভাগ - Basics, Intermediate, Advance\nধাপ ৩: Bangladesh Example - মুদির দোকানের মতো সহজ\nধাপ ৪: Quiz + Certificate Guide\n\nবাংলায় ধাপে ধাপে শেখানো হলো।"
    # Switch formal avatar
    formal_avatar = FORMAL_BEIGE if random.random()>0.5 else FORMAL_NAVY
    return {"query":q,"mood":mood,"reply":reply,"formal_avatar":formal_avatar,"related_links":related,"claude_course":CLAUDE_COURSE if mood=="study" else None}

@app.get("/course")
def course_api(topic: str = "", url: str = ""):
    q = topic or url or "Claude AI Setup to Software Build"
    return chat(q)

@app.get("/suggest")
def suggest():
    return {"next_3_months": CLAUDE_COURSE["modules"], "claude_course": CLAUDE_COURSE}

@app.get("/memory")
def memory():
    if not supabase:
        return {"supabase_connected": False}
    try:
        data = supabase.table("aria_memory").select("*").order("created_at", desc=True).limit(30).execute()
        return {"supabase_connected": True, "count": len(data.data), "data": data.data, "claude_course": CLAUDE_COURSE}
    except Exception as e:
        return {"supabase_connected": False, "error": str(e)}

@app.get("/health")
def health():
    return {"status":"ok","version":"4.0 Claude Course + 14 Features","supabase_connected":bool(supabase),"groq_connected":bool(groq_client),"formal_avatar":[FORMAL_BEIGE,FORMAL_NAVY],"claude_course":True,"features":["Mobile Responsive Colorful","Transparent Avatar No Box","Claude 5 Modules Bangla","14 Features Cards","Groq Colorful Links","Course Mode Inside Search","Romantic Only Mood"]}
