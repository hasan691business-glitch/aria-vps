import os, json, urllib.request
from typing import List, Dict
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()
GROQ_API_KEY=os.getenv("GROQ_API_KEY","")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY","")
OPENROUTER_API_KEY=os.getenv("OPENROUTER_API_KEY","")
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY","")
GITHUB_TOKEN=os.getenv("GITHUB_TOKEN","")
SUPABASE_URL=os.getenv("SUPABASE_URL","").rstrip("/")
SUPABASE_KEY=os.getenv("SUPABASE_KEY","")
chat_history: List[Dict]=[]

def _post(url, headers, payload):
    try:
        req=urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {"_error": str(e)}

def completion(messages, model):
    try:
        if model=="groq":
            d=_post("https://api.groq.com/openai/v1/chat/completions", {"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}, {"model":"llama-3.1-8b-instant","messages":messages,"max_tokens":900})
            return d["choices"][0]["message"]["content"], "groq-8b"
        if model=="chatgpt":
            d=_post("https://api.openai.com/v1/chat/completions", {"Authorization":f"Bearer {OPENAI_API_KEY}","Content-Type":"application/json"}, {"model":"gpt-4o-mini","messages":messages,"max_tokens":900})
            return d["choices"][0]["message"]["content"], "chatgpt-free"
        if model=="github":
            d=_post("https://models.github.ai/inference/chat/completions", {"Authorization":f"Bearer {GITHUB_TOKEN}","Content-Type":"application/json"}, {"model":"openai/gpt-4o-mini","messages":messages,"max_tokens":900})
            return d["choices"][0]["message"]["content"], "github-models"
        if model=="openrouter":
            d=_post("https://openrouter.ai/api/v1/chat/completions", {"Authorization":f"Bearer {OPENROUTER_API_KEY}","Content-Type":"application/json"}, {"model":"meta-llama/llama-3.1-8b-instruct:free","messages":messages,"max_tokens":900})
            return d["choices"][0]["message"]["content"], "openrouter-free"
        if model=="gemini":
            prompt="\n".join([m.get("content","") for m in messages])
            d=_post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}", {"Content-Type":"application/json"}, {"contents":[{"parts":[{"text":prompt}]}]})
            return d["candidates"][0]["content"]["parts"][0]["text"], "gemini-flash"
        if model=="groq70":
            d=_post("https://api.groq.com/openai/v1/chat/completions", {"Authorization":f"Bearer {GROQ_API_KEY}","Content-Type":"application/json"}, {"model":"llama-3.3-70b-versatile","messages":messages,"max_tokens":900})
            return d["choices"][0]["message"]["content"], "groq-70b"
    except Exception as e:
        return None, str(e)
    return None, "no-model"

def call_hexa(messages):
    for m in ["groq","chatgpt","github","openrouter","gemini","groq70"]:
        t, name = completion(messages, m)
        if t:
            return t, name
    return None, "all-busy"

def smart_fallback(q):
    ql=q.lower()
    if any(w in ql for w in ["kemon","how are you"]):
        return "ভালো আছি Mahmudul! তুমি কেমন আছো? আজ কোন কোর্সটা বাংলায় সহজ ভাবে করবে?"
    if any(w in ql for w in ["future","safe","skill","ki shikhbo"]):
        return "ভবিষ্যতের জন্য সেফ থাকতে এই ৪ টা কোর্স বাংলায় করো:\n1. Google AI Essentials - 5 ঘণ্টা - Free - Certificate আছে\n2. Nvidia AI Course - 6 ঘণ্টা - Free - Certificate আছে\n3. Claude Academy - 3 ঘণ্টা - Free\n4. Coursera Digital Marketing - 8 ঘণ্টা - Free to Learn\nকোনটা দিয়ে শুরু করবে? নাম লেখো।"
    if any(w in ql for w in ["course","shikhte"]):
        return "তুমি কোন কোর্স করতে চাও? 1. Google AI Essentials 2. Nvidia 3. Claude 4. Coursera - নাম লেখো বা Link দাও, আমি বাংলায় ৫ টা Module বানিয়ে দিচ্ছি।"
    return f"বুঝেছি Mahmudul। তুমি বললে: {q} - আমি বাংলায় সহজ ভাবে বুঝিয়ে দিচ্ছি। কোন কোর্স করতে চাও? Google, Nvidia, Claude, Coursera - নাম লেখো।"

def save_memory(role, content):
    chat_history.append({"role":role,"content":content})
    if len(chat_history)>40:
        chat_history.pop(0)
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            req=urllib.request.Request(f"{SUPABASE_URL}/rest/v1/aria_memory", data=json.dumps({"role":role,"content":content[:2000]}).encode(), headers={"apikey":SUPABASE_KEY,"Authorization":f"Bearer {SUPABASE_KEY}","Content-Type":"application/json","Prefer":"return=minimal"}, method="POST")
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass

def detect_source(link):
    l=(link or "").lower()
    if "google" in l: return "Google"
    if "nvidia" in l: return "Nvidia"
    if "claude" in l or "anthropic" in l: return "Claude"
    if "youtube" in l or "youtu.be" in l: return "YouTube"
    if "coursera" in l: return "Coursera"
    return "General"

def make_course(title, link):
    src=detect_source(link)
    topics=["পরিচয় ও বেসিক ধারণা","মূল কাজটা কিভাবে হয়","বাস্তব উদাহরণ দিয়ে শেখা","ভুলগুলো ও সতর্কতা","প্র্যাকটিস ও পরের ধাপ"]
    mods=[]
    for i,t in enumerate(topics,1):
        mods.append({"no":i,"title":f"Module {i}: {t}","desc":f"{title} - {t}। সহজ বাংলায় শিখবে। English Term (বাংলা অর্থ) সহ। উদাহরণ: মোবাইল / ফেসবুক / ইউটিউব দিয়ে।","quiz":[{"q":f"Module {i} এর মূল বিষয় কোনটা?","opts":["বেসিক ধারণা ও ব্যবহার","শুধু ইংরেজি মুখস্থ","কিছুই না"],"ans":0},{"q":"শেখার সবচেয়ে ভালো উপায় কোনটা?","opts":["উদাহরণ দিয়ে প্র্যাকটিস","শুধু পড়া"],"ans":0},{"q":"পরের ধাপে কি করবে?","opts":["প্র্যাকটিস + Quiz","ছেড়ে দেওয়া"],"ans":0}]})
    return {"title":title,"source":src,"link":link,"briefing":f"{title} - ১ পাতার সারাংশ: এই কোর্সটা {src} এর। ৫ টা Module এ ভাগ করা। প্রতিটা Module ~২ মিনিটে পড়া যায়। সহজ বাংলায়, Technical শব্দের বাংলা অর্থ সহ। শেষে Quiz দিবে, তারপর আসল জায়গায় গিয়ে পরীক্ষা দিয়ে আসল Certificate নিবে।","modules":mods,"exam_link":link,"certificate_note":"বাংলায় শিখে শেষ করো, তারপর আসল Course এর Link এ গিয়ে পরীক্ষা দাও - সেখান থেকে আসল Certificate পাবে।"}

class ChatIn(BaseModel):
    message: str = ""
class CourseIn(BaseModel):
    title: str = ""
    link: str = ""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML

@app.post("/api/chat")
async def api_chat(inp: ChatIn):
    q=(inp.message or "").strip()
    if not q:
        return {"response":"কি জানতে চাও Mahmudul? Course এর নাম লেখো বা Link দাও।","model":"aria"}
    save_memory("user", q)
    msgs=[{"role":"system","content":"You are Aria, personal AI agent for Mahmudul Hasan. Answer in simple Bangla Class 8 level. Explain hard English technical words as English Term (Bangla meaning). Use daily-life examples mobile/Facebook/YouTube. No Mudir Dokan example unless user asks about business/shop/accounting."}]
    for h in chat_history[-4:]:
        msgs.append({"role":h["role"] if h["role"] in ("user","assistant") else "user","content":h["content"]})
    msgs.append({"role":"user","content":q})
    txt, model = call_hexa(msgs)
    if not txt:
        txt=smart_fallback(q); model="smart"
    save_memory("assistant", txt)
    return {"response":txt,"model":model}

@app.post("/api/course")
async def api_course(inp: CourseIn):
    title=inp.title or inp.link or "Course"
    link=inp.link or ""
    return make_course(title, link)

@app.get("/api/suggest")
def suggest():
    return {"courses":[{"name":"Google AI Essentials","why":"AI এর বেসিক - সবার জন্য","duration":"5 ঘণ্টা","free":"Free","cert":"Certificate আছে","link":"https://grow.google/ai-essentials/"},{"name":"Nvidia AI Course","why":"Deep Learning ও AI - চাকরির জন্য","duration":"6 ঘণ্টা","free":"Free","cert":"Certificate আছে","link":"https://learn.nvidia.com"},{"name":"Claude Academy","why":"Prompt + AI Agent শেখা","duration":"3 ঘণ্টা","free":"Free","cert":"Free","link":"https://claude.ai/docs"},{"name":"Coursera Digital Marketing","why":"Marketing + Business","duration":"8 ঘণ্টা","free":"Free to Learn","cert":"Paid Certificate","link":"https://coursera.org"}]}

HTML = '<!DOCTYPE html><html lang="bn"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Aria - Personal AI Agent</title><style>*{box-sizing:border-box}body{margin:0;font-family:system-ui,Arial,sans-serif;background:#fff;color:#111}.top{position:sticky;top:0;background:#fff;border-bottom:1px solid #eee;display:flex;gap:10px;align-items:center;padding:10px 14px;z-index:10}.top input{flex:1;padding:12px 14px;border:1px solid #ddd;border-radius:999px;font-size:15px}.chip{background:#FEF7E0;border:1px solid #f5d97e;padding:6px 10px;border-radius:999px;font-size:13px;white-space:nowrap}.menuBtn{display:none}.layout{display:flex;gap:16px;max-width:1280px;margin:0 auto;padding:14px}.left{width:250px;flex-shrink:0;position:sticky;top:64px;height:calc(100vh - 80px);overflow-y:auto}.left a{display:block;padding:9px 10px;border-radius:10px;text-decoration:none;color:#222;font-size:14px}.left a:hover{background:#F3E8FD}.center{flex:1;min-width:0}.right{width:280px;flex-shrink:0}.hero{background:linear-gradient(135deg,#DCEEFF,#E8F0FE 55%,#F3E8FD);border-radius:18px;padding:18px;display:flex;gap:14px;align-items:center}.hero h1{margin:0 0 6px;font-size:26px}.avatar{width:170px;height:210px;object-fit:contain;flex-shrink:0;transition:transform .35s}.btn{background:#1a73e8;color:#fff;border:0;padding:10px 16px;border-radius:999px;font-size:14px;cursor:pointer}.card{background:#fff;border:1px solid #eee;border-radius:16px;padding:14px;margin-top:14px}.grid4{display:grid;grid-template-columns:1fr 1fr;gap:12px}.skill{border-radius:14px;padding:14px}.s1{background:#F3E8FD}.s2{background:#FCE8E6}.s3{background:#E6F4EA}.s4{background:#FEF7E0}.courseRow{display:flex;gap:10px;flex-wrap:wrap}.courseRow button{border:0;padding:10px 14px;border-radius:999px;color:#fff;cursor:pointer;font-weight:700}.g{background:#4285F4}.n{background:#76B900}.c{background:#D97757}.co{background:#0056D2}.y{background:#FF0000}.prof{display:flex;gap:10px;align-items:center;margin-top:14px;border:1px solid #eee;border-radius:14px;padding:10px}.footer{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:center;padding:16px;color:#666;font-size:13px;border-top:1px solid #eee;margin-top:14px}.chatPage{display:none;max-width:900px;margin:0 auto;padding:14px}.msg{padding:10px 12px;border-radius:14px;margin:8px 0;max-width:85%}.me{background:#E8F0FE;margin-left:auto}.ai{background:#F1F3F4}.inputRow{display:flex;gap:8px;position:sticky;bottom:0;background:#fff;padding:10px 0}.inputRow input{flex:1;padding:12px;border:1px solid #ddd;border-radius:999px}.mic{width:44px;height:44px;border-radius:50%;border:0;background:conic-gradient(#4285F4,#EA4335,#FBBC05,#34A853,#4285F4);color:#fff;font-size:18px;cursor:pointer}.bottomNav{display:none}.drawer{display:none}@media(max-width:900px){.left,.right{display:none}.menuBtn{display:inline-block}.layout{padding:10px}.hero{flex-direction:column;text-align:center}.avatar{width:130px;height:160px}.bottomNav{display:flex;position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #eee;justify-content:space-around;padding:10px;z-index:20}.bottomNav button{border:0;background:0;font-size:13px}.drawer{position:fixed;top:0;left:0;width:260px;height:100%;background:#fff;z-index:30;overflow-y:auto;padding:14px;box-shadow:0 0 20px rgba(0,0,0,.2)}.drawer.open{display:block}body{padding-bottom:60px}}</style></head><body>\n<div class="top"><button class="menuBtn" onclick="document.getElementById(\'drawer\').classList.toggle(\'open\')">☰</button><b>Aria</b><input id="topSearch" placeholder="Search skills, courses, Google, Nvidia, Claude..." onkeydown="if(event.key===\'Enter\')openChat()"><span class="chip">🔥 7 Day</span><span class="chip">📚 3 Courses</span><button class="mic" onclick="startMic()">🎤</button></div>\n<div id="drawer" class="drawer"><b>Menu</b><div id="drawerLinks"></div><button onclick="document.getElementById(\'drawer\').classList.remove(\'open\')">Close</button></div>\n<div id="dash"><div class="layout"><div class="left" id="leftNav"></div><div class="center"><div class="hero"><div style="flex:1"><h1>Good morning, Mahmudul! 👋</h1><p>আজ কোন কোর্সটা বাংলায় সহজ ভাবে করবে? আমি তোমাকে শেখাবো, Quiz নিবো, তারপর আসল জায়গায় পরীক্ষা দিয়ে Certificate নিবে।</p><div style="margin-top:12px;background:#fff;border-radius:14px;padding:12px"><b>Continue Learning - Google AI Essentials - 60%</b><div style="height:8px;background:#eee;border-radius:99px;margin:8px 0"><div style="width:60%;height:8px;background:#1a73e8;border-radius:99px"></div></div><button class="btn" onclick="startCourse(\'Google AI Essentials\',\'https://grow.google/ai-essentials/\')">Continue →</button></div></div><div class="avatar" style="font-size:80px">👩\u200d🏫</div></div>\n<div class="card"><b>Build Your Skills</b><div class="grid4" style="margin-top:10px"><div class="skill s1">💼 Business<br><small>12 Courses</small></div><div class="skill s2">💰 Finance<br><small>10 Courses</small></div><div class="skill s3">🎯 Deep Work<br><small>18 Courses</small></div><div class="skill s4">🌱 Personal Growth<br><small>24 Courses</small></div></div></div>\n<div class="card"><b>Popular Courses - বাংলায় সহজ ভাবে করো</b><div class="courseRow" style="margin-top:10px"><button class="g" onclick="startCourse(\'Google AI Essentials\',\'https://grow.google/ai-essentials/\')">Google</button><button class="n" onclick="startCourse(\'Nvidia AI Course\',\'https://learn.nvidia.com\')">Nvidia</button><button class="c" onclick="startCourse(\'Claude Academy\',\'https://claude.ai/docs\')">Claude</button><button class="co" onclick="startCourse(\'Coursera Digital Marketing\',\'https://coursera.org\')">Coursera</button><button class="y" onclick="startCourse(\'YouTube Course\',\'https://youtube.com\')">YouTube</button></div><div style="margin-top:10px"><input id="courseLink" placeholder="Course Link Paste করো - যেকোনো Link" style="width:100%;padding:11px;border:1px solid #ddd;border-radius:999px"><button class="btn" style="margin-top:8px" onclick="startCourse(document.getElementById(\'courseLink\').value||\'Course\', document.getElementById(\'courseLink\').value)">Course শুরু করো →</button></div></div>\n<div class="card" id="courseBox" style="display:none"></div>\n<div class="card"><b>Course Suggester - ভবিষ্যতের জন্য কি শিখবো?</b><div id="suggestBox"></div><button class="btn" onclick="loadSuggest()">Suggest করো</button></div></div>\n<div class="right"><div class="card"><b>Daily Goal</b><div style="font-size:28px;text-align:center;margin:10px 0">15 / 20 min</div><div style="text-align:center">Mon ✓ Tue ✓ Wed ✓ Thu ✓ Fri ○</div></div><div class="card"><b>Decision Journal</b><div>Hit Rate 78%</div><div style="height:8px;background:#eee;border-radius:99px;margin:8px 0"><div style="width:78%;height:8px;background:#0f9d58;border-radius:99px"></div></div><small>Coming in V16 - এখন Dashboard Preview</small></div><div class="card"><b>Knowledge Graph</b><small>Course → Skill → Certificate - Preview - V16 তে পুরোটা</small></div><div class="card" style="border:1px dashed #FB8C00;background:#FEF7E0"><b>🎁 Gift Box 3/5</b><div>প্রতিদিন ১ টা Course শেষ করলে Gift খুলবে</div></div></div></div></div>\n<div id="chatPage" class="chatPage"><button onclick="backDash()">← Back to Dashboard</button><h2>Aria Chat</h2><div style="display:flex;gap:8px"><button onclick="newThread()">✏️ New Thread</button><input placeholder="Search threads 🔍" style="flex:1;padding:10px;border:1px solid #ddd;border-radius:999px"></div><div id="chatArea" style="min-height:300px;margin-top:10px"></div><div class="inputRow"><input id="chatInput" placeholder="লেখো... Course এর নাম বা Link দাও" onkeydown="if(event.key===\'Enter\')sendChat()"><button class="mic" onclick="startMic()">🎤</button><button class="btn" onclick="sendChat()">Send</button></div><div style="margin-top:10px;color:#666;font-size:13px">Recent: বাচ্চাদের ভিটামিন ডি • Vitamin D3 and K2 Supplement • ম্যাগনেসিয়াম গ্লা</div></div>\n<div class="footer"><span>Created by Mahmudul Hasan | Aria Super Brain V15</span><span style="display:inline-flex;gap:8px;align-items:center;border:1px solid #eee;border-radius:999px;padding:4px 10px">👤 Mahmudul Hasan - Level 12 • Creator</span></div>\n<div class="bottomNav"><button onclick="showDash()">🏠 Home</button><button onclick="openChat()">💬 Chat</button><button onclick="showDash()">📚 Course</button></div>\n<script>\nvar leftItems=["Super Brain","Course Hunter - Universal","Translator+TTS","Mood Dress","Vault","Timeline Calendar","Voice Skill bn-BD","Telegram/Phone","LinkedIn Auto","Course Suggest","Auto Skill Saver","Quiz Cert","PWA","Knowledge Graph - V16","Decision Journal - V16","Life OS - V16","Meeting Capture - V16","Multi-Agent - V16","Business Decision - V17","Cashflow - V17","Finance Bridge - V17","Scenario - V17","Deep Work - V17","Opportunity Finder - V17"];\nvar navHtml=leftItems.map(function(x){return \'<a href="#" onclick="navClick(\\\'\'+x+\'\\\');return false">\'+x+\'</a>\'}).join(\'\')+\'<div class="prof"><div style="width:36px;height:36px;border-radius:50%;background:#5B4636;color:#fff;display:flex;align-items:center;justify-content:center">M</div><div><b>Mahmudul Hasan</b><br><small>Level 12 • Creator</small></div></div><div style="margin-top:10px;background:#F3E8FD;border-radius:12px;padding:10px"><b>Aria Plus Upgrade</b><br><small>সহজ বাংলায় সব Course</small></div>\';\ndocument.getElementById(\'leftNav\').innerHTML=navHtml;document.getElementById(\'drawerLinks\').innerHTML=navHtml;\nfunction navClick(x){if(x.indexOf(\'Course\')>=0||x.indexOf(\'Suggest\')>=0){loadSuggest()}else{openChat();addMsg(\'ai\',x+\' - এইটা V16 / V17 তে আসবে। এখন V15 তে Course + Chat + Suggest কাজ করছে।\')}}\nfunction showDash(){document.getElementById(\'dash\').style.display=\'block\';document.getElementById(\'chatPage\').style.display=\'none\';window.scrollTo(0,0)}\nfunction backDash(){showDash()}\nfunction openChat(){document.getElementById(\'dash\').style.display=\'none\';document.getElementById(\'chatPage\').style.display=\'block\';var q=document.getElementById(\'topSearch\').value;if(q){document.getElementById(\'chatInput\').value=q;sendChat()}}\nfunction newThread(){document.getElementById(\'chatArea\').innerHTML=\'\';addMsg(\'ai\',\'নতুন Thread শুরু হলো Mahmudul। কোন Course বাংলায় করবে?\')}\nfunction addMsg(who,txt){var d=document.createElement(\'div\');d.className=\'msg \'+(who===\'me\'?\'me\':\'ai\');d.textContent=(who===\'me\'?\'তুমি: \':\'Aria: \')+txt;document.getElementById(\'chatArea\').appendChild(d)}\nasync function sendChat(){var inp=document.getElementById(\'chatInput\');var q=inp.value.trim();if(!q)return;addMsg(\'me\',q);inp.value=\'\';try{var r=await fetch(\'/api/chat\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({message:q})});var j=await r.json();addMsg(\'ai\',j.response)}catch(e){addMsg(\'ai\',\'ভালো আছি Mahmudul! তুমি কোন Course করতে চাও?\')}}\nasync function loadSuggest(){var r=await fetch(\'/api/suggest\');var j=await r.json();var h=j.courses.map(function(c){return \'<div style="border:1px solid #eee;border-radius:12px;padding:10px;margin:8px 0"><b>\'+c.name+\'</b> - \'+c.why+\'<br><small>\'+c.duration+\' • \'+c.free+\' • \'+c.cert+\'</small><br><button class="btn" style="margin-top:6px" onclick="startCourse(\\\'\'+c.name+\'\\\',\\\'\'+c.link+\'\\\')">বাংলায় শুরু করো</button></div>\'}).join(\'\');document.getElementById(\'suggestBox\').innerHTML=h}\nasync function startCourse(title,link){showDash();var box=document.getElementById(\'courseBox\');box.style.display=\'block\';box.innerHTML=\'Loading... বাংলায় সহজ ভাবে বানাচ্ছি...\';try{var r=await fetch(\'/api/course\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({title:title,link:link})});var j=await r.json();var mods=j.modules.map(function(m){return \'<div style="border:1px solid #eee;border-radius:12px;padding:12px;margin:8px 0"><b>\'+m.title+\'</b><p>\'+m.desc+\'</p><b>Quiz - ৩ টা MCQ</b><div>\'+m.quiz.map(function(q){return \'<div style="margin:6px 0">\'+q.q+\'<br>\'+q.opts.map(function(o){return \'<label style="display:block"><input type="radio"> \'+o+\'</label>\'}).join(\'\')+\'</div>\'}).join(\'\')+\'</div><button onclick="alert(\\\'Quiz শেষ! ভালো করেছো Mahmudul।\\\')">Quiz শেষ</button></div>\'}).join(\'\');box.innerHTML=\'<h3>\'+j.title+\' - \'+j.source+\'</h3><p>\'+j.briefing+\'</p>\'+mods+\'<div style="background:#E6F4EA;border-radius:12px;padding:12px;margin-top:10px"><b>Certificate</b><p>\'+j.certificate_note+\'</p><button class="btn" onclick="makeCert(\\\'\'+j.title+\'\\\')">Certificate বানাও (PNG)</button><br><a href="\'+j.exam_link+\'" target="_blank">আসল জায়গায় পরীক্ষা দাও →</a></div>\';box.scrollIntoView()}catch(e){box.innerHTML=\'Course বানাতে সমস্যা হলো। আবার চেষ্টা করো।\'}}\nfunction makeCert(title){var c=document.createElement(\'canvas\');c.width=800;c.height=500;var x=c.getContext(\'2d\');x.fillStyle=\'#fff\';x.fillRect(0,0,800,500);x.fillStyle=\'#1a73e8\';x.font=\'bold 36px Arial\';x.fillText(\'Certificate\',280,100);x.fillStyle=\'#111\';x.font=\'24px Arial\';x.fillText(\'Mahmudul Hasan\',280,200);x.font=\'18px Arial\';x.fillText(title,180,260);x.fillText(\'Aria Super Brain V15 - Completed in Simple Bangla\',120,320);var a=document.createElement(\'a\');a.download=\'aria-certificate.png\';a.href=c.toDataURL();a.click()}\nfunction startMic(){try{var rec=new (window.SpeechRecognition||window.webkitSpeechRecognition)();rec.lang=\'bn-BD\';rec.onresult=function(e){document.getElementById(\'chatInput\').value=e.results[0][0].transcript;openChat();sendChat()};rec.start()}catch(e){alert(\'Mic এই Browser এ চলছে না - লিখে পাঠাও।\')}}\nloadSuggest();\n</script></body></html>\n'
