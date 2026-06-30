import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from pywa import WhatsApp, filters
from pywa.types import Message
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
wa = WhatsApp(os.getenv("WHATSAPP_TOKEN"), phone_id=os.getenv("PHONE_ID"))
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
devices = []

print("""
 ____ ___ ____ _____ _ _____ __ ____ 
| __ )/ _ \| _ \/ ___|| ____| \ | ____|| \/ | _ \ 
| _ \| |_) \___ \| _| | \| | _| |\/| |
| |_) |_| | __/ |___) |___| |\ |___ |_| |
|____/ \___/|_| |____/|_____|_| \_|_____||_| |_|____/ 
           BOSCOVS-MD WHATSAPP BOT v1.0
""")

@app.get("/")
def verify(req: Request):
    if req.query_params.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=req.query_params.get("hub.challenge"))
    return Response(status_code=403)

@app.post("/")
async def webhook(req: Request):
    wa.process_update(await req.json())
    return {"ok": True}

@app.get("/board", response_class=HTMLResponse)
async def board():
    return """<!DOCTYPE html><html><head><title>BOSCOVS-MD</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>body{background:#000;color:#00ff41;font-family:monospace;text-align:center;padding:20px}
    input,button{width:95%;padding:12px;margin:6px;background:#111;color:#00ff41;border:1px solid #00ff41;border-radius:8px}
   .card{background:#0a0a0a;padding:12px;margin:10px 0;border:1px solid #00ff41;border-radius:8px}</style></head><body>
    <h2>BOSCOVS-MD BOARD</h2><input id="name" placeholder="Your name">
    <button onclick="add()">ADD DEVICE</button><div id="list"></div>
    <script>async function add(){await fetch('/add-device',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('name').value})});load();}
    async function load(){document.getElementById('list').innerHTML=(await (await fetch('/devices')).json()).map(d=>`<div class="card">${d.name} - ${d.os}</div>`).join('');}
    load();</script></body></html>"""

@app.post("/add-device")
async def add_device(req: Request):
    ua = req.headers.get("user-agent","").lower()
    os_name = "iOS" if "iphone" in ua or "ipad" in ua else "Android" if "android" in ua else "Desktop"
    devices.append({"name":(await req.json())["name"],"os":os_name})
    return {"ok":True}

@app.get("/devices")
async def get_devices(): return devices

@wa.on_message(filters.command("start"))
def start(_, m: Message): m.reply_text("*BOSCOVS-MD ONLINE*\n/music name\n/video name\n/google text\n/img text\n/ping\n/board")

@wa.on_message(filters.command("ping"))
def ping(_, m: Message): m.reply_text("BOSCOVS-MD PONG ✅")

@wa.on_message(filters.command("google"))
def google(_, m: Message): m.reply_text("https://www.google.com/search?q=" + m.text.split(" ",1)[1])

@wa.on_message(filters.command("img"))
def img(_, m: Message): m.reply_image(image=f"https://source.unsplash.com/800x600/?{m.text.split(' ',1)[1]}", caption="BOSCOVS-MD")

@wa.on_message(filters.command("music"))
def music(_, m: Message):
    q = m.text.split(" ",1)[1]
    with YoutubeDL({'format':'bestaudio','quiet':True}) as ydl:
        info = ydl.extract_info(f"ytsearch1:{q}", download=False)['entries'][0]
        m.reply_audio(audio=info['url'], caption=f"BOSCOVS-MD | {info['title']}")

@wa.on_message(filters.command("video"))
def video(_, m: Message):
    q = m.text.split(" ",1)[1]
    with YoutubeDL({'format':'best[height<=480]','quiet':True}) as ydl:
        info = ydl.extract_info(f"ytsearch1:{q}", download=False)['entries'][0]
        m.reply_video(video=info['url'], caption=f"BOSCOVS-MD | {info['title']}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
