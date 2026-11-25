import asyncio, json, os, time, uuid, random, string, hashlib, hmac, warnings, socket, sys, threading
from datetime import datetime, timezone

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ═══════════════ NETWORK & DNS FIX ═══════════════
_ORIG_GETADDRINFO = socket.getaddrinfo
_GARENA_FAST_IPS = ["43.205.19.48", "34.124.234.158"]

def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host == "100067.connect.garena.com":
        ip = random.choice(_GARENA_FAST_IPS)
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port))]
    if family == 0 or family == socket.AF_UNSPEC:
        family = socket.AF_INET
    return _ORIG_GETADDRINFO(host, port, family, type, proto, flags)

socket.getaddrinfo = _patched_getaddrinfo

import requests
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore")

# ═══════════════ BRANDING ═══════════════
BRAND = "NG SUJEET 143"
PASSWORD_PREFIX = "NG_SUJEET_"

# ═══════════════ EXPIRATION ONLY (No License Key) ═══════════════
_EXPIRY_DATE = datetime(2026, 12, 1, 0, 0, 0, tzinfo=timezone.utc)

def is_system_expired() -> bool:
    return datetime.now(timezone.utc) > _EXPIRY_DATE

# ═══════════════ UI & COLORS ═══════════════
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    CYAN    = "\033[96m"
    MAGENTA = "\033[95m"
    PURPLE  = "\033[38;5;135m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"
    BOX_COLORS = ["\033[95m", "\033[96m", "\033[92m", "\033[93m", "\033[94m"]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    clear()
    print(f"""{C.CYAN}{C.BOLD}
███╗   ██╗ ██████╗     ███████╗██╗   ██╗     ██╗███████╗███████╗████████╗
████╗  ██║██╔════╝     ██╔════╝██║   ██║     ██║██╔════╝██╔════╝╚══██╔══╝
██╔██╗ ██║██║  ███╗    ███████╗██║   ██║     ██║█████╗  █████╗     ██║   
██║╚██╗██║██║   ██║    ╚════██║██║   ██║██   ██║██╔══╝  ██╔══╝     ██║   
██║ ╚████║╚██████╔╝    ███████║╚██████╔╝╚█████╔╝███████╗███████╗   ██║   
╚═╝  ╚═══╝ ╚═════╝     ╚══════╝ ╚═════╝  ╚════╝ ╚══════╝╚══════╝   ╚═╝   
{C.MAGENTA}           ════════════════════════════════════════════
                       ⚡  NG SUJEET v2  ⚡
                  PREMIUM ACCOUNT GENERATOR
           ════════════════════════════════════════════{C.RESET}
""")

def _box(title, lines, color=None):
    color = color or random.choice(C.BOX_COLORS)
    width = 62
    print(f"{color}{C.BOLD}╔{'═' * width}╗")
    print(f"║{title.center(width)}║")
    print(f"╠{'═' * width}╣")
    for ln in lines:
        visible = ln
        for code in [C.WHITE, C.YELLOW, C.CYAN, C.PURPLE, C.GREEN, C.MAGENTA, C.RED, C.RESET, C.BOLD]:
            visible = visible.replace(code, "")
        pad_spaces = max(0, width - 2 - len(visible))
        print(f"║ {ln}{' ' * pad_spaces} ║")
    print(f"╚{'═' * width}╝{C.RESET}")

def expired_banner():
    clear()
    print(f"""{C.RED}{C.BOLD}
╔══════════════════════════════════════╗
║          NG SUJEET v2                 ║
║          LICENSE EXPIRED             ║
╠══════════════════════════════════════╣
║                                      ║
║  Sorry! This Generator has expired.  ║
║                                      ║
║  We cannot provide this service      ║
║  at this moment.                     ║
║                                      ║
║  Please contact: NG SUJEET v2         ║
║                                      ║
╚══════════════════════════════════════╝{C.RESET}
""")

# ═══════════════ PROXY POOL ═══════════════
PROXY_POOL = []
PROXY_INDEX = 0
PROXY_LOCK = threading.Lock()
LAST_PROXY_FETCH = 0

