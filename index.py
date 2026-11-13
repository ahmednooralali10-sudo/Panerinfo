import time, requests, urllib3, os
from Crypto.Cipher import AES
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from flask import Flask, request, send_file, jsonify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

CDN = "https://cdn.jsdelivr.net/gh/ShahGCreator/icon@main/PNG"
K = b'Yg&tc%DEuh6%Zc^8'
V = b'6oyZDr22E3ychjM%'

FONT_URL = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/notosans/NotoSans-Bold.ttf"
FONT = None

def get_font():
    global FONT
    if FONT: return FONT
    try:
        r = requests.get(FONT_URL, timeout=10)
        FONT = BytesIO(r.content)
    except:
        FONT = None
    return FONT

def vr(n):
    d = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n: b |= 0x80
        d.append(b)
        if not n: break
    return bytes(d)

def pb(F):
    p = bytearray()
    for f, v in F.items():
        if isinstance(v, bool):
            p.extend(vr((f << 3) | 0)); p.extend(vr(1 if v else 0))
        elif isinstance(v, int):
            p.extend(vr((f << 3) | 0)); p.extend(vr(v))
        elif isinstance(v, str):
            d = v.encode(); p.extend(vr((f << 3) | 2)); p.extend(vr(len(d))); p.extend(d)
        elif isinstance(v, (bytes, bytearray)):
            d = bytes(v); p.extend(vr((f << 3) | 2)); p.extend(vr(len(d))); p.extend(d)
    return bytes(p)

def rv(data, pos):
    r = 0; s = 0
    while pos < len(data):
        b = data[pos]; pos += 1
        r |= (b & 0x7F) << s
        if not (b & 0x80): break
        s += 7
    return r, pos

def parse(data):
    f = {}; pos = 0; n = len(data)
    while pos < n:
        try: k, pos = rv(data, pos)
        except: break
        fn = k >> 3; wt = k & 7
        try:
            if wt == 0: v, pos = rv(data, pos)
            elif wt == 2: ln, pos = rv(data, pos); v = data[pos:pos+ln]; pos += ln
            elif wt == 5: v = data[pos:pos+4]; pos += 4
            elif wt == 1: v = data[pos:pos+8]; pos += 8
            else: break
        except: break
        f.setdefault(fn, []).append(v)
    return f

def enc(k, i, p):
    pl = 16 - (len(p) % 16)
    return AES.new(k, AES.MODE_CBC, i).encrypt(p + bytes([pl]*pl))

def oauth(uid, pwd):
    H = {"User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)", "Content-Type": "application/x-www-form-urlencoded"}
    try:
        R = requests.post("https://100067.connect.garena.com/oauth/guest/token/grant", headers=H, data={"uid": uid, "password": pwd, "response_type": "token", "client_type": "2", "client_id": "100067"}, verify=False, timeout=15)
    except: return None
    if R.status_code != 200: return None
    J = R.json()
    if "access_token" not in J or "open_id" not in J: return None
    return {"access_token": J["access_token"], "open_id": J["open_id"]}

def major_login(at, oi):
    P = {}
    P[3] = time.strftime("%Y-%m-%d %H:%M:%S"); P[4] = "free fire"; P[5] = 1; P[7] = "1.132.9"
    P[8] = "Android OS 14 / API-34 (UP1A.231005.007/V816.0.15.0.UNQMIXM)"
    P[9] = "Handheld"; P[10] = "Grameenphone"; P[11] = "CarrierDataNetwork"
    P[12] = 1666; P[13] = 750; P[14] = "352"; P[15] = "ARM64 FP ASIMD AES | 2400 | 8"
    P[16] = 5563; P[17] = "Mali-G57 MC2"
    P[18] = "OpenGL ES 3.2 v1.r32p1-01eac0.0a0b917d9265b4c01be9925306306139"
    P[19] = "Google|9cc73f7a-91f6-40f6-87ec-5b67e597eb8c"; P[20] = "59.152.5.188"
    P[21] = "en"; P[22] = oi; P[23] = "8"; P[24] = "Handheld"
    P[25] = "Xiaomi 2312DRAABI"; P[26] = "BD"; P[29] = at; P[30] = 1
    P[41] = "Grameenphone"; P[42] = "Cellular"
    P[57] = "7428b253defc164018c604a1ebbfebdf"
    P[60] = 109685; P[61] = 58294; P[62] = 797; P[63] = 18000; P[64] = 58818; P[65] = 109685
    P[66] = 58818; P[67] = 109685; P[73] = 2
    P[74] = "/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/lib/arm64"
    P[76] = 1
    P[77] = "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/base.apk"
    P[78] = 3; P[79] = 2; P[81] = "64"; P[83] = "2019121229"; P[85] = 3; P[86] = "OpenGLES2"
    P[87] = 4095; P[88] = 8
    P[89] = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    P[90] = "Dhaka"; P[91] = "C"; P[92] = 8043; P[93] = "android"
    P[94] = "KqsHT4XbSZhqerDNUhjbS3DxG/4+I62zQU2tZFJN91kBUICAlZ5yujshLKvjlk/KiShfKfis8EeB1PMhFHIodWPncZC4fCHYF3TcTwNj95aWY/S3"
    P[95] = 111207; P[96] = '{"cur_rate":[60,90,120],"support_etc2":false}'
    P[97] = 1; P[98] = 1; P[99] = "4"; P[100] = "4"; P[102] = "GQ]        e"; P[103] = 1
    P[104] = 45174; P[105] = 1
    P[106] = "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|a4332cb1c1a84e51dd77441e4856ed5a"
    P[107] = "1.9393e7b8e53e8aeb"
    H = {"User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)", "Accept": "*/*", "Accept-Encoding": "deflate, gzip", "X-GA-SV": str(int(time.time())), "Authorization": "Bearer ", "X-GA": "v1 1", "ReleaseVersion": "OB55", "Content-Type": "application/x-www-form-urlencoded", "X-Unity-Version": "2018.4.12f1"}
    try:
        R = requests.post("https://loginbp.ppmainecoonghj.com/MajorLogin", headers=H, data=enc(K, V, pb(P)), verify=False, timeout=20)
    except: return None
    if R.status_code not in (200, 201) or not R.content: return None
    body = R.content
    f = parse(body)
    j = f.get(8, [None])[0]
    s = f.get(10, [None])[0]
    if isinstance(j, bytes):
        try: jwt = j.decode()
        except: jwt = None
    else: jwt = j
    if not jwt:
        f = parse(body[64:]) if len(body) > 64 else {}
        j = f.get(8, [None])[0]
        s = f.get(10, [None])[0]
        if isinstance(j, bytes):
            try: jwt = j.decode()
            except: jwt = None
        else: jwt = j
    if not jwt: return None
    server = s.decode() if isinstance(s, bytes) else "https://clientbp.ppmainecoonghj.com"
    if not server.startswith("http"): server = "https://" + server
    return jwt, server

