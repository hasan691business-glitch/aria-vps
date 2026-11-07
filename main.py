import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import pathlib

app = FastAPI()

# Load base64 avatars (trimmed for size - using 2 poses for V15 light)
try:
    base_b64 = pathlib.Path("/mnt/data/image_20261105_125059_b64.txt").read_text()[:200000]  # trim
    wave_b64 = pathlib.Path("/mnt/data/image_20261105_125114_b64.txt").read_text()[:200000]
    tilt_b64 = pathlib.Path("/mnt/data/image_20261105_125110_b64.txt").read_text()[:200000]
except:
    base_b64 = ""
    wave_b64 = ""
    tilt_b64 = ""

HTML_PAGE = f"""
<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Aria + পার্সোনাল এআই এজেন্ট - V15 Final</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;font-family:'Google Sans',Roboto,Arial,sans-serif}}
body{{background:#F8F9FA;color:#202124;overflow-x:hidden}}
/* Top */
.topbar{{display:flex;align-items:center;justify-content:space-between;padding:12px 24px;background:white;border-bottom:1px solid #E8EAED;position:sticky;top:0;z-index:50}}
.searchBox{{flex:1;max-width:600px;margin:0 20px;position:relative}}
.searchBox input{{width:100%;padding:12px 16px 12px 44px;border-radius:24px;border:1px solid #DFE1E5;background:#F1F3F4;font-size:15px;outline:none}}
.searchBox input:focus{{background:white;box-shadow:0 1px 6px rgba(32,33,36,.28);border-color:transparent}}
.searchIcon{{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:#5F6368}}
.topIcons{{display:flex;gap:16px;align-items:center}}
.iconBadge{{background:#FEF7E0;padding:6px 10px;border-radius:16px;font-size:13px;font-weight:500}}
/* Layout */
.layout{{display:flex;min-height:100vh}}
.leftbar{{width:240px;background:white;border-right:1px solid #E8EAED;padding:16px 12px;display:flex;flex-direction:column;justify-content:space-between}}
.navItem{{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:8px;cursor:pointer;color:#5F6368;font-size:14px;margin:2px 0}}
.navItem.active{{background:#E8F0FE;color:#1967D2;font-weight:500}}
.navItem:hover{{background:#F1F3F4}}
.navSection{{font-size:11px;color:#5F6368;margin:16px 0 4px 12px;letter-spacing:0.8px}}
.upgradeCard{{background:linear-gradient(135deg,#E8F0FE,#F3E8FD);border-radius:12px;padding:12px;margin-top:12px}}
.profile{{display:flex;align-items:center;gap:10px;padding:12px;border-top:1px solid #E8EAED;margin-top:12px}}
.profileImg{{width:32px;height:32px;border-radius:50%;background:#ddd;object-fit:cover}}
.center{{flex:1;padding:20px 24px;max-width:900px}}
.hero{{background:linear-gradient(135deg,#E8F0FE 0%,#FFFFFF 100%);border-radius:24px;padding:24px 28px;display:flex;align-items:center;justify-content:space-between;position:relative;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1)}}
.heroText h1{{font-size:22px;font-weight:400;margin-bottom:6px}}
.heroText p{{color:#5F6368;font-size:14px;margin-bottom:16px}}
.btnPrimary{{background:#1A73E8;color:white;border:none;padding:10px 20px;border-radius:20px;font-size:14px;cursor:pointer;display:inline-flex;align-items:center;gap:8px}}
.btnPrimary:hover{{background:#1765CC}}
.heroAvatar{{width:280px;height:380px;position:relative;flex-shrink:0}}
.heroAvatar img{{width:100%;height:100%;object-fit:contain;position:absolute;top:0;left:0;transition:opacity 0.3s ease;filter:drop-shadow(0 12px 20px rgba(0,0,0,0.15))}}
#imgA{{opacity:1;z-index:2}}
#imgB{{opacity:0;z-index:1}}
.breathe{{animation:breathe 4s infinite ease-in-out}}
@keyframes breathe{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.015)}}}}
.section{{margin-top:24px}}
.sectionTitle{{font-size:16px;font-weight:500;margin-bottom:12px}}
.card{{background:white;border-radius:16px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,0.1);border:1px solid #E8EAED}}
.progressBar{{height:6px;background:#E8EAED;border-radius:3px;overflow:hidden;margin:8px 0}}
.progressFill{{height:100%;background:#1A73E8;width:60%}}
.skillsGrid{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}
.skillCard{{padding:14px;border-radius:12px;display:flex;align-items:center;gap:12px;cursor:pointer;border:1px solid transparent}}
.skillCard:hover{{border-color:#DADCE0}}
.skillIcon{{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px}}
.rightbar{{width:300px;padding:20px 16px;background:#F8F9FA}}
.goalCircle{{width:80px;height:80px;border-radius:50%;background:conic-gradient(#1A73E8 75%,#E8EAED 0);display:flex;align-items:center;justify-content:center;margin:0 auto;position:relative}}
.goalInner{{width:60px;height:60px;background:white;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:500}}
.dayChecks{{display:flex;gap:8px;justify-content:center;margin:12px 0}}
.day{{width:28px;height:28px;border-radius:50%;background:#E8F0FE;display:flex;align-items:center;justify-content:center;font-size:12px}}
.day.done{{background:#CEEAD6;color:#137333}}
.footer{{text-align:center;padding:16px;font-size:12px;color:#5F6368;display:flex;align-items:center;justify-content:center;gap:8px;border-top:1px solid #E8EAED;margin-top:24px;background:white}}
.footerImg{{width:28px;height:28px;border-radius:50%;object-fit:cover;border:1px solid #E8EAED}}
#chatArea{{margin-top:16px}}
.msg{{padding:12px;border-radius:16px;margin:8px 0;max-width:85%}}
.userMsg{{background:#E8F0FE;margin-left:auto}}
.aiMsg{{background:white;border:1px solid #E8EAED}}
@media(max-width:1100px){{.leftbar,.rightbar{{display:none}}.hero{{flex-direction:column}}.heroAvatar{{width:220px;height:300px}}}}
</style>
</head>
<body>
<div class="topbar">
<div style="display:flex;align-items:center;gap:8px"><span style="font-weight:500;color:#1A73E8">Aria</span><span style="color:#5F6368;font-size:14px">পার্সোনাল এআই এজেন্ট</span></div>
<div class="searchBox"><span class="searchIcon">🔍</span><input id="searchInput" placeholder="Search skills, courses, Google, Nvidia, Claude..." onkeypress="if(event.key==='Enter') doSearch()"></div>
<div class="topIcons"><span class="iconBadge">🔥 7 Day</span><span class="iconBadge">📚 3 Courses</span><button id="btnMic" style="width:40px;height:40px;border-radius:50%;border:none;background:conic-gradient(from 0deg,#FBBC05,#EA4335,#34A853,#4285F4,#FBBC05);color:white;cursor:pointer">🎤</button></div>
</div>
<div class="layout">
<div class="leftbar">
<div>
<div class="navItem active">🏠 Home</div>
<div class="navSection">LEARN</div>
<div class="navItem" onclick="openCourse()">📚 Course Hunter - Universal</div>
<div class="navItem">🌐 Translator+TTS</div>
<div class="navItem">🏆 Quiz Certificate</div>
<div class="navSection">PROGRESS</div>
<div class="navItem">🧠 Knowledge Graph</div>
<div class="navItem">📓 Decision Journal</div>
<div class="navItem">📅 Life OS</div>
<div class="navSection">BUSINESS</div>
<div class="navItem">💼 Business Decision Engine</div>
<div class="navItem">💰 Cashflow OS</div>
<div class="navItem">🔗 Finance Bridge</div>
<div class="navItem">📊 Scenario Planning</div>
<div class="navSection">LIBRARY</div>
<div class="navItem">🕰️ Memory Timeline</div>
<div class="navItem">🔒 Vault Master</div>
</div>
<div>
<div class="upgradeCard"><b>Aria Plus</b><div style="font-size:12px;color:#5F6368;margin:4px 0">Unlock unlimited courses & knowledge graph</div><button class="btnPrimary" style="padding:6px 12px;font-size:12px">Upgrade</button></div>
<div class="profile"><img class="profileImg" src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/" alt="Mahmudul"><div><div style="font-size:13px;font-weight:500">Mahmudul Hasan</div><div style="font-size:11px;color:#5F6368">Level 12 • Creator</div></div></div>
</div>
</div>
<div class="center">
<div class="hero" id="heroCard">
<div class="heroText">
<h1 id="greeting">Good morning, Mahmudul! 👋</h1>
<p>One skill closer to your future! Continue your journey with Aria.</p>
<button class="btnPrimary" onclick="openCourse()">Continue Learning <span>→</span></button>
<div id="chatArea"></div>
</div>
<div class="heroAvatar breathe" id="avatarWrapper">
<img id="imgA" src="{base_b64 if base_b64 else ''}" alt="Aria Avatar">
<img id="imgB" src="" alt="">
</div>
</div>
<div class="section">
<div class="sectionTitle">Continue Learning</div>
<div class="card" style="display:flex;gap:16px;align-items:center">
<img src="https://via.placeholder.com/80x60/E8F0FE/1967D2?text=AI" style="width:80px;height:60px;border-radius:8px;object-fit:cover">
<div style="flex:1"><div style="font-weight:500">Google AI Essentials - Unit 2 Lesson 3</div><div style="font-size:12px;color:#5F6368">Digital Dominance - সহজ বাংলায়</div><div class="progressBar"><div class="progressFill"></div></div><div style="font-size:11px;color:#5F6368">60% • 2/5 modules</div></div>
<button class="btnPrimary" onclick="openCourse()">Start</button>
</div>
</div>
<div class="section">
<div class="sectionTitle">Build Your Skills</div>
<div class="skillsGrid">
<div class="skillCard" style="background:#F3E8FD"><div class="skillIcon" style="background:#E9D2FD">💼</div><div><div style="font-weight:500">Business Decision</div><div style="font-size:12px;color:#5F6368">12 lessons</div></div></div>
<div class="skillCard" style="background:#FCE8E6"><div class="skillIcon" style="background:#F9DEDC">💰</div><div><div style="font-weight:500">Finance OS</div><div style="font-size:12px;color:#5F6368">10 lessons</div></div></div>
<div class="skillCard" style="background:#E6F4EA"><div class="skillIcon" style="background:#CEEAD6">🧠</div><div><div style="font-weight:500">Deep Work</div><div style="font-size:12px;color:#5F6368">24 lessons</div></div></div>
<div class="skillCard" style="background:#FEF7E0"><div class="skillIcon" style="background:#FEEFC3">🌱</div><div><div style="font-weight:500">Personal Growth</div><div style="font-size:12px;color:#5F6368">18 lessons</div></div></div>
</div>
</div>
<div class="section">
<div class="sectionTitle">Popular Courses - Free</div>
<div style="display:flex;gap:12px;overflow-x:auto;padding-bottom:8px">
<div class="card" style="min-width:140px;text-align:center"><div>🔍</div><div style="font-weight:500;font-size:13px">Google</div><div style="font-size:11px;color:#5F6368">4.9 ★</div></div>
<div class="card" style="min-width:140px;text-align:center"><div>💚</div><div style="font-weight:500;font-size:13px">Nvidia DLI</div><div style="font-size:11px;color:#5F6368">4.8 ★</div></div>
<div class="card" style="min-width:140px;text-align:center"><div>🤖</div><div style="font-weight:500;font-size:13px">Claude Docs</div><div style="font-size:11px;color:#5F6368">4.9 ★</div></div>
<div class="card" style="min-width:140px;text-align:center"><div>🎓</div><div style="font-weight:500;font-size:13px">Coursera</div><div style="font-size:11px;color:#5F6368">4.8 ★</div></div>
<div class="card" style="min-width:140px;text-align:center"><div>▶️</div><div style="font-weight:500;font-size:13px">YouTube</div><div style="font-size:11px;color:#5F6368">4.8 ★</div></div>
</div>
</div>
</div>
<div class="rightbar">
<div class="card" style="text-align:center">
<div style="font-weight:500;margin-bottom:12px">Your Daily Goal</div>
<div class="goalCircle"><div class="goalInner">15/20</div></div>
<div style="font-size:12px;color:#5F6368;margin-top:8px">15/20 min Today</div>
<div class="dayChecks"><span class="day done">✓</span><span class="day done">✓</span><span class="day done">✓</span><span class="day done">✓</span><span class="day">F</span></div>
</div>
<div class="card" style="margin-top:12px">
<div style="font-weight:500;font-size:14px">Decision Journal</div><div style="font-size:12px;color:#5F6368;margin:6px 0">Hit Rate 78% • 12 decisions logged</div><div class="progressBar"><div class="progressFill" style="width:78%"></div></div>
</div>
<div class="card" style="margin-top:12px">
<div style="font-weight:500;font-size:14px">Knowledge Graph</div><div style="font-size:11px;color:#5F6368;margin:6px 0">Google • Nvidia • Claude • Business</div><div style="display:flex;gap:4px;flex-wrap:wrap"><span style="background:#E8F0FE;padding:4px 8px;border-radius:12px;font-size:11px">AI Essentials</span><span style="background:#F3E8FD;padding:4px 8px;border-radius:12px;font-size:11px">Business</span></div>
</div>
<div class="card" style="margin-top:12px;background:#FEF7E0;border:1px dashed #F6BF26">
<div style="font-size:13px">🎁 Complete 2 more modules to unlock Certificate</div><div class="progressBar" style="margin-top:8px"><div class="progressFill" style="width:60%;background:#FBBC05"></div></div><div style="font-size:11px;color:#5F6368;margin-top:4px">3/5</div>
</div>
</div>
</div>
<div class="footer">Created by Mahmudul Hasan | Aria Super Brain V15 - Clean White - Formal Avatar <button id="btnBrain" style="margin-left:8px;width:32px;height:32px;border-radius:50%;border:1px solid #DADCE0;background:white;cursor:pointer">🧠</button><button id="btnCourse" style="width:32px;height:32px;border-radius:50%;border:1px solid #DADCE0;background:white;cursor:pointer">📚</button><button id="btnDoodle" style="width:32px;height:32px;border-radius:50%;border:1px solid #DADCE0;background:white;cursor:pointer">🎨</button></div>

<!-- Course Overlay -->
<div id="courseOverlay" style="display:none;position:fixed;inset:0;background:white;z-index:100;overflow-y:auto;padding:24px">
<div style="max-width:800px;margin:0 auto"><div style="display:flex;justify-content:space-between;align-items:center"><h2>📚 Course Mode - Universal Parser</h2><button onclick="closeCourse()" style="padding:8px 16px;border-radius:20px;border:1px solid #DADCE0;background:white;cursor:pointer">✕ Close</button></div>
<div style="margin:20px 0"><input id="courseLink" placeholder="Paste any link: grow.google, learn.nvidia.com, claude.ai/docs, youtube.com, coursera.org" style="width:100%;padding:14px;border-radius:12px;border:1px solid #DADCE0"><button onclick="parseCourse()" class="btnPrimary" style="margin-top:12px">Generate 5 Modules - সহজ বাংলায়</button></div>
<div id="courseResult"></div>
</div>
</div>

<script>
let avatarState='idle';
const frames={{
  base: `{base_b64 if base_b64 else ''}`,
  waveLow: `{wave_b64 if wave_b64 else ''}`,
  waveHigh: `{wave_b64 if wave_b64 else ''}`,
  tilt: `{tilt_b64 if tilt_b64 else ''}`
}};

let imgA=document.getElementById('imgA');
let imgB=document.getElementById('imgB');
let currentSrc=frames.base;
let isCrossfading=false;

function crossfadeTo(newSrc, duration=300){{
  if(isCrossfading || !newSrc) return;
  isCrossfading=true;
  imgB.src=newSrc;
  imgB.style.transition=`opacity ${{duration}}ms ease-out`;
  imgB.style.opacity='1';
  setTimeout(()=>{{
    imgA.src=newSrc;
    imgB.style.opacity='0';
    currentSrc=newSrc;
    isCrossfading=false;
  }}, duration);
}}

function setAvatarState(newState){{
  avatarState=newState;
  console.log('Avatar State:', newState);
  if(newState==='idle'){{
    crossfadeTo(frames.base, 300);
  }} else if(newState==='waving'){{
    crossfadeTo(frames.waveLow, 200);
    setTimeout(()=>crossfadeTo(frames.waveHigh, 200), 400);
    setTimeout(()=>crossfadeTo(frames.waveLow, 200), 800);
    setTimeout(()=>crossfadeTo(frames.base, 300), 1200);
  }} else if(newState==='explaining'){{
    crossfadeTo(frames.waveLow, 250);
    setTimeout(()=>crossfadeTo(frames.tilt, 300), 500);
  }} else if(newState==='romantic'){{
    crossfadeTo(frames.tilt, 400);
  }} else if(newState==='thinking'){{
    crossfadeTo(frames.tilt, 500);
  }}
  // Auto return to idle after 3s
  if(newState!=='idle'){{
    setTimeout(()=>{{ avatarState='idle'; crossfadeTo(frames.base, 400); }}, 3000);
  }}
}}

// Idle breathing only - subtle
setInterval(()=>{{
  if(avatarState==='idle' && Math.random()<0.15){{
    // occasional blink via opacity
    imgA.style.filter='brightness(0.96)';
    setTimeout(()=>imgA.style.filter='brightness(1)', 150);
  }}
}}, 1000);

function doSearch(){{
  const q=document.getElementById('searchInput').value.toLowerCase();
  if(!q) return;
  // Detect mood
  if(q.includes('miss you')||q.includes('love you')||q.includes('মনে পড়ছে')){{
    setAvatarState('romantic');
  }} else if(q.includes('brief')||q.includes('সংক্ষেপে')||q.includes('সহজ')){{
    setAvatarState('explaining');
  }} else if(q.includes('course')||q.includes('google')||q.includes('nvidia')||q.includes('claude')||q.includes('শিখতে')){{
    setAvatarState('waving');
  }} else {{
    setAvatarState('explaining');
  }}
  // Add to chat
  const area=document.getElementById('chatArea');
  area.innerHTML+=`<div class="msg userMsg">${{q}}</div><div class="msg aiMsg">Aria বুঝেছে: "${{q}}" - সহজ বাংলায় উত্তর দিচ্ছি... (Hexa Brain: Groq + ChatGPT + GitHub + OpenRouter + Claude + Gemini)</div>`;
}}

function openCourse(){{ document.getElementById('courseOverlay').style.display='block'; setAvatarState('waving'); }}
function closeCourse(){{ document.getElementById('courseOverlay').style.display='none'; setAvatarState('idle'); }}

function parseCourse(){{
  const link=document.getElementById('courseLink').value;
  if(!link) return alert('লিংক দাও');
  setAvatarState('explaining');
  const res=document.getElementById('courseResult');
  res.innerHTML=`<div class="card"><b>🔍 ${{link}} থেকে Content তুলছি... (Groq + Gemini + Claude Haiku Free)</b><div style="margin-top:12px">✅ 5 Modules Generated - সহজ বাংলায় (মুদির দোকান বাদ)</div><div style="margin-top:12px"><div style="padding:10px;background:#F8F9FA;border-radius:8px;margin:6px 0">Module 1: Digital Dominance - ডিজিটাল মানে অনলাইনে বেশি মানুষের কাছে পৌঁছানো</div><div style="padding:10px;background:#F8F9FA;border-radius:8px;margin:6px 0">Module 2: Customer Journey - কাস্টমার কিভাবে তোমাকে খুঁজে পায়</div><div style="padding:10px;background:#F8F9FA;border-radius:8px;margin:6px 0">Module 3: Content Strategy - সহজ ভাষায় কনটেন্ট বানানো</div><div style="padding:10px;background:#F8F9FA;border-radius:8px;margin:6px 0">Module 4: Data & Analytics - ডাটা দেখে সিদ্ধান্ত</div><div style="padding:10px;background:#F8F9FA;border-radius:8px;margin:6px 0">Module 5: Growth Hack - দ্রুত বড় হওয়ার টিপস</div></div><button class="btnPrimary" style="margin-top:12px">📝 Quiz Start (3 MCQ) + 📜 Certificate</button></div>`;
  setTimeout(()=>setAvatarState('idle'), 2000);
}}

// Buttons
document.getElementById('btnBrain').onclick=()=>{{ alert('🧠 Brain Drawer - 14 Features: Knowledge Graph, Decision Journal, Life OS, Meeting Capture, Multi-Agent Orchestrator, Business Decision Engine, Cashflow OS, Finance Bridge, Scenario Planning, Deep Work, Opportunity Finder, Translator, Voice, Vault - All in Left Sidebar Now'); setAvatarState('explaining'); }};
document.getElementById('btnMic').onclick=()=>{{ 
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SpeechRecognition) return alert('Mic not supported');
  const rec=new SpeechRecognition(); rec.lang='bn-BD'; rec.start();
  rec.onresult=(e)=>{{ document.getElementById('searchInput').value=e.results[0][0].transcript; doSearch(); }};
}};
document.getElementById('btnDoodle').onclick=()=>{{ alert('🎨 Festival Doodle: Feb 21 Bhasha, Mar 26 Independence, Apr 14 Pohela Boishakh, Eid, Durga Puja, Dec 16 Victory, Dec 25 Christmas - Asia/Dhaka'); }};

// Greeting
const hour=new Date().getHours();
let greet='Good morning';
if(hour>=12 && hour<17) greet='Good afternoon';
else if(hour>=17) greet='Good evening';
document.getElementById('greeting').textContent=`${{greet}}, Mahmudul! 👋`;
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_PAGE

@app.get("/health")
async def health():
    return {"status":"Aria V15 Final - Dashboard + Hexa Brain + Universal Course + Simple Bangla + Avatar State Machine - Idle/Triggered"}

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