def fetch_fresh_proxies():
    global PROXY_POOL, LAST_PROXY_FETCH
    if time.time() - LAST_PROXY_FETCH < 300 and PROXY_POOL:
        return
    try:
        sources = [
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=2500&country=all&ssl=yes&anonymity=elite",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        ]
        fetched = []
        for src in sources:
            try:
                r = requests.get(src, timeout=2.5)
                fetched.extend([p.strip() for p in r.text.strip().split("\n") if ":" in p])
                if len(fetched) >= 60:
                    break
            except Exception:
                continue
        if fetched:
            with PROXY_LOCK:
                PROXY_POOL = fetched
                LAST_PROXY_FETCH = time.time()
                random.shuffle(PROXY_POOL)
    except Exception:
        pass

def get_next_proxy():
    global PROXY_INDEX
    with PROXY_LOCK:
        if not PROXY_POOL:
            fetch_fresh_proxies()
        if not PROXY_POOL:
            return None
        PROXY_INDEX = (PROXY_INDEX + 1) % len(PROXY_POOL)
        return PROXY_POOL[PROXY_INDEX]

file_lock = asyncio.Lock()

# ═══════════════ TCP BOT ═══════════════
GLOBAL_TCP_STOP = threading.Event()
_ACTIVE_TCP_SOCKETS = []
_TCP_SOCKET_LOCK = threading.Lock()
_TCP_THREAD_STARTED = False
import select

def _tcp_poller():
    while not GLOBAL_TCP_STOP.is_set():
        with _TCP_SOCKET_LOCK:
            now = time.time()
            alive = []
            for s, start, dur in _ACTIVE_TCP_SOCKETS:
                if now - start < dur:
                    try:
                        r, _, _ = select.select([s], [], [], 0)
                        if r and not s.recv(512):
                            s.close(); continue
                        alive.append((s, start, dur))
                    except Exception:
                        try: s.close()
                        except Exception: pass
                else:
                    try: s.close()
                    except Exception: pass
            _ACTIVE_TCP_SOCKETS[:] = alive
        time.sleep(2)

def register_tcp_socket(s, duration=300):
    global _TCP_THREAD_STARTED
    with _TCP_SOCKET_LOCK:
        try:
            s.setblocking(False)
            _ACTIVE_TCP_SOCKETS.append((s, time.time(), duration))
            if not _TCP_THREAD_STARTED:
                _TCP_THREAD_STARTED = True
                threading.Thread(target=_tcp_poller, daemon=True).start()
        except Exception:
            pass

# ═══════════════ 3-FILE STORAGE ═══════════════
_Account_TXT = os.path.join(DIR_PATH, "Account_BD.txt")
_ACCOUNTS_JSON = os.path.join(DIR_PATH, "accounts.json")

async def _save_safe(acc_data, region_json_file):
    async with file_lock:
        try:
            entry = {
                "login_uid": acc_data["uid"],
                "password": acc_data["password"],
                "game_uid": acc_data["account_id"],
                "nickname": acc_data["name"],
                "server": acc_data["region"],
                "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            existing = []
            region_json_file = region_json_file if os.path.isabs(region_json_file) else os.path.join(DIR_PATH, region_json_file)
            if os.path.exists(region_json_file):
                try:
                    with open(region_json_file, "r", encoding="utf-8") as f:
                        c = f.read().strip()
                        if c: existing = json.loads(c)
                except Exception:
                    existing = []
            if not any(str(i.get("game_uid")) == str(entry["game_uid"]) for i in existing):
                existing.append(entry)
                _atomic_json(region_json_file, existing)

            acc_list = []
            if os.path.exists(_ACCOUNTS_JSON):
                try:
                    with open(_ACCOUNTS_JSON, "r", encoding="utf-8") as f:
                        c = f.read().strip()
                        if c: acc_list = json.loads(c)
                except Exception:
                    acc_list = []
            if not any(a.get("uid") == entry["login_uid"] for a in acc_list):
                acc_list.append({"uid": entry["login_uid"], "password": entry["password"]})
                _atomic_json(_ACCOUNTS_JSON, acc_list)

            with open(_Account_TXT, "a", encoding="utf-8") as f:
                f.write(f"{entry['login_uid']}:{entry['password']}\n")
        except Exception as e:
            print(f"{C.RED}[!] Save Error: {e}{C.RESET}")

def _atomic_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    if os.path.exists(path):
        os.remove(path)
    os.replace(tmp, path)

# ═══════════════ ACCOUNT CHECKER ═══════════════
async def check_saved_accounts():
    print(f"\n{C.CYAN}{C.BOLD}═══ 🔍 ACCOUNT CHECKER ═══{C.RESET}")
    print("1. BD Accounts (account_bd.json)")
    print("2. IND Accounts (account_ind.json)")
    print("3. accounts.json (all)")
    ch = input(f"\n{C.CYAN}Select (1-3): {C.RESET}").strip()
    target = {"1": "account_bd.json", "2": "account_ind.json", "3": _ACCOUNTS_JSON}.get(ch)
    if not target:
        print(f"{C.RED}[!] Invalid choice.{C.RESET}")
        input(f"{C.YELLOW}ENTER{C.RESET} to return...")
        return
    if not os.path.exists(target):
        print(f"{C.RED}[!] File '{target}' not found.{C.RESET}")
        input(f"{C.YELLOW}ENTER{C.RESET} to return...")
        return
    try:
        with open(target, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"{C.RED}[!] Read error: {e}{C.RESET}")
        input(f"{C.YELLOW}ENTER{C.RESET}...")
        return
    if not data:
        print(f"{C.YELLOW}[!] No accounts.{C.RESET}")
        input(f"{C.YELLOW}ENTER{C.RESET}...")
        return

    print(f"\n{C.GREEN}[*] Total: {len(data)}{C.RESET}\n")
    print(f"{'#':<4} {'Game UID':<14} {'Name':<16} {'Server':<8} Status")
    print("─" * 62)
    for i, acc in enumerate(data, 1):
        g = acc.get("game_uid") or acc.get("uid", "N/A")
        n = acc.get("nickname", "-")
        srv = acc.get("server", acc.get("region", "-"))
        print(f"{i:<4} {str(g):<14} {str(n):<16} {str(srv):<8} {C.GREEN}VALID{C.RESET}")
    input(f"\n{C.YELLOW}ENTER{C.RESET} to return...")

# ═══════════════ CRYPTO HELPERS ═══════════════
HKEY = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
xK = b'Yg&tc%DEuh6%Zc^8'
xV = b'6oyZDr22E3ychjM%'

def _gen_sig(payload: str) -> str:
    return hmac.new(HKEY.encode(), payload.encode(), hashlib.sha256).hexdigest()

def _aes_encrypt(data: bytes) -> bytes:
    return AES.new(xK, AES.MODE_CBC, xV).encrypt(pad(data, 16))

def EnV_VaRiAnT(n):
    d = []
    while True:
        b = n & 0x7F; n >>= 7
        if n: b |= 0x80
        d.append(b)
        if not n: break
    return bytes(d)

def _proto(fields: dict) -> bytes:
    out = bytearray()
    for f, v in fields.items():
        if isinstance(v, int):
            out += EnV_VaRiAnT((f << 3) | 0) + EnV_VaRiAnT(v)
        elif isinstance(v, (str, bytes)):
            b = v.encode() if isinstance(v, str) else v
            out += EnV_VaRiAnT((f << 3) | 2) + EnV_VaRiAnT(len(b)) + b
        elif isinstance(v, dict):
            nested = _proto(v)
            out += EnV_VaRiAnT((f << 3) | 2) + EnV_VaRiAnT(len(nested)) + nested
    return bytes(out)

def _first_varint(data: bytes, want: int):
    off = 0
    while off < len(data):
        key = shift = 0
        while True:
            b = data[off]; off += 1
            key |= (b & 0x7F) << shift
            if not (b & 0x80): break
            shift += 7
        fn, wt = key >> 3, key & 7
        if wt == 0:
            v = shift = 0
            while True:
                b = data[off]; off += 1
                v |= (b & 0x7F) << shift
                if not (b & 0x80): break
                shift += 7
            if fn == want: return v
        elif wt == 2:
            ln = shift = 0
            while True:
                b = data[off]; off += 1
                ln |= (b & 0x7F) << shift
                if not (b & 0x80): break
                shift += 7
            off += ln
        elif wt == 1: off += 8
        elif wt == 5: off += 4
        else: break
    return None

_PW_STASH: dict = {}
_CUSTOM_NAME = "Account"

def set_custom_name(n):
    global _CUSTOM_NAME
    _CUSTOM_NAME = n.strip() if n.strip() else "Account"

def generate_nickname():
    return f"{_CUSTOM_NAME}{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

def generate_password():
    body = ''.join(random.choices(string.ascii_letters + string.digits, k=26))
    return f"{PASSWORD_PREFIX}{body}"

def get_server_time():
    try:
        r = requests.head("https://www.google.com", timeout=3)
        d = r.headers.get('Date')
        if d:
            dt = datetime.strptime(d, "%a, %d %b %Y %H:%M:%S GMT")
            return int(dt.replace(tzinfo=timezone.utc).timestamp()), dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    return int(time.time()), time.strftime("%Y-%m-%d %H:%M:%S")

_GLOBAL_HTTP_SESSION = requests.Session()
_GLOBAL_HTTP_SESSION.verify = False
_adapter = requests.adapters.HTTPAdapter(pool_connections=500, pool_maxsize=500, max_retries=1)
_GLOBAL_HTTP_SESSION.mount("https://", _adapter)
_GLOBAL_HTTP_SESSION.mount("http://", _adapter)
_GLOBAL_HTTP_SESSION.headers.update({"Accept-Encoding": "gzip, deflate", "Connection": "Keep-Alive"})

MSDK_UA = "GarenaMSDK/4.0.42(NX809J ;Android 9;en;US;app 1.134.14 2024010012;)"

def guest_register(device_id, max_retries=10):
    for attempt in range(max_retries):
        try:
            password = generate_password()
            body = json.dumps({"app_id": 100067, "client_type": 2, "password": password, "source": 2}, separators=(',', ':'))
            headers = {
                "User-Agent": MSDK_UA, "Authorization": f"Signature {_gen_sig(body)}",
                "Accept": "application/json", "Content-Type": "application/json; charset=utf-8",
                "Host": "100067.connect.garena.com", "Connection": "Keep-Alive",
            }
            prox = None
            if attempt > 1:
                p = get_next_proxy()
                if p: prox = {"http": f"http://{p}", "https": f"http://{p}"}
            if prox:
                r = requests.post("https://100067.connect.garena.com/api/v2/oauth/guest:register", headers=headers, data=body, timeout=1.5, proxies=prox, verify=False)
            else:
                r = _GLOBAL_HTTP_SESSION.post("https://100067.connect.garena.com/api/v2/oauth/guest:register", headers=headers, data=body, timeout=1.5, verify=False)
            if r.status_code == 200:
                j = r.json()
                if "data" in j and "uid" in j["data"]:
                    uid = str(j["data"]["uid"])
                    _PW_STASH[uid] = password
                    return uid, password
            elif r.status_code == 429:
                fetch_fresh_proxies(); time.sleep(0.2)
            else:
                time.sleep(0.1)
        except Exception:
            time.sleep(0.1)
    return None, None

def guest_token(uid, max_retries=5):
    pw = _PW_STASH.get(str(uid))
    if not pw: return None
    for attempt in range(max_retries):
        try:
            body = json.dumps({"client_id": 100067, "client_secret": HKEY, "client_type": 2,
                               "password": pw, "response_type": "token", "uid": int(uid)}, separators=(',', ':'))
            headers = {"User-Agent": MSDK_UA, "Accept": "application/json",
                       "Content-Type": "application/json; charset=utf-8",
                       "Host": "100067.connect.garena.com", "Connection": "Keep-Alive"}
            prox = None
            if attempt > 1:
                p = get_next_proxy()
                if p: prox = {"http": f"http://{p}", "https": f"http://{p}"}
            if prox:
                r = requests.post("https://100067.connect.garena.com/api/v2/oauth/guest/token:grant", headers=headers, data=body, timeout=1.5, proxies=prox, verify=False)
            else:
                r = _GLOBAL_HTTP_SESSION.post("https://100067.connect.garena.com/api/v2/oauth/guest/token:grant", headers=headers, data=body, timeout=1.5, verify=False)
            if r.status_code == 200:
                j = r.json()
                if "data" in j and "access_token" in j["data"]:
                    d = j["data"]
                    return {"access_token": d["access_token"], "open_id": d.get("open_id", "")}
            elif r.status_code in (400, 429):
                fetch_fresh_proxies(); time.sleep(0.2)
            time.sleep(random.uniform(0.1, 0.3))
        except Exception:
            time.sleep(0.1)
    return None

def PyL(access_token, open_id, server_time_str, region):
    P = {}
    if region == "IND":
        P[3] = server_time_str; P[4] = "free fire"; P[5] = 1; P[7] = "1.134.14"
        P[8] = "Android OS 14 / API-34 (UP1A.231005.007/E156BXXS6AYD4)"
        P[9] = "Handheld"; P[10] = "airtel"; P[11] = "CarrierDataNetwork"
        P[12] = 2340; P[13] = 1080; P[14] = "295"
        P[15] = "ARM64 FP ASIMD AES | 2200 | 8"; P[16] = 5586
        P[17] = "Mali-G57 MC2"; P[18] = "OpenGL ES 3.2 v1.r38p1"
        P[19] = "Google|f4d8aefb-7549-4778-a92b-2ed885bf9ec4"
        P[20] = "27.61.46.111"; P[21] = "en"; P[22] = open_id; P[23] = "4"
        P[24] = "Handheld"; P[25] = "samsung SM-A155F"; P[26] = "IND"
        P[29] = access_token; P[30] = 1; P[41] = "airtel"; P[42] = "4G"
        P[57] = "7428b253defc164018c604a1ebbfebdf"
        P[60] = 108009; P[61] = 3859; P[62] = 5023; P[64] = 3987
        P[65] = 108009; P[66] = 3987; P[67] = 108009; P[70] = 4; P[73] = 3
        P[74] = "/data/app/~~OlJmIW-Yzl-44x2WnJP4Nw==/com.garena.game.ffi-_eDk_pQQMiFk1YUeqwJBvQ==/lib/arm64"
        P[76] = 3
        P[77] = "dd9d4c174e0472d34b7fd34bd5924bc9|/data/app/~~OlJmIW-Yzl-44x2WnJP4Nw==/com.garena.game.ffi-_eDk_pQQMiFk1YUeqwJBvQ==/base.apk"
        P[78] = 3; P[79] = 2; P[81] = "64"; P[83] = "2019121269"
        P[85] = 3; P[86] = "OpenGLES2"; P[87] = 8191; P[88] = 4
        P[90] = "Coimbatore"; P[91] = "TN"; P[92] = 9570; P[93] = "android"
        P[94] = "KqsHT54jON6bxITmlrRyOrXWBqKqZ4BoqPzT/mhtriAfRt2dt7gC8pnAJfj11alcEUA5sD8BshSYQhxXT9RFmU6YzcI1FKK4MwxJcF4+kvelPD1H"
        P[95] = 111207; P[96] = '{"cur_rate":null,"support_etc2":false}'
        P[97] = 1; P[99] = "4"; P[100] = "4"; P[104] = 11921; P[105] = 1
        P[106] = "https://dl-tata.freefireind.in/live/ABHotUpdates/|https://core-tata.freefireind.in/live/ABHotUpdates/|dff941d41e6e3a9e76f05ed71fdc8d87"
        P[107] = "1.6168622e0868ddbd"
    else:
        P[3] = server_time_str; P[4] = "free fire"; P[5] = 1; P[7] = "1.134.14"
        P[8] = "Android OS 14 / API-34 (UP1A.231005.007/V816.0.15.0.UNQMIXM)"
        P[9] = "Handheld"; P[10] = "Grameenphone"; P[11] = "CarrierDataNetwork"
        P[12] = 1666; P[13] = 750; P[14] = "352"
        P[15] = "ARM64 FP ASIMD AES | 2400 | 8"; P[16] = 5563
        P[17] = "Mali-G57 MC2"; P[18] = "OpenGL ES 3.2 v1.r32p1-01eac0.0a0b917d9265b4c01be9925306306139"
        P[19] = "Google|9cc73f7a-91f6-40f6-87ec-5b67e597eb8c"
        P[20] = "59.152.5.188"; P[21] = "en"; P[22] = open_id; P[23] = "8"
        P[24] = "Handheld"; P[25] = "Xiaomi 2312DRAABI"; P[26] = "BD"
        P[29] = access_token; P[30] = 1; P[41] = "Grameenphone"; P[42] = "Cellular"
        P[57] = "7428b253defc164018c604a1ebbfebdf"
        P[60] = 109685; P[61] = 58294; P[62] = 797; P[63] = 18000
        P[64] = 58818; P[65] = 109685; P[66] = 58818; P[67] = 109685; P[73] = 2
        P[74] = "/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/lib/arm64"
        P[76] = 1
        P[77] = "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/base.apk"
        P[78] = 3; P[79] = 2; P[81] = "64"; P[83] = "2019121229"
        P[85] = 3; P[86] = "OpenGLES2"; P[87] = 4095; P[88] = 8
        P[89] = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
        P[90] = "Dhaka"; P[91] = "C"; P[92] = 8043; P[93] = "android"
        P[94] = "KqsHT4XbSZhqerDNUhjbS3DxG/4+I62zQU2tZFJN91kBUICAlZ5yujshLKvjlk/KiShfKfis8EeB1PMhFHIodWPncZC4fCHYF3TcTwNj95aWY/S3"
        P[95] = 111207; P[96] = '{"cur_rate":[60,90,120],"support_etc2":false}'
        P[97] = 1; P[98] = 1; P[99] = "4"; P[100] = "4"; P[102] = "GQ]        e"
        P[103] = 1; P[104] = 45174; P[105] = 1
        P[106] = "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|a4332cb1c1a84e51dd77441e4856ed5a"
        P[107] = "1.9393e7b8e53e8aeb"
    return AES.new(xK, AES.MODE_CBC, xV).encrypt(pad(_proto(P), 16))

def MajorLogin(payload, sync_ts, login_host, release_version, max_retries=6):
    url = f"https://{login_host}/MajorLogin"
    headers = {"User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
               "Accept": "*/*", "Accept-Encoding": "deflate, gzip",
               "X-GA-SV": str(sync_ts), "Authorization": "Bearer ", "X-GA": "v1 1",
               "ReleaseVersion": release_version,
               "Content-Type": "application/x-www-form-urlencoded",
               "X-Unity-Version": "2018.4.12f1"}
    for attempt in range(max_retries):
        try:
            prox = None
            if attempt > 1:
                p = get_next_proxy()
                if p: prox = {"http": f"http://{p}", "https": f"http://{p}"}
            R = requests.post(url, headers=headers, data=payload, timeout=1.8, proxies=prox, verify=False)
            if R.status_code in (200, 201) and R.content and len(R.content) > 64:
                return R.content
            elif R.status_code in (400, 429):
                fetch_fresh_proxies(); time.sleep(0.2)
            time.sleep(random.uniform(0.1, 0.3))
        except Exception:
            time.sleep(0.1)
    return None

def ExtractMajorLogin(ml_resp):
    if not ml_resp or len(ml_resp) <= 64: return None
    body = ml_resp[64:] if ml_resp[0] != 0x0a else ml_resp
    f = {}
    pos, n = 0, len(body)
    while pos < n:
        try:
            key = shift = 0
            while True:
                b = body[pos]; pos += 1
                key |= (b & 0x7F) << shift
                if not (b & 0x80): break
                shift += 7
        except Exception: break
        fn, wt = key >> 3, key & 0x07
        try:
            if wt == 0:
                val = shift = 0
                while True:
                    b = body[pos]; pos += 1
                    val |= (b & 0x7F) << shift
                    if not (b & 0x80): break
                    shift += 7
            elif wt == 2:
                ln = shift = 0
                while True:
                    b = body[pos]; pos += 1
                    ln |= (b & 0x7F) << shift
                    if not (b & 0x80): break
                    shift += 7
                val = body[pos:pos+ln]; pos += ln
            elif wt == 5: val = body[pos:pos+4]; pos += 4
            elif wt == 1: val = body[pos:pos+8]; pos += 8
            else: break
        except Exception: break
        f.setdefault(fn, []).append(val)

    jwt_b = f.get(8, [None])[0]; url_b = f.get(10, [None])[0]
    key_b = f.get(22, [None])[0]; iv_b = f.get(23, [None])[0]
    if not jwt_b or not isinstance(key_b, bytes) or not isinstance(iv_b, bytes): return None
    return {"jwt": jwt_b.decode(), "url": url_b.decode() if url_b else None, "key": key_b, "iv": iv_b}

def BuildAuthToken(uid, jwt_str, ts, key, iv, mode="online"):
    ah = f"{int(uid):x}".zfill(16)
    enc = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(jwt_str.encode(), 16)).hex()
    th = f"{int(ts):x}"
    if len(th) % 2: th = "0" + th
    tsz = f"{len(enc)//2:02x}"
    pad_ = "00000" if mode == "chat" else "0000000000000"
    return f"9015{ah}{th}{pad_}{tsz}{enc}"

def _TuneSock(s):
    s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    try:
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 15)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)
    except Exception: pass

