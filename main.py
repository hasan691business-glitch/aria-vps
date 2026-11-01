import os, json, glob, datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Flexible Loader - Handles x5f names too
def load_text_file(possible_names):
    for name in possible_names:
        for file in glob.glob("**/"+name, recursive=True):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    return f.read()
            except:
                pass
        if os.path.exists(name):
            try:
                with open(name, "r", encoding="utf-8") as f:
                    return f.read()
            except:
                pass
    return ""

def load_json_file(possible_names):
    text = load_text_file(possible_names)
    try:
        return json.loads(text) if text else {}
    except:
        return {}

WARDROBE = load_json_file(["wardrobe.json", "wardrobe.json.txt"])
SYSTEM_PROMPT = load_text_file(["aria_system_prompt.txt", "aria_x5f_system_x5f_prompt.txt"])
CALENDAR = load_text_file(["aria_calendar.md", "aria_x5f_calendar.md"])

if not SYSTEM_PROMPT:
    SYSTEM_PROMPT = "You are Aria - Realistic Bengali Female Assistant - Loving Wife Personality - [Outfit: bengali_traditional]"

PRIVATE_WORDS = ["NID", "password", "bank", "bkash", "pin", "passport", "bKash PIN"]

def is_private(t): return any(w.lower() in t.lower() for w in PRIVATE_WORDS)

def choose_outfit(user_text: str):
    txt = user_text.lower()
    # Festival
    if "boishakh" in txt or "14 april" in txt or "pohela" in txt:
        outfit = "festival_boishakh"
    elif "eid" in txt:
        outfit = "festival_eid"
    elif "valentine" in txt or "14 feb" in txt:
        outfit = "festival_valentine"
    else:
        outfit = None
        if WARDROBE:
            for name, data in WARDROBE.items():
                kws = data.get("keywords", [])
                if any(k.lower() in txt for k in kws):
                    outfit = name
                    break
        if not outfit:
            # Simple Bengali mapping
            if "hotel" in txt or "cox" in txt or "beach" in txt or "sea" in txt:
                outfit = "beach_travel" if "beach_travel" in WARDROBE else "bengali_traditional"
            elif "saree" in txt or "শাড়ি" in txt:
                outfit = "bengali_traditional"
            else:
                outfit = "bengali_traditional"
    
    imgs = []
    if WARDROBE and outfit in WARDROBE:
        imgs = WARDROBE[outfit].get("images_we_created", [])
    img = imgs[0] if imgs else "image_20261030_135636.webp"
    return outfit, img

def get_reply(q: str):
    if is_private(q):
        return "[Outfit: daily_home_drawing_room] ⚠️ Private Info - এটা Private Vault এ আছে, Groq এ পাঠাইনি।"
    
    outfit, image = choose_outfit(q)
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        return f"[Outfit: {outfit} | Image: {image}] Aria Ready - Groq Key আছে, এখন 70B চালু!"

    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        full_sys = SYSTEM_PROMPT + f"\n\nTODAY OUTFIT: {outfit} | IMAGE: {image}\nRule: Start EVERY reply with [Outfit: {outfit} | Image: {image}] exactly."
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content": full_sys},
                {"role":"user","content": q}
            ],
            temperature=0.7,
            max_tokens=800
        )
        ans = resp.choices[0].message.content
        if not ans.startswith("[Outfit:"):
            ans = f"[Outfit: {outfit} | Image: {image}] {ans}"
        return ans
    except Exception as e:
        return f"[Outfit: {outfit} | Image: {image}] Error: {str(e)[:300]}"

@app.get("/")
def home():
    return {"status":"Aria VPS Live - Groq 70B - Auto Dress Active", "wardrobe_count": len(WARDROBE), "outfits": list(WARDROBE.keys())[:10]}

@app.get("/chat")
def chat(q: str):
    return {"q": q, "aria": get_reply(q)}

@app.get("/health")
def health():
    return {"alive": True, "model": "llama-3.3-70b-versatile", "time": str(datetime.datetime.now())}

# Gallery Serve
if os.path.exists("gallery"):
    app.mount("/gallery", StaticFiles(directory="gallery"), name="gallery")