def get_player(uid, jwt, server):
    p = enc(K, V, pb({1: int(uid), 2: 7}))
    H = {"Expect": "100-continue", "Authorization": f"Bearer {jwt}", "X-Unity-Version": "2018.4.11f1", "X-GA": "v1 1", "ReleaseVersion": "OB55", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)", "Host": server.replace("https://", "").replace("http://", "").split("/")[0], "Connection": "Keep-Alive", "Accept-Encoding": "gzip"}
    try:
        R = requests.post(server + "/GetPlayerPersonalShow", headers=H, data=p, timeout=15, verify=False)
    except: return None
    if R.status_code != 200: return None
    return parse(R.content)

def sub(fields, k):
    v = fields.get(k)
    if not v: return {}
    v = v[0]
    if isinstance(v, bytes): return parse(v)
    return v if isinstance(v, dict) else {}

def g(d, k):
    if not isinstance(d, dict): return None
    v = d.get(k)
    if isinstance(v, list): v = v[0] if v else None
    if isinstance(v, bytes):
        try: return v.decode()
        except: return v.hex()
    return v

def load_img(item_id):
    if not item_id: return Image.new("RGBA", (100, 100), (30, 30, 30, 255))
    try:
        r = requests.get(f"{CDN}/{item_id}.png", timeout=15)
        if r.status_code != 200: return Image.new("RGBA", (100, 100), (30, 30, 30, 255))
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except: return Image.new("RGBA", (100, 100), (30, 30, 30, 255))

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "ok", "msg": "Use /api/banner?paner=UID"})

@app.route('/api/banner', methods=['GET'])
def generate_banner():
    # يقرأ paner أولاً، وإذا ما لقاه يقرأ uid
    uid = request.args.get('paner') or request.args.get('uid')
    
    if not uid or not uid.isdigit():
        return jsonify({"error": "Valid UID required (?paner=12345)"}), 400

    try:
        acc = oauth("4555614870", "S7LHR6RDFK17-S1X_TEAM")
        if not acc: return jsonify({"error": "OAuth failed"}), 500
        
        res = major_login(acc["access_token"], acc["open_id"])
        if not res: return jsonify({"error": "Major login failed"}), 500
        
        jwt, server = res
        raw = get_player(uid, jwt, server)
        if not raw: return jsonify({"error": "Player not found or API failed"}), 404
        
        bi = sub(raw, 1)
        ci = sub(raw, 6)
        
        name = g(bi, 3) or "Unknown"
        avatar_id = g(bi, 12)
        banner_id = g(bi, 11)
        guild_name = g(ci, 2) or "No Guild"
        
        avatar = load_img(avatar_id)
        banner = load_img(banner_id)
        
        HEIGHT = 400
        WIDTH = 1000
        
        bg = Image.new("RGBA", (WIDTH, HEIGHT), (20, 20, 20, 255))
        
        if banner_id:
            banner = banner.resize((WIDTH, HEIGHT), Image.LANCZOS)
            bg.paste(banner, (0, 0))
            overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 160))
            bg = Image.alpha_composite(bg, overlay)
        
        avatar = avatar.resize((280, 280), Image.LANCZOS)
        mask = Image.new("L", (280, 280), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 280, 280), fill=255)
        bg.paste(avatar, (40, 60), mask=mask)
        
        draw = ImageDraw.Draw(bg)
        font_path = get_font()
        
        font_name = ImageFont.truetype(font_path, 60) if font_path else ImageFont.load_default()
        font_guild = ImageFont.truetype(font_path, 40) if font_path else ImageFont.load_default()
        font_uid = ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default()
        
        x = 360
        draw.text((x + 2, 72), str(name), font=font_name, fill="black")
        draw.text((x, 70), str(name), font=font_name, fill="white")
        draw.text((x + 2, 162), str(guild_name), font=font_guild, fill="black")
        draw.text((x, 160), str(guild_name), font=font_guild, fill="white")
        draw.text((x + 2, 232), str(uid), font=font_uid, fill="black")
        draw.text((x, 230), str(uid), font=font_uid, fill="#bbbbbb")
        
        img_io = BytesIO()
        bg.save(img_io, format='PNG')
        img_io.seek(0)
        
        return send_file(img_io, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