FIELD22_HEX = ("47475245010101008202000048d0c6912766f3f72cedb7201cf7a7098d74888b9eb4070aec58e1cd29f26559fb3b8d32cc302d17c00fe629c20b94bece7b75867df5d2c63ad694fe754b06ca5f200fcc316532ee2d705c69d64e873a976d73f1bada85dedb1271bfd90f13e6eb1f607b197ea5741550829c40b5b9ab59f305fd460c462ac2ba9a50561b453053303105b3329e6aef4bf468da4ae276023c26fa39932d0ec40d874a849550e72f67b2f1e0974f835df6a8b5f3cd886483abd0da7cbccc6cd4df72aa5b104e63ea2bfeaf7b08d5176d2a9b128b8630468f625392397e2e43f63969e842f6e2c001c6da1cab2660eacaf8fdbc20520e1316a538406c480f3eefae89171f542b6aa5a8da797673764b0b05ac26a31511759cbdad6826ab621d208e0cf5282a76eb8453f8f768fd8d52dd408d64c0063149605de6af9b34bdf22202ea8d132cd797bbfb6ac72455000c493b18085957df0144f73b36b1aec77f8f5ca3c838d1c2b7e065db59df08b0e8b87dc6769a12ed8ed729c5a3c58468afc6f0c52604a3448b3dbca6a587ccff08bbdcd22e767169949942742142f52f837bfe97f49c801cad0b2d3fd22101188bd5e1dafeeabc4259abe0c7f2b96c5ded89eac5843e7cb95177755b6cf63edd6abaccf03fadcb7084988b2c28d7f3574da8775f6a2de3a429513837ad8319fefa6eb9bfaa1a1a8b06f9d58778c953ab1fc38b4569879416e65625d15ce233cbfffb2cbd56aeb16e07e05da7a52bff20f1d4e11643a328b28105ab74256507f9fccab3bfd0575b4b6fb0fdbeb448c9a1e4e780a4dfdabb2b487cd83f42764816d9a6f3e313349b95ce6fb5ca6dbb60d2f5c3b5157da94c84e2b7ce0e47e5dcbf4d7c146089b104979a5627e4f70a0a8d51a9ce358761119e0eb5ec3d2d7fea4f87227f9dfeaeb3a4ccd2b4cd38caa754c827d45ff0d00d520db11a49fdb6f0b4010203")
KEYSTREAM = [0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30]

def major_register(open_id, access_token, nickname, sync_ts, lang, login_host, release_version, client_version, max_retries=6):
    encoded = "".join(chr(ord(c) ^ KEYSTREAM[i % len(KEYSTREAM)]) for i, c in enumerate(open_id))
    fields = {1: nickname, 2: access_token, 3: open_id, 5: 102000007, 6: 4, 7: 1, 8: 4,
              13: 1, 14: encoded.encode('latin1'), 15: lang, 16: 1,
              20: client_version, 21: 1, 22: bytes.fromhex(FIELD22_HEX)}
    payload = _aes_encrypt(_proto(fields))
    headers = {"User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
               "Accept": "*/*", "X-GA-SV": str(sync_ts), "Authorization": "Bearer",
               "X-GA": "v1 1", "ReleaseVersion": release_version,
               "Content-Type": "application/x-www-form-urlencoded",
               "X-Unity-Version": "2018.4.12f1", "Host": login_host, "Connection": "Keep-Alive"}
    for attempt in range(max_retries):
        try:
            prox = None
            if attempt > 1:
                p = get_next_proxy()
                if p: prox = {"http": f"http://{p}", "https": f"http://{p}"}
            if prox:
                r = requests.post(f"https://{login_host}/MajorRegister", data=payload, headers=headers, timeout=1.5, proxies=prox, verify=False)
            else:
                r = _GLOBAL_HTTP_SESSION.post(f"https://{login_host}/MajorRegister", data=payload, headers=headers, timeout=1.5, verify=False)
            if r.status_code == 200:
                aid = _first_varint(r.content, 3)
                if aid: return str(aid)
            elif r.status_code in (400, 429):
                fetch_fresh_proxies(); time.sleep(0.2)
            time.sleep(random.uniform(0.1, 0.3))
        except Exception:
            time.sleep(0.1)
    return None

def _bg_post_generation(url, login_payload, sync_ts, jwt, account_id, key, iv, release_version):
    try:
        headers = {"User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)",
                   "Accept": "*/*", "Accept-Encoding": "deflate, gzip",
                   "X-GA-SV": str(sync_ts), "Authorization": f"Bearer {jwt}",
                   "X-GA": "v1 1", "ReleaseVersion": release_version,
                   "Content-Type": "application/x-www-form-urlencoded",
                   "X-Unity-Version": "2018.4.12f1"}
        r = _GLOBAL_HTTP_SESSION.post(f"{url}/GetLoginData", headers=headers, data=login_payload, timeout=4)
        if r.status_code == 200 and r.content:
            gl = r.content; gl_p = {}; pos = 0
            while pos < len(gl):
                try:
                    key2 = shift = 0
                    while True:
                        b = gl[pos]; pos += 1
                        key2 |= (b & 0x7F) << shift
                        if not (b & 0x80): break
                        shift += 7
                    fn, wt = key2 >> 3, key2 & 0x07
                    if wt == 0:
                        val = shift = 0
                        while True:
                            b = gl[pos]; pos += 1
                            val |= (b & 0x7F) << shift
                            if not (b & 0x80): break
                            shift += 7
                    elif wt == 2:
                        ln = shift = 0
                        while True:
                            b = gl[pos]; pos += 1
                            ln |= (b & 0x7F) << shift
                            if not (b & 0x80): break
                            shift += 7
                        val = gl[pos:pos+ln]; pos += ln
                    elif wt == 5: val = gl[pos:pos+4]; pos += 4
                    elif wt == 1: val = gl[pos:pos+8]; pos += 8
                    else: break
                    gl_p.setdefault(fn, []).append(val)
                except Exception: break
            func_addr = gl_p.get(14, [None])[0]
            if func_addr and isinstance(func_addr, bytes):
                ip, port = func_addr.decode().split(":")
                s = socket.create_connection((ip, int(port)), timeout=3)
                _TuneSock(s)
                auth_hex = BuildAuthToken(account_id, jwt, sync_ts, key, iv, mode="online")
                s.sendall(bytes.fromhex(auth_hex))
                register_tcp_socket(s, 300)
    except Exception:
        pass

async def generate_one(sem, progress, region, lang, json_file, login_host, release_version, client_version):
    async with sem:
        sync_ts, sync_time_str = get_server_time()
        device_id = "02-" + str(uuid.uuid4())

        uid, password = await asyncio.to_thread(guest_register, device_id)
        if not uid: return None
        token_data = await asyncio.to_thread(guest_token, uid)
        if not token_data: return None
        open_id = token_data["open_id"]; access_token = token_data["access_token"]
        nickname = generate_nickname()

        account_id = await asyncio.to_thread(major_register, open_id, access_token, nickname, sync_ts, lang, login_host, release_version, client_version)
        if not account_id: return None

        login_payload = await asyncio.to_thread(PyL, access_token, open_id, sync_time_str, region)
        ml = await asyncio.to_thread(MajorLogin, login_payload, sync_ts, login_host, release_version)
        if not ml: return None
        ad = await asyncio.to_thread(ExtractMajorLogin, ml)
        if not ad: return None

        url = ad["url"] or f"https://client.{region.lower()}.freefiremobile.com"
        threading.Thread(target=_bg_post_generation,
                         args=(url, login_payload, sync_ts, ad["jwt"], account_id, ad["key"], ad["iv"], release_version),
                         daemon=True).start()

        acc_data = {"uid": uid, "password": password, "account_id": account_id,
                    "name": nickname, "region": region,
                    "open_id": open_id, "access_token": access_token,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        await _save_safe(acc_data, json_file)
        await progress("success", acc_data)
        return acc_data

# ═══════════════ MAIN ═══════════════
async def main():
    if is_system_expired():
        expired_banner()
        return

    while True:
        if is_system_expired():
            expired_banner()
            break

        banner()
        print(f"{C.CYAN}{C.BOLD}═══ MAIN MENU ═══{C.RESET}")
        print("1. Generate New Accounts")
        print("2. Check Saved Accounts")
        print("3. Exit")
        choice = input(f"\n{C.CYAN}Select (1-3): {C.RESET}").strip()

        if choice == "2":
            await check_saved_accounts(); continue
        elif choice == "3":
            print(f"{C.GREEN}Goodbye! — {BRAND}{C.RESET}"); break
        elif choice != "1":
            print(f"{C.RED}Invalid!{C.RESET}"); time.sleep(1); continue

        print(f"\n{C.MAGENTA}╔══ SERVER SELECTION ══╗{C.RESET}")
        print("1. BD Server")
        print("2. IND Server")
        sc = input(f"{C.CYAN}Select (1-2): {C.RESET}").strip()
        if sc == "2":
            region = "IND"; lang = "en"
            json_file = "account_ind.json"
        else:
            region = "BD"; lang = "en"
            json_file = "account_bd.json"
        login_host = "loginbp.ppmainecoonghj.com"
        release_version = "OB55"; client_version = "1.134.14"

        print(f"\n{C.MAGENTA}╔══ ACCOUNT NAME ══╗{C.RESET}")
        name_input = input(f"{C.CYAN}Prefix (Enter for 'SUJEET'): {C.RESET}").strip()
        set_custom_name(name_input or "SUJEET")

        try:
            target = int(input(f"\n{C.CYAN}How many accounts? {C.RESET}").strip())
            if target <= 0: continue
        except Exception:
            print(f"{C.RED}[!] Invalid count.{C.RESET}"); continue

        print(f"\n{C.YELLOW}[*] Region: {region} | Target: {target}{C.RESET}\n")

        concurrency = 25
        success_count = 0
        fail_streak = 0
        progress_lock = asyncio.Lock()
        start_ts = time.time()

        async def progress(status, data=None):
            nonlocal success_count, fail_streak
            async with progress_lock:
                if status == "success":
                    success_count += 1; fail_streak = 0
                    color = random.choice(C.BOX_COLORS)
                    _box(
                        f"  ✅  {BRAND} — SUCCESS  [{success_count}/{target}]  ",
                        [f"{C.WHITE}Name       : {C.YELLOW}{data['name']}",
                         f"{C.WHITE}Account ID : {C.CYAN}{data['account_id']}",
                         f"{C.WHITE}Login UID  : {C.PURPLE}{data['uid']}",
                         f"{C.WHITE}Password   : {C.GREEN}{data['password']}",
                         f"{C.WHITE}Server     : {C.MAGENTA}{data['region']}"],
                        color
                    )
                else:
                    fail_streak += 1
                    if fail_streak % 10 == 0:
                        print(f"  {C.DIM}{C.YELLOW}⚠ {fail_streak} soft-fails (rotating proxies...){C.RESET}")

        sem = asyncio.Semaphore(concurrency)
        stop_event = asyncio.Event()

        async def worker(_):
            while not stop_event.is_set() and success_count < target:
                try:
                    r = await generate_one(sem, progress, region, lang, json_file, login_host, release_version, client_version)
                    if r is None:
                        await progress("fail")
                        await asyncio.sleep(random.uniform(0.1, 0.4))
                except Exception:
                    await progress("fail")
                    await asyncio.sleep(random.uniform(0.1, 0.4))

        workers = [asyncio.create_task(worker(i)) for i in range(20)]
        while success_count < target:
            await asyncio.sleep(0.2)
            if all(w.done() for w in workers):
                workers = [asyncio.create_task(worker(i)) for i in range(20)]
        stop_event.set()
        for w in workers: w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

        elapsed = time.time() - start_ts
        _box(
            f"  🎉  {BRAND} — COMPLETE  ",
            [f"Total Generated : {success_count}/{target}",
             f"Server          : {region}",
             f"Time            : {elapsed:.1f}s",
             f"Saved to        : {json_file}, {_Account_TXT}, {_ACCOUNTS_JSON}",
             f"Credit          : {BRAND}"],
            C.GREEN
        )

        if _ACTIVE_TCP_SOCKETS:
            print(f"\n{C.CYAN}[*] 🤖 TCP Bots: keeping {len(_ACTIVE_TCP_SOCKETS)} accounts ONLINE for 5 min...{C.RESET}")
            try:
                for rem in range(300, 0, -10):
                    print(f"\r{C.GREEN}[ONLINE]{C.RESET} Time remaining: {rem//60:02d}:{rem%60:02d}  ", end="", flush=True)
                    await asyncio.sleep(10)
                print()
            except (KeyboardInterrupt, asyncio.CancelledError):
                GLOBAL_TCP_STOP.set()

        input(f"\n{C.YELLOW}ENTER{C.RESET} to return to menu...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{C.RED}[!] Exited.{C.RESET}")